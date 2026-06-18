# Group Research: group_694_linux_sources_os_linux_linux_fs_affs_dir_c_sources_os_linux_linux_fs_84f0ac424746

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/affs/dir.c -->
# File Research: sources/os/linux/linux/fs/affs/dir.c

Purpose: implements AFFS directory file operations, directory inode operations, and `readdir`.

Key interfaces:
- `affs_dir_operations`: open, llseek with cookie support, iterate, fsync, release, lease.
- `affs_dir_inode_operations`: create, lookup, link, unlink, symlink, mkdir, rmdir, rename, setattr.
- `affs_readdir()`: emits `.`/`..`, walks AFFS hash table buckets and per-bucket hash chains.

Implementation notes:
- Per-open state is `struct affs_dir_data`, storing the last inode and an i_version cookie for faster resumed iteration.
- `ctx->pos` encodes hash bucket in high bits and chain offset in low 16 bits, with positions `0` and `1` reserved for dots.
- Directory iteration locks the directory, reads the directory header block, follows `AFFS_TAIL(...)->hash_chain`, and emits names from AFFS tail records.
- If the inode i_version matches the saved cookie, iteration can jump directly to the saved chain inode.
- Handles extremely long chains by warning when the chain position reaches `0xffff`.

Dependencies:
- Relies on AFFS buffer helpers, directory locking, i_version helpers, and name storage in AFFS header/tail blocks.
- `affs_file_fsync()` is shared with regular files.

Edge cases:
- Unreadable directory/header blocks return `-EIO` or stop iteration.
- `dir_emit()` short-circuit leaves state suitable for a later resumed call.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/affs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/affs/file.c -->
# File Research: sources/os/linux/linux/fs/affs/file.c

Purpose: implements AFFS regular file operations, block mapping, page-cache address-space operations, OFS-specific data-block handling, truncation, and fsync.

Key interfaces:
- `affs_file_operations`: generic file read/write/mmap/splice plus AFFS open/release/fsync.
- `affs_aops`: normal FFS buffered I/O, direct I/O, bmap, writepages.
- `affs_aops_ofs`: OFS-specific read/write path using data block headers.
- `affs_get_block()`: maps or allocates data blocks through AFFS extension blocks.
- `affs_truncate()` and `affs_free_prealloc()` manage file shrink/grow and preallocation cleanup.

Implementation notes:
- File open/release tracks `i_opencnt`; final close truncates to `mmu_private` and frees preallocations.
- Extension blocks are cached using a last-extension buffer, a linear cache, and a small associative cache to avoid repeated chain walks.
- `affs_alloc_extblock()` creates `T_LIST` extension blocks and links them through the previous block’s `extension` field.
- `affs_get_block()` maps logical blocks by extension index and block index within the extension table, allocating blocks only for append-at-end writes.
- Normal FFS uses block helpers (`block_read_full_folio`, `mpage_writepages`, `cont_write_begin`, `generic_write_end`).
- Direct I/O refuses extending writes by returning `0` when the write would pass `mmu_private`.
- OFS data blocks have 24-byte headers, data size fields, sequence numbers, and `next` links; OFS read/write paths copy payloads around those headers.
- Writes clear the Amiga archived bit (`FIBF_ARCHIVED`) and mark the inode dirty.

Dependencies:
- Uses AFFS allocation/free helpers, checksums, metadata buffer tracking (`mmb_*`), block buffer helpers, page-cache/blockdev helpers.

Edge cases:
- Logical block requests beyond allowed append position are treated as filesystem errors.
- OFS extension-to-hole writes call `affs_extent_file_ofs()` to materialize zeroed data blocks.
- Truncate frees data blocks and extension blocks after the new EOF and trims extension caches.
- Enlarging truncate uses the active mapping write path to force allocation/accounting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/affs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/affs/inode.c -->
# File Research: sources/os/linux/linux/fs/affs/inode.c

Purpose: handles AFFS inode load/store, setattr, eviction, new inode allocation, and directory entry creation.

