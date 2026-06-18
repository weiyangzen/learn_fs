# sources/distributed-fs/ceph-client/tools/perf/util/mem-info.c

## Purpose

`mem-info.c` implements refcounted ownership for `struct mem_info`, the perf object that stores resolved instruction and data addresses plus memory data-source metadata for a sample.

## Important APIs, Types, and Functions

`mem_info__new()` allocates and initializes a refcounted `mem_info`. `mem_info__get()` increments the refcount. `mem_info__put()` decrements, exits embedded instruction/data `addr_map_symbol` fields, and frees on the final put. `mem_info__clone()` allocates a new object, deep-copies address map-symbol references with `addr_map_symbol__copy()`, and copies the data-source value.

## Control Flow

Creation uses `zalloc()` and `ADD_RC_CHK()`, then sets refcount to one. Put either frees on final reference or records an rc-check put. Clone is allocate-then-copy and returns NULL on allocation failure.

## State and Persistence Behavior

The object owns references embedded in its instruction and data address records. `data_src.val` is copied by value and persists with the object. Final destruction releases map/thread references through `addr_map_symbol__exit()`.

## Dependencies and Integration Points

It depends on `mem-info.h`, `map_symbol` ownership helpers, Linux zalloc, refcounting, and rc-check infrastructure. It is used by `sample__resolve_mem()`, hist entries, perf mem, perf c2c, and script formatting.

## Risks and Edge Cases

`mem_info__clone()` assumes the source is valid and does not copy any future fields unless updated. Borrowed symbol pointers inside the copied `addr_map_symbol` remain tied to DSO lifetime. Callers must not double-put or shallow-copy without ownership awareness.

## Test Signals

Tests should cover new/get/put finalization, clone independence of map/thread references, NULL put handling, and integration with memory sample resolution and c2c stats.
