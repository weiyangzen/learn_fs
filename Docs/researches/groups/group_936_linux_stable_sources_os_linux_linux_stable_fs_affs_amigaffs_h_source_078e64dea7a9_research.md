# Group Research: linux-stable AFFS/AFS source batch

Scope: `Docs/research_subset_a.md`

Files researched:
- `sources/os/linux/linux-stable/fs/affs/amigaffs.h`
- `sources/os/linux/linux-stable/fs/affs/bitmap.c`
- `sources/os/linux/linux-stable/fs/affs/dir.c`
- `sources/os/linux/linux-stable/fs/affs/file.c`
- `sources/os/linux/linux-stable/fs/affs/inode.c`
- `sources/os/linux/linux-stable/fs/affs/namei.c`
- `sources/os/linux/linux-stable/fs/affs/super.c`
- `sources/os/linux/linux-stable/fs/affs/symlink.c`
- `sources/os/linux/linux-stable/fs/afs/Kconfig`
- `sources/os/linux/linux-stable/fs/afs/Makefile`
- `sources/os/linux/linux-stable/fs/afs/addr_list.c`
- `sources/os/linux/linux-stable/fs/afs/addr_prefs.c`
- `sources/os/linux/linux-stable/fs/afs/afs.h`
- `sources/os/linux/linux-stable/fs/afs/afs_cm.h`
- `sources/os/linux/linux-stable/fs/afs/afs_fs.h`
- `sources/os/linux/linux-stable/fs/afs/afs_vl.h`
- `sources/os/linux/linux-stable/fs/afs/callback.c`
- `sources/os/linux/linux-stable/fs/afs/cell.c`
- `sources/os/linux/linux-stable/fs/afs/cm_security.c`
- `sources/os/linux/linux-stable/fs/afs/cmservice.c`
- `sources/os/linux/linux-stable/fs/afs/dir.c`
- `sources/os/linux/linux-stable/fs/afs/dir_edit.c`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/affs/amigaffs.h -->
# File Research: sources/os/linux/linux-stable/fs/affs/amigaffs.h

This header defines the AFFS on-disk constants and packed-ish layout structures used by the rest of the AFFS driver.

Major contents:
- Defines Amiga filesystem magic values for OFS, FFS, international, dircache, and MUFS variants.
- Defines AFFS primary and secondary block types: `T_SHORT`, `T_LIST`, `T_DATA`, `ST_ROOT`, `ST_USERDIR`, `ST_FILE`, `ST_SOFTLINK`, `ST_LINKFILE`, and `ST_LINKDIR`.
- Defines `AFFS_ROOT_BMAPS` as the number of bitmap pointers stored directly in the root block.
- Defines `AFFS_EPOCH_DELTA`, converting Amiga timestamps from the 1978-01-01 epoch to Unix time.

On-disk structure model:
- `struct affs_date` and `struct affs_short_date` describe Amiga date fields as days, minutes, and 1/50-second ticks.
- `struct affs_root_head` and `struct affs_root_tail` describe root block metadata, including bitmap block pointers, bitmap extension pointer, root/disk timestamps, disk name, dircache pointer, and root secondary type.
- `struct affs_head` and `struct affs_tail` describe normal file, directory, link, and extension block headers/tails.
- `struct slink_front` models a symlink header block whose payload is variable-length `symname`.
- `struct affs_data_head` models OFS data blocks, including sequence, size, next block, checksum, and data payload.

Permission definitions:
- The `FIBF_*` constants map Amiga protection bits to Linux mode handling.
- Owner bits are inverted for read/write/delete semantics where `NO*` bits mean denial.
- `FIBF_ARCHIVED` is intentionally cleared by Linux on writes.
- `FIBF_MASK` documents which protection bits Linux mutates.

Key dependencies:
- Used by AFFS helpers in `affs.h` and implementation files to address on-disk fields through endian-aware accessors.
- All multi-byte disk fields are big-endian types, so callers must use `be*_to_cpu()` and `cpu_to_be*()` conversions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/affs/amigaffs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/affs/bitmap.c -->
# File Research: sources/os/linux/linux-stable/fs/affs/bitmap.c

This file owns AFFS bitmap loading, free-space counting, block allocation, block freeing, and bitmap teardown.

Major responsibilities:
- Counts free blocks by summing per-bitmap `bm_free` counters under `s_bmlock`.
- Frees a block by locating its bitmap block, setting the target bit, adjusting the bitmap checksum, marking the bitmap dirty, and incrementing `bm_free`.
- Allocates a block near a goal, scanning bitmap blocks for a set bit, clearing it, fixing the checksum, updating `bm_free`, and returning the physical block number.
- Maintains a cached current bitmap buffer in `s_bmap_bh`/`s_last_bmap` to reduce repeated reads.
- Implements small preallocation by reserving additional free bits in the same 32-bit bitmap word and recording them in the inode’s `i_pa_cnt`/`i_lastalloc`.
- Initializes bitmap state during mount and releases it during unmount or read-only remount.

