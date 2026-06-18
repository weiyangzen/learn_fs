# File Research: sources/block-storage/kvdo/vdo/slab.c

This file implements lifecycle and state transitions for a single VDO slab. `vdo_make_slab()` allocates a `vdo_slab`, sets partition-relative start/end and translated metadata origins, creates its slab journal, and either marks the slab new with freshly allocated ref counts or normal-operation for later load.

Reference-count handling is central:
- `vdo_allocate_ref_counts_for_slab()` enforces single allocation and creates ref-count storage from slab configuration.
- `vdo_modify_slab_reference_count()` ignores zero-block slabs, preserves ref-count state for unrecovered slabs while releasing journal references, otherwise adjusts counts and updates free-block accounting when free status changes.
- `vdo_acquire_provisional_reference()` gives PBN locks provisional references and decrements free accounting if a provisional ref was acquired.

Admin-state integration:
- `initiate_slab_action()` dispatches draining, loading, and resuming behavior.
- Draining drains slab journal and ref counts, then `vdo_check_if_slab_drained()` completes when both are inactive.
- Loading decodes the slab journal, and normal/new load completion can allocate ref counts in `vdo_notify_slab_journal_is_loaded()`.

Recovery/scrubbing helpers manage `enum slab_rebuild_status`: unrecovered, replaying, rebuilding, rebuilt, and high-priority scrub states. `vdo_should_save_fully_built_slab()` decides whether rebuilt ref counts need persistence based on summary flags, non-empty data, or non-blank journal. Debug logging reports slab priority/free space or rebuild status plus journal/ref-count details.
