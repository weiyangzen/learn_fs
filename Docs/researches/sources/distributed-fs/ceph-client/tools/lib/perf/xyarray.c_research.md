<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/xyarray.c -->
# sources/distributed-fs/ceph-client/tools/lib/perf/xyarray.c

## Purpose
This file implements the internal `xyarray` rectangular storage helper.

## Important APIs, Types, and Functions
- `xyarray__new(int xlen, int ylen, size_t entry_size)` calculates row size, allocates zeroed storage with `zalloc`, and stores dimensions and entry counts.
- `xyarray__reset(struct xyarray *xy)` zeroes the payload contents.
- `xyarray__delete(struct xyarray *xy)` frees the allocation.

## Control Flow and State
Allocation is a single block containing metadata plus `xlen * ylen * entry_size` bytes. Reset operates only on the payload, preserving dimensions. The header inline accessors compute individual entry addresses.

## Dependencies and Integration Points
It depends on `internal/xyarray.h`, Linux `zalloc`, libc allocation, and string functions. Libperf internals use it where a two-dimensional CPU/thread index space needs compact storage.

## Risks and Test Signals
The allocation math has no explicit overflow checking and uses signed integer dimensions converted into `size_t`. Negative or very large dimensions would be unsafe if not filtered by callers. There is no direct unit test in this subset; coverage is indirect through evsel/evlist internals that allocate matrices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/xyarray.c -->
