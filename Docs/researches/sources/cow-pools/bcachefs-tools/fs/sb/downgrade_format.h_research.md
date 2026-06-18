# File Research: sources/cow-pools/bcachefs-tools/fs/sb/downgrade_format.h

This header defines the on-disk downgrade superblock field format.

Key definitions:
- `struct bch_sb_field_downgrade_entry`
  - `version`: metadata version threshold.
  - `recovery_passes[2]`: stable recovery pass bitmaps.
  - `nr_errors`: count of trailing fsck error IDs.
  - `errors[]`: little-endian fsck error IDs.
  - Packed and aligned to 2 bytes.
- `struct bch_sb_field_downgrade`
  - Standard superblock field header.
  - Flexible array of downgrade entries.

Important invariants:
- Entries are variable length and only 2-byte aligned.
- Recovery pass bitmaps are stored as little-endian u64 arrays.
- `errors[]` is counted by `nr_errors`.

Research notes:
- Consumers must parse carefully because section size is 8-byte aligned while entries are 2-byte aligned.
