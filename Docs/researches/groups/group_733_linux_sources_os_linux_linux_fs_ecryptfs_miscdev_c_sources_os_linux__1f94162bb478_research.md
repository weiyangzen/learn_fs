# Group Research: group_733_linux_sources_os_linux_linux_fs_ecryptfs_miscdev_c_sources_os_linux__1f94162bb478

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux`. This grouped report covers the requested Linux eCryptfs, efivarfs, EFS, and EROFS files in manifest order.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ecryptfs/miscdev.c -->
# File Research: sources/os/linux/linux/fs/ecryptfs/miscdev.c

Implements the `/dev/ecryptfs` miscdevice used for kernel-to-userspace eCryptfs daemon messaging.

Key behavior:
- Tracks daemon device opens with `ecryptfs_num_miscdev_opens`.
- `open` finds or spawns the daemon for the caller euid, marks `ECRYPTFS_DAEMON_MISCDEV_OPEN`, and stores the daemon in `file->private_data`.
- `poll` reports readable state when `msg_ctx_out_queue` is non-empty, while guarding against zombie, concurrent read, and concurrent poll states.
- `release` clears the miscdev-open flag, decrements the open count, and calls `ecryptfs_exorcise_daemon()`.
- `ecryptfs_send_miscdev()` packages an `ecryptfs_message`, links the message context onto the daemon outbound queue, increments the queued count, and wakes waiters.
- `read` blocks until a queued message exists, serializes packet type, big-endian counter, optional packet length, and optional message body to userspace, then frees or retains the message context depending on whether a reply is expected.
- `write` validates userspace packet lengths, copies the packet, accepts HELO/QUIT, and dispatches RESPONSE packets to `ecryptfs_process_response()`.
- Registers and deregisters a dynamic-minor miscdevice named `ecryptfs`.

Important interactions:
- Depends on daemon lifecycle and message-context helpers from the rest of eCryptfs.
- The packet format is a small framing layer around `struct ecryptfs_message` plus daemon sequence numbers.
- Module teardown asserts no miscdevice opens remain before deregistration.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ecryptfs/miscdev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ecryptfs/mmap.c -->
# File Research: sources/os/linux/linux/fs/ecryptfs/mmap.c

Defines eCryptfs address-space operations for encrypted/decrypted page-cache I/O.

Key behavior:
- `ecryptfs_writepages()` iterates writeback folios, encrypts each folio with `ecryptfs_encrypt_page()`, records mapping errors, and unlocks folios.
- Handles “view as encrypted” reads, including reconstructing an encrypted header view when metadata is stored in xattrs.
- `ecryptfs_read_folio()` chooses plain lower reads, encrypted-view reads, or decryption based on crypt-stat flags.
- `ecryptfs_write_begin()` prepares a folio, reads/decrypts lower content when needed, and fills holes by truncating/zeroing.
- `ecryptfs_write_end()` writes unencrypted passthrough data directly or encrypts the folio, updates upper size, and writes the size back to metadata.
- Writes plaintext inode size either to the lower file header or to the eCryptfs xattr.
- Provides `ecryptfs_bmap()` by forwarding to the lower inode `bmap()`.
- Exports `ecryptfs_aops` with read, write, writepages, migration, invalidation, dirty-folio, and bmap hooks.

Important interactions:
- Uses `ecryptfs_xattr_cache` for xattr metadata updates.
- Calls lower I/O helpers from `read_write.c`.
- Crypt-stat flags control whether data is passed through, decrypted, encrypted, exposed as encrypted, or metadata-backed by xattrs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ecryptfs/mmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ecryptfs/read_write.c -->
# File Research: sources/os/linux/linux/fs/ecryptfs/read_write.c

Provides lower-file read/write primitives and a page-oriented high-level write path for eCryptfs.

Key behavior:
- `ecryptfs_write_lower()` writes bytes to the lower file with `kernel_write()` and marks the eCryptfs inode dirty.
- `ecryptfs_write_lower_page_segment()` maps a folio locally and writes a segment to the corresponding lower-file offset.
- `ecryptfs_write()` fills holes with zeros, copies caller data into eCryptfs folios, encrypts pages when required, or writes lower page segments for unencrypted files.
- Updates the eCryptfs inode size and encrypted-file size metadata when writes extend the file.
- Aborts long writes if a fatal signal is pending.
- `ecryptfs_read_lower()` wraps `kernel_read()` on the lower file.
- `ecryptfs_read_lower_page_segment()` maps a folio, reads lower bytes into it, and flushes D-cache state.

Important interactions:
- Assumes each eCryptfs inode private object has a valid `lower_file`.
- Used by address-space operations and metadata-writing paths in `mmap.c`.
- Preserves the split between logical upper offsets and physical lower-file storage.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ecryptfs/read_write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ecryptfs/super.c -->
# File Research: sources/os/linux/linux/fs/ecryptfs/super.c

Defines eCryptfs superblock operations and inode-cache behavior.

Key behavior:
- Allocates `struct ecryptfs_inode_info` from `ecryptfs_inode_info_cache`.
- Initializes each inode’s crypt-stat, lower-file mutex, lower-file refcount, and lower-file pointer.
- Frees inode private storage and destroys crypt-stat state during inode destruction.
- `statfs` delegates to the lower filesystem, then rewrites the filesystem magic and adjusts reported name length for encrypted filename constraints.
- `evict_inode` truncates page cache, clears the inode, and drops the lower inode reference.
- `show_options` emits active eCryptfs mount crypt options, including auth token signatures, cipher, key size, passthrough, xattr metadata, encrypted view, unlink sigs, and mount-auth-token-only mode.

Important interactions:
- `ecryptfs_sops` is the central superblock operation table used by mount setup.
- Mount option display depends on `ecryptfs_mount_crypt_stat`.
- Inode teardown asserts the lower file has already been released.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ecryptfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/efivarfs/Kconfig -->
# File Research: sources/os/linux/linux/fs/efivarfs/Kconfig

Defines the `EFIVAR_FS` build option.

Key behavior:
- Adds tristate “EFI Variable filesystem” support.
- Depends on `EFI`.
- Defaults to module build.
- Describes efivarfs as the replacement for sysfs EFI variable access without the old 1024-byte size limit.

Important interactions:
- The built module is named `efivarfs`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/efivarfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/efivarfs/Makefile -->
# File Research: sources/os/linux/linux/fs/efivarfs/Makefile

Builds the efivarfs module.

Key behavior:
- Adds `efivarfs.o` when `CONFIG_EFIVAR_FS` is enabled.
- Links `inode.o`, `file.o`, `super.o`, and `vars.o` into the module.

Important interactions:
- Keeps all efivarfs VFS operations and EFI variable helpers in one module object.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/efivarfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/efivarfs/file.c -->
# File Research: sources/os/linux/linux/fs/efivarfs/file.c

Implements file operations for individual EFI variable files.

Key behavior:
- Writes expect a leading 32-bit attributes word followed by variable data.
- Rejects invalid attribute bits outside `EFI_VARIABLE_MASK`.
- Uses `efivar_entry_set_get_size()` to atomically set firmware variable data and learn the new size.
- Treats `-ENOENT` after a successful set as deletion and sets inode size to zero.
- Reads rate-limit per user, queries variable size, reads attributes plus data, and returns them as the file payload.
- Represents uncommitted newly-created variables as zero-length files returning EOF.
- Open increments `open_count`; release decrements it and removes a deleted zero-size variable dentry when the last opener closes.

Important interactions:
- Uses inode locking to serialize size and removed-state updates.
- File private data points at `struct efivar_entry`.
- Write/delete behavior is coupled to `simple_recursive_removal()` cleanup in release.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/efivarfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/efivarfs/inode.c -->
# File Research: sources/os/linux/linux/fs/efivarfs/inode.c

Implements efivarfs inode creation, directory operations, unlink, file attributes, and setattr handling.

Key behavior:
- `efivarfs_get_inode()` creates simple inodes with mount uid/gid, timestamps, mode, and immutable flag unless the variable is removable.
- Valid efivarfs filenames must be `VariableName-GUID`.
- `create` validates filename/GUID, rejects the Linux EFI random seed variable, determines removability, creates the inode, and initializes the in-memory EFI variable name/GUID.
- `unlink` deletes the EFI variable from firmware before removing the dentry.
- Directory inode operations provide `lookup`, `unlink`, and `create`.
- File attribute get/set exposes only the immutable flag.
- `efivarfs_setattr()` intentionally copies attributes without updating `i_size`, because file size reflects firmware variable state.

Important interactions:
- Removability is controlled by the variable validation whitelist in `vars.c`.
- Non-removable variables are immutable by default.
- `i_private` points to the embedded `struct efivar_entry`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/efivarfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/efivarfs/internal.h -->
# File Research: sources/os/linux/linux/fs/efivarfs/internal.h

Declares efivarfs private types and helper interfaces.

Key behavior:
- Defines mount options containing uid and gid.
- Defines superblock private state with mount options, superblock pointer, and EFI ops notifier.
- Defines EFI variable identity as UTF-16 name plus vendor GUID.
- Defines `struct efivar_entry`, embedding a VFS inode plus open count and removed flag.
- Provides `efivar_entry()` container helper.
- Declares variable enumeration, get, set/get-size, delete, validation, name conversion, removability, and presence-check helpers.
- Exposes efivarfs file operations, directory inode operations, and inode allocation helper.

Important interactions:
- Shared contract between `file.c`, `inode.c`, `super.c`, and `vars.c`.
- Separates firmware variable identity from VFS inode state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/efivarfs/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/efivarfs/super.c -->
# File Research: sources/os/linux/linux/fs/efivarfs/super.c

Implements efivarfs mounting, superblock operations, dentry handling, enumeration, freeze/thaw resync, and module registration.

Key behavior:
- Allocates/free `struct efivar_entry` inodes.
- Registers a notifier so EFI variable ops transitions can force the superblock read-only or read-write.
- `statfs` reports firmware variable storage via `QueryVariableInfo()` when available and accounts for reserved space.
- Custom dentry compare/hash treats the variable-name portion as case-sensitive and the GUID portion as case-insensitive.
- Mount options support `uid=` and `gid=`.
- `fill_super` sets magic, operations, dentry ops, no-cache dentries, root inode, write support flags, notifier, and initial EFI variable enumeration.
- Enumeration callback skips the Linux EFI random seed variable and creates a persistent dentry per firmware variable.
- `unfreeze_fs` rescans firmware variables, updates inode sizes, removes missing variables, and creates newly discovered entries.
- `init_fs_context` rejects unavailable EFI services and initializes default root uid/gid.
- Registers the `efivarfs` filesystem with `FS_POWER_FREEZE`.

Important interactions:
- Uses `efivar_init()` from `vars.c` for enumeration and duplicate detection.
- Uses `try_lookup_noperm()` for variable presence and resync checks.
- Backed by anonymous/single-super style VFS state, not a block device.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/efivarfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/efivarfs/vars.c -->
# File Research: sources/os/linux/linux/fs/efivarfs/vars.c

Implements EFI variable validation, name conversion, enumeration, and firmware get/set/delete wrappers.

Key behavior:
- Validates known sensitive EFI variables such as BootOrder, Boot####, Driver####, console paths, language strings, timeout, and OS indications.
- Load-option validation checks hex suffixes, descriptor length, file-path length, and valid EFI device-path termination.
- Maintains a sorted validation/whitelist table; variables in the table are considered removable.
- `efivar_get_utf8name()` converts UTF-16 variable names to `name-guid` UTF-8 filenames and replaces slashes with `!`.
- `efivar_validate()` converts names to UTF-8 and dispatches matching validators.
- `efivar_init()` iterates firmware variables under `efivar_lock()`, handles old firmware buffer-size quirks, detects duplicate variables when requested, and calls a supplied callback for each variable.
- `efivar_entry_delete()` deletes a variable by calling SetVariable with zero attributes and size.
- `efivar_entry_size()` gets variable size through the expected `EFI_BUFFER_TOO_SMALL` status.
- `efivar_entry_get()` wraps GetVariable with locking.
- `efivar_entry_set_get_size()` validates data, sets the variable, then re-queries size to detect overwrite, append, or deletion.

Important interactions:
- Imports the `EFIVAR` namespace.
- Provides the policy boundary that prevents malformed boot variables from being written through efivarfs.
- Locking centralizes EFI runtime service access and keeps set/get-size behavior atomic.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/efivarfs/vars.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/efs/Kconfig -->
# File Research: sources/os/linux/linux/fs/efs/Kconfig

Defines the `EFS_FS` build option.

Key behavior:
- Adds tristate support for the SGI IRIX EFS filesystem.
- Depends on `BLOCK` and selects `BUFFER_HEAD`.
- Documents the implementation as read-only.
- Module name is `efs`.

Important interactions:
- EFS support is for legacy SGI media and partitions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/efs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/efs/Makefile -->
# File Research: sources/os/linux/linux/fs/efs/Makefile

Builds the EFS filesystem module.

Key behavior:
- Adds `efs.o` when `CONFIG_EFS_FS` is enabled.
- Links `super.o`, `inode.o`, `namei.o`, `dir.o`, `file.o`, and `symlink.o`.

Important interactions:
- The module is organized around read-only VFS operations plus extent mapping.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/efs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/efs/dir.c -->
# File Research: sources/os/linux/linux/fs/efs/dir.c

Implements EFS directory iteration.

Key behavior:
- Exposes directory file operations with generic llseek/read, `efs_readdir`, and generic lease support.
- Directory inode operations only provide lookup.
- `efs_readdir()` maps `ctx->pos` to an EFS directory block and slot.
- Reads each directory block through `sb_bread(efs_bmap())`.
- Validates the EFS directory block magic.
- Iterates active slots, validates name bounds, and emits directory entries with inode numbers and unknown d_type.
- Updates `ctx->pos` using block/slot encoding.

Important interactions:
- Uses EFS fixed 512-byte directory blocks and slot offset tables.
- Relies on `efs_bmap()` for logical-to-physical block mapping.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/efs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/efs/efs.h -->
# File Research: sources/os/linux/linux/fs/efs/efs.h

Defines EFS on-disk structures, in-memory inode private state, constants, and internal APIs.

Key behavior:
- Sets EFS block size to 512 bytes.
- Defines extent format, device encoding, 128-byte disk inode layout, directory entries, directory block layout, slot macros, and maximum name length.
- Defines `struct efs_inode_info` with direct extents, extent counts, last extent cache, and embedded VFS inode.
- Provides `INODE_INFO()` and `SUPER_INFO()` container helpers.
- Declares directory, symlink, inode, lookup, export, block mapping, and bmap interfaces.

Important interactions:
- Shared by all EFS implementation files.
- The extent structure is stored on disk in packed byte form and converted manually in `inode.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/efs/efs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/efs/file.c -->
# File Research: sources/os/linux/linux/fs/efs/file.c

