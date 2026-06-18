# sources/distributed-fs/orangefs/src/common/misc/str-utils.c

## Purpose

`str-utils.c` implements shared string and path helpers for OrangeFS. It covers path merging and normalization, path segment iteration, base-name and prefix handling, comma-list tokenization, handle-range parsing and merging, fallback libc functions for platforms missing `strnlen` or `strstr`, and key/value string splitting.

## Important APIs and functions

- `PINT_merged_path_len()` computes the required length for joining two paths with one slash and a terminator.
- `PINT_merge_paths()` joins an absolute base path, slash, and relative component into a caller-supplied `PVFS_PATH_MAX + 1` buffer.
- `PINT_is_dot_dir()` detects `"."` and `".."`.
- `PINT_string_rm_extra_slashes()` and `PINT_string_rm_extra_slashes_rts()` collapse repeated slashes in place, optionally removing a trailing slash.
- `PINT_string_count_segments()` counts non-empty path segments using `PINT_string_next_segment()`.
- `PINT_get_base_dir()` returns the parent directory of an absolute path.
- `PINT_string_next_segment()` iterates path segments by temporarily replacing separators with NUL bytes and restoring them on the next call.
- `PINT_parse_handle_ranges()` parses textual handle extents such as `1-10,20-30` into `PVFS_handle_extent` values across repeated calls using an integer status offset.
- `PINT_get_path_element()` copies the Nth path segment into an output buffer.
- `PINT_get_next_path()` allocates a copy of the remainder of a path after a requested number of slash separators.
- `PINT_split_string_list()` splits comma-delimited strings into an allocated token array, and `PINT_free_string_list()` frees it.
- `PINT_remove_base_dir()` copies the last component from an absolute path.
- `PINT_remove_dir_prefix()` validates a qualified/expanded PVFS path, checks an absolute prefix, updates the path object's mount-point flags, and points `pvfs_path` at the suffix inside the input pathname.
- `PINT_merge_handle_range_strs()` allocates `"range1,range2"`.
- Fallback `strnlen()` and `strstr()` are compiled only when platform probes say they are missing.
- `PINT_split_keyvals()` parses comma-separated `key:value` pairs into separate allocated key and value arrays.

## Control flow

Path normalization functions are mostly in-place linear scans. Segment iteration stores state outside the function through `inout_segp` and `opaquep`: the first call starts at `pathname`, later calls restore the slash previously replaced by NUL, skip separators, return the next segment start, and either save the next separator or mark end-of-string with `NULL`.

Handle-range parsing uses the caller's `status` offset as an opaque cursor. Each call parses the next unsigned integer as both first and last, optionally parses a range end after `-`, consumes whitespace and an optional comma, updates `status`, and returns 1 for a found extent, 0 for no more ranges, or -1 for invalid arguments/format.

List and key/value splitters first count expected elements, allocate pointer arrays, then allocate/copy individual strings. `PINT_remove_dir_prefix()` is unusual because it calls `PVFS_path_from_expanded()`, checks path magic and flags, then mutates fields on the returned path object rather than returning the suffix directly.

## State and persistence behavior

These helpers do not persist data. They either mutate caller-owned strings in place, write into caller-provided buffers, or allocate caller-owned arrays/strings. `PINT_string_next_segment()` temporarily mutates the pathname while iteration is active and restores the last slash on the next call. `PINT_remove_dir_prefix()` mutates state inside a `PVFS_path_t` associated with the input path conversion.

## Dependencies and integration points

The file depends on PVFS limits and error codes, `PVFS_handle_extent`, and `pvfs-path.h`. It is used by server config parsing for comma lists, handle ranges, and merged range strings, and by broader path resolution code that needs slash normalization, segment extraction, prefix removal, and key/value option parsing.

## Risks and edge cases

- `PINT_merged_path_len()` returns `short`, which can truncate for long input even though PVFS paths can be much larger than `SHRT_MAX` in principle.
- `PINT_merge_paths()` uses `strcat()` after checking combined length, so the destination must truly be at least `PVFS_PATH_MAX + 1`.
- `PINT_string_count_segments()` mutates and restores the input through `PINT_string_next_segment()`; callers may not expect a counting function to write to its argument.
- `PINT_get_path_element()` copies into `local_pathname[PVFS_NAME_MAX]`, not `PVFS_PATH_MAX`, so long paths are truncated before segment extraction.
- `PINT_split_string_list()` returns early on empty tokens without freeing already allocated token memory and can leave partially initialized arrays.
- `PINT_remove_dir_prefix()` returns error without releasing any object returned by `PVFS_path_from_expanded()` if that API allocates; ownership depends on pvfs-path internals.
- `PINT_split_keyvals()` uses `if (*ptr != ',' || *ptr != '\0')`, which is always true for any single character. The counting loop still advances by commas, but the condition is logically suspect and should be regression-tested.
- Several functions assume non-null output pointer parameters after top-level checks; misuse can crash.

## Test signals

Tests should cover root paths, repeated and trailing slashes, relative path rejection, output-buffer-too-small paths, segment iteration restoration, long path truncation behavior, handle ranges with whitespace, singletons, invalid delimiters, empty comma elements, merged range allocation, prefix boundary cases such as `/mnt/pvfs2fake`, key/value lists with missing colon or extra colon, and fallback builds without libc `strnlen` or `strstr`.
