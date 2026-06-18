# File Research: sources/cow-pools/bcachefs-tools/fs/data/reconcile/format.h

## Purpose
Defines on-disk reconcile/rebalance extent entries and the btree/work/accounting IDs used to track background reconciliation.

## Main Interfaces and Behavior
- Header comments describe reconcile metadata:
  - extents carry `bch_extent_reconcile` when background processing is pending;
  - indirect extents may carry reconcile opts to preserve owning inode IO-path options;
  - scan cookies represent option-change propagation work;
  - separate normal, hipri, pending, and physical work btrees track work.
- `struct bch_extent_rebalance_v1` is an older packed format with IO options and “from inode” bits.
- `struct bch_extent_reconcile` stores type, moving pointer bitmask, hipri/pending bits, `need_rb` bitmask, six IO options, and six “from inode” markers.
- `struct bch_extent_reconcile_bp` stores an index into reconcile scan backpointer space for btree pointer reconcile work.
- `BCH_RECONCILE_OPTS()` enumerates persisted IO options: data replicas, checksum, erasure coding, background compression, background target, promote target.
- `BCH_RECONCILE_ACCOUNTING()` enumerates accounting buckets for replicas, checksum, erasure code, compression, target, high priority, pending, and stripes.
- `RECONCILE_WORK_IDS()` defines none, hipri, normal, and pending. Static maps convert work IDs to logical and physical reconcile work btree IDs.
- Scan-cookie constants reserve cookies for filesystem, metadata, pending, stripes, and per-device scans.

## Risks and Invariants
- `pending` work is not represented in the physical work map.
- The bitfield width of targets/options bounds representable option values.
