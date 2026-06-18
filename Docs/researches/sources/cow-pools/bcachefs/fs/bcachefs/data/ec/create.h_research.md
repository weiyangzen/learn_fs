# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/create.h

Declares stripe-creation state machines and allocator-facing EC interfaces.

Key contents:
- `struct ec_dev_stripe_state` tracks per-disk-label allocation striping state for data and parity buckets.
- `struct ec_stripe_new` represents an in-progress stripe, including refs, allocated buckets, old/new stripe buffers, block maps, and repair/move context.
- `struct ec_stripe_head` groups in-progress stripe creation by disk label, algorithm, redundancy, and watermark.
- Inline ref handling starts stripe creation when IO refs drain and frees when stripe refs drain.
- Iteration macros define data, parity, and combined block ranges.

Dependencies and interactions:
- Shared by allocator/write path, EC create worker, copygc/repair, and trigger/open-stripe tracking.
