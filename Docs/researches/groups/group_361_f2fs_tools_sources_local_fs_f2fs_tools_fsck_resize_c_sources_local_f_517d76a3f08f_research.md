# Group Research: group_361_f2fs_tools_sources_local_fs_f2fs_tools_fsck_resize_c_sources_local_f_517d76a3f08f

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/resize.c -->
# File Research: sources/local-fs/f2fs-tools/fsck/resize.c

Implements `resize.f2fs` metadata relocation for growing and safe shrinking F2FS volumes.

Key responsibilities:
- Computes a target superblock layout in `get_new_sb()`: `block_count`, segment counts, SIT/NAT/SSA positions, main-area start, section count, reserved segments, and overprovisioning.
- Handles checkpoint bitmap pressure through `cp_payload`, including large NAT bitmap support and checkpoint checksum offset changes.
- Migrates existing main-area valid blocks in `migrate_main()`, copying data/node blocks to the new offset and updating either data block addresses or NAT entries from summary metadata.
- Rewrites SSA through `move_ssa()` / `migrate_ssa()`, including packed SSA support via 4 KiB sub-block writes.
- Shrinks NAT only if soon-to-be-removed NAT blocks are all zero in `shrink_nats()`, then rewrites NAT set 0 and clears NAT bitmap in `migrate_nat()`.
- Rebuilds SIT from in-memory segment entries in `migrate_sit()`, remapping old segment numbers by the relocation offset.
- Rebuilds checkpoint packs in `rebuild_checkpoint()`: updates counts, current segment numbers, version bitmaps, NAT bits flags, checksum, orphan blocks, summary blocks, and disables the old checkpoint.
- Entry point `f2fs_resize()` dispatches grow vs shrink based on target block count.

Important control flow:
- Grow: flush journals, derive `new_sb`, validate capacity, optionally shrink NAT, defragment if the new main area overlaps old main data, migrate main if needed, migrate SSA/NAT/SIT, rebuild checkpoint, write both superblocks.
- Shrink: requires `c.safe_resize`, flushes journals, validates capacity, checks NAT shrink safety, defragments blocks past the new end into remaining space, writes new superblock, rebuilds checkpoint. Several full metadata migration calls are present but commented out.

Notable dependencies:
- Uses global configuration `c`, superblock helpers from `f2fs_fs.h`, fsck metadata helpers from `fsck.h`, segment summaries, NAT/SIT bitmaps, checkpoint helpers, and defragmentation.
- Uses `update_data_blkaddr()` and `update_nat_blkaddr()` to keep logical mappings consistent after physical relocation.

Behavioral notes:
- Safe shrink is intentionally constrained; non-safe shrink is rejected.
- Expanding with `safe_resize` is rejected.
- Assertions are heavy and usually abort the tool on I/O or metadata invariant failure.
- The user-facing message has a typo: `"reszie wanted"` and `"defragement"`, but behavior is unaffected.

<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/resize.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/segment.c -->
# File Research: sources/local-fs/f2fs-tools/fsck/segment.c

Provides userspace block allocation, file read/write, sload file population, extent recalculation, and host-managed zoned update support.

Key responsibilities:
- `reserve_new_block()` finds a free main-area block, updates segment validity maps, SIT/main bitmaps, valid block/node/inode counters, dirty state, and SSA summary.
- `new_data_block()` allocates a data block for a dnode and updates inode block accounting.
- `f2fs_quota_size()` reads quota inode size.
- `f2fs_read()` reads file contents through F2FS node mapping, handling partial block reads and stopping at `NULL_ADDR` / `NEW_ADDR`.
- `f2fs_write_ex()` is the common write engine behind normal writes, compressed-data writes, and address-tag writes (`COMPRESS_ADDR`, `NEW_ADDR`, `NULL_ADDR`).
- `bulkread()` retries interrupted host reads and reports EOF for compression ingestion.
- `f2fs_fix_mutable()` fills mutable compressed-cluster tail blocks with `NEW_ADDR` unless compression is readonly.
- `update_largest_extent()` scans data block addresses and writes the largest consecutive extent into the inode extent cache.
- `f2fs_build_file()` copies a host regular file into the image, with inline-data support, optional sload compression, normal block writes, extent update, and free segment refresh.
- `update_block()` handles in-place block replacement normally, but on host-managed zoned devices relocates old blocks to a new free block and updates SIT, SSA, and node/NAT references.

