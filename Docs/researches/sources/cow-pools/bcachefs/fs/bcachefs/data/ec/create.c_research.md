# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/create.c

Implements erasure-coded stripe creation, reuse, widening support, and repair/resilver stripe replacement.

Key entry points:
- `bch2_ec_stripe_head_get()` exposes stripe-head allocation to the sector allocator.
- `bch2_ec_stripe_create_start()` queues completed stripe creation work.
- `bch2_resume_logged_op_stripe_update()` resumes interrupted extent updates after a logged stripe update op.
- `bch2_stripe_repair()` creates replacement stripes for degraded stripes.

Important details:
- Stripe creation allocates data/parity buckets, fills data buffers, generates Reed-Solomon parity/checksums, writes parity/moved blocks, inserts the stripe key, and updates all extents pointing to stripe blocks.
- Extent updates walk backpointers for old buckets, replace direct pointers with new stripe pointers, drop stale EC pointers, and commit with disk reservations.
- Logged operation records old/new stripe indexes and old block map so crash recovery can complete extent updates.
- Stripe reuse selects reusable fragmented stripes from the stripe fragmentation LRU, can retain live data blocks, and allocates only missing/new blocks.
- `can_widen` is computed from RW member sets so stripes can later be reused at wider geometry.
- Device write refs protect devices during stripe creation and repair.

Dependencies and interactions:
- Uses allocation stripe state, open buckets, disk labels/targets, EC IO buffers, EC triggers, backpointers, logged ops, move/copygc contexts, and reconcile marking.