Implements read-only block mapping helpers for regular file I/O.

Key behavior:
- `efs_get_block()` rejects create requests with `-EROFS`.
- Returns holes/EOF without mapping when logical block is beyond `i_blocks`.
- Maps valid logical blocks through `efs_map_block()` and `map_bh()`.
- `efs_bmap()` validates non-negative and in-range block numbers, then returns the physical block mapping.

Important interactions:
- Used by `block_read_full_folio()`, `generic_block_bmap()`, directory reads, and symlink reads.
- Enforces the filesystem’s read-only behavior at the block-mapping layer.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/efs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/efs/inode.c -->
# File Research: sources/os/linux/linux/fs/efs/inode.c

Implements EFS inode loading and extent-based logical block mapping.

Key behavior:
- Defines address-space operations using `block_read_full_folio()` and `generic_block_bmap()`.
- `extent_copy()` converts the raw 8-byte on-disk extent into CPU-endian bitfields.
- `efs_iget()` computes the disk location of an inode from cylinder group layout, reads the dinode, fills VFS metadata, decodes device numbers, copies direct extents, and installs operations by file type.
- Regular files use `generic_ro_fops` plus EFS address-space operations.
- Symlinks use page symlink operations and EFS symlink aops.
- Special files are initialized from decoded device numbers.
- `efs_extent_check()` tests whether an extent covers a logical block.
- `efs_map_block()` maps logical blocks through direct extents or indirect extent blocks, caching the last matching extent.

