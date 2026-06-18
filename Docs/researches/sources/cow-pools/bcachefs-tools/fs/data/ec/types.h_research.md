# File Research: sources/cow-pools/bcachefs-tools/fs/data/ec/types.h

Defines in-memory EC summary, GC mirror, and per-filesystem EC state.

Key responsibilities:
- Defines compact `struct stripe` summary fields.
- Defines `struct gc_stripe` with lock, alive flag, geometry, block sector counters, pointers, and replica accounting.
- Defines `struct bch_fs_ec` with:
  - stripe buffer memory accounting and waitlist,
  - open stripe/new bucket hash tables,
  - stripe-head and per-device stripe-state lists/locks,
  - pending stripe list/waitqueue/sequence,
  - stripe create workqueue,
  - stripe hint,
  - stripe delete work,
  - EC block bioset,
  - genradix GC stripe storage.

Important interactions:
- Embedded in `struct bch_fs` and initialized by `init.c`.
- Used by create/trigger/io code for all EC lifecycle state.
