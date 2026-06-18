# File Research: sources/block-storage/kvdo/vdo/radix-sort.c

Read completely: 392 lines.

This file implements an unstable in-place American Flag radix sort for fixed-length byte-string keys. It sorts an array of key pointers, not key contents, using an 8-bit radix and insertion sort for small piles.

`make_radix_sorter()` preallocates reusable heap state: histogram bins, pile pointers, insertion-sort task storage, and a bounded task stack sized from the maximum count. `radix_sort()` validates zero-length and small-count cases, rejects counts larger than the preallocated capacity, and then processes sorting tasks iteratively. `measure_bins()` builds a 256-bin histogram for the current byte offset, `push_bins()` sets pile boundaries and schedules follow-up tasks, and the main loop cycles keys into their piles in place. Small piles are handled with insertion sort using `memcmp()` from the active offset.

Dependencies: UDS memory allocation, `memcmp`/`memset`, compiler inline macros, `UDS_SUCCESS`, and `UDS_INVALID_ARGUMENT`.

Security/reliability notes: the sorter relies on the invariant that histogram fields are cleared as each task is consumed; error paths explicitly clear bins before returning. The public API requires all key pointers to reference at least `length` bytes. Sorting is unstable by design.
