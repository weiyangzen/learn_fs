# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/accounting_format.h

This header defines the on-disk format for `KEY_TYPE_accounting`.

The key idea is that an accounting key is a `struct disk_accounting_pos`, a type-tagged union overlaid on a `bpos`. Values are variable-length arrays of `u64` counters. Updates written through the write buffer are deltas, and the persistent btree value becomes the accumulated counter state when deltas are flushed or replayed.

The file documents a critical replay invariant: every accounting update receives a unique `bversion` derived from journal position. Journal replay compares journal key version against the btree key version to decide whether a delta still needs replay. Therefore accounting write-buffer flushes must preserve strict temporal ordering, especially while journal replay is active.

Data types:
- `BCH_DATA_free`
- `BCH_DATA_sb`
- `BCH_DATA_journal`
- `BCH_DATA_btree`
- `BCH_DATA_user`
- `BCH_DATA_cached`
- `BCH_DATA_parity`
- `BCH_DATA_stripe`
- `BCH_DATA_need_gc_gens`
- `BCH_DATA_need_discard`
- `BCH_DATA_unstriped`

`data_type_is_empty()` treats free, need-gc-gens, and need-discard as empty states. `data_type_is_hidden()` marks superblock and journal data as hidden from normal capacity accounting.

Accounting types and counter counts:
- `nr_inodes`: 1 counter.
- `persistent_reserved`: 1 counter, keyed by replica count.
- `replicas`: 1 counter, keyed by a replicas entry.
- `dev_data_type`: 3 counters: bucket count, live sectors, fragmented sectors.
- `compression`: 3 counters: extent count, uncompressed size, compressed size.
- `snapshot`: 1 counter.
- `btree`: 3 counters: sectors, nodes, non-leaf nodes.
- `rebalance_work`: 1 counter.
- `inum`: 3 counters: extent count, logical sectors, on-disk sectors.
- `reconcile_work`: 2 counters.
- `dev_leaving`: 1 counter.

The packed structs under `bch_acct_*` define the key fields for each type. `struct disk_accounting_pos` contains the type byte and a packed union of those subtype fields, or the raw `_pad` `bpos` overlay.