Key interfaces:
- `affs_iget()`: reads AFFS header block into a VFS inode.
- `affs_write_inode()`: writes mode/protection, size, uid/gid, and timestamps back to disk.
- `affs_setattr()`: validates and applies VFS attribute changes.
- `affs_evict_inode()`: final cleanup, truncate/free on unlink, metadata sync/invalidate.
- `affs_new_inode()` and `affs_add_entry()`: allocate a header block and insert it into a directory hash chain.

Implementation notes:
- `affs_iget()` validates block checksum and `T_SHORT` type, initializes AFFS private fields, converts protection bits to Unix mode, and selects operations by `stype`.
- Directories get `affs_dir_inode_operations` and `affs_dir_operations`; regular files get AFFS file ops and normal/OFS address ops; symlinks use symlink aops.
- UID/GID handling supports mount overrides and MUFS `0xffff` translation.
- Timestamps are converted from AFFS datestamps plus `AFFS_EPOCH_DELTA` and timezone offset.
- `affs_write_inode()` skips unlinked inodes, updates root or normal tail timestamps, writes protection/size/owner fields, fixes checksums, and marks metadata buffers dirty.
- `affs_add_entry()` creates normal entries or additional link header blocks for `ST_LINKFILE`/`ST_LINKDIR`, maintains link chains, and inserts into the parent directory hash table.

Dependencies:
- Depends on AFFS block allocation, checksum, bitmap, hash insertion, dentry name copying, and metadata buffer tracking.

Edge cases:
- Unsupported `ST_LINKFILE` during inode load is treated as bad inode.
- Attribute changes that conflict with mount-enforced uid/gid/mode/protect options return `-EPERM` unless quiet mode is set.
- On add-entry failure, allocated link blocks are freed and locks released.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/affs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/affs/namei.c -->
# File Research: sources/os/linux/linux/fs/affs/namei.c

Purpose: implements AFFS VFS name operations, name hashing/comparison, lookup, create/remove/link/symlink/rename, and export operations.

Key interfaces:
- Dentry ops: `affs_dentry_operations`, `affs_intl_dentry_operations`.
- `affs_lookup()`, `affs_create()`, `affs_mkdir()`, `affs_unlink()`, `affs_rmdir()`, `affs_link()`, `affs_symlink()`, `affs_rename2()`.
- Export ops: `affs_export_ops`.

Implementation notes:
- Supports normal DOS and international uppercase folding for case-insensitive hashing/comparison.
- Names are validated with `affs_check_name()` and may be truncated to `AFFSNAMEMAX` unless no-truncate mount behavior applies.
- `affs_find_entry()` hashes the target name to a parent bucket and walks AFFS hash chains, matching with AFFS case folding.
- `affs_lookup()` stores the real header block in `d_fsdata`; file links resolve through `original`.
- Create/mkdir allocate a new inode, set mode/protection, assign ops, and call `affs_add_entry()`.
- Symlink creation rewrites Unix absolute paths into AFFS volume-relative syntax using `s_volume`, strips redundant slashes, and handles `.`/`..` path patterns.
- Rename removes the old hash entry, rewrites the name, and inserts into the new parent; exchange rename removes both entries then reinserts swapped names.

Dependencies:
- Uses AFFS hash/table helpers, inode allocation, remove/insert hash helpers, symlink aops, and exportfs generic inode-handle helpers.

Edge cases:
- Rename has a TODO about restoring the old directory entry if insertion into the new directory fails.
- Directory hard links are commented out/disabled in lookup.
- NFS export inode lookup rejects invalid block numbers with `-ESTALE`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/affs/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/affs/super.c -->
# File Research: sources/os/linux/linux/fs/affs/super.c

Purpose: implements AFFS filesystem registration, superblock lifecycle, mount option parsing, root discovery, remount handling, statfs, inode cache management, and delayed superblock commits.

Key interfaces:
- `affs_sops`: alloc/free inode, write/evict inode, put/sync super, statfs, show_options.
- `affs_context_ops`: parse parameters, get block-device tree, reconfigure, free context.
- `affs_fs_type`: Linux filesystem type registration for `affs`.

