# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/types.h

Defines EC runtime and GC data structures.

Key contents:
- `struct stripe` is a compact in-memory stripe summary for heap/scan use.
- `struct gc_stripe` stores GC-time stripe state, block sector counts, pointers, and replicas entry.
- `struct bch_fs_ec` holds stripe buffer accounting, open-stripe/new-bucket hash tables, stripe heads, dev stripe state, pending stripe list/waitqueue/sequence, create workqueue, stripe hint/delete work, EC bioset, and GC stripe genradix.

Dependencies and interactions:
- Embedded in `struct bch_fs`.
- Fields are initialized by EC init and mutated by create/trigger/IO paths.
