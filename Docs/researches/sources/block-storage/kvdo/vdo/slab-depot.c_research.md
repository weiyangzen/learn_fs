# File Research: sources/block-storage/kvdo/vdo/slab-depot.c

Implements the slab depot runtime: the top-level manager for all slabs, per-zone block allocators, slab summary, resize state, load/drain orchestration, scrub scheduling, and aggregated statistics.

Construction/allocation:
- `vdo_decode_slab_depot()` validates slab size is a power of two, allocates the depot with per-zone allocator slots, records persisted state, and calls `allocate_components()`.
- `allocate_components()` creates the action manager, slab summary, per-zone block allocators, and all slab objects.
- `allocate_slabs()` allocates or extends a slab pointer array, creates slabs assigned round-robin to physical zones, and preserves existing slabs during resize preparation.
- `vdo_allocate_slab_ref_counts()` walks slabs in reverse order through `slab_iterator` and allocates each slab’s refcounts.

Lookup/query API:
- `vdo_get_slab_number()` maps PBN to slab number using the depot’s `slab_size_shift`.
- `vdo_get_slab()` returns the owning slab, entering read-only mode on invalid non-zero PBNs.
- `vdo_get_slab_journal()` returns the owning slab journal.
- `vdo_get_increment_limit()` delegates to the slab’s refcounts unless the slab is unrecovered.
- `vdo_is_physical_data_block()` validates that a PBN is the zero block or maps into the data portion of a slab.
- `vdo_get_slab_depot_allocated_blocks()` sums allocator-owned allocated counts.
- `vdo_get_slab_depot_data_blocks()` returns slab count times data blocks per slab.

Action manager orchestration:
- The depot action manager fans operations out to block allocators on physical-zone threads.
- `vdo_load_slab_depot()` loads slab summary first, then block allocators.
- `vdo_prepare_slab_depot_to_allocate()` sets load type, initializes scrub-zone accounting, and prepares allocators.
- `vdo_drain_slab_depot()` drains allocator/slab metadata for save/flush/rebuild/suspend.
- `vdo_resume_slab_depot()` resumes allocators unless read-only.
- `vdo_commit_oldest_slab_journal_tail_blocks()` records a recovery-journal block release request and schedules the default action; the action eventually runs `vdo_release_tail_block_locks()` across zones.

Resize:
- `vdo_prepare_to_grow_slab_depot()` validates growth, computes new slab count, abandons stale prepared slabs, allocates new slabs, and records old/new sizes.
- `vdo_use_new_slabs()` schedules allocator registration for prepared slabs and finalizes the active slab array.
- `vdo_abandon_new_slabs()` frees prepared-but-unused resize slabs.

Scrubbing/recovery:
- `vdo_scrub_all_unrecovered_slabs()` schedules zone scrub actions.
- `vdo_notify_zone_finished_scrubbing()` decrements zone scrub count and, when last, transitions VDO from recovering to dirty if appropriate.

Statistics/diagnostics:
- Aggregates block allocator, refcount, slab journal, and slab summary stats into `vdo_statistics`.
- `vdo_dump_slab_depot()` logs zone counts, slab count, and release request state.
