# Group Research: group_975_linux_stable_sources_os_linux_linux_stable_fs_ecryptfs_miscdev_c_sou_8b1018e2a484

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/miscdev.c -->
# File Research: sources/os/linux/linux-stable/fs/ecryptfs/miscdev.c

## Summary
Implements the eCryptfs misc character device `/dev/ecryptfs`, used for kernel-to-userspace daemon messaging.

## Main Responsibilities
- Registers and deregisters the misc device.
- Opens one daemon channel per effective UID.
- Queues kernel requests to the daemon and wakes daemon readers.
- Parses daemon responses, hello, and quit packets.
- Handles daemon poll, read, write, and release operations.

## Key APIs
- `ecryptfs_send_miscdev()`
- `ecryptfs_init_ecryptfs_miscdev()`
- `ecryptfs_destroy_ecryptfs_miscdev()`

## Important Behavior
Outgoing messages are stored as `ecryptfs_msg_ctx` entries on `daemon->msg_ctx_out_queue`. `read()` formats queued messages as packet type, big-endian counter, optional encoded length, and optional `struct ecryptfs_message`.

Incoming `write()` validates packet size, parses the encoded message length, copies the user buffer, and dispatches `ECRYPTFS_MSG_RESPONSE` to `ecryptfs_process_response()`.

## Risks
Daemon lifetime depends on flags such as `ECRYPTFS_DAEMON_MISCDEV_OPEN`, `ECRYPTFS_DAEMON_IN_READ`, and `ECRYPTFS_DAEMON_ZOMBIE` under two mutex domains. Packet-size validation is central because data crosses directly from userspace into kernel response handling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/miscdev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/mmap.c -->
# File Research: sources/os/linux/linux-stable/fs/ecryptfs/mmap.c

## Summary
Provides eCryptfs address-space operations for reading, writing, encrypting, decrypting, and syncing inode size metadata.

## Main Responsibilities
- Encrypts dirty folios during writeback.
- Reads lower data and decrypts it unless encrypted-view mode is active.
- Synthesizes encrypted-view headers when metadata lives in xattrs.
- Implements write begin/end behavior and hole zeroing.
- Writes logical file size to either the lower file header or metadata xattr.

## Key APIs
- `ecryptfs_write_inode_size_to_metadata()`
- `ecryptfs_aops`

## Important Behavior
`read_folio()` chooses between passthrough lower read, encrypted-view copy-up, or decryption. `write_begin()` prepares missing or partial pages, fills holes through truncate, and handles encrypted-view data. `write_end()` encrypts completed pages and updates encrypted metadata size.

## Risks
This file has delicate ordering around folio uptodate state, lower inode size, encrypted metadata, and xattr writes. The address-space ops still use block dirty/invalidate hooks under `CONFIG_BLOCK`, with an in-file warning that this is a compatibility compromise.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/mmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/read_write.c -->
# File Research: sources/os/linux/linux-stable/fs/ecryptfs/read_write.c

## Summary
Contains lower-file read/write helpers and a page-by-page eCryptfs write helper used outside the normal mmap path.

## Main Responsibilities
- Performs `kernel_write()` and `kernel_read()` against the lower file.
- Maps folios for lower page segment read/write.
- Implements arbitrary-offset writes with hole zeroing and optional encryption.
- Updates encrypted inode-size metadata after extending writes.

## Key APIs
- `ecryptfs_write_lower()`
- `ecryptfs_write_lower_page_segment()`
- `ecryptfs_write()`
- `ecryptfs_read_lower()`
- `ecryptfs_read_lower_page_segment()`

## Important Behavior
`ecryptfs_write()` starts at the old EOF when writing past EOF, fills gaps with zeros, copies requested data once the target offset is reached, encrypts full pages when needed, and grows `i_size` after successful writes.

## Risks
The helper assumes a valid lower file pointer in inode-private state. In the unencrypted branch of `ecryptfs_write()`, the size passed to `ecryptfs_write_lower_page_segment()` is based on cumulative copied data, so this path deserves caution when auditing partial or multi-page unencrypted writes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/read_write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/super.c -->
# File Research: sources/os/linux/linux-stable/fs/ecryptfs/super.c

