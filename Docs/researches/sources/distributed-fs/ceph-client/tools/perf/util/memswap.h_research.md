# sources/distributed-fs/ceph-client/tools/perf/util/memswap.h

## Purpose

`memswap.h` declares fixed-width memory byte-swap helpers and a small union useful for viewing a 64-bit value as two 32-bit words.

## Important APIs, Types, and Functions

`union u64_swap` exposes `val64` and `val32[2]`. The declared functions are `mem_bswap_64()` and `mem_bswap_32()`.

## Control Flow

There is no local flow. Callers include this header and invoke the implementation on mutable buffers.

## State and Persistence Behavior

The header defines no global state. The union is a value type; swap functions mutate caller-owned memory.

## Dependencies and Integration Points

It depends on Linux integer types. It is used by perf data parsing or conversion code that handles cross-endian data.

## Risks and Edge Cases

The API accepts byte counts rather than element counts, so callers must pass correctly sized buffers. The union can expose endian-sensitive word order and should be used carefully.

## Test Signals

Compile tests should cover both function declarations and union usage. Runtime tests should validate byte-order conversion with representative perf data values.
