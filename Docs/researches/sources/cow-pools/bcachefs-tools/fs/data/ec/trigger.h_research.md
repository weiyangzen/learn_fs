# File Research: sources/cow-pools/bcachefs-tools/fs/data/ec/trigger.h

Declares stripe bkey operations and inline helpers for stripe variable layout, LRU scoring, pointer matching, GC stripe locking, and open-stripe tracking.

Key responsibilities:
- Defines `bch2_bkey_ops_stripe` with validate, text, swab, trigger, check/repair, and minimum value size.
- Computes checksums-per-device, checksum offsets, blockcount offsets, stripe value size, checksum get/set.
- Computes widening target and clamped `can_widen` value.
- Defines `STRIPE_LRU_POS_EMPTY` and `stripe_lru_pos()`:
  - Empty stripes get special delete-worker position.
  - Reusable stripes are scored by empty data blocks plus `can_widen`.
- Provides pointer-to-stripe matching helpers for live stripe keys and GC stripe mirrors.
- Provides GC stripe bitlock helpers.
- Declares GC stripe memory allocation, new-stripe bucket lookup/add/delete, open-stripe check, and stripe handle tryget/put.

Important interactions:
- Layout helpers must match `ec/format.h` variable-length `struct bch_stripe`.
- `stripe_lru_pos()` drives both deletion and reuse/copygc prioritization.
