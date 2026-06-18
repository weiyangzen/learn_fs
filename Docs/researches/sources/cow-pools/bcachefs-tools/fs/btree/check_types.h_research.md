# File Research: sources/cow-pools/bcachefs-tools/fs/btree/check_types.h

## Purpose

`check_types.h` defines small data structures used by btree GC/checking.

## Types

### GC Phases

`GC_PHASES()` expands to:

- `not_running`
- `start`
- `sb`
- `btree`

`enum gc_phase` is generated from that macro.

### `struct gc_pos`

Represents current GC progress:

- `phase`: current GC phase.
- `btree`: btree id for btree-walk phase.
- `level`: btree level.
- `pos`: btree key position.

This is the state compared by `gc_pos_cmp()` and read by `gc_visited()`.

### `struct reflink_gc`

Temporary reflink GC accounting record:

- `offset`
- `size`
- `refcount`

`reflink_gc_table` is a generic radix tree of these entries.

### `struct bch_fs_gc`

Filesystem-wide GC runtime state:

- `pos_lock`: seqcount protecting `pos`.
- `pos`: current GC position.
- `lock`: rw semaphore protecting GC state and allocation marking.

### `struct bch_fs_gc_gens`

State for asynchronous generation cleanup:

- `pos`: progress marker as `bbpos`.
- `work`: workqueue item.
- `lock`: mutex ensuring one generation GC at a time.
