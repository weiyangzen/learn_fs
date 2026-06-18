# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/accounting_format.h

This header defines the on-disk format for `KEY_TYPE_accounting` values and accounting key positions.

Format model:
- The accounting btree key position is a `struct disk_accounting_pos`, a type-tagged union overlaid on `struct bpos`.
- The value is `struct bch_accounting`, a flexible array of `__u64 d[]` counters.
- Updates stored through the write buffer are deltas. The persistent btree value becomes the accumulated counter value after write-buffer flush or journal replay.
- Accounting key `bversion` is a replay ordering marker derived from journal position, allowing journal replay to determine which deltas are newer than the btree value.

Data types:
- `BCH_DATA_TYPES()` defines bucket/data categories: free, superblock, journal, btree, user, cached, parity, stripe, need-gc-gens, need-discard, unstriped.
- `data_type_is_empty()` treats free, need-gc-gens, and need-discard as empty bucket states.
- `data_type_is_hidden()` marks superblock and journal as hidden usage.

Accounting types:
- `nr_inodes`: one counter, total filesystem inode count.
- `persistent_reserved`: one counter, reservation sectors by replica count.
- `replicas`: one counter, usage by replicas entry.
- `dev_data_type`: three counters, per-device bucket count, sectors, and fragmentation.
- `compression`: three counters, extent count, uncompressed size, compressed size.
- `snapshot`: one counter, per-snapshot on-disk usage.
- `btree`: three counters, btree sectors, node count, non-leaf node count.
- `rebalance_work`: one counter.
- `inum`: three counters, extent count, logical extent sectors, on-disk sectors.
- `reconcile_work`: two counters.
- `dev_leaving`: one counter.

Important constraints:
- `BCH_ACCOUNTING_MAX_COUNTERS` is 3, and all accounting types must fit that limit.
- The `disk_accounting_pos` layout is packed and must remain exactly the size of `struct bpos`.
- Adding accounting types extends the type-tagged key space without changing the btree schema.
