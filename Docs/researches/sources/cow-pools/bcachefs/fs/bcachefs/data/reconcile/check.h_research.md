# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/reconcile/check.h

## Role

`check.h` declares the reconcile consistency checker.

## API

- `int bch2_check_reconcile_work(struct bch_fs *);`

## Use

Called by fsck/mount repair paths to verify reconcile work queues and related metadata.