Bitmap format and accounting:
- Bitmap bit value `1` means free and `0` means allocated.
- Each bitmap block reserves the first 32 bits for checksum storage, so `s_bmap_bits = blocksize * 8 - 32`.
- `affs_init_bitmap()` walks bitmap pointers from the root block and bitmap extension blocks, validates checksums, and calculates free counts with `memweight()`.
- The last bitmap block is corrected so bits beyond the partition end are forced allocated, then the checksum is recomputed.

Error handling:
- Invalid frees outside the partition are reported as AFFS errors.
- Double-free attempts are detected by testing whether the bit is already set.
- Bitmap read failures clear the cached bitmap buffer and return gracefully for free or allocation paths.
- Invalid bitmap checksums cause the filesystem to be mounted read-only rather than trusted for writes.

Concurrency:
- All bitmap mutation and cached bitmap buffer changes are serialized by `s_bmlock`.
- The allocation path updates both the in-memory counter and on-disk bitmap/checksum while the lock is held.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/affs/bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/affs/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/affs/dir.c

This file provides AFFS directory file operations and directory iteration.

Major responsibilities:
- Defines directory `file_operations` with open, release, llseek with cookies, shared iteration, fsync, and leases.
- Defines directory `inode_operations` for create, lookup, link, unlink, symlink, mkdir, rmdir, rename, and setattr.
- Allocates per-open `struct affs_dir_data`, storing the last emitted inode and directory version cookie.
- Implements `affs_readdir()` over AFFS hash table chains.

Directory iteration model:
- AFFS directories store hash buckets in the directory header block.
- `ctx->pos` encodes `hash_pos` in the upper bits and `chain_pos` in the lower 16 bits, offset by two after dot entries.
- If more than 65535 entries are encountered in a chain, the code warns and advances to the next hash bucket.
- On stable inode version, iteration can resume directly from `data->ino`; otherwise it rewalks from the hash bucket and chain position.
- Entries are read from file header blocks, names are taken from `AFFS_TAIL(...)->name`, and emitted with `DT_UNKNOWN`.

Consistency and locking:
- Directory traversal is protected by `affs_lock_dir()`/`affs_unlock_dir()`.
- Inode versioning is used to decide whether cached readdir position state is still valid.
- Buffer heads for the directory and current file header are released on all normal paths.
- Read errors while following chains return `-EIO` where possible and log AFFS errors.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/affs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/affs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/affs/file.c

This file implements AFFS regular-file I/O, block mapping, extension block caching, OFS data-block handling, truncation, preallocation cleanup, and fsync.

Major responsibilities:
- Tracks open count and on last close truncates pending size changes and frees preallocated blocks.
- Maps logical file blocks to AFFS data block numbers through header/extension block tables.
- Allocates and links extension blocks as files grow beyond the block pointer capacity of a single header block.
- Provides normal FFS address-space operations using Linux block helpers.
- Provides OFS-specific address-space operations because OFS stores a data header before each payload.
- Clears the Amiga archived bit on file writes.
- Frees file blocks and extension blocks during shrink/truncate and inode eviction.

Extension block cache:
- `i_ext_bh`/`i_ext_last` cache the last extension block.
- A linear cache `i_lc` stores every Nth extension block key.
- An associative cache `i_ac` stores recently used extension keys.
- `affs_grow_extcache()` allocates and resizes cache density as `i_extcnt` grows.
- `affs_get_extblock_slow()` handles sequential access, cache lookup, fallback chain walking, and extension block allocation.

FFS block mapping:
- `affs_get_block()` validates requested logical blocks, locks the extension cache, locates the extension block, maps an existing data block, and optionally allocates exactly the next block.
- New block allocation updates `mmu_private`, `i_blkcnt`, block pointer table, block count, first-data pointer, checksum, and inode dirty state.
- Direct I/O refuses extending writes beyond `mmu_private`, falling back to buffered allocation.

OFS data handling:
- OFS data blocks have `struct affs_data_head`, so file payload size is `s_data_blksize`, not raw block size.
- `affs_do_read_folio_ofs()` copies payload bytes from AFFS data areas into folios.
- `affs_extent_file_ofs()` fills holes by allocating OFS data blocks, setting headers, zeroing partial tails, and linking `next` pointers.
- `affs_write_begin_ofs()` extends files before writes when needed and ensures folios are fully populated for short-write safety.
- `affs_write_end_ofs()` writes payload into OFS blocks, initializes new data headers, updates per-block size and next links, fixes checksums, and updates file size.

Truncation:
- Growing a file delegates through the mapping write path to allocate or zero the target range.
- Shrinking clears extension caches beyond the retained extension, frees excess data blocks, clears block pointers, fixes checksums, updates `i_blkcnt`/`i_extcnt`, and frees extension blocks in the old tail chain.
- OFS truncation also clears the last retained data block’s `next` pointer.
- Preallocated blocks are always released after truncation.

Synchronization:
- Metadata buffer heads modified by this file are tracked in `i_metadata_bhs`.
- `affs_file_fsync()` waits for writeback, writes the inode synchronously, and syncs the underlying block device.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/affs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/affs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/affs/inode.c

This file translates AFFS on-disk header blocks into Linux inodes, writes inode metadata back, creates new inodes, evicts inodes, handles setattr, and inserts directory entries.