Important interactions:
- Depends on superblock geometry loaded by `super.c`.
- Extent magic validation treats nonzero magic as corruption.
- The indirect extent search reads extent blocks with `sb_bread()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/efs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/efs/namei.c -->
# File Research: sources/os/linux/linux/fs/efs/namei.c

Implements EFS lookup and exportfs inode handle resolution.

Key behavior:
- `efs_find_entry()` scans directory blocks and slots for an exact bytewise name match.
- `efs_lookup()` maps the found inode number through `efs_iget()` and splices aliases.
- Provides NFS/export helpers via `generic_fh_to_dentry()` and `generic_fh_to_parent()`.
- `efs_nfs_get_inode()` rejects inode 0 and stale generation mismatches.
- `efs_get_parent()` resolves `..` and returns a dentry alias for the parent inode.

Important interactions:
- Shares the directory parsing format used by `dir.c`.
- Export operations in `super.c` call these helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/efs/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/efs/super.c -->
# File Research: sources/os/linux/linux/fs/efs/super.c

Implements EFS module registration, superblock setup, SGI volume-header parsing, and statfs.

Key behavior:
- Registers a block-device filesystem named `efs`.
- Allocates EFS private inodes from `efs_inode_cache`.
- Provides export operations for inode-number file handles.
- Parses the SGI volume header, validates checksum, scans partition entries, and locates an EFS slice.
- Validates the EFS superblock magic and loads filesystem geometry/free-count fields.
- `fill_super` sets 512-byte block size, reads volume header and superblock, forces read-only mode, installs super/export operations, loads root inode, and creates root dentry.
- Reconfigure always syncs and forces read-only.
- `statfs` reports total/free data blocks, inode counts, fsid, block size, and max name length.

Important interactions:
- Uses SGI partition constants from `<linux/efs_vh.h>` and superblock layout from `<linux/efs_fs_sb.h>`.
- EFS is mounted with `FS_REQUIRES_DEV`.
- All mutation attempts are prevented by read-only mount state and read-only file/block operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/efs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/efs/symlink.c -->
# File Research: sources/os/linux/linux/fs/efs/symlink.c

Implements EFS symlink page reading.

Key behavior:
- Rejects symlink targets longer than two EFS blocks.
- Reads up to the first 512 bytes from logical block 0.
- Reads a second block when needed.
- Copies the target into the folio, appends a NUL terminator, and completes folio read status.

Important interactions:
- Uses `efs_bmap()` to locate symlink data blocks.
- Installed as `efs_symlink_aops` by `efs_iget()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/efs/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/erofs/Kconfig -->
# File Research: sources/os/linux/linux/fs/erofs/Kconfig

