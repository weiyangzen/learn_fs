# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/repair.h

Purpose: Small public header for VDO repair/recovery entry points. It exposes the dirty-load repair driver and the per-allocator slab journal replay callback used while the slab depot is being loaded.

Important APIs, types, and functions: declares `vdo_repair(struct vdo_completion *parent)` and `vdo_replay_into_slab_journals(struct block_allocator *allocator, void *context)`. It includes `types.h` for forward declarations and VDO core type aliases. The header intentionally does not expose `struct repair_completion`; all repair state is private to `repair.c`.

Control flow contract: admin/load code calls `vdo_repair()` with a parent completion on the admin thread when a VDO is dirty, forced into rebuild, or rebuilding for upgrade. Slab depot load code calls `vdo_replay_into_slab_journals()` for each block allocator, passing the private repair context provided by `repair.c` during depot loading.

State and persistence behavior: no state is defined here, but both declarations participate in persistent recovery. `vdo_repair()` ultimately reads and interprets the recovery journal, updates block-map/slab metadata, and reinitializes the journal state. `vdo_replay_into_slab_journals()` replays journaled refcount effects into allocator-owned slab journals before repaired metadata is drained.

Dependencies and integration points: integrates `repair.c` with the VDO target/load path and slab depot. Callers must provide valid VDO completions, allocator completions, and the repair context established by the repair state machine.

Risks and test signals: because the context argument is opaque, misuse by slab depot callers would fail at runtime rather than compile time. Tests should verify both exported functions are invoked on their expected admin or physical-zone threads, propagate completion failures, and are not called after the repair completion has been freed.
