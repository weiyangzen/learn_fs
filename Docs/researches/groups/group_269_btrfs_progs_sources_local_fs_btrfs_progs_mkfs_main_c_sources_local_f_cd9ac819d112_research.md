# Group Research: group_269_btrfs_progs_sources_local_fs_btrfs_progs_mkfs_main_c_sources_local_f_cd9ac819d112

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/mkfs/main.c -->
# File Research: sources/local-fs/btrfs-progs/mkfs/main.c

## Role

`mkfs/main.c` is the main implementation of the `mkfs.btrfs` command. It parses user options, validates feature/profile/device combinations, prepares target devices or image files, creates the initial Btrfs trees and block groups, optionally populates the new filesystem from `--rootdir`, and finalizes the filesystem by cleaning temporary chunks, initializing optional roots, discarding free space, and fixing the on-disk signature on close.

## Main Data Structures

- `struct mkfs_allocation` tracks allocated byte totals for data, metadata, mixed, system, and remap block groups so verbose output can report final allocation profiles.
- `struct prepare_device_progress` carries per-device preparation state into `pthread_create()` workers, including fd, path, requested size, discovered size, and return status.
- Global option state:
  - `opt_zero_end`: whether preparation zeros the device end.
  - `opt_discard`: whether whole-device and free-space discard are attempted.
  - `opt_zoned`: whether zoned mode is enabled.
  - `opt_oflags`: open flags shared by device-preparation threads.

## Key Control Flow

`BOX_MAIN(mkfs)` is the command entry point.

1. Initializes CPU/hash/config feature machinery.
2. Parses options for profiles, features, label, UUIDs, node/sector sizes, `--rootdir`, subvolumes, inode flags, compression, reflink, shrink, discard, verbosity, and experimental parameters.
3. Applies defaults:
   - sectorsize defaults to 4 KiB.
   - nodesize defaults to max(sectorsize, default node size).
   - profile defaults depend on single-device vs multi-device and mixed-bg mode.
4. Validates option combinations:
   - `--rootdir` is single-device only.
   - `--shrink`, `--reflink`, `--subvol`, `--inode-flags`, and `--compress` require `--rootdir`.
   - zoned mode rejects `--rootdir`, mixed-bg, and RAID5/6.
   - remap-tree rejects mixed-bg and zoned mode.
   - extent-tree-v2/remap-tree force no-holes, free-space-tree, and block-group-tree dependencies.
5. Canonicalizes `source_dir` and validates requested rootdir subvolumes and inode-flag paths through `rootdir.c`.
6. Checks device overwrite safety, UUID validity, minimum size, RAID profile feasibility, and zoned profile support.
7. Prepares devices in parallel with `prepare_one_device()`.
8. Calls `make_btrfs()` to create the initial on-disk filesystem.
9. Opens the filesystem with write/temporary-super/exclusive flags.
10. Creates metadata/system/default data chunks, optional RAID stripe/remap/global roots, and the initial root directory.
11. Adds additional devices, creates final RAID-profile block groups, commits, and re-COWs existing trees into the final profiles.
12. Creates the data relocation tree unless remap-tree is enabled.
13. If `--rootdir` is set, calls `btrfs_mkfs_fill_dir()` to populate the filesystem, then optionally calls `btrfs_mkfs_shrink_fs()`.
14. Rebuilds the UUID tree, removes temporary chunks, initializes quota roots if requested, prints verbose summary, discards free space, sets `finalize_on_close`, and closes the ctree.

## Important Functions

- `create_metadata_block_groups()` allocates initial system, metadata/mixed, and optional remap block groups. It handles zoned system group sizing and records allocation totals.
- `create_data_block_groups()` creates the initial data block group unless mixed block groups are enabled.
- `make_root_dir()` creates the root-tree directory object, the fs-tree root directory, and the root-tree `"default"` dir item/ref.
- `__recow_root()`, `recow_global_roots()`, and `recow_roots()` walk tree leaves and force COW of tree blocks so metadata moves from temporary chunks into final-profile chunks.
- `create_one_raid_group()` and `create_raid_groups()` allocate profile-specific system, metadata/mixed, and data block groups.
- `zero_output_file()` initializes a regular output image by zeroing the first MiB and extending it to the target size.
- `list_all_devices()` prints a sorted device table, including zone counts in zoned mode.
- `is_temp_block_group()`, `next_block_group()`, and `cleanup_temp_chunks()` identify and remove empty temporary single-profile chunks after final chunks exist.
- `discard_logical_range()`, `queue_discard_logical()`, `discard_all_devices()`, and `discard_free_space()` translate logical free-space ranges to device ranges and submit discard, skipping RAID56 mappings.
- `update_chunk_allocation()` recomputes allocation totals from block-group cache after rootdir population may have allocated extra chunks.
- `create_global_root()` and `create_global_roots()` create extra extent/csum/free-space roots for extent-tree-v2 global roots.
- `setup_quota_root()` creates and initializes qgroup/simple-quota metadata, then runs qgroup verification and repair to fill accounting.
- `setup_raid_stripe_tree_root()` and `setup_remap_tree_root()` create optional feature roots and wire them into fs_info/super fields.
- `prepare_one_device()` is the thread callback that opens and prepares each target using `btrfs_prepare_device()`.
- `parse_compression()` recognizes `no`, `zlib[:level]`, `lzo[:level]`, and `zstd[:level]`, subject to compile-time support and level limits.
- `parse_subvolume()` parses `--subvol` entries into `rootdir_subvol` records, including default and read-only modes.
- `parse_inode_flags()` parses comma-separated `nodatacow` and `nodatasum` flags for a `FLAGS:PATH` option.

