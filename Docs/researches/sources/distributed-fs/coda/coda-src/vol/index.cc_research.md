# sources/distributed-fs/coda/coda-src/vol/index.cc

Purpose: wraps RVM-backed vnode lists as an index-like C++ abstraction for callers that expect volume/vnode index operations.

Important APIs: `vindex` stores volume id, recoverable volume index, vnode class, device, and object-size metadata. `elts()` returns active slot count, `vnodes()` returns allocated vnode count, `IsEmpty()` checks whether a class-local slot's recoverable list is empty, `get`/`oget` call `ExtractVnode`, and `put`/`oput` call `ReplaceVnode`. `vindex_iterator` iterates through all non-null vnodes in a class by traversing `rec_smolist` arrays.

Control flow/state: constructor either accepts a supplied recoverable volume index or looks one up with `HashLookup`. Iteration selects small or large vnode-list arrays, then advances list-by-list, skipping `vNull` entries and copying the class-appropriate disk-object size.

Dependencies/integration: integrates recovery routines (`ExtractVnode`, `ReplaceVnode`, `ActiveVnodes`, `AllocatedVnodes`) with volume bitmap construction, dump/backup tooling, and vnode cache initialization. Risks include unchecked constructor failure state after a failed `HashLookup`, array bounds assumptions inherited from recovery functions, and needing large-vnode buffers for directory entries. Test signals: iterate sparse small/large lists, confirm `IsEmpty` for multi-uniquifier slots, replace/delete through `put`, and build a volume bitmap from iterator output.
