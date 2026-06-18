# File Research: sources/cow-pools/bcachefs-tools/src/copy_fs.rs

Implements the Rust replacement for copying or migrating a POSIX directory tree into a bcachefs filesystem. It is used by `format --source` and `bcachefs migrate`.

Primary state:
- `MigrateType::{Copy, Migrate}` controls whether file data is copied or existing physical extents are linked.
- `CopyFsState` tracks migration parameters, extent ranges, verbosity, file/input/write/link counters, and hardlink mapping.

Metadata operations:
- Constructs `qstr` and `subvol_inum` values for bcachefs C APIs.
- Creates or updates files with `bch2_create_trans`, `bch2_dirent_lookup`, and `bch2_fsck_write_inode`.
- Replaces mismatching directory entries with recursive removal.
- Preserves uid, gid, mode, rdev, timestamps, symlinks, xattrs, sparse layout, and hardlinks.
- Skips root `lost+found`, `.` and `..`, and, during migrate, the bcachefs backing inode itself.

Data copy/migration:
- Copy mode uses `copy_sync_file_data`, SEEK_DATA/SEEK_HOLE, bcachefs reads, and mismatch detection to avoid rewriting identical aligned blocks.
- Migrate mode uses FIEMAP to link suitable physical extents with `rust_link_data`, copying extents that are unknown, encoded, not aligned, inline, or inside the reserved bcachefs superblock area.
- Tracks linked physical ranges, then creates `old_migrated_filesystem` and links holes to reserve old filesystem space.
- Symlink contents are written as bcachefs file data after punching old content.

Directory traversal:
- Reads source entries with `rustix::fs::Dir`, collects `fstatat` metadata without following symlinks, sorts by type/name, deletes destination entries not present in the source, and recurses into directories.
- Uses `fchdir` before processing child entries, matching the C conversion style but making current-directory state process-global.

Important edge cases:
- Xattrs are best-effort: listing failure is silently ignored, unsupported namespaces are skipped, and individual value read failures are skipped.
- FIEMAP unknown extents trigger an `fsync` and a second FIEMAP pass.
- Unaligned logical or physical extents are fatal in migrate mode.
- `reserve_old_fs_space` assumes device 0 and uses `nbuckets * bucket_size` for total sector coverage.

Potential concerns:
- Several operations call `CString::new(...).unwrap()`, which can panic on interior NULs from host paths/xattrs.
- `copy_data` performs a single `pread` into the requested slice and does not loop for short reads.
- `copy_sync_file_data` accumulates `i_sectors_delta` from punch operations but does not apply it to `dst.bi_sectors`, unlike other punch/write paths.
- `ranges_sort_merge` merges overlapping ranges but not immediately adjacent ranges (`end == next.start` is merged because of `>=`, so adjacency at exact boundary is merged only when `end >= start`, which includes equality).
