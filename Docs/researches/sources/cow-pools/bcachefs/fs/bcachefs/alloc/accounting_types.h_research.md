# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/accounting_types.h

This small header defines the in-memory accounting containers.

`struct accounting_mem_entry` stores:
- `pos`: the accounting key position.
- `bversion`: the accounting bkey version.
- `nr_counters`: number of counters for this entry.
- `v[2]`: two per-CPU counter arrays. Index 0 is normal accounting; index 1 is used during GC accounting verification.

`struct bch_accounting_mem` stores:
- `k`: a dynamic array of `accounting_mem_entry`, sorted in Eytzinger order for fast lookup.
- `gc_running`: whether GC comparison counters are allocated and active.

This file is the data-structure companion to `accounting.c` and `accounting.h`.