Important interactions:
- Used by `sload.c` to materialize host files into the F2FS image.
- Used by fsck/repair paths for allocation and zoned-device copy-on-write style updates.
- Tightly depends on node traversal (`get_dnode_of_data()`), NAT lookup, SIT segment entries, summary entries, and `f2fs_io_type_to_rw_hint()`.

Behavioral notes:
- For readonly F2FS feature images, allocation maps node and data writes into hot node/data segment choices.
- Compression write path creates a `COMPRESS_ADDR` header block, writes compressed payload, and adjusts `i_compr_blocks` / `i_blocks`.
- Many failures are handled by `ASSERT`, so callers generally do not get recoverable error handling after deep metadata corruption or I/O failure.

<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/segment.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/sload.c -->
# File Research: sources/local-fs/f2fs-tools/fsck/sload.c

Implements `sload.f2fs`, which recursively loads a host directory tree into an existing F2FS image.

Key responsibilities:
- Scans host directories with `scandir()` while filtering `.` and `..`.
- Builds `struct dentry` records with name, image path, host full path, mode, uid/gid, size, mtime, file type, symlink target, and hardlink identity.
- Creates F2FS directories, regular files, and symlinks through `f2fs_mkdir()`, `f2fs_create()`, and `f2fs_symlink()`.
- Recursively calls `build_directory()` for subdirectories and calls `f2fs_build_file()` for regular file data.
- Supports Android `fs_config` / canned fs config when available, overriding uid/gid/mode/capabilities.
- Supports SELinux labeling through `selabel_lookup()` and `inode_set_selinux()`.
- Entry point `f2fs_sload()` initializes fsck state, configures SELinux/Android file config, flushes journals, initializes hardlink cache, builds the tree, labels root, updates current segment info, flushes SIT, and writes checkpoint.

Important dependencies:
- Depends on `fsck.h` for F2FS creation helpers and global `c`.
- Depends on `segment.c` for file content writing.
- Depends on `xattr.c` for SELinux xattr installation.
- Platform-gated: Windows builds stub `build_directory()` to return failure.

Behavioral notes:
- Host metadata is read with `lstat()` to avoid following symlinks.
- If `c.fixed_time == -1` and `c.from_dir` is set, source mtimes are preserved; otherwise fixed time is used.
- The function returns `0` at the end of `build_directory()` even after some internal `ret` paths have jumped to cleanup, so some per-entry failures may be reduced to logged/partial behavior depending on where they occur.

<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/sload.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/xattr.c -->
# File Research: sources/local-fs/f2fs-tools/fsck/xattr.c

Implements minimal F2FS extended-attribute read/write support used mainly by sload SELinux labeling.

Key responsibilities:
- `read_all_xattrs()` combines inline xattrs and optional xattr node contents into one temporary buffer, initializes a missing xattr header, and can sanity-check the xattr nid during fsck.
- `__find_xattr()` iterates xattr entries, matches name index/name, and bounds-checks entries against the available xattr space.
- `write_all_xattrs()` copies inline xattr data back into the inode and writes or allocates the external xattr node if the serialized xattr area exceeds inline storage.
- `f2fs_setxattr()` validates name/value length, loads the inode, finds/removes/replaces an entry, checks free space, appends a new entry, writes all xattrs, and updates the inode.
- `inode_set_selinux()` is the exported helper that stores `security.selinux` using F2FS security xattr index.

Important constraints:
- The implementation explicitly asserts that only `F2FS_XATTR_INDEX_SECURITY` is supported in `f2fs_setxattr()`.
- `value == NULL` is rejected early, despite comments describing a remove operation, so this file currently supports set/replace semantics, not removal.
- External xattr blocks are ordinary node blocks with footer space zeroed while reading and preserved/written through node update paths.

