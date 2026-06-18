# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/accounting.h

This header provides the inline API and public declarations for disk accounting.

Key inline helpers:
- `bch2_u64s_neg()` negates an array of counters in place.
- `bch2_accounting_counters()` derives the counter count from the accounting key value size.
- `bch2_accounting_key_is_zero()` checks whether all counters are zero.
- `bch2_accounting_accumulate()` adds one accounting value into another and preserves the newer `bversion`.
- `fs_usage_data_type_to_base()` maps data-type usage into aggregate filesystem usage buckets: btree, data, cached.
- `bpos_to_disk_accounting_pos()` and `disk_accounting_pos_to_bpos()` map between the structured accounting key and the opaque btree position, with endian handling.
- `disk_accounting_key_init()` and `bch2_disk_accounting_mod2()` are convenience macros for constructing typed accounting positions and submitting deltas.

In-memory accounting:
- `bch2_accounting_is_mem()` excludes accounting types that are not maintained in the fast in-memory table, currently `snapshot` and `inum`.
- `bch2_accounting_mem_mod_locked()` is the central commit-path in-memory updater. For normal updates it also accumulates `trans->fs_usage_delta` and per-device percpu usage.
- `bch2_accounting_mem_add()` wraps the updater under `capacity.mark_lock`.
- `bch2_accounting_mem_read_counters()` and `bch2_accounting_mem_read()` provide indexed and position-based reads.

Transaction integration:
- `journal_pos_to_bversion()` converts a transaction journal reservation plus accounting-buffer offset into the unique accounting version.
- `bch2_accounting_trans_commit_hook()` assigns that version and applies the accounting delta to memory unless `BCH_TRANS_COMMIT_skip_accounting_apply` is set.
- `bch2_accounting_trans_commit_revert()` negates and reapplies an accounting update to undo in-memory effects on commit failure.

Declared operations cover validation/printing, superblock updates, accounting readout, GC verification, device usage initialization/removal, clean verification, and shutdown.

Correctness notes:
- `bch2_accounting_mem_mod_locked()` loops until the accounting position exists, inserting if necessary.
- GC-mode accounting updates are ignored when `gc_running` is false.
- Per-device hidden usage is increased for `BCH_DATA_sb` and `BCH_DATA_journal` by bucket size, not by live sectors.
