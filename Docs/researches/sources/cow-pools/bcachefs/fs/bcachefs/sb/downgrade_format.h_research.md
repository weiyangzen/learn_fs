# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/downgrade_format.h

This header defines the on-disk format of the downgrade superblock section.

Key types:
- `struct bch_sb_field_downgrade_entry`: packed entry containing target metadata version, two words of stable recovery-pass bits, error count, and flexible array of fsck error IDs.
- `struct bch_sb_field_downgrade`: superblock field wrapper containing a variable-length list of entries.

Important invariant:
- Entries are `__packed __aligned(2)`, so code must not assume natural 64-bit alignment for `recovery_passes`.
