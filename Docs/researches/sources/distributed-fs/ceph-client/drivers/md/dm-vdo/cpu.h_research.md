# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/cpu.h

## Purpose

`cpu.h` provides small CPU-cache prefetch helpers for UDS/VDO code. It wraps compiler builtins so callers can request read or write prefetching for one address or a range of cache lines.

## Important APIs, Types, And Functions

- `uds_prefetch_address(address, for_write)`: calls `__builtin_prefetch` for read or write when `for_write` is compile-time constant.
- `uds_prefetch_range(start, size, for_write)`: computes the cache-line span for an address range and prefetches each line using `uds_prefetch_address`.

## Control Flow

`uds_prefetch_address` first checks `__builtin_constant_p(for_write)`. With optimization disabled or non-constant flags, it does nothing. `uds_prefetch_range` calculates an initial alignment offset, derives the number of `L1_CACHE_BYTES` lines touched by the range, then loops line by line.

## State And Persistence Behavior

The file has no persistent or logical state. Prefetching is a performance hint only and must not be required for correctness. The comments explicitly allow invalid addresses because prefetch hints should not fault in the same way as normal loads/stores.

## Dependencies And Integration Points

The header depends on Linux `cache.h` for `L1_CACHE_BYTES` and standard integer/pointer types via surrounding includes. It can be included by indexing, hashing, or data-path code that scans memory buffers.

## Risks And Edge Cases

- `for_write` must be constant for the helper to emit a builtin call.
- `uds_prefetch_range` adds one cache line after integer division, so it may prefetch one extra line beyond the exact range. That is acceptable for a hint but relevant to performance analysis.
- Very large `size` values can generate long loops; callers should use it for bounded hot ranges.

## Test Signals

Compile tests across GCC/Clang and optimized/unoptimized builds are the main signal. Microbenchmarks can compare hot-path scans with and without prefetching, but correctness tests should not depend on observable behavior.
