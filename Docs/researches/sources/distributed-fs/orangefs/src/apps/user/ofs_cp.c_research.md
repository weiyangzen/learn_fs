<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/ofs_cp.c -->
# sources/distributed-fs/orangefs/src/apps/user/ofs_cp.c

## Purpose
Implements `ofs_cp`, a copy utility that works across local and OrangeFS paths while preserving selected metadata and applying OrangeFS layout, distribution, and datafile hints at destination creation.

## Important APIs, Types, And Functions
`cp_options` stores copy flags, buffer size, striping/datafile/layout hints, source/destination paths, and timing totals. `main` parses arguments, allocates a transfer buffer, chooses one-to-one or directory-copy mode, traverses sources with FTS, and delegates file copies. `copy_file` opens source/destination, builds `PVFS_hint` values (`PVFS_HINT_DFILE_COUNT_NAME`, distribution, layout, server list), streams read/write data, and preserves mode/owner/timestamps. `edit_dest_path`, `Wtime`, `print_timings`, `parse_args`, and `usage` support traversal, reporting, and command-line handling.

## Control Flow
Destination classification comes from `stat`/`pvfs_stat_mask`. Recursive directory copies use `fts_open` with symlink following on command-line roots but physical traversal. Directories are created preorder and metadata adjusted postorder. Files are copied in `buf_size` chunks; symlinks are recreated with `readlink`/`symlink`.

## State And Persistence
It creates files/directories/symlinks, truncates destination files, updates permissions, ownership, and times, and can set OrangeFS creation hints. Runtime state is the global destination buffer, a per-copy transfer buffer, and aggregate byte count.

## Dependencies And Integration Points
Depends on POSIX file APIs, FTS, `orange.h`, `pint-sysint-utils.h`, PVFS stat helpers, and OrangeFS hint-aware open support (`O_HINTS`). It integrates with OrangeFS layout and distribution xattr/creation paths indirectly through hints.

## Risks And Test Signals
Risks include hand-maintained `index` instead of `optind`, long-path truncation in `dest_path_buffer`, no cleanup of allocated `server_list`/one-to-one path strings, partial write handling without retry, symlink `readlink` result not NUL-terminated before `symlink`, and option definitions marking long options with `has_arg=0` even when arguments are required. Test signals are local-to-OFS, OFS-to-local, OFS-to-OFS, recursive, symlink, metadata-preserving, layout/list-layout, large-buffer, overwrite, and missing-destination scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/ofs_cp.c -->