Implementation notes:
- `affs_commit_super()` updates root tail disk-change time and checksum, then dirties/syncs the root block.
- `affs_mark_sb_dirty()` schedules delayed root-block commit through `system_long_wq`.
- Mount options include block size, mode, MUFS, no filename truncation, symlink prefix, protect/immutable, reserved blocks, root block, uid/gid overrides, verbose, and volume.
- `affs_fill_super()` probes block sizes/root block positions, validates root block checksum/type, reads the boot signature, and sets flags for FFS/OFS, INTL, MUFS, dircache, and read-only fallback.
- Dircache variants are mounted read-only if write access was requested.
- OFS reduces data block size by 24 bytes and sets `SB_NOEXEC`.
- Initializes bitmap state before reading the root inode; selects international or normal dentry ops.
- Reconfigure preserves only historical remount option behavior and updates prefix/volume under `symlink_lock`.

Dependencies:
- Uses fs_context parser APIs, block device helpers, AFFS bitmap initialization/free, AFFS inode cache, root block macros, and export ops.

Edge cases:
- Several early failure paths return without local cleanup in this file because block-super teardown handles most initialized state later.
- Root block probing compensates for odd partition-size/reserved-block geometry by trying the calculated root and the next block.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/affs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/affs/symlink.c -->
# File Research: sources/os/linux/linux/fs/affs/symlink.c

Purpose: implements AFFS symlink page loading and symlink inode operations.

Key interfaces:
- `affs_symlink_aops.read_folio = affs_symlink_read_folio`.
- `affs_symlink_inode_operations`: `get_link = page_get_link`, `setattr = affs_setattr`.

Implementation notes:
- Reads the symlink text from the inode’s AFFS header block.
- If the stored name contains `:`, treats the prefix as an AFFS assign/volume name and prepends mount `s_prefix` or `/`.
- Converts repeated slash semantics into Unix parent-directory references by inserting `..` when a slash follows a slash.
- Caps generated link text at 1023 bytes and NUL-terminates the folio buffer.
- Marks the folio uptodate and unlocks it on success.

Dependencies:
- Uses AFFS block read/release helpers and `symlink_lock` for stable prefix access.

Edge cases:
- Block read failure unlocks the folio and returns `-EIO`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/affs/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/Kconfig -->
# File Research: sources/os/linux/linux/fs/afs/Kconfig

Purpose: declares build-time configuration for the Linux AFS client.

Key entries:
- `AFS_FS`: tristate Andrew File System client, depends on `INET`, selects `AF_RXRPC`, `DNS_RESOLVER`, `NETFS_SUPPORT`, and `CRYPTO_KRB5`.
- `AFS_DEBUG`: optional dynamic debugging.
- `AFS_FSCACHE`: optional local caching through fscache, constrained by built-in/module compatibility.
- `AFS_DEBUG_CURSOR`: optional server cursor debug dumps.

Implementation notes:
- Help text still describes the driver as experimental and points to `Documentation/filesystems/afs.rst`.
- `AFS_FSCACHE` is a bool gated on both AFS and FSCACHE linkage mode.

Dependencies:
- Network, RxRPC, DNS resolver, netfs, Kerberos crypto, and optional fscache infrastructure.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/Makefile -->
# File Research: sources/os/linux/linux/fs/afs/Makefile

Purpose: lists object files linked into the `kafs` module/built-in object.

Key interfaces:
- `obj-$(CONFIG_AFS_FS) := kafs.o`.
- `kafs-y` includes address management, callbacks, cells, cache-manager service, directory logic, dynroot, file I/O, flocking, fs/vl/yfs clients, inode/super, rotation/probing, security, server/volume management, write, xattr.
- `kafs-$(CONFIG_PROC_FS) += proc.o`.

Implementation notes:
- The files in this work item are part of the core `kafs-y` object set.
- Procfs support is conditional, but address preferences and cell code include proc-facing hooks when proc is available through other compilation units.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/addr_list.c -->
# File Research: sources/os/linux/linux/fs/afs/addr_list.c

Purpose: manages AFS server address lists, parses textual/DNS-provided addresses, merges RxRPC peers, and associates peers with server records.

Key interfaces:
- `afs_alloc_addrlist()`, `afs_get_addrlist()`, `afs_put_addrlist()`.
- `afs_parse_text_addrs()`: parses delimited IPv4/IPv6 address lists with optional `+port`.
- `afs_dns_query()`: resolves VL server addresses through DNS.
- `afs_merge_fs_addr4()` and `afs_merge_fs_addr6()`.
- `afs_set_peer_appdata()`.

