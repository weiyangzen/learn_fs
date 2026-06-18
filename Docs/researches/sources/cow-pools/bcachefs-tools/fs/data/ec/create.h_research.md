# File Research: sources/cow-pools/bcachefs-tools/fs/data/ec/create.h

Defines EC stripe creation state structures, helpers, and public interfaces.

Key responsibilities:
- Defines `ec_dev_stripe_state`, `ec_stripe_new_bucket`, `ec_stripe_handle`, `ec_stripe_new`, and `ec_stripe_head`.
- Defines `STRIPE_REF_io` and `STRIPE_REF_stripe` reference classes.
- Provides helpers for data/parity block counts and iteration ranges.
- Declares EC device selection, stripe formability, widening cache, stripe cancellation, bucket cancellation, stripe-head get/put, stripe create/delete, stripe repair, diagnostics, and logged-op resume APIs.
- Implements `ec_stripe_new_get()` / `ec_stripe_new_put()`.
- On final IO ref drop, assigns a monotonic `seq`, wakes flush waiters, and starts stripe creation work.
- Provides bkey ops for logged stripe-update operations.

Important interactions:
- `ec_stripe_new` ties together allocation state, old/new stripe buffers, open stripe handles, block maps, disk reservation, and moving context.
- `ec_stripe_head` is the allocator-facing staging object for each disk-label/algorithm/redundancy/watermark tuple.
