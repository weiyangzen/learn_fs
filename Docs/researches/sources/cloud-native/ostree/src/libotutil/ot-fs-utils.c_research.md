# sources/cloud-native/ostree/src/libotutil/ot-fs-utils.c

## Purpose
Provides fd-relative filesystem helpers for converting paths, opening streams, tolerating missing files, mmap/read-all behavior, temporary file mapping, line parsing, and directory size calculation.

## Important APIs, Types, And Functions
Functions include `ot_fdrel_to_gfile`, `ot_readlinkat_gfile_info`, `ot_openat_read_stream`, `ot_ensure_unlinked_at`, `ot_openat_ignore_enoent`, `ot_dfd_iter_init_allow_noent`, `ot_fd_readall_or_mmap`, `ot_map_anonymous_tmpfile_from_content`, `ot_parse_file_by_line`, and `ot_get_dir_size`. `MapData` plus `map_data_destroy` owns mmap cleanup for `GBytes`.

## Control Flow
Most helpers wrap one syscall/libglnx operation and convert errors to `GError`. `ot_fd_readall_or_mmap` stats the file, returns empty bytes if the offset is beyond EOF, mmaps files larger than 16 KiB from the requested offset, or seeks and reads small files into memory. `ot_get_dir_size` recursively iterates directories, sums regular file sizes, and optionally rounds each file to a block-size multiple.

## State And Persistence Behavior
No persistent state is written except temporary anonymous files in `ot_map_anonymous_tmpfile_from_content`. Helpers operate fd-relative to reduce path races and support sysroot/repo code.

## Dependencies And Integration Points
Depends on libglnx, GIO Unix streams, mmap, xattrs include availability, and Unix fd APIs. It is used by sysroot, repo, static delta, and metadata code.

## Risks
`ot_openat_ignore_enoent` leaves `errno` meaningful to callers only indirectly and returns fd `-1` for missing files. `ot_fd_readall_or_mmap` uses `mmap` with an offset that must be page-aligned on many systems; callers passing arbitrary offsets may see `EINVAL`. Recursive size calculation does not follow symlinks but can still be expensive on large trees.

## Test Signals
Tests should cover missing file handling, symlink read info, follow/no-follow stream opens, mmap and small-read paths, offset beyond EOF, anonymous tmpfile mapping, line callback errors, directory recursion, and block rounding.
