# File Research: sources/cow-pools/bcachefs-tools/fs/sb/errors_format.h

This header defines fsck error flags, the full fsck/superblock error ID catalog, and the on-disk error-count field.

Key definitions:
- `enum bch_fsck_flags`
  - `FSCK_CAN_FIX`
  - `FSCK_CAN_IGNORE`
  - `FSCK_AUTOFIX`
  - `FSCK_ERR_NO_LOG`
  - `FSCK_ERR_SILENT`
- `BCH_SB_ERRS()`: macro table mapping symbolic error names to stable numeric IDs and flags.
- `enum bch_sb_error_id`: generated stable fsck error IDs.
- `bch_sb_field_error_entry`: packed value plus last error timestamp.
- `struct bch_sb_field_errors`: superblock field header plus trailing error entries.
- Bitfields:
  - `BCH_SB_ERROR_ENTRY_ID`
  - `BCH_SB_ERROR_ENTRY_NR`

Error families:
- Clean/dirty journal state and jset validation errors.
- Journal entry and btree node/bset structural errors.
- Filesystem and device usage accounting mismatches.
- Allocation, bucket generation, discard, freespace, and backpointer errors.
- Extent pointer, CRC, stripe, reflink, snapshot, subvolume, inode, dirent, xattr, quota, and root errors.
- Accounting key and reconcile work errors.
- VFS integration and compression/device/journal bucket errors.

Important invariants:
- Numeric IDs are stable and sparse.
- `MAX` defines the current upper bound.
- Error entry ID is 16 bits; error count is 48 bits.
- Flags express fsck policy hints but the table itself is also persistent ABI.

Research notes:
- This is one of the core compatibility headers for fsck diagnostics. Renumbering entries would break persisted error counts and downgrade/upgrade policy tables.
