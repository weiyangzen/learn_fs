# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/check_types.h

This header defines the lightweight state types used by btree GC/checking code.

Core responsibilities:
- Defines `GC_PHASES()` and `enum gc_phase` with `not_running`, `start`, `sb`, and `btree`.
- Defines `struct gc_pos`, the ordered GC cursor: phase, btree ID, btree level, and btree position.
- Defines `struct reflink_gc` and `reflink_gc_table` for reflink reference tracking in a generic radix tree.
- Defines `struct bch_fs_gc`, which stores current GC position plus a read/write semaphore guarding periods where bucket `gc_mark` state is not globally reliable.
- Defines `struct bch_fs_gc_gens`, the async generation-GC cursor/work item state.

Important invariants:
- `gc_pos.phase` is the coarse phase ordering; btree, level, and `bpos` refine ordering only for btree scanning.
- `bch_fs_gc.lock` protects allocation code from trusting bucket GC marks while GC is in progress.
- `bch_fs_gc_gens` serializes async generation work with a mutex and work item.

Dependencies:
- Includes `btree/bbpos_types.h` for btree/bpos cursor typing.
- Uses Linux generic radix tree support for reflink GC tables.
- Assumes bcachefs core types such as `enum btree_id`, `struct bpos`, `seqcount_t`, `rw_semaphore`, `work_struct`, and `mutex`.

Risk points:
- The bitfield sizing in `gc_pos` is compact and tied to enum ranges.
- GC state is shared between online update paths and background checking, so lock discipline is part of the data model.
