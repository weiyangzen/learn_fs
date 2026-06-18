# File Research: sources/cow-pools/bcachefs-tools/fs/data/copygc_types.h

Defines per-filesystem copygc state.

Key responsibilities:
- `struct bch_fs_copygc` tracks the copygc thread, write point, wait timing, running flag, run/kick counters, running waitqueue, and dedicated workqueue.

Important interactions:
- Populated by `copygc.c` and embedded in `struct bch_fs`.
- `write_point` is passed into moving context so copygc relocations use a dedicated writepoint.
