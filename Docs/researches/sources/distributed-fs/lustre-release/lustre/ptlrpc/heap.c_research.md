# sources/distributed-fs/lustre-release/lustre/ptlrpc/heap.c

## Purpose
`heap.c` implements Lustre's generic binary min-heap used by PTLRPC/NRS code. It stores caller-owned `struct binheap_node` pointers, orders them through caller-provided callbacks, and uses a segmented pointer array so the heap can grow without reallocating one contiguous large table.

## Important APIs, types, and functions
- Allocation macros: `CBH_ALLOC()` chooses CPT-aware or normal allocation and honors `CBH_FLAG_ATOMIC_GROW`; `CBH_FREE()` frees one pointer fragment.
- Capacity management: `binheap_grow()` allocates single, double, and triple indirect pointer fragments in `CBH_SIZE` chunks.
- Lifecycle: `binheap_create()` allocates and preallocates capacity; `binheap_destroy()` frees all pointer fragments and the heap object.
- Access and ordering: `binheap_pointer()`, `binheap_find()`, `binheap_bubble()`, and `binheap_sink()`.
- Mutators: `binheap_insert()`, `binheap_remove()`, and `binheap_relocate()`.
- Exported symbols: create, destroy, find, insert, remove, and relocate.

## Control flow
`binheap_create()` validates that a compare callback exists, allocates the heap on the requested CPT if provided, initializes counters and private data, pre-grows to the requested count without atomic growth, then enables `CBH_FLAG_ATOMIC_GROW` for future inserts if requested. Inserts grow capacity if `cbh_nelements == cbh_hwm`, call optional `hop_enter()`, append the node at the end, increment the element count, and bubble it toward the root. Removes validate the node index, replace the removed slot with the last node unless removing the last node, relocate the replacement by bubbling or sinking, poison the removed node index, and call optional `hop_exit()`. `binheap_relocate()` is the caller-facing operation for priority changes.

## State and persistence behavior
The heap stores only in-memory pointers and per-node `chn_index` values. Capacity high-water mark grows in `CBH_SIZE` chunks and is not shrunk on removal. Node ownership remains with callers; this file only owns the pointer indirection arrays and the heap object. `CBH_POISON` marks removed nodes. There is no persistence and no internal synchronization.

## Dependencies and integration points
The implementation depends on `lustre_net.h`, `heap.h`, Lustre allocation wrappers, assertions, and optional CPT allocation APIs. The header notes NRS policies as the primary consumer, with heap instances tied to CPTs. Callers provide ordering and entry/exit hooks through `struct binheap_ops`.

## Risks
- No locking is provided; callers must serialize insert, remove, find, and priority-change operations.
- `binheap_remove()` returns early when removing the last node before poisoning the node or calling `hop_exit()`, so callers and hooks must account for that behavior.
- Capacity is never reduced, so transient large workloads keep pointer fragments until destroy.
- Compare callback semantics define heap correctness; inconsistent ordering can corrupt scheduling behavior.
- Triple-indirect growth has hard limits based on `CBH_SHIFT` and 32-bit index space.

## Test signals
Test with ordered, reverse-ordered, random, and equal-priority inserts; repeated remove-root sequences; removal of arbitrary middle and last elements; priority increases/decreases followed by relocate; forced growth through single/double/triple indirection boundaries; callback failure from `hop_enter()`; atomic allocation mode; CPT allocation; and debug assertions for stale or double-removed nodes.
