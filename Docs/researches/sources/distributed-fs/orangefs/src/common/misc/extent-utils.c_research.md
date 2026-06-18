<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/extent-utils.c -->
# sources/distributed-fs/orangefs/src/common/misc/extent-utils.c

Purpose: helper routines for parsing and querying PVFS handle extents. These support configuration or validation code that needs to reason about handle ranges.

Important functions: `PINT_create_extent_list()` parses a handle-range string with `PINT_parse_handle_ranges()`, allocates `PVFS_handle_extent` objects, and appends them to a `PINT_llist`. `PINT_handle_in_extent()` checks inclusive first/last bounds. `PINT_handle_in_extent_array()` scans an extent array for a handle. `PINT_handle_in_extent_list()` scans a linked list of extent pointers. `PINT_extent_array_count_total()` sums the inclusive counts represented by an extent array. `PINT_release_extent_list()` frees extent objects and the list with `PINT_llist_free(..., PINT_free2)`.

Control flow is straightforward scanning and parsing. State is caller-owned list/array memory; there is no persistence. Dependencies include `str-utils` for parsing, `llist`, PVFS storage/type definitions, allocation, and assertions.

Risks: allocation failures are handled with `assert()` rather than graceful error returns in `PINT_create_extent_list()`. The parser status variable is not inspected after the loop, so invalid trailing input behavior depends entirely on `PINT_parse_handle_ranges()`. `PINT_extent_array_count_total()` can overflow `uint64_t` for very large or overlapping ranges and does not validate `last >= first`. Tests should cover null inputs, malformed ranges, max-handle extents, overlapping ranges, empty arrays, overflow boundaries, and release of partially built lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/extent-utils.c -->
