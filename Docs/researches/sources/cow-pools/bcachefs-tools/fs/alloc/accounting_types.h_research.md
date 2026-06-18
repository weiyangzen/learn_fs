# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/accounting_types.h

This small header defines the in-memory accounting structures.

Structures:
- `struct accounting_mem_entry`
  - `pos`: accounting key position, matching `disk_accounting_pos_to_bpos()`.
  - `bversion`: latest version seen for the accounting key.
  - `nr_counters`: number of counters for this entry.
  - `v[2]`: percpu counter arrays. `v[0]` is live accounting; `v[1]` is used during GC accounting verification.
- `struct bch_accounting_mem`
  - `k`: dynamic array of `accounting_mem_entry`.
  - `gc_running`: whether GC shadow counters are currently allocated/active.

Role:
- This is the backing storage for the fast in-memory accounting table managed by `accounting.c`.
- Entries are sorted with Eytzinger layout for fast lookup by accounting position.
- Counter arrays are percpu, enabling low-contention commit-path updates and cheap aggregate reads.