Defines EROFS build-time feature options.

Key behavior:
- Adds `EROFS_FS`, depending on block devices and selecting CRC32 and iomap support.
- Optional features include debug checks, xattrs, POSIX ACLs, security labels, file-backed mounts, compression, LZMA, DEFLATE, Zstandard, hardware acceleration, deprecated fscache-on-demand reads, per-CPU decompression workers, high-priority workers, and page-cache sharing.
- Compression options select their corresponding decompressor libraries.
- File-backed EROFS is enabled by default.
- On-demand fscache support is documented as deprecated.

Important interactions:
- Feature flags control which object files are linked by the Makefile and which helpers compile as stubs in `internal.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/erofs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/erofs/Makefile -->
# File Research: sources/os/linux/linux/fs/erofs/Makefile

Builds EROFS core and optional feature objects.

Key behavior:
- Core objects are `super.o`, `inode.o`, `data.o`, `namei.o`, `dir.o`, and `sysfs.o`.
- Adds xattr, compression, algorithm-specific decompressors, crypto acceleration, file-backed I/O, fscache, and inode-sharing objects according to Kconfig options.

Important interactions:
- Mirrors the feature gates defined in `Kconfig`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/erofs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/erofs/compress.h -->
# File Research: sources/os/linux/linux/fs/erofs/compress.h

Declares EROFS decompression request structures, decompressor interfaces, and shared compression helpers.

Key behavior:
- `z_erofs_decompress_req` describes input/output page arrays, offsets, sizes, algorithm, in-place/partial/fill-gap flags, and allocation policy.
- `z_erofs_decompressor` defines optional config/init/exit hooks plus the decompression callback.
- Defines markers for short-lived and preallocated folios.
- Provides helpers to identify/recycle short-lived decompression pages.
- Declares LZMA, DEFLATE, ZSTD, decompressor table, stream-buffer switching, compressed-size fixup, subsystem init/exit, and crypto acceleration hooks.
- Provides no-op crypto engine helpers when acceleration is disabled.

Important interactions:
- Shared by all decompressor implementations and compressed-data read paths.
- The request structure is the ABI between zdata/zmap code and algorithm-specific decoders.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/erofs/compress.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/erofs/data.c -->
# File Research: sources/os/linux/linux/fs/erofs/data.c

Implements EROFS metadata buffering, uncompressed block mapping, device mapping, online folio completion, iomap integration, and regular file operations.

Key behavior:
- `erofs_bread()` reads metadata folios from block device, fscache inode, file-backed mapping, or metabox mapping and optionally kmaps them.
- `erofs_init_metabuf()` selects the correct metadata mapping based on metabox, file-backed, fscache, or block-device mode.
- `erofs_map_blocks()` maps flat plain/inline data and chunk-based data, returning logical/physical lengths, device id, metadata flags, and hole state.
- Validates inline data does not cross a metadata block.
- `erofs_map_dev()` resolves device ids and flat-device offsets to block devices, files, fscache blobs, and DAX devices.
- Online folio helpers track split async completions, error state, and D-cache flushing in `folio->private`.
- Iomap operations map holes, inline data, and mapped extents for read, DAX, direct I/O, fiemap, bmap, SEEK_DATA, and SEEK_HOLE.
- `erofs_read_folio()` and `erofs_readahead()` use iomap reads, resolving shared inodes when page-cache sharing is enabled.
- File read supports DAX, direct I/O for block-backed uncompressed files, and buffered reads.
- File operations include llseek, read_iter, ioctl, mmap setup, splice, THP unmapped-area helper, and leases.

Important interactions:
- Compression fiemap delegates to `z_erofs_iomap_report_ops`.
- File-backed and fscache modes are selected through `internal.h` helpers.
- DAX mmap rejects shared writable mappings because EROFS is read-only.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/erofs/data.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/erofs/decompressor.c -->
# File Research: sources/os/linux/linux/fs/erofs/decompressor.c

Implements core EROFS decompression support, including LZ4, plain transforms, stream buffer management, algorithm config parsing, and decompressor lifecycle.

Key behavior:
- Loads LZ4 configuration from compression config records or legacy superblock fields.
- Tracks LZ4 pcluster and sliding-distance requirements and grows global buffers accordingly.
- Prepares sparse output page arrays by allocating short-lived bounce pages where needed.
- Handles LZ4 input/output overlap, including in-place decompression, vmapped input, and per-CPU bounce buffers.
- `z_erofs_fixup_insize()` skips zero padding to determine exact compressed payload start.
- Provides optimized single-page LZ4 and general multi-page LZ4 decode paths.
- Implements shifted/interlaced plain transforms for non-compressing encoded layouts.
- `z_erofs_stream_switch_bufs()` coordinates multi-call streaming decoders, maps new input/output pages, allocates gap pages, and avoids input/output overlap by bouncing.
- Defines the runtime decompressor table for shifted, interlaced, LZ4, and optional LZMA/DEFLATE/ZSTD.
- Parses compression config records from metadata and calls each algorithm’s config hook.
- Initializes/exits all enabled decompressor backends.

Important interactions:
- Used by compressed read paths outside this group.
- Algorithm availability is checked against on-disk `available_compr_algs`.
- Short-lived pages are returned through the EROFS pagepool.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/erofs/decompressor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/erofs/decompressor_crypto.c -->
# File Research: sources/os/linux/linux/fs/erofs/decompressor_crypto.c

Provides optional hardware/crypto API decompression acceleration for EROFS.

Key behavior:
- Wraps the kernel async compression API (`crypto_acomp`) for decompression.
- Builds scatterlists from request input and output pages.
- Fixes compressed input size before submitting the async request.
- Converts crypto decompression errors to `-EIO`.
- Maintains per-algorithm crypto engine lists; currently DEFLATE has a named `qat_deflate` engine entry.
- `z_erofs_crypto_decompress()` locates an enabled engine, allocates missing output pages, and dispatches crypto decompression.
- `z_erofs_crypto_enable_engine()` allocates and enables a matching crypto transform by name.
- Can disable all engines and show enabled engine names.

Important interactions:
- Used opportunistically by DEFLATE for non-partial decoding.
- Protected by `z_erofs_crypto_rwsem`.
- Falls back via `-EOPNOTSUPP` when no engine is enabled.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/erofs/decompressor_crypto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/erofs/decompressor_deflate.c -->
# File Research: sources/os/linux/linux/fs/erofs/decompressor_deflate.c

Implements EROFS DEFLATE decompression.

Key behavior:
- Maintains a global pool of zlib inflate streams sized by `deflate_streams` or possible CPUs.
- Lazily allocates zlib workspaces when DEFLATE config is loaded.
- Validates DEFLATE config and windowbits.
- Decompression obtains exact input size, waits for an available stream, initializes raw inflate, and streams through `z_erofs_stream_switch_bufs()`.
- Uses a per-stream bounce page and forces `fillgaps` because DEFLATE cannot write to NULL output buffers.
- Returns stream contexts to the pool and wakes waiters.
- Optionally attempts crypto-accelerated DEFLATE first for non-partial requests.

Important interactions:
- Registered as `z_erofs_deflate_decomp`.
- Uses common streaming and padding helpers from `decompressor.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/erofs/decompressor_deflate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/erofs/decompressor_lzma.c -->
# File Research: sources/os/linux/linux/fs/erofs/decompressor_lzma.c

