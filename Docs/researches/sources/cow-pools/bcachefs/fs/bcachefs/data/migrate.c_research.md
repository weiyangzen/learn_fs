# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/migrate.c

## Role

`migrate.c` implements data dropping during device removal or forced device-data evacuation. It removes pointers to a device from user data, metadata btree nodes, stripes, and backpointer-discovered keys while preserving durability rules unless force flags allow degradation or loss.

## Main Flow

`drop_dev_ptrs()` is the core routine:
- checks whether a key has the target device
- reassembles a mutable key with sufficient maximum buffer space
- drops the device pointer
- computes durability
- refuses loss/degradation unless permitted by flags
- marks readable keys as needing reconcile, or converts unreadable user data to an error key

User data scan:
- `bch2_dev_usrdata_drop()` walks all btrees that may contain data pointers except stripes.
- `bch2_dev_usrdata_drop_key()` updates keys with `BTREE_UPDATE_internal_snapshot_node`.

Metadata scan:
- `bch2_dev_metadata_drop()` walks btree nodes by level and updates node keys.
- Metadata loss removal is explicitly unimplemented when forced loss is requested.

Backpointer scan:
- `bch2_dev_data_drop_by_backpointers()` walks `BTREE_ID_backpointers` for one device.
- `data_drop_bp()` resolves each backpointer to its referenced key and dispatches to btree pointer, stripe invalidation, or user data pointer dropping.

## Important Behavior

Backpointer-based dropping retries up to ten full iterations because reconcile and stripe reshape can modify backpointers for read-only devices while the scan is running.

`dev_has_data()` checks actual device usage counters to decide whether the scan has converged.

## Invariants

- Stripe keys are excluded from generic user-data scans and handled through EC/stripe-specific invalidation.
- If dropping a pointer would reduce durability below policy, the operation requires force flags.
- Btree pointer keys are updated through btree-node update paths, not regular leaf updates.
