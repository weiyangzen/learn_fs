# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_refcount.h

## Purpose
`xfs_refcount.h` declares the public libxfs interface for refcount btree lookup, update intents, COW reservation tracking, query callbacks, and validation. It is the contract between bmap/reflink/defer code and the refcount implementation.

## Important APIs and types
The header exposes lookup/get functions, `xfs_refcount_insert`, range query, `xfs_refcount_has_records`, per-AG and realtime record validators, and `xfs_refcount_btrec_to_irec`. `enum xfs_refcount_intent_type` defines deferred operation types: increase, decrease, allocate COW, and free COW. `struct xfs_refcount_intent` carries the deferred list node, target `xfs_group`, operation type, blockcount, startblock, and realtime flag.

`xfs_refcount_encode_startblock` is a central inline helper that folds the refcount domain into the high startblock bit. `xfs_refcount_check_domain` encodes a core invariant: COW-domain records must have refcount 1, while shared-domain records must have refcount at least 2.

## Control flow and integration
Callers should enqueue logical operations through `xfs_refcount_increase_extent`, `xfs_refcount_decrease_extent`, `xfs_refcount_alloc_cow_extent`, and `xfs_refcount_free_cow_extent`; deferred processing calls `xfs_refcount_finish_one` or `xfs_rtrefcount_finish_one`. Query users provide an `xfs_refcount_query_range_fn` callback and receive validated in-core records.

## State and persistence behavior
The header does not store state itself, but defines the in-memory deferred operation shape that backs logged refcount intent items. The `XFS_REFCOUNT_ITEM_OVERHEAD` estimate documents how much log reservation each dirty refcount record is assumed to consume, including space for split/continuation behavior.

## Dependencies, risks, and test signals
The API depends on `xfs_btree_cur`, `xfs_trans`, `xfs_bmbt_irec`, `xfs_perag`, and `xfs_rtgroup`. Callers must pass group-relative block ranges of the correct domain, avoid using COW fork mappings for normal refcount updates, and expect operations to be continued across transactions. Tests should verify domain encoding, saturation behavior, deferred intent replay, and COW record validation.