Dependencies:
- Uses xattr layout macros from `xattr.h`.
- Uses node allocation/update helpers, NAT lookup, segment entry hints, and `update_block()` for zoned-safe updates.

<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/xattr.h -->
# File Research: sources/local-fs/f2fs-tools/fsck/xattr.h

Defines userspace F2FS xattr, fscrypt context, fsverity location, and POSIX ACL on-disk structures and helper macros.

Key contents:
- `struct f2fs_xattr_header` and `struct f2fs_xattr_entry` describe F2FS xattr storage.
- Defines fscrypt v1/v2 context structures, expected sizes, and `fscrypt_context_size()`.
- Defines `struct fsverity_descriptor_location`.
- Defines POSIX ACL structures and `f2fs_acl_count()` for validating ACL entry count from serialized size.
- Provides fallback `XATTR_*` prefix and flag definitions when system headers do not provide them.
- Defines F2FS xattr indexes for user, POSIX ACL, trusted, security, encryption, and verity namespaces.
- Provides xattr iteration/alignment macros: `XATTR_ALIGN`, `ENTRY_SIZE`, `XATTR_NEXT_ENTRY`, `XATTR_FIRST_ENTRY`, `list_for_each_xattr`.
- Defines inline/external xattr capacity helpers such as `VALID_XATTR_BLOCK_SIZE`, `XATTR_SIZE()`, `MIN_OFFSET`, `MAX_VALUE_LEN`, and `MAX_INLINE_XATTR_SIZE`.

Important dependencies:
- Includes `f2fs.h`, so it relies on inode layout helpers, `inline_xattr_size()`, block size, node footer size, and endian helpers.
- Used by `xattr.c` and fsck/sload xattr-related paths.

Behavioral notes:
- `IS_XATTR_LAST_ENTRY(entry)` treats four zero bytes as the list terminator.
- Several structures are protected with `static_assert` to maintain on-disk ABI sizes.

<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/fsck/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/include/android_config.h -->
# File Research: sources/local-fs/f2fs-tools/include/android_config.h

Provides a static configure-style capability header for Android/non-autoconf builds.

Key contents:
- For Linux, defines availability of common headers and functions: fcntl, fallocate, linux fs/ioctl/xattr/verity/fiemap headers, mount APIs, xattr APIs, uuid, clock APIs, sparse library, liblz4, libuuid, etc.
- Enables `HAVE_LIBSELINUX` only when `WITH_SLOAD` is defined.
- Enables `HAVE_LINUX_BLKZONED_H` for Bionic builds.
- For Apple, defines a smaller capability set including POSIX ACL, sys/mount, sys/xattr, fallocate, sparse, liblz4, and conditional libselinux.
- For Windows, only defines sparse support.

Role in the tree:
- Included by `f2fs_fs.h` under `WITH_ANDROID` when no generated `config.h` is present.
- Controls compile-time feature gates in mkfs, sload, xattr, device, and zoned support code.

<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/include/android_config.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/include/f2fs_fs.h -->
# File Research: sources/local-fs/f2fs-tools/include/f2fs_fs.h

Central shared userspace F2FS header: on-disk format definitions, configuration state, feature table, endian helpers, block-layout math, and public helper prototypes.

