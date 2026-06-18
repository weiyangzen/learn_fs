# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/trigger.h

Public EC stripe bkey operations and inline stripe layout helpers.

Key contents:
- `bch2_bkey_ops_stripe` binds validate, text, swab, trigger, and min value size.
- Helpers compute checksum count, checksum offsets, blockcount offsets, value size, checksum get/set.
- `stripe_widen_target_nr_data()` and `stripe_widen_value()` compute widening capacity.
- `stripe_lru_pos()` scores empty/reusable stripes for deletion or reuse.
- Pointer-match helpers compare extent pointers to stripe blocks.
- GC stripe lock helpers and declarations for open-stripe/new-bucket hash operations.

Dependencies and interactions:
- Used throughout EC create, IO, init, trigger, copygc, and extents logic.
