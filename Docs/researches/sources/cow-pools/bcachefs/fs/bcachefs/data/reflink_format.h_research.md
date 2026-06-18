# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/reflink_format.h

On-disk format definitions for reflink pointer keys, indirect extent values, and indirect inline data.

Key contents:
- `struct bch_reflink_p` stores a packed `idx_flags`, `front_pad`, and `back_pad`.
- Bitfields define `REFLINK_P_IDX`, `REFLINK_P_ERROR`, and `REFLINK_P_MAY_UPDATE_OPTIONS`.
- `struct bch_reflink_v` stores a 64-bit refcount followed by normal extent entries.
- `struct bch_indirect_inline_data` stores a 64-bit refcount followed by inline data bytes.

Important invariants:
- `front_pad` and `back_pad` remember the full indirect range referenced when a reflink pointer was created; this is required to preserve refcount correctness after the indirect extent is split.
- `REFLINK_P_MAY_UPDATE_OPTIONS` gates whether inode IO options may propagate to shared indirect extents.
