# File Research: sources/block-storage/kvdo/vdo/radix-sort.h

Read completely: 55 lines.

This header declares the reusable radix sorter API. `make_radix_sorter()` reserves heap storage for up to a maximum key count, `free_radix_sorter()` releases it, and `radix_sort()` sorts fixed-length key pointers in place without further allocation.

The header documents that heap usage is logarithmically proportional to the maximum key count and that sorting is unstable.

Dependencies: local `compiler.h` for `__must_check`.

Security/reliability notes: callers must size the sorter for the largest count they will pass and must provide valid fixed-length byte arrays for every key.
