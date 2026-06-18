# sources/distributed-fs/ceph-client/tools/perf/util/fncache.h

## Purpose

`fncache.h` declares the filename availability cache API.

## Important APIs, Types, and Functions

It exposes `bool file_available(const char *name);` behind the `_FCACHE_H` include guard.

## Control Flow

Callers pass a path-like string and receive whether it was readable according to the cache-backed implementation.

## State and Persistence Behavior

The header has no state. The implementation maintains process-global cache state.

## Dependencies and Integration Points

The header assumes `bool` is available before inclusion or through surrounding build context, because it does not include `<stdbool.h>`. It is paired with `fncache.c`.

## Risks and Edge Cases

The missing direct `stdbool.h` include can make isolated inclusion fragile. The guard name uses `FCACHE`, not `FNCACHE`, which is harmless but inconsistent with the file name.

## Test Signals

Compile tests should include this header both after and before common perf headers to verify `bool` visibility assumptions. Runtime behavior is covered by `fncache.c` tests.
