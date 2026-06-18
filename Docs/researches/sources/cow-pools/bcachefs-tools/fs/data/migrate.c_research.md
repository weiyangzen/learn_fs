# File Research: sources/cow-pools/bcachefs-tools/fs/data/migrate.c

## Purpose
Implements data removal from a device, either by scanning data btrees or by using backpointers. It drops device pointers from user data, metadata btree pointers, and stripes while enforcing degradation/loss force flags.

## Main Interfaces and Behavior
- `drop_dev_ptrs()` reassembles a key, removes pointers for a target device, checks resulting durability against metadata/data replica requirements, and either marks the key for reconcile or converts unreadable user data to an error key.
- Metadata and data use different force flags: metadata loss/degradation versus data loss/degradation.
- `drop_btree_ptrs()` updates an in-memory btree node key after dropping device pointers.
- `bch2_dev_usrdata_drop_key()` updates a normal data key; deleted keys have size forced to zero because this path does not go through the extent overwrite iterator.
- `bch2_dev_btree_drop_key()` resolves a backpointer to a btree node and drops the device pointer from that node key.
- `bch2_dev_usrdata_drop()` scans all pointer-bearing btrees except stripes and applies device-pointer drops with progress tracking.
- `bch2_dev_metadata_drop()` scans btree nodes at all levels and drops metadata pointers. It does not implement forced metadata-lost removal.
- `data_drop_bp()` resolves a backpointer and dispatches to btree pointer drop, stripe invalidation, or user data drop.
- `bch2_dev_data_drop_by_backpointers()` scans the backpointer namespace for the device, repeatedly flushing and rescanning until the device has no data buckets. It tracks progress by `dev_data_buckets()` lows and aborts after 10 stalled scans.
- `bch2_dev_data_drop()` performs full user-data then metadata scans without relying on backpointers.

## Dependencies and Coupling
Uses backpointer lookup, btree node update, write-buffer flushing, EC stripe invalidation, reconcile option setting, durability accounting, and progress indicators.

## Risks and Invariants
- Backpointer scanning races with reconcile and stripe reshape; the function intentionally retries based on observed remaining device data rather than a fixed iteration cap.
- Open stripes are skipped and `bch2_fs_ec_flush_outstanding()` is called before rescanning.
- Metadata-lost removal is explicitly unimplemented.