Implements EROFS microLZMA decompression.

Key behavior:
- Maintains a global stream pool sized by `lzma_streams` or possible CPUs.
- Validates LZMA config format and dictionary size.
- Resizes all stream decoder states when a larger dictionary is required, isolating the stream list to avoid races.
- Decompression fixes exact input size, obtains an available stream, resets the microLZMA decoder, and streams input/output buffers with overlap protection.
- Uses per-stream bounce buffers and returns stream contexts to the pool after each request.
- Cleans up decoder states on exit.

Important interactions:
- Registered as `z_erofs_lzma_decomp`.
- Uses kernel XZ microLZMA decoder and common EROFS stream switching.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/erofs/decompressor_lzma.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/erofs/decompressor_zstd.c -->
# File Research: sources/os/linux/linux/fs/erofs/decompressor_zstd.c

Implements EROFS Zstandard decompression.

Key behavior:
- Maintains a global pool of ZSTD stream contexts sized by `zstd_streams` or possible CPUs.
- Validates ZSTD config and window log.
- Resizes all stream workspaces when a larger dictionary/window is required.
- Isolates stream lists under spinlock and waits when no stream is available.
- Decompression fixes exact input size, initializes a ZSTD dstream, uses common stream switching, and detects corrupted or truncated streams.
- Forces `fillgaps` because ZSTD requires real output buffers.
- Frees workspaces and contexts on exit.

