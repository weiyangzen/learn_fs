# File Research: sources/block-storage/kvdo/vdo/slab-summary.h

This header defines the in-memory model and API for VDO slab summaries. A slab summary stores restart/recovery hints per slab: rough free-block count, clean/dirty state, whether ref counts must be loaded, and slab-journal tail block offset.

Key structures:
- `struct slab_status`: small scrub-ordering record with slab number, cleanliness, and 7-bit emptiness hint.
- `struct slab_summary_block`: one persisted summary block, with active entry array, outgoing packed buffer, write VIO, and waiter queues for current/next writes.
- `struct slab_summary_zone`: per-physical-zone summary state, admin state, write count, zone thread id, and flexible array of summary blocks.
- `struct slab_summary`: global summary container with partition origin, hint scaling, blocks/entries sizing, active zone list, and atomic write statistics.

Public API covers construction/freeing, zone lookup, zone drain/resume, entry updates, summarized value accessors, slab status extraction, origin reset after partition movement, load, and statistics collection. The header depends on slab, layout, completion, admin-state, wait-queue, and statistics types, reflecting its role as a metadata component coordinated by physical-zone threads.