Major responsibilities:
- `affs_iget()` reads a header block, validates checksum/type, initializes AFFS-private inode state, maps Amiga permissions and ownership, and assigns VFS operation tables by secondary type.
- `affs_write_inode()` writes protection, size, UID/GID, and timestamps back to AFFS tail or root-tail fields.
- `affs_setattr()` enforces mount-option restrictions, handles truncate-on-size-change, copies attributes, and converts Linux mode back to Amiga protection bits.
- `affs_evict_inode()` truncates deleted files, syncs metadata for live files, releases extension caches, releases cached extension blocks, frees preallocation, and frees the inode header block on last unlink.
- `affs_new_inode()` allocates a disk block, creates a VFS inode, initializes AFFS private state, and inserts it into the inode hash.
- `affs_add_entry()` initializes a header or link block and inserts it into the parent directory hash table.

Inode decoding:
- Directories receive `affs_dir_inode_operations` and `affs_dir_operations`.
- Regular files receive `affs_file_inode_operations`, `affs_file_operations`, and either `affs_aops` or `affs_aops_ofs`.
- Symlinks receive `affs_symlink_inode_operations` and `affs_symlink_aops`.
- `ST_LINKFILE` entries resolve through `original`; `ST_LINKDIR` is treated as a directory-like inode without full operation setup.
- MUFS UID/GID translation handles `0xffff` specially for root.