## Dependencies and Interactions

This file is tightly integrated with Btrfs shared code:

- Tree and transaction operations from `kernel-shared/ctree.h`, `disk-io.h`, `transaction.h`, `volumes.h`, and `zoned.h`.
- Feature parsing and validation from `common/fsfeatures.h`.
- Device probing/preparation from `common/device-utils.h` and `common/device-scan.h`.
- Rootdir population and sizing from `mkfs/rootdir.h`.
- Quota verification from `check/qgroup-verify.h`.
- Profile parsing, minimum size logic, and low-level mkfs creation from `mkfs/common.h`.

`main.c` delegates the content-copying complexity to `rootdir.c`; its responsibility is to ensure the target filesystem is sized, created, and opened correctly before rootdir import.

## Notable Invariants

- `--rootdir` only supports one target device and is rejected with zoned mode.
- Mixed block groups require matching data and metadata profiles.
- Remap-tree requires no-holes/free-space-tree/block-group-tree and cannot be combined with mixed-bg or zoned mode.
- Extent-tree-v2 requires at least one global root and forces dependent features.
- Finalization is delayed until the filesystem is fully built; `finalize_on_close` is set only at the end.
- Temporary block groups are removed only if empty and if their profile does not match the final mkfs profile.
- RAID56 free-space discard is skipped because mapping/discard semantics are unsafe for this path.

## Error Handling

The file consistently reports negative errno-style errors through `error()`/`error_msg()`, aborts transactions on setup failures where needed, and converts final command status to boolean shell exit status. Some fatal validation paths call `exit(1)` directly. Transaction commit failures are reported with the shared transaction error message macro.

## Research Notes

This is the orchestration layer for mkfs. Most Btrfs metadata details are in shared helpers, but `main.c` defines the exact command behavior, feature compatibility matrix, initial tree/chunk construction sequence, temporary-to-final profile migration, rootdir integration point, and final cleanup sequence.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/mkfs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/mkfs/rootdir.c -->
# File Research: sources/local-fs/btrfs-progs/mkfs/rootdir.c

## Role

`mkfs/rootdir.c` implements `mkfs.btrfs --rootdir`. It walks a host directory tree and materializes it into the newly created Btrfs filesystem, preserving metadata such as modes, ownership, timestamps, xattrs, symlinks, hardlinks, sparse holes, special-file types, selected inode flags, and requested subvolume boundaries. It also estimates image size for rootdir creation and can shrink a populated single-device image down to the last used device extent.

## Traversal State

The file uses process-global state for one rootdir import:

- `current_path`: stack of current Btrfs directory inodes during `nftw()` preorder traversal.
- `g_trans`: active transaction used by callbacks.
- `g_subvols`: remaining requested subvolume definitions.
- `g_inode_flags_list`: remaining requested inode-flag overrides.
- `next_subvol_id`: object id allocator for requested subvolumes.
- `default_subvol_id`: selected default subvolume id.
- `g_compression` and `g_compression_level`: rootdir compression mode.
- `g_do_reflink`: whether file data should be cloned with `FICLONERANGE`.
- `hardlink_root`: rb-tree keyed by `(st_dev, st_ino, btrfs_root)` for hardlink reconstruction without crossing subvolume boundaries.
- checksum ioctl cache:
  - `g_get_csums_supported`
  - `g_last_csums_dev`
  - `g_last_csums_dev_ok`

## Key Data Structures

- `struct inode_entry` stores a Btrfs root pointer and inode number for the current path stack.
- `struct hardlink_entry` maps host inode identity to the first Btrfs inode created for that file inside the same subvolume root.
- `struct rootdir_path` tracks traversal depth and directory stack.
- `struct source_descriptor` carries file fd, buffers, size, path, optional compression work buffers, and source device id into extent-writing helpers.