Important interactions:
- Registered as `z_erofs_zstd_decomp`.
- Uses `zstd_dstream_workspace_bound()` and kernel ZSTD streaming APIs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/erofs/decompressor_zstd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/erofs/dir.c -->
# File Research: sources/os/linux/linux/fs/erofs/dir.c

Implements EROFS directory iteration.

Key behavior:
- Parses sorted fixed-block directory entries and variable-length names.
- `erofs_fill_dentries()` validates name offsets, name lengths, maximum name length, and block bounds before emitting entries.
- `erofs_readdir()` reads directory blocks through `erofs_bread()`, supports arbitrary starting positions, and performs optional directory readahead.
- Handles fatal signals with `-ERESTARTSYS`.
- Emits a synthetic `.` entry at end for directories with the on-disk dot entry omitted.
- Directory file operations include llseek, generic read, iterate, ioctl, compat ioctl, and generic leases.

Important interactions:
- Uses inode `dot_omitted` populated by `inode.c`.
- Directory readahead size comes from `EROFS_I_SB(dir)->dir_ra_bytes`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/erofs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/erofs/erofs_fs.h -->
# File Research: sources/os/linux/linux/fs/erofs/erofs_fs.h

Defines the EROFS on-disk format.

Key behavior:
- Defines superblock offset, compatible/incompatible feature bits, and full incompatible-feature mask.
- Defines device slot format and 144-byte superblock layout, including 48-bit block/root fields, compression algorithm bitmap, device table metadata, packed/metabox inode nids, xattr prefix metadata, and build time.
- Defines inode data layouts: flat plain, compressed full, flat inline, compressed compact, and chunk-based.
- Defines compact and extended inode layouts.
- Defines inline/shared xattr headers, xattr entry format, long xattr prefixes, name filters, and xattr sizing helpers.
- Defines chunk mapping formats, null address marker, block-map entry, chunk index, directory entry format, and max name length.
- Defines compression algorithm ids and config records for LZ4, LZMA, DEFLATE, and ZSTD.
- Defines compressed map headers, lcluster indexes, extent records, advise bits, and extent record sizing.
- `erofs_check_ondisk_layout_definitions()` uses build-time assertions to lock structure sizes and layout assumptions.

