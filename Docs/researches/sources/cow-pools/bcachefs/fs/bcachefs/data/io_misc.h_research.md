# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/io_misc.h

## Role

`io_misc.h` declares the miscellaneous range-mutation APIs implemented in `io_misc.c`.

## API Surface

- Fallocate: `bch2_extent_fallocate()`
- Punch hole: `bch2_fpunch_snapshot()`, `bch2_fpunch_at()`, `bch2_fpunch()`
- Truncate logged op formatting, ops table, resume, and start: `bch2_logged_op_truncate_to_text()`, `bch2_bkey_ops_logged_op_truncate`, `bch2_resume_logged_op_truncate()`, `bch2_truncate()`
- Insert/collapse logged op formatting, ops table, resume, and start: `bch2_logged_op_finsert_to_text()`, `bch2_bkey_ops_logged_op_finsert`, `bch2_resume_logged_op_finsert()`, `bch2_fcollapse_finsert()`

## Key Detail

The logged-op bkey operation tables only provide value text formatting and minimum value size. Behavioral resume is driven by logged-op infrastructure calling the declared resume functions.
