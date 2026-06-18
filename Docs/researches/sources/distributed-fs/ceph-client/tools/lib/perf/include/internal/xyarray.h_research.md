<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/xyarray.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/xyarray.h

## Purpose
This internal header defines a compact two-dimensional array allocator used by libperf internals for fixed-size entries addressed by `(x, y)` indices, commonly useful for CPU/thread matrices such as fd or mmap tables.

## Important APIs, Types, and Functions
- `struct xyarray` records row size, entry size, total entries, max x/y bounds, and an 8-byte-aligned `contents[]` payload.
- `xyarray__new(int xlen, int ylen, size_t entry_size)` allocates zeroed storage.
- `xyarray__delete` frees it; `xyarray__reset` zeroes the payload.
- `__xyarray__entry` computes the unchecked address.
- `xyarray__entry` adds bounds checks and returns `NULL` on invalid indices.
- `xyarray__max_x` and `xyarray__max_y` expose dimensions.

## Control Flow and State
The allocator stores all entries contiguously. Addressing is `x * row_size + y * entry_size`; callers own any object semantics inside the raw memory.

## Dependencies and Integration Points
It depends on Linux compiler alignment helpers and is implemented by `xyarray.c`. It integrates with libperf internals that need rectangular, zero-initialized data without per-cell allocation overhead.

## Risks and Test Signals
There is no overflow guard for `xlen * ylen * entry_size`, so callers must pass sane sizes. `__xyarray__entry` is intentionally unchecked; public internal callers should prefer `xyarray__entry` unless they already proved bounds. Coverage is indirect through libperf tests that allocate fd/count matrices in evsel/evlist paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/xyarray.h -->