Important interactions:
- Shared with userspace tooling and kernel implementation; changes here are on-disk format changes.
- Many runtime checks in `inode.c`, `data.c`, and decompressor code interpret these fields.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/erofs/erofs_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/erofs/fileio.c -->
# File Research: sources/os/linux/linux/fs/erofs/fileio.c

Implements EROFS file-backed image I/O.

Key behavior:
- Defines request objects embedding a bio, fixed bvec array, kiocb, superblock, and refcount.
- Submits reads to the backing file with `vfs_iocb_iter_read()`, optionally using direct I/O when mount option and file mode allow it.
- Completion validates full-length reads, propagates errors to bios or online folios, ends bios, and frees request state.
- Provides bio allocation/submission wrappers for code that issues block-like reads against file-backed devices.
- `erofs_fileio_scan_folio()` maps each folio range, copies inline metadata, zeroes holes, or batches mapped extents into file-backed bio-style reads.
- Splits online folio completion for each attached async segment.
- Implements read_folio and readahead aops for file-backed mode.

Important interactions:
- Uses `erofs_map_blocks()` and `erofs_map_dev()` to translate logical file data to backing-file offsets.
- Cooperates with online folio helpers in `data.c`.
- Selected by `erofs_get_aops()` when `CONFIG_EROFS_FS_BACKED_BY_FILE` and file-backed mode are active.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/erofs/fileio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/erofs/fscache.c -->
# File Research: sources/os/linux/linux/fs/erofs/fscache.c

Implements deprecated EROFS fscache/cachefiles on-demand read support.

Key behavior:
- Defines fscache I/O and request wrappers with refcounted completion.
- Reads cache data through `fscache_begin_read_operation()`, `prepare_ondemand_read()`, and `fscache_read()`.
- Provides bio allocation/submission wrappers for fscache-backed devices.
- Metadata read_folio reads from a fscache cookie-backed anonymous inode.
- Data reads map logical ranges, copy inline metadata, zero holes, or read mapped extents from the proper fscache cookie.
- Readahead drains folios from the readahead control and completes them through request completion.
- Manages shared fscache domains, volumes, cookies, and a pseudo mount for shareable anonymous blob inodes.
- Registers the primary filesystem blob cookie and unregisters cookies/domain/volume on teardown.
- Shared-domain mode enforces uniqueness for the primary fsid blob.

Important interactions:
- Used only when `CONFIG_EROFS_FS_ONDEMAND` and fscache mode are active.
- Multi-device mappings use per-device fscache cookies.
- Domain and cookie lists are protected by separate mutexes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/erofs/fscache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/erofs/inode.c -->
# File Research: sources/os/linux/linux/fs/erofs/inode.c

Implements EROFS inode loading, VFS operation assignment, inode lookup, stat attributes, and ioctls.

