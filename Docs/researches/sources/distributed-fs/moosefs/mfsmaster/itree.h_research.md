# sources/distributed-fs/moosefs/mfsmaster/itree.h

## Purpose
`itree.h` declares an opaque interval-tree API for mapping inclusive `uint32_t` ranges to nonzero ids. The MooseFS master uses it for topology IP-range classification.

## Important APIs
`itree_add_interval(void *o, uint32_t f, uint32_t t, uint32_t id)` returns a new root after adding or replacing a range. If `id` is `0`, the range is deleted. Reversed endpoints are accepted by the implementation.

`itree_find(void *o, uint32_t v)` returns the id for the interval containing `v`, or `0` if no interval matches. `itree_rebalance(void *o)` returns a rebalanced root and may also merge adjacent same-id intervals. `itree_freeall(void *o)` frees the whole tree.

## Control Flow And State
The root pointer is opaque and caller-owned. Every mutating call can change the root pointer, so callers must assign the return value. The API is deliberately small: no iterator, serialization, or count interface is exposed.

The id value `0` is reserved for deletion/miss semantics. Consumers must use positive/nonzero ids for meaningful mappings.

## Dependencies And Integration Points
The header includes fixed-width integer definitions and is consumed by `topology.c`. Its `void *` API avoids exposing the implementation type across files, but it also means the compiler cannot validate root pointer provenance.

## Risks
Misusing the returned root pointer is the main integration risk. A caller that ignores the return value from add or rebalance can leak nodes or continue searching stale tree state.

Because no const-qualified find signature is exposed, read-only consumers cannot express immutability through the type system.

## Test Signals
Header-level tests should verify callers update roots after add/rebalance, use id `0` only for deletion/miss, and free trees during topology reload or shutdown. Build tests should catch accidental exposure of the internal `itnode` representation.