## Summary
Defines eCryptfs superblock operations and inode allocation/destruction behavior.

## Main Responsibilities
- Allocates eCryptfs inode-private objects from `ecryptfs_inode_info_cache`.
- Initializes and destroys per-inode cryptographic state.
- Forwards `statfs()` to the lower filesystem while adjusting type/name length.
- Drops lower inode references on eviction.
- Emits mount options through `show_options()`.

## Key APIs
- `ecryptfs_sops`
- `ecryptfs_inode_info_cache`

## Important Behavior
Allocated inodes initialize `crypt_stat`, lower-file mutex/count state, and an empty lower-file pointer. Destruction asserts that the lower file has already been released, then destroys cryptographic state.

## Risks
Lifetime is stacked: eCryptfs inode teardown must release lower file and lower inode references exactly once. Mount option display walks global auth token state under its mutex.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ecryptfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/efivarfs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/efivarfs/Kconfig

## Summary
Declares the EFI variable filesystem configuration option.

## Main Contents
- `CONFIG_EFIVAR_FS`
- Depends on `EFI`
- Defaults to module build
- Module name is `efivarfs`

## Important Behavior
The help text positions efivarfs as the replacement for old EFI variable sysfs support because it avoids the old 1024-byte variable size limit.

## Risks
None in code logic; enabling this exposes firmware variables through a filesystem interface, with safety handled by the implementation files.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/efivarfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/efivarfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/efivarfs/Makefile

## Summary
Builds the efivarfs module.

## Main Contents
`efivarfs.o` is built from:
- `inode.o`
- `file.o`
- `super.o`
- `vars.o`

## Risks
The object list shows the implementation is compact and all behavior is concentrated in inode, file, superblock, and firmware-variable helper code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/efivarfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/efivarfs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/efivarfs/file.c

## Summary
Implements regular-file operations for EFI variables exposed through efivarfs.

## Main Responsibilities
- Reads EFI variable attributes plus data.
- Writes attributes plus data to firmware.
- Tracks open counts and deferred removal.
- Removes dentries after deletion once all opens close.

## Key APIs
- `efivarfs_file_operations`

## Important Behavior
Writes require at least a 32-bit attribute word and reject unknown attribute bits. After a successful set, the file size is updated to attributes plus firmware-reported data size. If firmware reports `ENOENT`, size becomes zero and release removes the file.

Reads rate-limit callers through the user ratelimit state, query variable size first, then return attributes followed by data.

## Risks
Writes call firmware runtime services under inode serialization. Zero-size files represent uncommitted or deleted variables, so users of `i_size` must preserve that meaning.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/efivarfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/efivarfs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/efivarfs/inode.c

## Summary
Implements efivarfs inode creation, directory operations, immutable flag handling, and custom setattr behavior.

## Main Responsibilities
- Allocates inodes with mount uid/gid.
- Validates efivarfs filenames of `Name-GUID` form.
- Creates new variable dentries.
- Deletes firmware variables on unlink.
- Exposes and updates `FS_IMMUTABLE_FL`.

## Key APIs
- `efivarfs_get_inode()`
- `efivarfs_dir_inode_operations`

## Important Behavior
Created variables copy the filename prefix into UTF-16-ish firmware-name storage and parse the trailing GUID. The Linux EFI random seed variable is blocked from creation. Variables not whitelisted by validation policy are created immutable by default.

## Risks
Name validation is security-sensitive because filenames encode firmware variable identity. `efivarfs_setattr()` intentionally avoids normal size updates so file size continues to reflect firmware variable state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/efivarfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/efivarfs/internal.h -->
# File Research: sources/os/linux/linux-stable/fs/efivarfs/internal.h

## Summary
Defines efivarfs private structures and cross-file interfaces.

## Main Contents
- `struct efivarfs_mount_opts`
- `struct efivarfs_fs_info`
- `struct efi_variable`
- `struct efivar_entry`
- Firmware variable helper declarations.
- File, directory, and inode operation declarations.