## Validation API

- `btrfs_mkfs_validate_subvols()` canonicalizes each requested subvolume path, verifies it exists and is a directory, stores its host `(st_dev, st_ino)`, and rejects duplicate subvolume specifications.
- `btrfs_mkfs_validate_inode_flags()` canonicalizes each flagged path, verifies it exists, stores `(st_dev, st_ino)`, and rejects duplicate flag records for the same inode.

These validation passes run before filesystem creation is committed to rootdir population.

## Metadata Import

- `stat_to_inode_item()` converts host `struct stat` into a Btrfs inode item, copying uid/gid/mode and atime/ctime/mtime seconds.
- `add_xattr_item()` copies xattrs with `llistxattr()` and `lgetxattr()` into Btrfs xattr items, ignoring unsupported-xattr filesystems.
- `add_symbolic_link()` reads the symlink target and stores it as an inline extent.
- `ftype_to_btrfs_type()` maps POSIX file modes to Btrfs dir item types.
- `update_inode_flags()` applies requested `nodatacow` and `nodatasum`; `nodatacow` implies `nodatasum` for regular files.
- `search_and_update_inode_flags()` applies and removes the matching inode-flag record by host inode identity.

## File Data Import

Regular file content flows through `add_file_items()` and `add_file_item_extent()`.

Supported behavior:

- Empty files need no extents.
- Small files below inline limits are inserted as inline extents, optionally compressed if that reduces size.
- Larger files are split into at most 1 MiB extents (`MAX_EXTENT_SIZE`) to fit mkfs-time small block groups.
- Sparse holes are detected with `SEEK_DATA`/`SEEK_HOLE` and represented as Btrfs hole extents when aligned.
- Data checksums are inserted unless inode flags disable data checksumming.
- Optional compression supports zlib, LZO, and ZSTD when compiled in.
- Optional reflink writes use `FICLONERANGE` from the source fd into the destination device range after logical-to-physical mapping.
- If the source is Btrfs and checksum settings match, the code tries `BTRFS_IOC_GET_CSUMS` to import existing checksums instead of recomputing them.

Important helpers:

- `insert_reserved_file_extent()` inserts extent-tree records, removes allocated space from the free-space tree, inserts the file extent, updates inode nbytes, and increments extent refs. It handles disk bytenr 0 as a hole extent.
- `read_from_source()` performs aligned pread loops into the staging buffer.
- `try_compressed_write()` compresses a range, writes compressed bytes, creates csums for compressed sectors, sets inode compression flags, and inserts a compressed file extent.
- `do_reflink_write()` maps Btrfs logical destination ranges to physical device ranges and clones source ranges into those offsets.
- zlib/LZO/ZSTD helpers implement both regular compressed extents and inline compressed extents.

## Directory, Subvolume, and Hardlink Import

`ftw_add_inode()` is the main `nftw()` callback.

- The rootdir itself updates the existing fs-tree root inode and initializes `current_path`.
- Before processing each entry, the path stack is popped until it matches the traversal depth.
- If a directory matches a requested subvolume `(st_dev, st_ino)`, `ftw_add_subvol()` creates a Btrfs subvolume, links it under the current parent, updates its root inode metadata/xattrs, marks it default if requested, and pushes it onto the path stack.
- For non-directory hardlinked files, the rb-tree allows later links to reuse the first Btrfs inode in the same root. Cross-subvolume hardlinks are intentionally not recreated as hardlinks.
- New inodes are allocated with `btrfs_find_free_objectid()`, inserted, linked into the parent directory, decorated with xattrs, and then populated according to type.
- Directories are pushed onto the traversal stack after insertion.
- Regular files call `add_file_items()` and then rewrite the inode item with updated nbytes/flags.
- Symlinks call `add_symbolic_link()` and then update the inode item.

`set_default_subvolume()` updates the root-tree `"default"` dir item to point at the requested default subvolume and sets the default-subvol incompat feature bit.

`btrfs_mkfs_fill_dir()` is the public import entry point. It validates compression availability/default levels, initializes global traversal state, runs `nftw(source_dir, ftw_add_inode, 32, FTW_PHYS)`, drains the path stack, sets the default subvolume if requested, and frees remaining hardlink records.

## Size Estimation

`btrfs_mkfs_size_dir()` estimates the minimum target size for `--rootdir`.

- It walks the source with `nftw(..., FTW_PHYS)`.
- `ftw_add_entry_size()` counts every inode and sums regular-file data.
- `add_data_size()` prefers allocated blocks for sparse files when `SEEK_DATA` works; otherwise it falls back to rounded file size.
- Metadata estimate is `inode_count * (PATH_MAX * 3 + sectorsize) + data_size / 8`.
- Data and metadata chunk estimates account for minimal chunk thresholds and DUP multipliers.
- Returned size is `min_dev_size + estimated_data_extra + estimated_metadata_extra`.

