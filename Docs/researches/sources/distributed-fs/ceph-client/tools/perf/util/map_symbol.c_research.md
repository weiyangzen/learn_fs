# sources/distributed-fs/ceph-client/tools/perf/util/map_symbol.c

## Purpose

`map_symbol.c` implements small ownership helpers for bundled thread/map/symbol address-resolution results. These helpers keep reference counts correct when map-symbol records are copied or destroyed.

## Important APIs, Types, and Functions

`map_symbol__exit()` drops the contained thread and map references. `addr_map_symbol__exit()` delegates for the embedded `map_symbol`. `map_symbol__copy()` takes new references to source thread and map and copies the raw symbol pointer. `addr_map_symbol__copy()` copies the embedded map-symbol plus raw, resolved, physical, level, and page-size address fields.

## Control Flow

All functions are straight-line. Exit functions call `thread__zput()` and `map__zput()`. Copy functions use `thread__get()` and `map__get()` so the destination owns independent references to the same thread/map objects.

## State and Persistence Behavior

The functions mutate only the destination or target structures. Symbols are not refcounted here; their lifetime is expected to be tied to the referenced DSO/map. Address fields are plain value copies.

## Dependencies and Integration Points

The file depends on `map_symbol.h`, `maps.h`, `map.h`, and `thread.h`. It is used by memory info, branch info, callchain/LBR stitching, and address-location code that stores resolved IP/data addresses beyond a stack frame.

## Risks and Edge Cases

Copying into a destination that already owns references without first exiting it would leak those references. Raw symbol pointers can become stale if DSO symbols are deleted while records persist. Null thread/map inputs rely on `thread__get()`/`map__get()` tolerating null.

## Test Signals

Tests should check copy/exit refcount changes, null-safe behavior, repeated clone/free cycles through `mem_info__clone()`, and LBR stitch cleanup paths that use `map_symbol__exit()`.
