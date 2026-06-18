# sources/distributed-fs/ceph-client/tools/perf/util/maps.h

## Purpose

`maps.h` declares the map-collection interface and kernel-map metadata used by perf machines and threads.

## Important APIs, Types, and Functions

`struct kmap` stores an optional relocation reference symbol, owning `maps`, and a fixed-size name for extra kernel maps. Public functions cover lifecycle, emptiness/equality, copying, iteration, removal by callback, parent machine access, refcount access for tests, libunwind/libdw accessors, printing, insert/remove, address and symbol lookup, `addr_map_symbol` lookup, overlap insertion, lookup by DSO name, next-entry lookup, merging, end fixup, and first-map loading.

## Control Flow

There is no implementation flow in the header. It defines the operations that callers use to mutate maps under implementation-managed locking and lookup symbols from address collections.

## State and Persistence Behavior

`struct maps` is opaque, so state is owned by `maps.c`. `struct kmap` is embedded behind kernel maps and persists with the map. Refcounting is exposed through `maps__get()`, `maps__put()`, and `maps__zput()`.

## Dependencies and Integration Points

The header depends on Linux refcount/types and perf machine/map declarations. It is used by `machine.c`, `map.c`, thread map handling, unwind code, and symbol resolution code.

## Risks and Edge Cases

Because `struct maps` is opaque, callers must not assume storage shape and must use accessors. `maps__nr_maps()` and `maps__refcnt()` are marked test-only. Kernel map names are capped by `KMAP_NAME_LEN`, so copying must use bounded string helpers.

## Test Signals

Header-level tests are compile and ABI-style tests through all map users. Functional tests should verify every declared operation is implemented and keeps refcount and locking behavior consistent.