Implementation notes:
- Address lists are flex-array allocations capped at `AFS_MAX_ADDRESSES`, refcounted, and freed by RCU.
- Peer references are released on final free.
- Parser supports bracketed IPv6, delimiter normalization for colon/comma cases, duplicate delimiters, and port validation.
- DNS results are interpreted either as SRV-style data for `afs_extract_vlserver_list()` or as text address lists.
- IPv4 peers are kept before IPv6 peers; within each family, insertion order is sorted by `rxrpc_peer *` pointer.
- `afs_set_peer_appdata()` diffs old/new sorted lists to set or clear server pointers in RxRPC peer appdata.

Dependencies:
- RxRPC peer lookup/refcounting, DNS resolver, VL server list allocation, and AFS/YFS service port constants.

Edge cases:
- Empty address lists return `-EDESTADDRREQ`.
- Invalid syntax returns `-EINVAL` with trace/debug problem labels.
- When the list is full, additional addresses are silently ignored by merge functions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/addr_list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/addr_prefs.c -->
# File Research: sources/os/linux/linux/fs/afs/addr_prefs.c

Purpose: implements address preference parsing, procfs updates, and applying priority preferences to server address lists.

Key interfaces:
- `afs_proc_addr_prefs_write()`: handles writes to `/proc/fs/afs/addr_prefs`.
- `afs_get_address_preferences()` and `_rcu()`: apply preference priorities to an `afs_addr_list`.

Implementation notes:
- Input commands are whitespace-split by `afs_split_string()` and support:
  - `add udp <IP>[/mask] <priority>`
  - `del udp <IP>[/mask]`
- Address parser accepts IPv4, IPv6, bracketed IPv6, and subnet masks; zero-length masks and oversized masks are rejected.
- Preferences are sorted by family and address/subnet order; IPv4 entries precede IPv6 entries, tracked by `ipv6_off`.
- Exact match updates existing priority; subnet match inserts tighter prefixes ahead of broader ones.
- Updates copy the old RCU-published list, mutate the copy under inode lock, increment version, publish with `rcu_assign_pointer`, and release the version with `smp_store_release`.
- Address lists cache the last applied preference version to avoid repeated scans.

Dependencies:
- Procfs seq-file network namespace lookup, RCU, RxRPC remote address access, and release/acquire memory ordering.

Edge cases:
- Preference count is capped at 255.
- The inner matching loops break only from switch cases, not the surrounding loop, so later preferences may still be inspected after a match; the final observed behavior depends on sorted ordering.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/addr_prefs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/afs.h -->
# File Research: sources/os/linux/linux/fs/afs/afs.h

Purpose: defines public/common AFS protocol types, constants, status records, access masks, callbacks, volume metadata, and XDR UUID layout.

Key contents:
- Name/path/cell/volume/server limits: `AFS_MAXCELLNAME`, `AFS_MAXVOLNAME`, `AFSNAMEMAX`, `AFSPATHMAX`, etc.
- Core typedefs: volume ID, vnode ID, data version.
- Enums for volume type, file type, and lock type.
- `struct afs_fid`: volume, vnode low/high, unique generation.
- Callback structs and callback break records.
- `struct afs_volume_info`, `struct afs_file_status`, `struct afs_status_cb`, `struct afs_volsync`, `struct afs_volume_status`.
- ACL access bit masks and file status change flags.
- `AFS_BLOCK_SIZE` and `struct afs_uuid__xdr`.

Implementation notes:
- `afs_status_cb` carries status/callback presence flags and inline per-file abort state.
- File status stores both client and server mtimes, access rights, mode, type, nlink, lock count, and abort code.
- Some historical callback fields are commented out, showing simplified in-kernel tracking.

Dependencies:
- Shared by FS, VL, callback, inode, and directory code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/afs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/afs_cm.h -->
# File Research: sources/os/linux/linux/fs/afs/afs_cm.h

Purpose: defines AFS cache-manager service constants and operation IDs.