Major areas:
- Platform setup: Android config inclusion, tool feature gates (`WITH_DUMP`, `WITH_DEFRAG`, `WITH_RESIZE`, `WITH_SLOAD`, etc.), Linux type fallbacks, write-life hint fallback, SELinux include gates.
- Core integer typedefs and endian conversion macros for little-endian F2FS disk structures.
- Debug/logging/assertion macros used across tools.
- Global constants: magic, block/sector sizing, checkpoint pack count, path/device limits, version lengths, curseg types, feature bits, file flags, checkpoint flags, inode inline flags, fault injection types.
- `struct f2fs_configuration`, the global `c`, centralizes mkfs/fsck/dump/sload/resize parameters, device information, feature toggles, compression configuration, current segment offsets, cached summaries, NAT/SIT journals, fault injection state, and zoned-device settings.
- Disk format structures: `f2fs_super_block`, `f2fs_checkpoint`, orphan block footer, inode, node footer, NAT entry/block, SIT entry/block, summary/journal structures, dentry block layout, device list entries.
- Layout macros: address counts per inode/direct/indirect node, dentry slot math, summary block layout, checkpoint bitmap offsets, SIT/NAT sizing, block/segment/zone alignment.
- Helper macros `set_sb()`, `get_sb()`, `set_cp()`, `get_cp()` hide endian conversion for global `sb`/`cp`.
- Inline helpers for extra inode size, inline xattr address count, reserved/overprovision calculation, checkpoint CRC folding, quota inode checks, feature parsing, root owner parsing, inode initialization, and structure-size runtime checks.
- Zoned block-device compatibility structs and helpers for older/newer Linux zone-report formats.

Important design notes:
- Many on-disk structs deliberately use zero-length arrays and comments warning not to use `sizeof` for block-sized objects because their usable layout depends on `F2FS_BLKSIZE`.
- `static_assert` guards fixed ABI sizes such as superblock, checkpoint header, node footer, NAT entry, SIT entry, summary entry, and directory entry.
- The feature table defines user-settable mkfs feature names, including `encrypt`, `extra_attr`, `quota`, `casefold`, `compression`, `ro`, and `packed_ssa`; some internal features such as `blkzoned` and `device_alias` are not directly settable.
- `check_block_struct_sizes()` is a runtime assertion suite for configurable block sizes and packed SSA.

Notable issue:
- On little-endian builds, `be32_to_cpu(x)` is defined using `__builtin_bswap64(x)`, which is suspicious for a 32-bit big-endian conversion. Any caller expecting a 32-bit swap may get incorrect widening/truncation behavior.

<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/include/f2fs_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/include/quota.h -->
# File Research: sources/local-fs/f2fs-tools/include/quota.h

Defines quota file constants and disk structures used by `mkfs.f2fs` when creating quota inodes.

Key contents:
- Quota types: user, group, project, and `MAXQUOTAS`.
- Bit masks for enabled quota types: `QUOTA_USR_BIT`, `QUOTA_GRP_BIT`, `QUOTA_PRJ_BIT`, `QUOTA_ALL_BIT`.
- Current quota file magic values via `INITQMAGICS`.
- Quota timing defaults: one-week inode and block grace periods.
- `QT_TREEOFF` and `V2_DQINFOOFF` offsets.
- Disk structs:
  - `v2_disk_dqheader`: magic and version.
  - `v2_disk_dqinfo`: grace periods, flags, block count, free block, free entry.
  - `v2r1_disk_dqblk`: quota id, inode limits/counts, block limits/current space, timers.
- `static_assert` guards expected serialized sizes.

Usage:
- `mkfs/f2fs_format.c` uses this header to synthesize initial quota file contents for enabled user/group/project quota features.

<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/include/quota.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/mkfs/Makefile.am -->
# File Research: sources/local-fs/f2fs-tools/mkfs/Makefile.am

Automake build definition for mkfs formatting components.

Key contents:
- Sets include flags for libuuid/libblkid and the top-level `include` directory.
- Builds `sbin_PROGRAMS = mkfs.f2fs` from `f2fs_format_main.c`, `f2fs_format.c`, and `f2fs_format_utils.c`.
- Links `mkfs.f2fs` with libuuid, libblkid, and `libf2fs.la`.
- Installs `f2fs_fs.h` as an include header and keeps `f2fs_format_utils.h` as a non-installed header.
- Builds shared library `libf2fs_format.la` from the same formatter sources, with version-info variables.
- `install-exec-hook` moves `libf2fs_format.so.*` to `root_libdir` when configured and leaves a relative symlink in `libdir`.
- `uninstall-hook` removes root-libdir copies.

Build implications:
- `-DWITH_BLKDISCARD` and `_FILE_OFFSET_BITS=64` are applied to mkfs and formatter library builds.
- The formatter implementation is available both as a command and as a library surface.

