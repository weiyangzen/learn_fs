# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/format.h

Defines the on-disk `struct bch_stripe` format.

Key fields:
- Stripe sectors, algorithm, `needs_reconcile`, `can_widen`, block count, redundancy count.
- Checksum granularity and checksum type.
- `disk_label` for target grouping.
- Flexible array of extent pointers followed by variable-length checksums and per-block sector counts.

Important details:
- `can_widen` is a 3-bit saturating value.
- Comments note a format limitation: checksum size is implicit, making blockcount access dependent on known checksum type.
- Format is packed and 8-byte aligned.

Dependencies and interactions:
- Accessor layout helpers live in `trigger.h`.
- Used by EC create, IO, trigger, fsck/check, and read reconstruction.
