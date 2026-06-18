# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/accounting.h

This header exposes disk accounting helpers, transaction hooks, and in-memory accounting operations.

Counter helpers:
- `bch2_u64s_neg()` negates a vector of counters.
- `bch2_accounting_counters()` derives the number of counters from a `KEY_TYPE_accounting` value size.
- `bch2_accounting_neg()`, `bch2_accounting_key_is_zero()`, and `bch2_accounting_accumulate()` manipulate accounting values.
- `bch2_accounting_accumulate_maybe_kill()` accumulates and removes zeroed replicas entries when appropriate.

Filesystem usage helpers:
- `fs_usage_data_type_to_base()` maps `BCH_DATA_btree`, user/parity, and cached data types into aggregate filesystem usage fields.

Position conversion:
- `bpos_to_disk_accounting_pos()` and `disk_accounting_pos_to_bpos()` reinterpret accounting keys as btree positions, with byte swapping on little-endian systems so the typed union sorts correctly as a `bpos`.

API and convenience macros:
- `bch2_disk_accounting_mod()` is the main update API.
- `disk_accounting_key_init()` initializes typed accounting keys.
- `bch2_disk_accounting_mod2()` builds a typed key inline and submits a delta.
- `bch2_fs_accounting_read_key2()` is the analogous typed-key read helper.

Bkey operations:
- `bch2_bkey_ops_accounting` supplies validation, text rendering, byte swap, and minimum value size for accounting bkeys.

In-memory accounting:
- `enum bch_accounting_mode` distinguishes normal, GC, and read initialization paths.
- `bch2_accounting_is_mem()` identifies accounting types mirrored in memory.
- `bch2_bkey_is_accounting_mem()` checks whether a bkey is an in-memory accounting key.
- `bch2_accounting_mem_mod_locked()` is the hot path called from transaction commit. It updates aggregate filesystem usage, per-device usage, and the matching per-CPU accounting entry. It inserts missing memory entries when needed.

Transaction hooks:
- `journal_pos_to_bversion()` converts a journal reservation and offset into a unique accounting version.
- `bch2_accounting_trans_commit_hook()` stamps accounting deltas with versions and applies them to memory counters unless accounting apply is skipped.
- `bch2_accounting_trans_commit_revert()` negates and reapplies a committed delta to roll back memory accounting after a failed commit path.

The header ties accounting into transaction commit, GC, device usage initialization/removal, filesystem accounting reads, clean verification, and shutdown.