Key contents:
- `AFS_CM_PORT = 7001`.
- `CM_SERVICE = 1`.
- Cache-manager operation IDs: `CBCallBack`, `CBInitCallBackState`, `CBProbe`, `CBGetLock`, `CBGetCE`, `CBGetXStatsVersion`, `CBGetXStats`, `CBInitCallBackState3`, `CBProbeUuid`, `CBTellMeAboutYourself`.
- `AFS_CAP_ERROR_TRANSLATION`.

Implementation notes:
- Used by incoming cache-manager RPC dispatch and security challenge handling.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/afs_cm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/afs_fs.h -->
# File Research: sources/os/linux/linux/fs/afs/afs_fs.h

Purpose: defines AFS file service port, service ID, operation IDs, and file-service abort/error codes.

Key contents:
- `AFS_FS_PORT = 7000`, `FS_SERVICE = 1`.
- File service ops include fetch/store data, ACL/status, create/remove/rename/symlink/link/mkdir/rmdir, callback give-up, volume info/status, bulk status, locks, lookup, 64-bit data ops, capabilities.
- Error codes include volume restart/salvage/not found/offline/busy/moved/I/O/quota/full/restricted states.

Implementation notes:
- Operation IDs are consumed by fsclient/yfsclient operation descriptors elsewhere and referenced by callback/security code.
- Error constants are translated into Linux errors in higher-level operation handling.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/afs_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/afs_vl.h -->
# File Research: sources/os/linux/linux/fs/afs/afs_vl.h

Purpose: defines AFS Volume Location service constants, operations, errors, VLDB entry layout, and XDR request/response structures.

Key contents:
- `AFS_VL_PORT = 7003`, `VL_SERVICE = 52`, `YFS_VL_SERVICE = 2503`.
- VL/YFS operation IDs for entry lookup, probes, address lookup, endpoints, cell name, and capabilities.
- VL error code enum.
- YFS server/endpoint indexes and endpoint family tags.
- `struct afs_vldbentry`: volume name, type, server count, clone ID, flags, volume IDs, and server records.
- XDR structs for ListAddrByAttributes and UUID VLDB entries.

Implementation notes:
- Supports both classic AFS VL and UUID/YFS-extended server addressing.
- Flags identify read-write/read-only/backup volume presence and per-server volume placement.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/afs_vl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/callback.c -->
# File Research: sources/os/linux/linux/fs/afs/callback.c

Purpose: handles callback invalidation from AFS fileservers, including vnode callbacks, volume-level callbacks, mmap invalidation, and callback-state reinitialization.

Key interfaces:
- `afs_invalidate_mmap_work()`.
- `afs_init_callback_state()`.
- `afs_break_callback()` / `__afs_break_callback()`.
- `afs_break_callbacks()`.

Implementation notes:
- Mmap invalidation unmaps all pages for the vnode mapping so later faults revalidate.
- Server callback-state reinitialization clears callback promises for all volumes attached to the server and queues mmap invalidation when needed.
- Breaking a vnode callback clears new-content state, clears permits, increments callback break counters, updates volume break check, wakes lock waiters, and queues mmap invalidation for mapped files.
- Volume callback break clears per-server and volume callback expiries, increments `cb_v_break`, releases RCU before walking open mmap list, and initializes callbacks for open mmaps.
- Callback batches are grouped by volume ID; volume-wide breaks use vnode/unique zero.

Dependencies:
- Uses volume and server lists, seqlocks, RCU, inode lookup by FID, open mmap lists, and permit/cache callback tracking.

Edge cases:
- If a matching volume or inode is absent, callback break is traced as a miss rather than fatal.
- `afs_break_volume_callback()` assumes a valid volume pointer after lookup; caller path must ensure this is safe for volume-wide callback records.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/callback.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/cell.c -->
# File Research: sources/os/linux/linux/fs/afs/cell.c

Purpose: manages AFS cell records: lookup, allocation, DNS/VL server refresh, root cell setup, proc activation, lifecycle references, timers, garbage collection, and purge.

Key interfaces:
- `afs_find_cell()`, `afs_lookup_cell()`, `afs_cell_init()`.
- `afs_get_cell()`, `afs_put_cell()`, `afs_use_cell()`, `afs_unuse_cell()`.
- `afs_queue_cell()`, `afs_set_cell_timer()`, `afs_cell_purge()`.