<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/mkfs/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/mkfs/f2fs_format.c -->
# File Research: sources/local-fs/f2fs-tools/mkfs/f2fs_format.c

Implements the actual `mkfs.f2fs` formatting algorithm: compute layout, initialize metadata areas, create initial filesystem objects, write checkpoint packs, and write superblocks.

Key responsibilities:
- Maintains global raw superblock `raw_sb`, `sb`, and checkpoint pointer `cp`.
- Device helpers choose target device ranges, handle aliased devices, compute next/last zones, and avoid placing active segments on alias-only regions.
- Defines default cold/hot extension lists and merges user extension lists into the superblock.
- `f2fs_prepare_super_block()` is the layout core:
  - Sets magic/version/block geometry.
  - Computes segment0 alignment, device segment ranges, multi-device metadata/device boundaries, zoned alignment constraints, total segment counts, SIT/NAT/SSA sizes, checkpoint payload size, main-area start, section/main segment counts, overprovision/reserved segments, UUID, root/node/meta ino values, quota/lost+found/alias ino reservations, active segment placement, version strings, casefold settings, feature bits, and optional superblock checksum.
- `f2fs_init_sit_area()` and `f2fs_init_nat_area()` zero initial SIT and NAT sets.
- `f2fs_write_check_point_pack()` constructs the first valid checkpoint pack:
  - Initializes checkpoint counters, current segment numbers/offsets, valid node/data counts, free/user blocks, checkpoint flags, bitmap sizes, checksum.
  - Writes compact data summary with NAT/SIT journals, node summaries, second checkpoint page, optional NAT bits, and an invalid second checkpoint pack with version zero.
- `f2fs_write_super_block()` writes two superblock copies with the superblock at byte offset 1024 inside each block.
- Root construction:
  - `add_dentry()` serializes directory entries into dentry blocks.
  - `f2fs_add_default_dentry_root()` creates `.`, `..`, optional `lost+found`, and optional alias-file dentries.
  - `f2fs_write_root_inode()` initializes and writes the root inode plus root dentry data block.
- Quota construction:
  - `f2fs_write_default_quota()` synthesizes v2 quota file contents.
  - `f2fs_write_qf_inode()` creates quota inodes and points them at quota data blocks.
- Optional `lost+found` construction creates its dentry block and inode.
- Device alias support:
  - Creates pinned regular-file inodes representing aliased devices.
  - Marks corresponding SIT entries fully valid as cold data and sets inode extent to the aliased device range.
- `f2fs_create_root_dir()` orchestrates root, quota, lost+found, alias, obsolete dnode cleanup, and default NAT updates.
- `f2fs_format_device()` is the high-level formatter sequence: prepare superblock, trim, initialize SIT/NAT, create root objects, write checkpoint, write superblock.

Important dependencies:
- Uses `f2fs_fs.h` for on-disk ABI and helpers.
- Uses `quota.h` for quota file layout.
- Uses `f2fs_format_utils.h` for discard/trim.
- Uses lower-level device I/O helpers declared in `f2fs_fs.h`.

Behavioral notes:
- The formatter is very layout-sensitive; many values are rounded to segment/zone boundaries.
- Zoned mode has strict checks: metadata must fit in conventional/random zones, and trim is required by main.
- Readonly F2FS feature images use a reduced active-log model and no overprovision/reserved segments.
- Metadata journals are initialized in summary-block spare areas rather than immediately writing all NAT/SIT entries.

<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/mkfs/f2fs_format.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/mkfs/f2fs_format_main.c -->
# File Research: sources/local-fs/f2fs-tools/mkfs/f2fs_format_main.c

Implements `mkfs.f2fs` command-line parsing, defaults, overwrite checks, and top-level program flow.

Key responsibilities:
- `mkfs_usage()` prints all supported options.
- `f2fs_show_info()` reports tool version, debug level, extension list usage, label, trim status, Android defaults, and enabled major features.
- Android default handling in `add_default_options()`:
  - Enables debug level, force overwrite, 4 KiB wanted sector size, root owner `0:0`.
  - Disables NAT bits and linear lookup by default for Android.
  - Enables encryption, quota/project quota, extra attrs, verity, and write hints unless readonly mode short-circuits.
