# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/errors_format.h

This header defines fsck error flags, the stable fsck/superblock error catalog, and the on-disk errors field.

Key responsibilities:
- Defines fsck error behavior flags: can fix, can ignore, autofix, no log, and silent.
- Lists all stable `BCH_FSCK_ERR_*` IDs with numeric IDs and flags.
- Generates `enum bch_sb_error_id`.
- Defines packed on-disk error entries and the variable-length errors superblock field.
- Defines bitfield accessors for 16-bit error ID and 48-bit count.

Error categories include:
- Clean/dirty journal state and journal entry validation.
- B-tree node, bset, topology, and root errors.
- Filesystem/device usage accounting.
- Allocation, freespace, bucket generation, discard, and backpointer errors.
- Extent pointer, checksum/compression, stripe, reflink, and reservation errors.
- Snapshot/subvolume/inode/dirent/xattr/quota namespace errors.
- Accounting/reconcile/workqueue and VFS consistency errors.
- Device flush and journal bucket sequence errors.

Important invariant:
- Numeric IDs are stable and sparse; the final `MAX` entry establishes `BCH_FSCK_ERR_MAX`.