Directory entry insertion:
- Hard links allocate a separate link block, set `original`, splice it into the original inode’s `link_chain`, and force the VFS nlink to two.
- New header blocks receive `T_SHORT`, key, AFFS name, secondary type, parent pointer, checksum, and metadata dirty tracking.
- The dentry stores the actual header block number in `d_fsdata`.
- Parent hash insertion is serialized by `affs_lock_dir()`; link-chain updates use `affs_lock_link()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/affs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/affs/namei.c -->
# File Research: sources/os/linux/linux-stable/fs/affs/namei.c

This file implements AFFS pathname operations, dentry hashing/comparison, lookup, creation, deletion, symlink creation, link creation, rename, and export operations.

Major responsibilities:
- Provides DOS and international case-folding functions.
- Defines dentry hash and compare operations that enforce AFFS name limits and optional no-truncate behavior.
- Implements AFFS directory hash calculation.
- Finds directory entries by following the appropriate hash bucket chain.
- Implements VFS lookup, create, mkdir, rmdir, unlink, symlink, link, and rename operations.
- Provides NFS export support through inode-number file handles and parent lookup.

Name handling:
- Names are case-insensitive under either ASCII-only DOS rules or AFFS international rules.
- Names longer than `AFFSNAMEMAX` can compare equal by truncation unless `nofilenametruncate` is active.
- `affs_hash_name()` computes the AFFS on-disk hash by folding each character and using the legacy `hash * 13 + ch` formula modulo directory hash size.

Lookup and object creation:
- `affs_lookup()` locks the parent directory, finds the matching header block, stores the real header block in `d_fsdata`, resolves file hard-link blocks to their original inode, and returns `d_splice_alias()`.
- `affs_create()` and `affs_mkdir()` allocate a new inode, set mode/protection, install file or directory operations, and call `affs_add_entry()`.
- `affs_symlink()` stores AFFS-formatted symlink text in the inode header table area, translating absolute Unix paths into AFFS volume-prefixed form and compressing `.`/`..` path components.
- `affs_link()` creates an `ST_LINKFILE` entry pointing to the original file.

Rename behavior:
- Normal rename removes the old header from its old parent hash, changes the stored name, and inserts it into the new parent hash.
- Existing destinations are removed before insertion unless `RENAME_NOREPLACE` prevents it at VFS level.
- `RENAME_EXCHANGE` removes both headers, swaps names/parents by reinserting each into the opposite location, and marks both metadata buffers dirty.
- Directory hash updates are individually locked by parent directory.

Export support:
- `affs_get_parent()` reads the AFFS parent pointer from the child header.
- `affs_nfs_get_inode()` validates block range then calls `affs_iget()`.
- `affs_export_ops` uses generic 32-bit inode file handle encoding.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/affs/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/affs/super.c -->
# File Research: sources/os/linux/linux-stable/fs/affs/super.c

This file implements AFFS superblock setup, mount option parsing, remount handling, statfs, delayed superblock updates, inode cache lifecycle, and module registration.

Major responsibilities:
- Defines AFFS `super_operations`, file-system type, fs-context operations, and inode slab cache.
- Parses mount options such as `bs`, `mode`, `mufs`, `nofilenametruncate`, `prefix`, `protect`, `reserved`, `root`, `setgid`, `setuid`, `verbose`, and `volume`.
- Finds and validates the AFFS root block across plausible block sizes and root locations.
- Reads the boot block signature to determine OFS/FFS, international, dircache, and MUFS behavior.
- Initializes bitmap state, root inode, dentry operations, export operations, and superblock flags.
- Supports remount/reconfigure by syncing, flushing delayed superblock work, updating mutable options, and allocating/freeing bitmaps as read-write state changes.

Mount probing:
- Starts with device size in 512-byte sectors, sets a large temporary block size, then tries logical block size through page size unless `bs=` fixes it.
- Computes default root block as the middle of the partition after reserved blocks.
- Tries the computed root and one adjacent block to handle odd partition-size rounding.
- Valid root blocks require checksum success, root head primary type `T_SHORT`, and root tail secondary type `ST_ROOT`.

Filesystem variant handling:
- Dircache AFFS variants are forced read-only for writes.
- OFS variants set `SF_OFS` and `SB_NOEXEC`; their data block size is reduced by the OFS data header size.
- International variants set `SF_INTL` and use international dentry operations.
- MUFS variants set `SF_MUFS` and alter UID/GID interpretation.

Superblock writes:
- `affs_commit_super()` updates the root block disk-change timestamp, fixes checksum, marks it dirty, and optionally waits.
- `affs_mark_sb_dirty()` queues delayed writeback using `dirty_writeback_interval`.
- `affs_sync_fs()` commits the root block synchronously or asynchronously depending on VFS request.

Cleanup:
- `affs_kill_sb()` kills the block super, frees bitmap state, releases root buffer, frees symlink prefix, destroys locks, and RCU-frees `sbi`.
- Inode cache creation/destruction is handled at module init/exit.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/affs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/affs/symlink.c -->
# File Research: sources/os/linux/linux-stable/fs/affs/symlink.c

This file implements AFFS symlink page-cache population and symlink inode operations.

Major responsibilities:
- Reads a symlink inode’s AFFS header block.
- Converts AFFS symlink syntax into a Linux path string in the target folio.
- Handles Amiga assign or volume-name prefixes containing `:`.
- Converts doubled slash patterns into parent-directory `..` components.
- Provides address-space operations and inode operations for symlink inodes.

Conversion details:
- If the stored symlink contains `:`, the code prepends the mount’s configured `s_prefix` or `/`, then copies the volume/assign name up to `:`, emits `/`, and continues after the colon.
- The symlink prefix and volume fields are protected by `symlink_lock`.
- Output is capped at 1023 bytes plus NUL.
- `page_get_link` is used as the VFS `.get_link` implementation after the folio is filled.

Error handling:
- Failure to read the symlink header block unlocks the folio and returns `-EIO`.
- Successful reads mark the folio uptodate before unlocking.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/affs/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/afs/Kconfig

This file defines kernel configuration options for the Linux AFS client.

Configuration entries:
- `AFS_FS` is a tristate Andrew File System client option depending on `INET`.
- `AFS_FS` selects `AF_RXRPC`, `DNS_RESOLVER`, `NETFS_SUPPORT`, and `CRYPTO_KRB5`.
- Help text describes the client as experimental and historically read-only/unsecured in the visible prompt text.
- `AFS_DEBUG` enables runtime-controllable debugging messages for the AFS client.
- `AFS_FSCACHE` enables local caching through the generic filesystem cache manager when AFS and FSCACHE linkage modes are compatible.
- `AFS_DEBUG_CURSOR` enables server cursor debugging dumps when server rotation fails.

Build implications:
- Enabling `AFS_FS` pulls in the RxRPC transport and DNS resolver support required by the implementation files in this group.
- `AFS_FSCACHE` gates integration with fscache usage visible in directory and vnode data paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/afs/Makefile

This Makefile builds the AFS client module/object.

Major contents:
- Defines `kafs-y` as the object list for the AFS client.
- Includes address management, cell/server/volume management, callback service, directory operations, file operations, locking, RxRPC client helpers, security, validation, VL service, YFS protocol, writeback, xattrs, mountpoints, and dynroot support.
- Adds `proc.o` conditionally when `CONFIG_PROC_FS` is enabled.
- Hooks the composite object into `obj-$(CONFIG_AFS_FS)` as `kafs.o`.

Relevance to this batch:
- The listed files here are a subset of the full `kafs-y` object.
- `addr_list.o`, `addr_prefs.o`, `callback.o`, `cell.o`, `cm_security.o`, `cmservice.o`, `dir.o`, and `dir_edit.o` are directly included.
- The current files depend on other objects such as `fsclient.o`, `vlclient.o`, `rotate.o`, `server.o`, `volume.o`, `validation.o`, `security.o`, and `internal.h` declarations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/addr_list.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/addr_list.c

This file manages AFS server address lists and DNS-derived VL server address records.

Major responsibilities:
- Allocates, refcounts, RCU-frees, and traces `struct afs_addr_list`.
- Parses delimited textual IPv4/IPv6 address lists with optional `+port` suffixes.
- Builds a one-server VL server list around parsed explicit addresses.
- Queries DNS `afsdb` data for a cell and converts the resolver result into a VL server list.
- Merges IPv4 and IPv6 endpoints into ordered RxRPC peer lists.
- Maintains RxRPC peer appdata backpointers when a server’s address list changes.

Address parsing:
- `afs_parse_text_addrs()` accepts delimiter-separated address strings and adapts `:` delimiter to comma when necessary for IPv6-like input.
- IPv6 addresses can be bracketed.
- Each parsed address is converted with `in4_pton()` or `in6_pton()`.
- Ports are parsed from `+1234`, with range checking.
- Invalid syntax returns `-EINVAL` with trace/debug problem markers; empty input returns `-EDESTADDRREQ`.

Address list ordering:
- IPv4 peers are stored before IPv6 peers.
- Within each family group, peers are sorted by peer pointer.
- Duplicate peers are detected and dropped by releasing the newly looked-up peer.
- Lists cap at `AFS_MAX_ADDRESSES`.

DNS behavior:
- `afs_dns_query()` asks the DNS resolver for `afsdb` data with `srv=1`.
- Resolver output beginning with a NUL record is passed to `afs_extract_vlserver_list()`.
- Plain text output is parsed as comma-separated addresses.
- Zero DNS expiry is normalized to a short default future expiry.

Peer appdata:
- `afs_set_peer_appdata()` sets or clears per-peer appdata for new, removed, or retained peers by walking old and new ordered lists.
- This lets incoming RxRPC/cache-manager security paths recover the owning `afs_server` from peer data.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/addr_list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/addr_prefs.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/addr_prefs.c

This file implements configurable address preferences for AFS server endpoint selection.

Major responsibilities:
- Parses commands written to `/proc/fs/afs/addr_prefs`.
- Maintains an RCU-published sorted preference list.
- Supports adding and deleting UDP IPv4/IPv6 address or subnet priorities.
- Applies current preference priorities to address lists when their version is stale.

Input grammar:
- Commands are split on whitespace up to newline.
- Supported commands are `add udp <IP>[/mask] <prio>` and `del udp <IP>[/mask>`.
- IPv6 addresses may be bracketed.
- Subnet masks default to `/32` for IPv4 and `/128` for IPv6.
- Mask zero and masks larger than the address family width are rejected.
- Only `udp` is accepted as the protocol.

Preference ordering:
- Preferences are partitioned with IPv4 first and IPv6 starting at `ipv6_off`.
- Within a family, entries are sorted by network address and subnet specificity.
- Exact matches update an existing priority.
- More specific subnet matches can be inserted before broader entries.
- The list expands by allocating a larger rounded-up flexible array, capped at 255 entries.

RCU/versioning:
- Writers take the proc file inode lock, clone the old list, apply all commands, publish with `rcu_assign_pointer()`, then release a new version with `smp_store_release()`.
- Old lists are freed with `kfree_rcu()`.
- Address lists store `addr_pref_version`; preference application is skipped if versions already match.
- Readers can use `afs_get_address_preferences()` to avoid RCU locking when the version is unchanged.

Application to endpoints:
- `afs_get_address_preferences_rcu()` walks IPv4 and IPv6 peers in an `afs_addr_list`, extracts remote socket addresses from RxRPC peers, finds the first exact/subnet preference match, and writes the priority into each address slot.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/addr_prefs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/afs.h -->
# File Research: sources/os/linux/linux-stable/fs/afs/afs.h

This header defines common public AFS protocol types, limits, status records, callback records, volume records, and XDR helper structures.

Major definitions:
- Cell, volume, server, filename, pathname, and opaque-field length limits.
- VL and probe lifespan constants.
- Core typedefs for volume IDs, vnode IDs, and data versions.
- Volume type enum for read-write, read-only, and backup volumes.
- File type enum for file, directory, symlink, and invalid.
- Lock type enum and lock wait timeout.
- `struct afs_fid`, combining volume ID, vnode ID, high vnode bits, and unique generation.
- Callback type, callback promise, and callback-break records.
- AFS UUID layout.

Status and metadata:
- `struct afs_file_status` carries size, data version, client/server mtimes, author/owner/group, caller and anonymous access masks, Unix mode, file type, nlink, lock count, and abort status.
- `struct afs_status_cb` combines status with callback data and flags indicating which parts were returned.
- `struct afs_volsync` and `struct afs_volume_status` model volume-level synchronization and quota/status data.

Access model:
- Defines AFS ACL permission bits for read, write, insert, lookup, delete, lock, administer, and user-defined A-H permissions.
- Defines status-change mask bits for mtime, owner, group, mode, and segment size.

Wire/XDR structures:
- `AFS_BLOCK_SIZE` is 1024.
- `struct afs_uuid__xdr` represents UUID fields expanded into big-endian XDR words.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/afs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/afs_cm.h -->
# File Research: sources/os/linux/linux-stable/fs/afs/afs_cm.h

This header defines the AFS cache-manager service constants and callback operation IDs.

Major contents:
- Defines `AFS_CM_PORT` as 7001.
- Defines `CM_SERVICE` service ID as 1.
- Enumerates cache-manager RPC operation numbers:
  - `CBCallBack`
  - `CBInitCallBackState`
  - `CBProbe`
  - `CBGetLock`
  - `CBGetCE`
  - `CBGetXStatsVersion`
  - `CBGetXStats`
  - `CBInitCallBackState3`
  - `CBProbeUuid`
  - `CBTellMeAboutYourself`
- Defines `AFS_CAP_ERROR_TRANSLATION`, advertised by callback capability replies.

Usage:
- `cmservice.c` uses these operation numbers to route incoming server-to-client callback RPCs.
- `cm_security.c` uses service identity and capability constants when handling RxRPC/RxGK security challenges and callback appdata.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/afs_cm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/afs_fs.h -->
# File Research: sources/os/linux/linux-stable/fs/afs/afs_fs.h

This header defines AFS file-service port, service ID, file-service RPC operation numbers, and AFS file-service abort/error codes.

Major contents:
- Defines `AFS_FS_PORT` as 7000 and `FS_SERVICE` as 1.
- Enumerates classic file-service operations including fetch/store data, fetch/store ACL, fetch/store status, remove, create, rename, symlink, link, mkdir, rmdir, callback release, volume info/status, root volume, bulk status, locks, and lookup.
- Enumerates extended operation IDs such as inline bulk status, 64-bit fetch/store data, give-up-all-callbacks, and get-capabilities.
- Defines volume/file service abort codes such as `VNOVNODE`, `VNOVOL`, `VOFFLINE`, `VDISKFULL`, `VOVERQUOTA`, `VMOVED`, `VIO`, and `VSALVAGING`.

Usage:
- Directory operations use these constants indirectly through AFS/YFS operation dispatch tables.
- Callback and security paths check `FS_SERVICE` when routing challenges and callback-related appdata.
- Remote deletion detection maps aborts like `VNOVNODE` into local vnode deletion state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/afs_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/afs_vl.h -->
# File Research: sources/os/linux/linux-stable/fs/afs/afs_vl.h

This header defines AFS and YFS Volume Location service constants, operation IDs, error codes, VLDB record layouts, and VL address XDR structures.

Major contents:
- Defines VL service port 7003, AFS VL service ID 52, and YFS VL service ID 2503.
- Enumerates VL operations for lookup by ID/name, probing, UUID-based lookup, address lookup, YFS endpoint/cell-name lookup, and capabilities.
- Defines VL error codes covering duplicate IDs/names, no entry, bad names, bad servers, permission errors, memory errors, and release state errors.
- Defines YFS server and endpoint selector constants.
- Defines `YFS_MAXENDPOINTS`.

VLDB records:
- `struct afs_vldbentry` models legacy VLDB entries with volume name, volume type, server count, clone ID, flags, type-specific volume IDs, and up to eight server/partition/flag records.
- Server flags indicate RW/RO/BACK volume placement, UUID references, new replication site, and do-not-use status.
- `AFS_VLDB_MAXNAMELEN` is 65.

XDR records:
- `struct afs_ListAddrByAttributes__xdr` models address lookup attributes by IP, index, or UUID.
- `struct afs_uvldbentry__xdr` models UUID-capable VLDB entries with server UUIDs, uniques, partitions, flags, type volume IDs, clone ID, and spare words.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/afs_vl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/callback.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/callback.c

This file handles AFS callback invalidation for vnodes and whole volumes.

Major responsibilities:
- Invalidates mmap mappings after callback breaks by unmapping file page-cache PTEs in workqueue context.
- Handles server-requested callback state reinitialization by expiring callback promises for all volumes known to a server.
- Breaks individual vnode callbacks, clears permit caches, wakes lock waiters, and queues mmap invalidation when needed.
- Looks up volumes by volume ID under RCU/seqlock protection.
- Handles volume-level callback breaks by expiring server and volume callback promises, incrementing the volume callback break counter, and invalidating mmapped vnodes.
- Dispatches batches of callback-break records grouped by volume.

Callback semantics:
- `__afs_break_callback()` clears `AFS_VNODE_NEW_CONTENT`, clears the callback promise, increments `cb_break` only if a promise was present, updates `cb_v_check`, clears permits, and handles lock/mmap side effects.
- Volume callbacks are represented by FID records with vnode and unique both zero.
- Volume-level breaks set `cb_expires_at` to `AFS_NO_CB_PROMISE` for the matching server entry and the volume.
- `cb_v_break` is incremented with release semantics so directory and vnode validation can notice volume-level invalidations.

Concurrency:
- Individual vnode breaks are protected by `cb_lock` seqlock.
- Server volume lists are walked under `server->cell->vs_lock`.
- Volume rb-tree lookup under RCU uses `read_seqbegin_or_lock()` because lockless rb-tree walks can race with mutations.
- Volume-level callback updates take `cb_v_break_lock`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/callback.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/cell.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/cell.c

This file manages AFS cell records, root/workstation cell setup, DNS updates for VL servers, lifecycle references, proc exposure, timers, and garbage collection.

Major responsibilities:
- Looks up cells by name in a network namespace rb-tree.
- Allocates cells with normalized lowercase names, key descriptions, VL server lists, locks, timers, volume/server trees, and dynamic root inode numbers.
- Creates or finds cells through `afs_lookup_cell()`, including preallocation outside locks and duplicate insertion handling.
- Sets or replaces the root/workstation cell from module/proc configuration.
- Refreshes VL server lists from DNS with TTL clamping and DNS status translation.
- Activates cells in procfs, deactivates them, purges servers, and removes dead cells from rb-trees.
- Maintains both reference count and active-use count.

Cell states:
- Cells progress through setting up, unlooked, active, removing, and dead states.
- State changes use release stores and wakeups so waiters observe preceding error/status updates.
- Lookup callers may wait for active/dead unless they are preloading/root/dynroot paths.
- Dead cells return their stored error to lookup callers.

DNS behavior:
- `afs_update_cell()` calls `afs_dns_query()`, maps DNS/resolver errors to `DNS_LOOKUP_*` statuses, clamps expiry between min and max TTL, and replaces the VL server list when useful.
- Configured address lists are treated as `DNS_RECORD_FROM_CONFIG` and can satisfy active lookup without DNS success.
- DNS lookup count is release-published for waiters.

Lifecycle:
- `afs_use_cell()` increments both reference and active counters.
- `afs_unuse_cell()` decrements active, sets an inactivity timestamp, may arm a GC timer, then drops the reference.
- Inactive cells with VL servers are retained for `afs_cell_gc_delay`; live namespace shutdown expires them immediately.
- Final destruction cancels timers/work, RCU-frees the cell, drops VL server lists, alias/root references, anonymous key, dynamic inode ID, and name storage.
- `afs_cell_purge()` unpins root cell and no-GC cells, queues management, and waits for all cells outstanding.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/cell.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/cm_security.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/cm_security.c

This file handles security challenge processing for the AFS cache manager and, when enabled, constructs RxGK callback credentials.

Major responsibilities:
- Processes RxRPC out-of-band challenge packets queued on the AFS socket.
- Routes challenge responses by service ID and security class.
- Supports RxKAD challenge responses when `CONFIG_RXKAD` is enabled.
- Supports RxGK and YFS-RxGK challenge responses when `CONFIG_RXGK` is enabled.
- Creates a cache-manager security keyring and random callback token key for RxGK.
- Builds encrypted YFS callback appdata tokens for file servers.

Challenge routing:
- Only file-service and VL-service IDs are accepted for challenge responses.
- Unknown service/security combinations are rejected with user aborts and AFS unsupported-security abort codes.
- For YFS RxGK file-service challenges, the server is recovered from RxRPC peer appdata and per-server callback appdata is lazily created under `cm_token_lock`.

RxGK token creation:
- `afs_create_token_key()` creates a `kafs` keyring, attaches it to the RxRPC socket, finds AES128 Kerberos enctype support, generates random key material, and stores an `rxrpc_s` key.
- `afs_create_yfs_cm_token()` builds YFS appdata containing initiator and acceptor UUIDs, capabilities, callback key enctype/key, and an encrypted token container.
- Token sizing is calculated with XDR alignment helpers and Kerberos encryption buffer sizing.
- The token embeds callback key material, security level, timestamps/lifetimes, and server UUID identity, then encrypts the token body with Kerberos AEAD helpers.

OOB processing:
- `afs_process_oob_queue()` drains socket OOB messages and responds to challenge packets, freeing each OOB skb afterward.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/cm_security.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/cmservice.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/cmservice.c

This file implements the server-to-client AFS/YFS cache-manager RPC service.

Major responsibilities:
- Routes incoming callback service calls by operation ID.
- Defines call types for callback break, callback-state initialization, probe, probe-UUID, capabilities, and YFS callback break.
- Unmarshals incoming XDR request data in resumable stages.
- Breaks callbacks before replying to preserve cache coherency.
- Sends empty, simple, or abort replies through RxRPC helper functions.
- Cleans up per-call buffers in the call destructor.

Supported operations:
- `CB.CallBack` unmarshals classic AFS FID arrays and callback arrays, validates count limits, and schedules callback breaks.
- `CB.InitCallBackState` discards request data and reinitializes all callback promises associated with the server.
- `CB.InitCallBackState3` unmarshals a UUID and checks it against the server UUID.
- `CB.Probe` replies empty to indicate the cache manager is alive.
- `CB.ProbeUuid` compares the supplied UUID against the client UUID and aborts negatively on mismatch.
- `CB.TellMeAboutYourself` replies with interface UUID and capabilities, including error translation.
- `YFSCB.CallBack` unmarshals 64-bit YFS FIDs and queues the same callback-break work path.

Unmarshalling model:
- Each deliver function uses `call->unmarshall` state to support partial network delivery.
- Temporary extraction, fixed-size buffer extraction, discard iterators, and final call-state checks are used consistently.
- Protocol count mismatches return protocol errors rather than processing malformed callback arrays.

Work handlers:
- Callback break work calls `afs_break_callbacks()` while the server is still delaying visibility.
- Init callback state work calls `afs_init_callback_state()`.
- Probe and tell-me work send replies and drop the call reference.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/cmservice.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/dir.c

This file implements AFS directory reading, validation, lookup, dentry revalidation, create/link/symlink/mkdir/unlink/rmdir/rename operations, directory cache writeback, and dentry lifecycle hooks.

Major responsibilities:
- Defines AFS directory file, inode, address-space, and dentry operations.
- Reads whole directories synchronously into folio-queue buffers.
- Validates 2 KiB AFS directory blocks and iterates entries using bitmap slot allocation.
- Performs local directory search and server-side status fetches for lookup.
- Uses inline bulk status where available to prefetch neighboring lookup targets.
- Revalidates dentries against directory data-version changes and invalidation windows.
- Implements mutating directory operations through `struct afs_operation` dispatch to AFS/YFS RPC clients.
- Applies local directory blob edits after successful mutations when data-version deltas match.
- Handles silly rename for busy unlink/rename targets.

Directory read model:
- AFS directories are read as a single unit to avoid inconsistent contents across partial reads.
- `afs_read_dir()` uses `validate_lock` and reloads only when directory contents are invalid or unread.
- Directory size must be at least one block and no more than 1024 directory blocks.
- `afs_dir_check()` verifies magic in each block and NUL-terminates block data so string functions are bounded.
- Directory iteration rounds positions to dirent boundaries and then walks folio queues block by block.

Lookup:
- `afs_do_lookup()` first searches the cached directory by hash using `afs_dir_search()`.
- The found FID is used to locate an existing inode or to fetch status from the server.
- If the callback server supports inline bulk status, the code scans ahead up to 50 FIDs and fetches statuses in one operation.
- The primary looked-up inode is returned; speculative neighbors may be instantiated or updated.
- `@sys` names are expanded by trying configured sysname substitutions without installing a persistent `@sys` dentry.

Dentry validation:
- RCU validation checks parent deletion and callback validity, then compares `d_fsdata` against directory data version and `invalid_before`.
- Non-RCU validation may request a key, validate the parent directory, re-search for the name, and compare vnode/unique IDs.
- Positive dentries are invalidated if their target vnode changes or the unique generation changes.
- Negative dentries remain valid if the name is still absent.
- Deleted or pseudo-dir dentries are requested to be unhashed on final dput.

Mutation operations:
- Create, mkdir, symlink, link, unlink, rmdir, and rename allocate `afs_operation`, set vnode parameters and expected data-version deltas, dispatch AFS/YFS RPCs, commit returned statuses, update dentry versions, and patch directory caches if safe.
- New regular files, directories, and symlinks instantiate local inodes after successful server creation; new dirs and symlinks initialize local cached contents.
- Unlink validates the victim, uses sillyrename when the dentry is busy, and handles directory conflict by fetching victim status after the unlink.
- Rmdir locks the victim directory’s `rmdir_lock`, clears local deleted state on success, and normalizes `-EEXIST` to `-ENOTEMPTY`.
- Rename supports normal replacement, YFS no-replace, and YFS exchange. It drops dentries temporarily to avoid races with revalidation, handles busy replacement targets through sillyrename, adjusts subdirectory `..` data versions, patches local cached directories, and calls `d_move()` or `d_exchange()`.

Cache/writeback:
- Directory fscache cookies are used around read and mutation operations.
- `afs_dir_writepages()` writes valid directory folio-queue contents as a single blob to the cache while holding `validate_lock`; nonblocking writeback re-dirties the inode on lock conflict.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/dir_edit.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/dir_edit.c

This file performs local edits to cached AFS directory blobs after server-confirmed mutations.

Major responsibilities:
- Finds, sets, and clears contiguous slot bits in an AFS directory block bitmap.
- Maps directory blocks from a vnode’s folio-queue directory buffer, extending the buffer if needed.
- Scans directory blocks for names.
- Initializes new directory blocks and block-zero metadata.
- Adds, removes, or updates directory entries in cached directory data.
- Initializes the `.` and `..` entries for a newly created directory.

Directory block model:
- Each AFS directory block has 64 slots; slot zero is metadata.
- Block zero has additional reserved slots and allocation counters/hash table metadata.
- Entry length determines slot count with `afs_dir_calc_slots()`.
- The first `AFS_DIR_BLOCKS_WITH_CTR` blocks have allocation counters stored in block-zero metadata.
- Hash buckets in block zero point to slot entries; dirents have `hash_next` links.

Add edits:
- `afs_edit_dir_add()` validates directory size, maps metadata block, calculates required slots, searches existing or newly initialized blocks for contiguous free slots, writes the dirent, sets bitmap bits, decrements allocation counters, inserts into the hash chain, increments inode version, and marks the directory dirty.
- If the directory cache is invalid, too large, oddly sized, out of slots despite server success, or otherwise inconsistent, it invalidates the directory instead of forcing an unsafe edit.

Remove edits:
- `afs_edit_dir_remove()` validates size, initializes a search iterator, finds the target in its hash bucket, clears bitmap bits, increments allocation counters, zeroes dirent slots, and repairs the hash chain head or previous dirent link.
- Hash-chain mismatches emit warnings and abandon the edit path.
- On success, inode version is set to the server data version and the directory is marked dirty.

Update edits:
- `afs_edit_dir_update()` scans blocks for a named entry and updates its vnode/unique fields.
- It is used for replacing a dirent target and updating `..` during cross-directory renames.
- Missing entries or invalidated directories cause cache invalidation or edit abandonment.

New directory initialization:
- `afs_mkdir_init_dir()` requires a one-block directory, initializes block zero, writes `.` pointing to the new vnode and `..` pointing to the parent, sets two bitmap slots, updates allocation counters, marks the inode dirty, and sets directory valid/read flags.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/dir_edit.c -->