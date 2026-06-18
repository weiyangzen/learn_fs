# sources/distributed-fs/ceph/src/librados/librados_c.h

## Purpose

`librados_c.h` is a small internal compatibility header for the C ABI implementation. It defines the legacy/base pool-stat layout used by older symbol versions of `rados_ioctx_pool_stat`, allowing `librados_c.cc` to expose both the current public struct and the older base ABI.

## Important APIs, Types, and Functions

The only declared type is `__librados_base::rados_pool_stat_t`, with fields for bytes, kilobytes, object counts, clone/copy counts, degraded/missing/unfound counts, and read/write operation and kilobyte counters. It intentionally omits newer fields present in the current public `rados_pool_stat_t`, such as user bytes and compression stats.

## Control Flow and Data Flow

There is no runtime control flow. `librados_c.cc` includes this header, computes current pool stats into the modern `rados_pool_stat_t`, then copies the subset of fields into `__librados_base::rados_pool_stat_t` for the base symbol implementation.

## State and Persistence Behavior

The header defines ABI data shape only. It does not store state or mutate cluster data. Its field ordering and sizes are effectively persistent ABI contract for old clients linked against base librados symbols.

## Dependencies and Integration Points

It depends on `include/types.h` and public `include/rados/librados.h`. Its integration point is the versioned C API implementation in `librados_c.cc` and the build's symbol-version support.

## Risks and Edge Cases

Changing this struct would break old binary clients. Removing it would break the base symbol path. Adding current fields here would also be wrong because base callers allocated the old size. Tests must ensure the default symbol uses the modern struct while the base symbol copies exactly the legacy subset.

## Test Signals

Tests should verify ABI size/layout where possible, symbol-version availability, old pool-stat callers receiving correct legacy fields, and current callers receiving additional user/compression fields through the default symbol.
