# File Research: sources/cow-pools/bcachefs-tools/fs/data/migrate.h

## Purpose
Public declarations for device data-drop operations.

## Main Interfaces
- `bch2_dev_data_drop_by_backpointers(struct bch_fs *, struct bch_dev *, unsigned flags, struct printbuf *)`
- `bch2_dev_data_drop(struct bch_fs *, unsigned dev_idx, unsigned flags, struct printbuf *)`

## Notes
The backpointer variant takes a live `struct bch_dev *`; the full scan variant takes a device index.