Key behavior:
- Reads compact or extended on-disk inodes from normal metadata or metabox metadata.
- Validates inode format, datalayout, nonnegative size, chunk format, and compressed-filesystem availability.
- Fills mode, uid/gid, nlink, mtime, size, start block, rdev, xattr size, chunk fields, DAX flag, and dot-omitted state.
- Caches small inline symlink targets as fast symlinks and validates their length/NUL behavior.
- Assigns file, directory, symlink, or special inode operations and address-space operations.
- Uses inode sharing when enabled, switching regular file fops to `erofs_ishare_fops`.
- `erofs_iget()` uses `iget5_locked()` keyed by nid with inode-number squashing on narrow `ino_t`.
- `getattr` reports immutable and compressed attributes and direct-I/O alignment when supported.
- Implements `FS_IOC_GETFSLABEL`.
- Exposes generic, page symlink, and fast symlink inode operation tables.

Important interactions:
- Uses xattr/ACL helpers to cache no-ACL state and list xattrs.
- Calls `erofs_get_aops()` to select compressed, fscache, file-backed, or standard aops.
- DAX is limited to regular flat plain or chunk-based inodes under `DAX_ALWAYS`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/erofs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/erofs/internal.h -->
# File Research: sources/os/linux/linux/fs/erofs/internal.h

Defines EROFS in-memory state, mount options, mapping structures, feature helpers, and internal function prototypes.

Key behavior:
- Provides logging macros and debug BUG behavior.
- Defines EROFS scalar types for nid, offsets, and block numbers.
- Defines device info, mount options, device table context, LZ4 state, fscache/domain state, xattr prefix state, superblock private state, and inode private state.
- Defines mount flags for user xattrs, ACLs, DAX, direct I/O, and inode sharing.
- Provides mode helpers for file-backed and fscache mounts.
- Defines metadata buffer state and block/offset conversion helpers.
- Generates feature-test helpers for compat and incompat superblock bits.
- Defines metabox inode-number conversion and inode metadata location helpers.
- Defines map flags for mapped extents, inline metadata, partial mappings, fragment data, and full encoded-data coverage.
- Declares all major EROFS VFS operation tables, mapping helpers, sysfs helpers, decompression helpers, fscache/fileio helpers, and inode-sharing helpers.
- `erofs_get_aops()` selects compressed, fscache, file-backed, or standard address-space operations.

Important interactions:
- Central private header used by all EROFS implementation files.
- Compile-time feature stubs keep call sites simple when optional features are disabled.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/erofs/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/erofs/ishare.c -->
# File Research: sources/os/linux/linux/fs/erofs/ishare.c

Implements experimental EROFS page-cache sharing among files with identical content fingerprints.

Key behavior:
- Uses an anonymous EROFS mount to host shared inodes.
- Builds a fingerprint from inode xattrs plus domain id and hashes it with xxhash.
- `erofs_ishare_fill_inode()` finds or creates a shared inode keyed by fingerprint, verifies matching aops and size, and links the real inode into the shared inode’s list.
- `erofs_ishare_free_inode()` unlinks the real inode and drops the shared inode reference.
- Open creates a backing file pointing at the shared inode mapping and rejects `O_DIRECT`.
- Read iter clones the kiocb onto the backing file and reads from the shared page cache.
- mmap swaps the VMA file to the backing file after security checks.
- fadvise forwards to the backing file.
- `erofs_real_inode()` resolves a shared anonymous inode back to one linked real inode for mapping decisions.
- Init mounts the anonymous filesystem and sets up backing-device info; exit unmounts it.

Important interactions:
- Requires `CONFIG_EROFS_FS_PAGE_CACHE_SHARE`.
- Depends on xattr fingerprinting from `xattr.c`.
- Excluded with fscache-on-demand by Kconfig.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/erofs/ishare.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/erofs/namei.c -->
# File Research: sources/os/linux/linux/fs/erofs/namei.c

Implements EROFS name lookup using sorted directory blocks.

Key behavior:
- Defines internal qstr ranges for lookup comparisons.
- `erofs_dirnamecmp()` compares names while reusing already matched prefixes and tolerating corrupted on-disk names outside debug builds.
- `find_target_block()` binary-searches directory blocks by their first entry name, keeping the best candidate block.
- `find_target_dirent()` binary-searches within a directory block.
- `erofs_namei()` resolves a qstr to nid and file type or returns `-ENOENT`.
- `erofs_lookup()` rejects names longer than `EROFS_NAME_LEN`, calls `erofs_namei()`, loads the inode with `erofs_iget()`, and splices aliases.
- Directory inode operations provide lookup, getattr, listxattr, ACL retrieval, and fiemap.

Important interactions:
- Relies on EROFS directory entries being sorted alphabetically.
- Uses `erofs_bread()` for directory block access.
- Lookup returns raw on-disk nid, including possible metabox nid flag.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/erofs/namei.c -->