Implementation notes:
- Cells live in a per-net RB tree keyed case-insensitively by lowercase cell name.
- Allocation validates names, stores name and key description in one allocation, creates an initial VL server list from configured addresses or DNS-unavailable placeholder, assigns dynamic-root inode numbers, and initializes locks/timers/work.
- Lookup may preallocate a candidate outside `cells_lock`, then insert or discard it if another thread won.
- Cell state is published with release ordering and waiters use `wait_var_event`.
- DNS updates query AFSDB/SRV/text records, classify lookup status, clamp TTL between min and max, and RCU-replace the VL server list when useful.
- Active counts are separate from object refs. Dropping the final active use schedules a management timer; final object free is workqueue plus RCU.
- Manager transitions setup to unlooked/active, performs DNS lookup when requested, expires inactive cells, deactivates proc entries, purges servers, removes from RB tree, releases root volume, and marks dead.
- Purge unpins root/workstation cells, queues all cells, and waits for `cells_outstanding` to reach zero.

Dependencies:
- DNS resolver, VL server list management, proc cell setup/removal, server purge, volume refs, workqueues, timers, RB tree, RCU.

Edge cases:
- Configured VL server addresses bypass DNS expiry by setting `TIME64_MAX`.
- Root cell validation rejects empty, leading/trailing dot, slash, and double-dot names.
- On lookup failure after activation, active references are dropped with `afs_unuse_cell()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/cell.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/cm_security.c -->
# File Research: sources/os/linux/linux/fs/afs/cm_security.c

Purpose: handles RxRPC out-of-band security challenges for AFS/VL/YFS services and, when RxGK is enabled, creates cache-manager callback tokens.

Key interfaces:
- `afs_process_oob_queue()`.
- `afs_create_token_key()` under `CONFIG_RXGK`.

Implementation notes:
- OOB worker dequeues RxRPC challenge messages and responds based on service ID and security index.
- Accepts challenges for FS, VL, YFS FS, and YFS VL services; unknown services are rejected with `afs_abort_unsupported_sec_class`.
- Supports RxKAD challenge response when configured.
- Supports RxGK and YFS-RxGK; YFS callback appdata is lazily generated per server under `cm_token_lock`.
- RxGK token key creation builds a `kafs` keyring, attaches it to the socket, chooses AES128 CTS HMAC SHA1, generates a random callback key, and creates an `rxrpc_s` key.
- YFS CM token construction builds XDR appdata containing initiator/server UUIDs, capabilities, callback key, and encrypted token container.

Dependencies:
- RxRPC challenge APIs, Linux keyrings, Kerberos crypto helpers, random bytes, YFS protocol constants.

Edge cases:
- Missing RxGK key returns `-ENOKEY`; unsupported enctype returns `-ENOPKG`.
- Appdata size is checked after construction and logged if mismatched.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/cm_security.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/cmservice.c -->
# File Research: sources/os/linux/linux/fs/afs/cmservice.c

Purpose: implements incoming AFS/YFS cache-manager RxRPC service dispatch, unmarshalling, callback break execution, probes, callback-state reset, and capability replies.

Key interfaces:
- `afs_cm_incoming_call()`: assigns call type based on operation ID and service.
- Call types for `CB.CallBack`, `CB.InitCallBackState`, `CB.InitCallBackState3`, `CB.Probe`, `CB.ProbeUuid`, `CB.TellMeAboutYourself`, and `YFSCB.CallBack`.

Implementation notes:
- Callback calls are executed in workqueue handlers; callback breaks are performed before sending the reply to maintain server cache-coherency ordering.
- Classic `CB.CallBack` unmarshals a bounded FID array (`AFSCBMAX`), discards matching callback records, and verifies call state before reply.
- YFS callback unmarshalling supports wider YFS FID layout and `YFSCBMAX`.
- Init callback state calls clear server callback state.
- InitCallBackState3 and ProbeUuid decode UUIDs from 11 XDR words; ProbeUuid aborts if the UUID does not match the client UUID.
- TellMeAboutYourself replies with client UUID and `AFS_CAP_ERROR_TRANSLATION`.

Dependencies:
- AFS call extraction helpers, RxRPC abort/reply helpers, callback break code, YFS protocol structs, operation ID constants.

Edge cases:
- Callback FID count over protocol max returns protocol error.
- Classic callback count must match FID count unless zero.
- Unsupported incoming operation IDs return false to dispatch.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/cmservice.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/dir.c -->
# File Research: sources/os/linux/linux/fs/afs/dir.c

Purpose: implements AFS directory file/inode/dentry operations, complete remote directory reads, directory iteration, lookup and bulk-status lookup-ahead, dentry revalidation, create/remove/link/symlink/rename operations, local directory-cache edits after server mutations, and directory cache writeback.

Key interfaces:
- `afs_dir_file_operations`, `afs_dir_inode_operations`, `afs_dir_aops`, `afs_fs_dentry_operations`.
- Directory read/iterate: `afs_read_dir()`, `afs_dir_iterate()`, `afs_readdir()`.
- Lookup/revalidation: `afs_lookup()`, `afs_d_revalidate()`, `afs_d_delete()`, `afs_d_iput()`.
- Mutations: create, mkdir, rmdir, unlink, link, symlink, rename.
- `afs_dir_writepages()` writes directory folio-queue contents to cache as one blob.

Implementation notes:
- AFS directories are read synchronously as a single unit with `netfs_read_single()` to avoid observing inconsistent directory contents across multiple reads.
- Directory storage is a folio queue in the vnode; valid/read state is tracked by `AFS_VNODE_DIR_VALID` and `AFS_VNODE_DIR_READ`.
- Directory blocks are 2048-byte AFS XDR blocks; validation checks magic, forces final byte NUL, and dumps the directory on failure.
- Iteration walks bitmap-marked slots, validates multi-slot names, computes the next slot by name length, and emits vnode number plus unique ID for internal lookup filldir paths.
- Lookup first validates the parent, handles `@sys` substitution through configured sysnames, hashes/searches the directory, then optionally scans ahead for up to 50 FIDs and uses FS/YFS InlineBulkStatus for speculative inode population.
- Dentry versions are stored in `d_fsdata` using directory data version. Revalidation compares against current `data_version` and `invalid_before`; slow revalidation can re-search by name and compare vnode/unique.
- Dentries for deleted, silly-renamed, or pseudodir inodes are unhashed.
- Mutating operations allocate `afs_operation`, set vnode parameters and expected data-version deltas, issue FS/YFS RPCs, commit statuses, and edit the local directory cache only if the server data-version delta matches exactly.
- Unlink and rename integrate sillyrename for busy files, using `DCACHE_NFSFS_RENAMED`.
- Rename handles normal, YFS no-replace, and YFS exchange paths; updates child `..` entries and directory data versions for moved subdirectories.
- Directory writeback locks `validate_lock` and writes the folio queue through netfs only if the directory cache is valid.

Dependencies:
- Netfs/fscache, AFS operation framework, fsclient/yfsclient RPCs, callback validation, directory edit/search helpers, sillyrename helpers, sysname substitution, dentry and inode versioning.

Edge cases:
- Directory read retries on `-ESTALE`, with retry limits.
- Very small or over-large directories are rejected.
- RCU revalidation returns `-ECHILD` when it cannot prove validity.
- Rename intentionally drops dentries around server operations to avoid races with `d_revalidate()` seeing stale parent data versions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/dir_edit.c -->
# File Research: sources/os/linux/linux/fs/afs/dir_edit.c

Purpose: edits the client’s cached AFS directory blob after successful server-side create, mkdir, symlink, link, unlink, rmdir, rename, sillyrename, or subdirectory parent changes.

Key interfaces:
- `afs_edit_dir_add()`.
- `afs_edit_dir_remove()`.
- `afs_edit_dir_update()`.
- `afs_mkdir_init_dir()`.

Implementation notes:
- Directory blocks contain 64 fixed slots with an 8-byte bitmap; names may consume multiple contiguous 32-byte dirent slots.
- `afs_find_contig_bits()`, set, and clear helpers manage contiguous slot allocation in the block bitmap.
- `afs_dir_get_block()` maps a requested directory block from the vnode’s folio queue, extending storage with `netfs_alloc_folioq_buffer()` when adding blocks.
- New blocks are initialized with AFS directory magic, reserved metadata bitmap entries, and allocation counters in block 0.
- Add chooses a block with sufficient free slots, initializes a new block if necessary, writes vnode/unique/name, adjusts bitmap/allocation counter, links into the hash bucket, increments inode version, and marks the inode dirty.
- Remove locates the entry through the hash-chain search helper, clears bitmap and dirent slots, adjusts allocation counters, repairs hash-chain predecessor or bucket head, sets inode version to server data version, and marks dirty.
- Update scans blocks linearly for an entry and rewrites the vnode/unique pair, used especially for `..` updates.
- New mkdir cache initialization creates block 0 plus `.` and `..`, adjusts counters, marks directory valid/read, and marks dirty.

Dependencies:
- Folio queue directory storage, directory search helper functions, netfs dirty marking, AFS directory constants and XDR structs.

Edge cases:
- If directory size is invalid, too large, not block-aligned, callback-broken, or hash-chain expectations fail, the directory cache is invalidated for redownload.
- `afs_edit_dir_add()` notes a TODO around maintaining `hash_next`, but it does update the bucket head and new entry link.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/dir_edit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/dir_search.c -->
# File Research: sources/os/linux/linux/fs/afs/dir_search.c

Purpose: provides hash-based lookup into cached AFS directory contents.

Key interfaces:
- `afs_dir_hash_name()`.
- `afs_dir_init_iter()`.
- `afs_dir_find_block()`.
- `afs_dir_search_bucket()`.
- `afs_dir_search()`.

Implementation notes:
- Hash function multiplies by 173 and maps into the fixed AFS directory hash table, with special handling for signed overflow semantics.
- Iterator setup computes required name slots, target bucket, maximum loop count, and previous-entry state.
- `afs_dir_find_block()` maps the folio containing a directory block and unmaps any previous mapped block.
- Bucket search starts from block 0 hashtable bucket, follows `hash_next`, validates reserved slot ranges, compares NUL-terminated names, returns vnode/unique on match, and tracks predecessor for edit/remove.
- Loop count limits prevent infinite traversal on corrupt hash chains.
- `afs_dir_search()` ensures the directory is read and valid, captures inode i_version as directory version, searches the bucket, unlocks validation, and retries a few times on stale data.

Dependencies:
- AFS directory folio queue, validation lock from `afs_read_dir()`, directory invalidation, XDR directory structures.

Edge cases:
- Empty directories return `-ENOENT`.
- Missing or invalid blocks invalidate the directory and return `-ESTALE`.
- Deleted vnode during retry stops with `-ESTALE`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/dir_search.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/dir_silly.c -->
# File Research: sources/os/linux/linux/fs/afs/dir_silly.c

Purpose: implements AFS sillyrename behavior for unlinking or replacing busy open files on a stateless server.

Key interfaces:
- `afs_sillyrename()`.
- `afs_silly_iput()`.

Implementation notes:
- Busy unlink/rename targets are renamed in the same directory to hidden names of the form `.__afs%04X`, matching salvager expectations.
- Sillyrename uses the normal FS/YFS rename operation, marks the original dentry with `DCACHE_NFSFS_RENAMED`, stores the key on the directory vnode, and locally edits the directory cache by removing the old name and adding the silly name when data-version deltas match.
- On success, the dentry is moved to the silly name and the vnode gets `AFS_VNODE_SILLY_DELETED`.
- On final dentry inode put, `afs_silly_iput()` allocates/coordinates a parallel dentry, marks lock state deleted, then sends FS/YFS remove-file to delete the silly name.
- If lookup races find an alias, sillyrename state can be transferred to the alias dentry instead of immediately unlinking.

Dependencies:
- AFS operation framework, rename/remove-file RPCs, directory edit helpers, dentry locking, rmdir lock, key references, fsnotify/namei behavior inherited from NFS-style sillyrename.

Edge cases:
- A dentry already silly-renamed returns `-EBUSY`.
- If the generated hidden name lookup fails, the operation returns that error rather than risking deletion of an in-use file.
- `-ERESTARTSYS` after rename causes both dentries to be dropped because the server result is unknown.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/dir_silly.c -->