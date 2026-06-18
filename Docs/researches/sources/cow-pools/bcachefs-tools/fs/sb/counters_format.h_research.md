# File Research: sources/cow-pools/bcachefs-tools/fs/sb/counters_format.h

This header defines persistent counter IDs, types, descriptions, and on-disk counter layout.

Key definitions:
- `enum bch_counters_flags`
  - `TYPE_COUNTER`: event counters.
  - `TYPE_SECTORS`: sector amount counters.
- `BCH_PERSISTENT_COUNTERS()`: macro table of all persistent counters with stable numeric IDs, type flags, and descriptions.
- `enum bch_persistent_counters`: generated runtime enum order.
- `bch2_counter_flags[]`: generated counter type map.
- `enum bch_persistent_counters_stable`: generated stable on-disk IDs.
- `struct bch_sb_field_counters`: superblock field header plus flexible array of little-endian u64 counter values.
- `check_bch_counter_ids_unique()`: compile-time switch trick for duplicate stable ID detection.

Counter families:
- Sync/fsync and data read/write/update counters.
- Promotion and no-promotion reason counters.
- Reconcile scan/work counters.
- Stripe allocation/update/repair counters.
- Copygc and discard counters.
- Bucket allocation and sector allocation counters.
- Btree cache/node/path counters.
- Journal reservation/full/reclaim/write counters.
- GC generation counters.
- Transaction restart and commit counters.
- Write buffer and accounting slowpath counters.
- Generic thrown error counter.

Important invariants:
- Stable IDs are sparse and must remain unique.
- `TYPE_SECTORS` counters are measured in sectors.
- The superblock field stores values by stable ID slot, not runtime enum index.

Research notes:
- This header is both user-facing telemetry taxonomy and persistent format.
- Adding counters requires choosing a stable unused ID and correct type flag.
