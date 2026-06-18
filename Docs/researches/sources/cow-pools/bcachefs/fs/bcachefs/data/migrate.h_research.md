# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/migrate.h

## Role

`migrate.h` declares device-data drop APIs.

## API

- `bch2_dev_data_drop_by_backpointers(struct bch_fs *, struct bch_dev *, unsigned, struct printbuf *)`
- `bch2_dev_data_drop(struct bch_fs *, unsigned dev_idx, unsigned flags, struct printbuf *)`

## Use

These functions are called by device removal/evacuation management paths that need to delete or invalidate references to a device.
