# sources/distributed-fs/ceph-client/tools/perf/util/map_symbol.h

## Purpose

`map_symbol.h` defines compact containers for resolved perf addresses. It pairs a thread, map, and symbol with optional address metadata used by branch, memory, and callchain code.

## Important APIs, Types, and Functions

`struct map_symbol` contains `thread`, `map`, and `sym`. `struct addr_map_symbol` embeds `map_symbol` and adds original address, resolved address (`al_addr`), address level, physical address, and data page size. The header declares exit and copy helpers for both structures.

## Control Flow

No local runtime flow exists. Callers populate these records from address-location lookups, copy them when storing longer-lived sample data, and exit them to release references.

## State and Persistence Behavior

The structs are value containers. Thread and map fields are refcount-owned according to the helper functions; symbol is a borrowed pointer. Physical address and page size persist with memory sample data when supplied by the kernel.

## Dependencies and Integration Points

It depends on Linux integer types and forward declarations for thread, maps, map, and symbol. It is integrated with `mem_info`, branch stacks, callchain cursors, hist entries, and map/symbol resolution.

## Risks and Edge Cases

Borrowed `sym` lifetime depends on map/DSO stability. Callers must not mix shallow assignment with helper-managed ownership unless they understand refcounts. `al_level` is a char and should only store expected address-location level values.

## Test Signals

Compile coverage and ownership tests through `map_symbol__copy()`/`addr_map_symbol__copy()` are the main signals. Memory and branch sample tests should confirm copied records survive after temporary address locations are exited.