## Important Details
`efivar_entry` embeds both firmware identity and VFS inode state, plus `open_count` and `removed` state for deferred deletion. The helper `efivar_entry()` converts a VFS inode to its containing entry.

## Risks
The header encodes the central lifetime model: firmware variables, dentries, and inodes are represented by one embedded object.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/efivarfs/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/efivarfs/super.c -->
# File Research: sources/os/linux/linux-stable/fs/efivarfs/super.c

## Summary
Implements efivarfs mount, superblock, dentry, statfs, freeze/thaw resync, and module registration logic.

## Main Responsibilities
- Allocates efivarfs private inodes.
- Parses `uid=` and `gid=` mount options.
- Builds the root and populates variable dentries from firmware.
- Handles case-sensitive variable names and case-insensitive GUID suffixes.
- Tracks EFI ops read-only/read-write notifier events.
- Resyncs filesystem state on thaw.

## Key APIs
- `efivarfs_variable_is_present()`
- `efivarfs_init_fs_context()`
- `efivarfs_kill_sb()`

## Important Behavior
Mount uses `get_tree_single()`. Initial population calls `efivar_init()` and creates persistent dentries for each firmware variable except the Linux EFI random seed. `statfs()` reports exact EFI storage information when firmware supports `QueryVariableInfo()`.

## Risks
Dentry hashing/comparison must match firmware identity rules. Thaw resync deletes missing variables and creates newly discovered ones, so it mutates the dentry tree based on firmware state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/efivarfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/efivarfs/vars.c -->
# File Research: sources/os/linux/linux-stable/fs/efivarfs/vars.c

## Summary
Wraps EFI variable runtime operations and validates sensitive variable formats.

## Main Responsibilities
- Validates boot-order, load-option, device-path, uint16, and ASCII-string variables.
- Converts EFI UTF-16 names plus GUIDs to efivarfs filenames.
- Iterates firmware variables at mount/resync time.
- Deletes, sizes, reads, and writes EFI variables under the efivar lock.

## Key APIs
- `efivar_get_utf8name()`
- `efivar_validate()`
- `efivar_variable_is_removable()`
- `efivar_init()`
- `efivar_entry_delete()`
- `efivar_entry_size()`
- `efivar_entry_get()`
- `efivar_entry_set_get_size()`

## Important Behavior
The validation table is both a format validator and whitelist for variables that are not immutable by default. Duplicate firmware variables during enumeration trigger a warning and terminate enumeration to avoid infinite loops.

## Risks
Firmware behavior is not trusted: enumeration size is capped, duplicates are detected, malformed boot variables are rejected, and EFI status codes are converted carefully.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/efivarfs/vars.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/efs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/efs/Kconfig

## Summary
Declares SGI EFS filesystem support.

## Main Contents
- `CONFIG_EFS_FS`
- Depends on `BLOCK`
- Selects `BUFFER_HEAD`
- Described as read-only support for older SGI IRIX EFS media.

## Important Behavior
The help text explicitly states this implementation only offers read-only access.

## Risks
None in logic; enabling it adds support for old on-disk media formats handled by the EFS driver.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/efs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/efs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/efs/Makefile

## Summary
Builds the EFS filesystem module.

## Main Contents
`efs.o` is built from:
- `super.o`
- `inode.o`
- `namei.o`
- `dir.o`
- `file.o`
- `symlink.o`

## Risks
The module is small and all behavior is read-only block, inode, directory, lookup, and symlink support.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/efs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/efs/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/efs/dir.c

## Summary
Implements EFS directory file operations and readdir.

## Main Responsibilities
- Reads directory blocks through `sb_bread()`.
- Validates directory block magic.
- Iterates directory slots and emits entries.
- Checks entry bounds within a directory block.

## Key APIs
- `efs_dir_operations`
- `efs_dir_inode_operations`

## Important Behavior
Directory position encodes block and slot. Each block is mapped through `efs_bmap()`, checked for `EFS_DIRBLK_MAGIC`, then slots are walked and names emitted with `DT_UNKNOWN`.

