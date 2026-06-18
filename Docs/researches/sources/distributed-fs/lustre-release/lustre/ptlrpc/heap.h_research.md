# sources/distributed-fs/lustre-release/lustre/ptlrpc/heap.h

## Purpose
`heap.h` declares the public interface and data structures for Lustre's generic binary min-heap. It documents expected caller responsibilities: embed `struct binheap_node` in caller objects, provide a mandatory comparison callback, and perform external locking.

## Important APIs, types, and functions
- Constants: `CBH_SHIFT`, `CBH_SIZE`, `CBH_MASK`, `CBH_NOB`, and `CBH_POISON` define fragment sizing and removed-node poison value.
- Flags: `CBH_FLAG_ATOMIC_GROW` requests atomic allocation for capacity growth after creation.
- `struct binheap_ops`: optional `hop_enter()` and `hop_exit()` callbacks plus mandatory `hop_compare()` predicate. The predicate returns true when node `a` should sort before node `b`.
- `struct binheap`: contains triple/double/single indirect element arrays, element count, high-water mark, flags, ops, caller private data, and CPT placement fields.
- Public functions: `binheap_create()`, `binheap_destroy()`, `binheap_find()`, `binheap_insert()`, `binheap_remove()`, and `binheap_relocate()`.
- Inline helpers: `binheap_size()`, `binheap_is_empty()`, `binheap_root()`, and `binheap_remove_root()`.

## Control flow
Consumers include this header, embed `struct binheap_node` in schedulable objects, initialize the node index according to local convention, create a heap with callbacks, insert nodes, inspect index 0 with `binheap_root()`, and remove root or arbitrary nodes as scheduling decisions are made. If a node's priority changes while it is in the heap, callers invoke `binheap_relocate()` to restore ordering.

## State and persistence behavior
The header exposes the heap internals rather than making `struct binheap` opaque. The heap tracks current size in `cbh_nelements`, allocated pointer capacity in `cbh_hwm`, and each node's current position in its embedded `chn_index`. State is volatile and caller-owned except for the heap's pointer fragments.

## Dependencies and integration points
The header relies on `struct binheap_node` being declared elsewhere in Lustre headers, and on `struct cfs_cpt_table` for CPT-aware allocation. It is intended for PTLRPC/NRS users but generic enough for other kernel-internal Lustre users needing a min-heap.

## Risks
- Because internals are public, consumers can accidentally mutate heap fields and violate invariants.
- The interface does not encode locking; misuse in concurrent paths can corrupt `chn_index` and pointer arrays.
- `hop_compare()` semantics are easy to invert, producing a max-heap or unstable ordering.
- `binheap_root()` and `binheap_remove_root()` call `binheap_find(0)` and return NULL on empty heaps; callers must handle NULL.

## Test signals
Header-level validation should include compile coverage for callback signatures, users that call all inline helpers on empty and non-empty heaps, static analysis for external locking around heap mutation, and ABI/API compatibility checks for NRS policy users embedding `struct binheap_node`.
