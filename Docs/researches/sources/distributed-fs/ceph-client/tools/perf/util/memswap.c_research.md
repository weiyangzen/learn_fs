# sources/distributed-fs/ceph-client/tools/perf/util/memswap.c

## Purpose

`memswap.c` provides in-place byte-swap helpers for 32-bit and 64-bit words. It supports perf data handling where endianness conversion is needed for arrays of fixed-width values.

## Important APIs, Types, and Functions

`mem_bswap_32(void *src, int byte_size)` treats the buffer as `u32` words and applies `bswap_32()` while decrementing by four bytes. `mem_bswap_64(void *src, int byte_size)` does the same for `u64` words with `bswap_64()`.

## Control Flow

Both functions are simple loops: cast the pointer, swap the current word, decrement `byte_size` by the word width, and advance to the next word until `byte_size <= 0`.

## State and Persistence Behavior

The functions mutate the caller-provided memory in place and allocate no state. Converted bytes persist in the supplied buffer.

## Dependencies and Integration Points

The file depends on `<byteswap.h>`, Linux integer types, and `memswap.h`. It integrates with perf file/event readers that need endian conversion of numeric arrays.

## Risks and Edge Cases

The functions assume `byte_size` is a multiple of the word size and that `src` is suitably aligned for `u32` or `u64` access on the target architecture. Negative or non-multiple sizes are not validated; a non-multiple positive size still swaps a full final word. Callers are responsible for choosing the correct width.

## Test Signals

Tests should cover known 32-bit and 64-bit patterns, zero sizes, multiple elements, non-host-endian perf data fixtures, and sanitizer/alignment checks on strict-alignment architectures.