## Risks
The code trusts many old on-disk layout fields after minimal checks. It does validate that name data remains inside the directory block before `dir_emit()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/efs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/efs/efs.h -->
# File Research: sources/os/linux/linux-stable/fs/efs/efs.h

## Summary
Defines EFS in-memory and on-disk structures, constants, helpers, and cross-file declarations.

## Main Contents
- 512-byte block constants.
- On-disk extent, inode, device, directory entry, and directory block layouts.
- `struct efs_inode_info`.
- Conversion helpers `INODE_INFO()` and `SUPER_INFO()`.
- Function declarations for inode, block mapping, lookup, export, and bmap operations.

## Important Details
EFS uses up to 12 direct extents stored in the inode and indirect extent blocks for larger files. Directory entries are slot-offset based inside fixed-size directory blocks.

## Risks
Bitfield and packed on-disk extent interpretation must remain consistent with IRIX EFS layout assumptions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/efs/efs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/efs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/efs/file.c

## Summary
Provides EFS block mapping helpers for regular file reads.

## Main Responsibilities
- Maps logical file blocks to physical blocks.
- Rejects create/write block mapping requests.
- Bounds block access by `inode->i_blocks`.

## Key APIs
- `efs_get_block()`
- `efs_bmap()`

## Important Behavior
`efs_get_block()` returns `-EROFS` for create requests and maps existing blocks through `efs_map_block()`. `efs_bmap()` validates negative and past-EOF block numbers before mapping.

## Risks
All I/O depends on correctness of `efs_map_block()` from `inode.c`; this file mainly enforces read-only behavior and range checks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/efs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/efs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/efs/inode.c

## Summary
Implements EFS inode loading, address-space operations, extent decoding, and logical-to-physical block mapping.

## Main Responsibilities
- Reads on-disk inodes from cylinder group layout.
- Converts extent byte fields into CPU-order extent records.
- Initializes VFS inode mode, ownership, times, size, device IDs, and file operations.
- Maps logical blocks through direct or indirect extents.

## Key APIs
- `efs_iget()`
- `efs_map_block()`

## Important Behavior
Inode block and offset are computed from EFS cylinder group metadata. Regular files use `generic_ro_fops` and block read aops. Symlinks use a custom symlink address-space op. Extent mapping caches the last successful extent in `lastextent`.

## Risks
Indirect extent search is subtle and depends on old EFS extent layout. Corrupt extent magic or unsupported inode modes fail inode loading.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/efs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/efs/namei.c -->
# File Research: sources/os/linux/linux-stable/fs/efs/namei.c

## Summary
Implements EFS name lookup and NFS export filehandle helpers.

## Main Responsibilities
- Finds directory entries by linear scanning.
- Looks up child inodes by inode number.
- Converts export filehandles to dentries/parents.
- Finds a directory parent using the `..` entry.

## Key APIs
- `efs_lookup()`
- `efs_fh_to_dentry()`
- `efs_fh_to_parent()`
- `efs_get_parent()`

## Important Behavior
`efs_find_entry()` reads each mapped directory block, checks magic, walks slots, and compares names by length and bytes.

## Risks
Lookup is linear and block-format dependent. Directory corruption returns lookup miss or errors depending on where the failure occurs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/efs/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/efs/super.c -->
# File Research: sources/os/linux/linux-stable/fs/efs/super.c

## Summary
Implements EFS filesystem registration, mount, superblock validation, SGI volume header handling, statfs, and inode-cache setup.

## Main Responsibilities
- Registers the `efs` filesystem.
- Allocates/free EFS inode cache objects.
- Parses SGI volume headers and finds EFS slices.
- Validates EFS superblocks.
- Forces read-only mounts.
- Provides NFS export operations.

## Key APIs
- `efs_fill_super()`
- `efs_validate_vh()`
- `efs_validate_super()`

## Important Behavior
Mount reads block 0 as an SGI volume header, optionally derives an EFS partition start, then reads the EFS superblock. The root inode is loaded from `EFS_ROOTINODE`. Reconfigure always sets `SB_RDONLY`.

## Risks
Several early mount error paths return without freeing `s_fs_info` directly, relying on mount teardown. On-disk volume headers and superblocks are minimally validated for old-media compatibility.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/efs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/efs/symlink.c -->
# File Research: sources/os/linux/linux-stable/fs/efs/symlink.c

## Summary
Implements EFS symlink folio reads.

## Main Responsibilities
- Reads symlink target data from one or two EFS blocks.
- Rejects symlinks larger than two EFS blocks.
- Null-terminates the target in the folio.

## Key APIs
- `efs_symlink_aops`

## Important Behavior
The symlink read path maps block 0 and optionally block 1 through `efs_bmap()`, copies target bytes, appends `'\0'`, and completes the folio read.

## Risks
Symlink targets are limited to 1024 bytes. Failed block reads complete the folio with error.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/efs/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/erofs/Kconfig

## Summary
Declares EROFS and its optional features.

## Main Contents
- Core `CONFIG_EROFS_FS`
- Debugging
- xattrs, POSIX ACLs, security labels
- File-backed image support
- Compression and algorithms: LZ4, LZMA, DEFLATE, Zstd
- Hardware decompression acceleration
- Deprecated fscache on-demand support
- Per-CPU decompression workers
- Experimental page-cache sharing

## Important Behavior
Core EROFS depends on block support and selects common infrastructure such as CRC32 and iomap. Feature options select algorithm libraries and cache/crypto dependencies as needed.

## Risks
Many behavior combinations are compile-time dependent, especially compression, file-backed mode, fscache mode, and inode/page-cache sharing.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/erofs/Makefile

## Summary
Builds EROFS core and optional feature objects.

## Main Contents
Core objects:
- `super.o`
- `inode.o`
- `data.o`
- `namei.o`
- `dir.o`
- `sysfs.o`

Optional objects cover xattrs, compressed data, decompressor algorithms, crypto acceleration, file-backed I/O, fscache, and page-cache sharing.

## Risks
The object list mirrors the feature matrix; missing config options directly remove decompressor or backend support.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/compress.h -->
# File Research: sources/os/linux/linux-stable/fs/erofs/compress.h

## Summary
Defines EROFS decompression request structures, decompressor vtable, temporary page markers, and shared streaming helpers.

## Main Contents
- `struct z_erofs_decompress_req`
- `struct z_erofs_decompressor`
- `struct z_erofs_stream_dctx`
- Short-lived/preallocated page markers
- Decompressor registry declarations
- Crypto decompression hooks

## Important Details
Requests carry input/output page arrays, offsets, sizes, algorithm ID, in-place flags, partial-decoding flags, and allocation flags. Streaming decompressor state tracks current input/output page positions and bounce-buffer state.

## Risks
The same request structure supports software, crypto, in-place, partial, and sparse-output decompression, so flags must be interpreted consistently by each algorithm.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/compress.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/data.c -->
# File Research: sources/os/linux/linux-stable/fs/erofs/data.c

## Summary
Implements EROFS metadata buffering, logical block mapping, device mapping, uncompressed file I/O, iomap operations, DAX mapping, and file operations.

## Main Responsibilities
- Reads metadata from block, file-backed, fscache, or metabox mappings.
- Maps flat, inline, and chunk-based inode data.
- Resolves multi-device mappings.
- Tracks online folio completion for multipart reads.
- Implements iomap read, readahead, fiemap, bmap, direct I/O, and DAX mmap.

## Key APIs
- `erofs_read_metabuf()`
- `erofs_map_blocks()`
- `erofs_map_dev()`
- `erofs_fiemap()`
- `erofs_file_fops`

## Important Behavior
Flat files map to `startblk`; inline tail data maps to metadata. Chunk-based files read chunk indexes or block arrays. File-backed metadata avoids double caching by using the backing file mapping after range verification.

## Risks
Inline data must not cross a filesystem block. Device selection depends on device IDs, flat-device mode, and unified address ranges.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/data.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/decompressor.c -->
# File Research: sources/os/linux/linux-stable/fs/erofs/decompressor.c

## Summary
Implements the core compressed-data decompressor registry plus LZ4 and plain transform modes.

## Main Responsibilities
- Loads LZ4 compression configuration.
- Prepares sparse output pages for LZ4.
- Handles overlap and in-place decompression cases.
- Fixes compressed input size by skipping zero padding.
- Implements shifted/interlaced plain transforms.
- Parses compression configuration records.
- Initializes/exits registered decompressors.

## Key APIs
- `z_erofs_fixup_insize()`
- `z_erofs_stream_switch_bufs()`
- `z_erofs_parse_cfgs()`
- `z_erofs_init_decompressor()`
- `z_erofs_exit_decompressor()`

## Important Behavior
The LZ4 path can decompress directly, vm-map multi-page inputs/outputs, use global bounce buffers, or perform true in-place decompression when page overlap and margins allow.

## Risks
In-place decompression is highly sensitive to page ordering, margins, and overlap detection. Unsupported configured algorithms fail mount with `-EOPNOTSUPP`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/decompressor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/decompressor_crypto.c -->
# File Research: sources/os/linux/linux-stable/fs/erofs/decompressor_crypto.c

## Summary
Provides optional crypto API based hardware-accelerated decompression support for EROFS.

## Main Responsibilities
- Converts decompression page arrays into scatterlists.
- Submits asynchronous crypto compression requests and waits.
- Maintains configured crypto accelerator transforms.
- Enables, disables, and lists accelerator engines.

## Key APIs
- `z_erofs_crypto_decompress()`
- `z_erofs_crypto_enable_engine()`
- `z_erofs_crypto_disable_all_engines()`
- `z_erofs_crypto_show_engines()`

## Important Behavior
The current engine table advertises `qat_deflate` for DEFLATE. Output holes are filled with short-lived pages before submitting to crypto because the scatterlist destination requires pages.

## Risks
The enable function matches by `strncmp(name, crypto_name, len)`, so caller-provided lengths matter. Accelerator failures are converted to I/O errors in decompression.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/decompressor_crypto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/decompressor_deflate.c -->
# File Research: sources/os/linux/linux-stable/fs/erofs/decompressor_deflate.c

## Summary
Implements EROFS DEFLATE decompression using pooled zlib inflate streams, with optional crypto acceleration fallback.

## Main Responsibilities
- Configures and lazily allocates a stream pool.
- Validates DEFLATE config records.
- Waits for an available stream context.
- Streams input/output pages through `z_erofs_stream_switch_bufs()`.
- Returns stream contexts to the pool.

## Key APIs
- `z_erofs_deflate_decomp`

## Important Behavior
By default, the stream count is `num_possible_cpus()`. The software path uses raw DEFLATE via `zlib_inflateInit2(..., -MAX_WBITS)`. Non-partial requests try crypto acceleration first when enabled.

## Risks
Pool exhaustion blocks waiters. The in-kernel zlib path cannot customize window bits despite validating the on-disk field.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/decompressor_deflate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/decompressor_lzma.c -->
# File Research: sources/os/linux/linux-stable/fs/erofs/decompressor_lzma.c

## Summary
Implements EROFS microLZMA decompression with a pooled set of decoder contexts.

## Main Responsibilities
- Allocates LZMA stream records at init.
- Validates LZMA config records and dictionary size.
- Resizes all stream decoder states when a larger dictionary is needed.
- Streams compressed input and decompressed output across pages.

## Key APIs
- `z_erofs_lzma_decomp`

## Important Behavior
The config path isolates all available stream records before replacing decoder states, then returns them to the global pool. Decompression waits for a stream, runs `xz_dec_microlzma_run()`, and returns the stream.

## Risks
Dictionary resizing and active stream pooling require careful locking and waitqueue coordination. Unsupported format or dictionary sizes fail configuration.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/decompressor_lzma.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/decompressor_zstd.c -->
# File Research: sources/os/linux/linux-stable/fs/erofs/decompressor_zstd.c

## Summary
Implements EROFS Zstd decompression with pooled stream workspaces.

## Main Responsibilities
- Allocates stream records.
- Validates Zstd config format and window log.
- Grows workspace allocation for larger dictionary/window sizes.
- Streams pages through the shared EROFS streaming decompressor helper.

## Key APIs
- `z_erofs_zstd_decomp`

## Important Behavior
The pool defaults to `num_possible_cpus()`. Config computes dictionary size from `windowlog + 10`, reallocates workspaces when needed, and tracks the maximum dictionary size globally.

## Risks
Workspace resizing temporarily isolates all streams and must restore pool availability correctly. Zstd stream errors are surfaced as textual reasons.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/decompressor_zstd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/erofs/dir.c

## Summary
Implements EROFS directory iteration.

## Main Responsibilities
- Reads directory data blocks from the inode mapping.
- Validates dirent name offsets and name lengths.
- Emits directory entries.
- Performs directory readahead.
- Synthesizes `.` when the on-disk dot entry is omitted.

## Key APIs
- `erofs_dir_fops`

## Important Behavior
A directory block begins with an array of `struct erofs_dirent`; `de[0].nameoff` gives the end of the dirent array and start of name data. Iteration validates this structure before emitting names.

## Risks
Directory corruption is reported as `-EFSCORRUPTED`. Correctness depends on sorted/packed dirent layout and valid name offsets.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/erofs_fs.h -->
# File Research: sources/os/linux/linux-stable/fs/erofs/erofs_fs.h

## Summary
Defines the EROFS on-disk format.

## Main Contents
- Superblock, device slot, compact inode, extended inode, xattr, chunk, dirent, compressed map, lcluster, and extent structures.
- Compatible and incompatible feature flags.
- Datalayout, inode-format, xattr, compression algorithm, and compressed-index constants.
- Compile-time layout assertions.

## Important Details
EROFS supports flat, inline, compressed full/compact, and chunk-based inode layouts. Optional features include 48-bit addressing, device tables, metabox metadata compression, fragments, dedupe, long xattr prefixes, and multiple compression algorithms.

## Risks
This header is ABI-like on-disk format definition. Any structure size or bit assignment change would affect filesystem compatibility; `erofs_check_ondisk_layout_definitions()` enforces key layout sizes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/erofs_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/fileio.c -->
# File Research: sources/os/linux/linux-stable/fs/erofs/fileio.c

## Summary
Implements file-backed EROFS read I/O, allowing filesystem images to be accessed through backing files instead of block devices.

## Main Responsibilities
- Builds read requests as bios backed by `kiocb` file reads.
- Scans folios into mapped, inline, hole, and device-backed segments.
- Copies inline data directly and zeroes holes.
- Submits merged backing-file reads.
- Completes online folio state.

## Key APIs
- `erofs_fileio_bio_alloc()`
- `erofs_fileio_submit_bio()`
- `erofs_fileio_aops`

## Important Behavior
`erofs_fileio_scan_folio()` maps each folio range through `erofs_map_blocks()`, then either copies metadata, zeroes, or appends the folio to a pending backing-file bio-like request. Direct I/O is used when the mount option and backing file allow it.

## Risks
Request lifetime uses both bio completion and explicit refcounting. Partial backing-file reads are treated as I/O errors.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/fileio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/fscache.c -->
# File Research: sources/os/linux/linux-stable/fs/erofs/fscache.c

## Summary
Implements deprecated fscache-backed on-demand EROFS access and shared-domain cookie management.

## Main Responsibilities
- Reads data from fscache cookies into folios or bios.
- Handles inline data and holes for fscache-backed files.
- Registers fscache volumes and cookies.
- Supports shared domains across EROFS instances.
- Manages anonymous inodes for cached blobs.

## Key APIs
- `erofs_fscache_access_aops`
- `erofs_fscache_register_fs()`
- `erofs_fscache_unregister_fs()`
- `erofs_fscache_register_cookie()`
- `erofs_fscache_unregister_cookie()`

## Important Behavior
Data reads map logical ranges first, then choose inline copy, zero fill, or fscache read. Domain mode uses a pseudo mount and shared cookie list so blobs can be reused across mounts.

## Risks
This feature is explicitly deprecated in Kconfig. It has complex refcounting across requests, cookies, domains, pseudo inodes, and asynchronous fscache callbacks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/fscache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/erofs/inode.c

## Summary
Loads EROFS inodes, assigns operations, handles symlinks, getattr/statx, ioctl, and inode lookup by NID.

## Main Responsibilities
- Reads compact or extended on-disk inode records.
- Decodes mode, uid/gid, nlink, size, timestamps, block/chunk/compression metadata.
- Initializes regular, directory, symlink, and special inode operations.
- Supports fast inline symlinks.
- Reports immutable/compressed statx attributes and DIO alignment.
- Implements `FS_IOC_GETFSLABEL`.

## Key APIs
- `erofs_iget()`
- `erofs_getattr()`
- `erofs_ioctl()`
- `erofs_generic_iops`

## Important Behavior
`iget5_locked()` keys the inode cache by NID while squashing inode numbers for 32-bit `ino_t`. Compressed inodes require zip support and available algorithms. DAX is enabled only for eligible flat/chunk regular files.

## Risks
On-disk inode parsing validates unsupported layouts, negative sizes, invalid chunk formats, and bogus modes. Metabox and 48-bit addressing affect inode location and inode-number presentation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/internal.h -->
# File Research: sources/os/linux/linux-stable/fs/erofs/internal.h

## Summary
Defines EROFS in-kernel private structures, flags, helpers, and cross-module interfaces.

## Main Contents
- `struct erofs_sb_info`
- `struct erofs_inode`
- Device, fscache, domain, xattr-prefix, buffer, map, and map-device structures.
- Mount option flags.
- Feature-check helper macros.
- Metadata, mapping, inode, file, fscache, fileio, compression, sysfs, shrinker, and inode-share declarations.

## Important Details
The header centralizes mode selection: compressed inodes use `z_erofs_aops`, fscache mode uses `erofs_fscache_access_aops`, file-backed mode uses `erofs_fileio_aops`, otherwise normal `erofs_aops`.

## Risks
Many compile-time feature stubs are defined here. Callers must handle `-EOPNOTSUPP` when a feature-dependent implementation is absent.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/ishare.c -->
# File Research: sources/os/linux/linux-stable/fs/erofs/ishare.c

## Summary
Implements experimental EROFS page-cache sharing among files with identical content fingerprints.

## Main Responsibilities
- Builds shared anonymous inodes keyed by xattr fingerprints.
- Links real inodes to shared inodes.
- Routes reads and mmap through backing files using shared mappings.
- Rejects direct I/O for shared files.
- Initializes and tears down the anonymous share mount.

## Key APIs
- `erofs_ishare_fill_inode()`
- `erofs_ishare_free_inode()`
- `erofs_real_inode()`
- `erofs_ishare_fops`

## Important Behavior
Fingerprint lookup uses `xxh32()` as the iget hash and full fingerprint comparison for equality. Reads clone the caller `kiocb` onto an allocated backing file whose inode and mapping point at the shared inode.

## Risks
Correctness depends on fingerprint uniqueness and matching aops/file size. The shared inode keeps a list of real inodes, and `erofs_real_inode()` grabs any live one for actual mapping context.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/ishare.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/namei.c -->
# File Research: sources/os/linux/linux-stable/fs/erofs/namei.c

## Summary
Implements EROFS directory name lookup using sorted directory blocks and binary search.

## Main Responsibilities
- Compares lookup names against on-disk names.
- Binary-searches candidate directory blocks.
- Binary-searches dirents inside the target block.
- Converts dirents to NIDs and file types.
- Provides directory inode operations.

## Key APIs
- `erofs_namei()`
- `erofs_dir_iops`

## Important Behavior
EROFS directory entries are sorted alphabetically, so lookup first binary-searches blocks by their first names, then searches within the selected block. Prefix match lengths are reused to reduce repeated comparisons.

## Risks
Lookup assumes valid sorted directory data. Corrupt blocks with no dirents or invalid name offsets produce `-EFSCORRUPTED`; overlong lookup names fail with `-ENAMETOOLONG`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/namei.c -->