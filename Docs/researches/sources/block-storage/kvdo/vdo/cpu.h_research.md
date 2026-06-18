# File Research: sources/block-storage/kvdo/vdo/cpu.h

## Purpose
Provides cache-line sizing and prefetch helpers.

## Cache Line Selection
- PPC: 128 bytes.
- s390x: 256 bytes.
- x86_64 and aarch64: 64 bytes.
- Unknown architectures fail compilation.

## Functions
- `prefetch_address(address, for_write)`: wraps `__builtin_prefetch()` only when `for_write` is compile-time constant.
- `prefetch_range(start, size, for_write)`: prefetches all cache lines overlapping a byte range, accounting for address alignment.

## Research Notes
This header is architecture-sensitive and intentionally uses a `#define` for `CACHE_LINE_BYTES` because enum constants are not sufficient for all compile-time uses.
