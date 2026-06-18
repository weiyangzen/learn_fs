# File Research: sources/block-storage/kvdo/vdo/slab-depot.h

Defines `struct slab_depot` and its public management API.

Concept:
- A slab depot owns every slab and every per-physical-zone block allocator for a VDO.
- It keeps one slab pointer array to simplify PBN-to-slab mapping.
- Operations have thread constraints: load/save from load thread, allocation/refcount updates on physical-zone threads, recovery-journal tail commits on the journal-zone thread.

Important fields:
- Zone counts, VDO pointer, `slab_config`, slab summary, action manager.
- First/last/origin block and `slab_size_shift`.
- Load type and recovery-journal lock release request state.
- Scrubbing zone counter.
- Current slabs plus prepared resize slabs.
- Per-zone `block_allocator *allocators[]`.

Public API covers:
- Decode/free/record persisted state.
- Allocate refcounts.
- Zone allocator and PBN/slab/journal lookup.
- Data-block validity and increment limit queries.
- Capacity/statistics.
- Load, prepare-to-allocate, drain, resume.
- Resize prepare/use/abandon.
- Slab journal tail-block commit requests.
- Slab summary access.
- Scrubbing and diagnostics.