The estimate intentionally over-allocates so population is less likely to hit ENOSPC; `--shrink` can reduce image size afterward.

## Shrink Support

- `get_device_extent_end()` finds the exclusive end of the last device extent for a devid.
- `set_device_size()` updates in-memory device size, chunk-tree device item size, super total bytes, and commits the change.
- `btrfs_mkfs_shrink_fs()` only supports single-device filesystems. It computes the last used device extent, verifies sectorsize alignment, updates device/super sizes, and truncates the backing file if it is a regular file and `shrink_file_size` is true.

## Error Handling and Edge Cases

- `FTW_DNR` and `FTW_NS` during sizing abort early with `-EPERM`.
- xattr unsupported cases are nonfatal.
- Compression failure due to poor ratio returns `-E2BIG` and falls back to uncompressed data; first-block compression failure can mark the inode `NOCOMPRESS`.
- Reflink and checksum import require block-aligned ranges; partial tail blocks fall back to normal read/write/checksum behavior.
- `BTRFS_IOC_GET_CSUMS` support is cached; `ENOTTY` disables future attempts.
- Hardlink records are removed once all host-reported links are found, but links outside rootdir mean records may remain until final rb-tree cleanup.
- The traversal deliberately uses `FTW_PHYS`, so symlinks are copied as symlinks rather than followed.

## Research Notes

This file is the rootdir materialization engine. It bridges host filesystem metadata and Btrfs on-disk item construction, with special care for subvolume boundaries, sparse file layout, compression compatibility, checksumming, and post-population image minimization.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/mkfs/rootdir.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-progs/mkfs/rootdir.h -->
# File Research: sources/local-fs/btrfs-progs/mkfs/rootdir.h

## Role

`mkfs/rootdir.h` is the public interface between the main mkfs command and the `--rootdir` implementation in `rootdir.c`. It declares the option data structures used by `main.c` and the functions used to validate, size, populate, and shrink a rootdir-created filesystem.

## Public Constants

- `ZLIB_BTRFS_DEFAULT_LEVEL` is `3`.
- `ZLIB_BTRFS_MAX_LEVEL` is `9`.
- `ZSTD_BTRFS_DEFAULT_LEVEL` is `3`.
- `ZSTD_BTRFS_MAX_LEVEL` is `15`.

These are used by both option parsing and rootdir compression setup.

## Public Types

`struct rootdir_subvol` represents one `--subvol` request.

Fields:

- `list`: intrusive list node.
- `dir[PATH_MAX]`: path inside the source directory.
- `st_dev`, `st_ino`: host inode identity filled during validation.
- `is_default`: whether this subvolume becomes the default subvolume.
- `readonly`: whether the created subvolume is read-only.

`struct rootdir_inode_flags_entry` represents one `--inode-flags` request.

Fields:

- `list`: intrusive list node.
- `inode_path[PATH_MAX]`: path inside the source directory.
- `st_dev`, `st_ino`: host inode identity filled during validation.
- `nodatacow`: request `BTRFS_INODE_NODATACOW`.
- `nodatasum`: request `BTRFS_INODE_NODATASUM`.

Both structures store host inode identity because later traversal matches by `(st_dev, st_ino)`, not by raw path string.

## Public Functions

- `btrfs_mkfs_validate_subvols(source_dir, subvols)` validates requested subvolume paths, ensures they are existing directories, records host inode identities, and rejects duplicates.
- `btrfs_mkfs_validate_inode_flags(source_dir, inode_flags)` validates requested inode-flag paths, records host inode identities, and rejects duplicates.
- `btrfs_mkfs_fill_dir(trans, source_dir, root, subvols, inode_flags_list, compression, compression_level, do_reflink)` populates the new filesystem from the host directory tree.
- `btrfs_mkfs_size_dir(dir_name, sectorsize, min_dev_size, meta_profile, data_profile)` estimates the target size needed before rootdir import.
- `btrfs_mkfs_shrink_fs(fs_info, new_size_ret, shrink_file_size)` shrinks a populated single-device filesystem/image to the last used device extent.

## Dependencies

The header exposes only forward declarations for `struct btrfs_fs_info` and `struct btrfs_root`, includes list support, and depends on Btrfs compression enum definitions from `kernel-shared/compression.h`.

## Research Notes

This header is intentionally narrow. It gives `main.c` enough structure to collect command-line rootdir requests, validate them before formatting, and then hand all import details to `rootdir.c`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-progs/mkfs/rootdir.h -->