- Compile-time default feature gates can enable casefold and project-id support.
- `f2fs_parse_options()` parses options for block size, extra devices and aliases, extensions, defaults, write hints, large NAT bitmap, label, zoned mode, overprovision, feature list, fake checkpoint seed, root owner, sparse mode, sections/zones, trim, fixed timestamp, UUID, casefold encoding/flags, reserved sections, target sectors, and device path.
- Validates feature dependencies: project quota, inode checksum, flexible inline xattr, inode crtime, and compression all require `extra_attr`.
- Disables `packed_ssa` for 4 KiB blocks.
- Calls `check_block_struct_sizes()` after options are resolved.
- With blkid, detects existing filesystems or partition tables and requires `-f` before overwriting.
- `main()` initializes configuration, parses options, checks mounted/writable device state, probes device/F2FS info, enforces zoned-mode constraints, formats, finalizes, and reports success/failure.

Important dependencies:
- Uses `INIT_FEATURE_TABLE` / `parse_feature()` from `f2fs_fs.h`.
- Uses libblkid when available for overwrite protection.
- Calls `f2fs_format_device()` from `f2fs_format.c`.

Behavioral notes:
- Extra devices are parsed as `device[@alias_filename]`; alias filenames cannot contain `/`.
- Custom target sectors are rejected for multi-device format.
- Sparse mode disables trim.
- Zoned device formatting requires both zoned feature mode and trim.

<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/mkfs/f2fs_format_main.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/mkfs/f2fs_format_utils.c -->
# File Research: sources/local-fs/f2fs-tools/mkfs/f2fs_format_utils.c

Provides mkfs discard/trim helpers for regular files, block devices, and zoned devices.

Key responsibilities:
- `trim_device()` skips aliased devices, stats the target, and computes the full device byte range.
- For regular files, attempts `fallocate(FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE)` when supported.
- For block devices:
  - In zoned mode, calls `f2fs_reset_zones()`.
  - Otherwise tries secure discard (`BLKSECDISCARD`) first, then ordinary discard (`BLKDISCARD`).
- Stub `trim_device()` returns success when no supported discard API is available.
- Android-only `is_wiped_device()` checks whether the first 16 MiB of the first device is already zero and can skip trimming.
- `f2fs_trim_devices()` iterates all configured devices, trims those not already wiped, sets `c.trimmed`, and fails on trim errors.

Dependencies:
- Uses global `c`, `struct device_info`, Linux `BLKDISCARD` / `BLKSECDISCARD`, fallocate punch-hole flags, and zoned reset helpers.
- Public prototypes are declared in `f2fs_format_utils.h`.

Behavioral notes:
- Discard failures are often logged as informational and not fatal unless the device type is unsupported or the outer helper returns failure.
- Alias devices are deliberately not discarded because their contents are represented by alias inodes rather than normal free space.

<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/mkfs/f2fs_format_utils.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/f2fs-tools/mkfs/f2fs_format_utils.h -->
# File Research: sources/local-fs/f2fs-tools/mkfs/f2fs_format_utils.h

Small formatter utility header.

Contents:
- Includes `f2fs_fs.h`.
- Declares external global configuration `struct f2fs_configuration c`.
- Declares formatter utility functions:
  - `f2fs_trim_device(int, uint64_t)`
  - `f2fs_trim_devices(void)`
  - `f2fs_format_device(void)`

Notes:
- `f2fs_trim_device(int, uint64_t)` is declared here but this file group only contains `f2fs_trim_devices()` and an internal `trim_device(int)` implementation in `f2fs_format_utils.c`; the public declaration may be implemented elsewhere or be stale.
- Used by `f2fs_format_main.c` / `f2fs_format.c` to connect command-line flow with formatting and trim helpers.

<!-- END FILE RESEARCH: sources/local-fs/f2fs-tools/mkfs/f2fs_format_utils.h -->