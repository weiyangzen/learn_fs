# File Research: sources/cow-pools/bcachefs-tools/fs/data/io_misc.h

## Purpose
Declares fallocate, hole punch, truncate, and insert/collapse helpers, plus bkey ops for logged operations.

## Main Interfaces
- `bch2_extent_fallocate()`
- `bch2_fpunch_snapshot()`, `bch2_fpunch_at()`, `bch2_fpunch()`
- `bch2_logged_op_truncate_to_text()`, `bch2_resume_logged_op_truncate()`, `bch2_truncate()`
- `bch2_logged_op_finsert_to_text()`, `bch2_resume_logged_op_finsert()`, `bch2_fcollapse_finsert()`
- `bch2_bkey_ops_logged_op_truncate` and `bch2_bkey_ops_logged_op_finsert` expose text renderers and minimum value sizes.

## Dependencies
Relies on transaction, iterator, subvolume inode, inode opts, printbuf, bkey, and write point types from the surrounding bcachefs codebase.
