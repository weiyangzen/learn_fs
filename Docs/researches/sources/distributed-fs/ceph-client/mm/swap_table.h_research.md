# sources/distributed-fs/ceph-client/mm/swap_table.h

Purpose: defines the compact atomic per-slot table used by each swap cluster. The table records whether a slot is free, bad, cached by a folio PFN, or represented by a shadow value, and embeds a small swap reference count into the high bits.

Important APIs and types: `struct swap_table` is an array of `atomic_long_t entries[SWAPFILE_CLUSTER]`. Encoding helpers include `null_to_swp_tb()`, `pfn_to_swp_tb()`, `folio_to_swp_tb()`, and `shadow_to_swp_tb()`. Classifiers include `swp_tb_is_null()`, `swp_tb_is_folio()`, `swp_tb_is_shadow()`, `swp_tb_is_bad()`, and `swp_tb_is_countable()`. Extractors include `swp_tb_to_folio()`, `swp_tb_to_shadow()`, `swp_tb_get_count()`, and `__swp_tb_mk_count()`. Cluster-table accessors are `__swap_table_set()`, `__swap_table_xchg()`, `__swap_table_get()`, and RCU-safe `swap_table_get()`.

Control flow: swap allocator, swap cache, and swapoff code lock a cluster and use the double-underscore helpers to mutate entries. Lockless readers use `swap_table_get()` inside an RCU read-side critical section; freed page-backed tables are RCU-delayed. Counts sit in the upper bits and either fit directly or, when saturated at `SWP_TB_COUNT_MAX`, are extended by `swap_cluster_info.extend_table` in `swapfile.c`.

State and persistence: each entry is a single machine word. Null means allocatable, shadow means swapped out without cache and may carry an `xa_value`, PFN means the slot is cached by a folio and carries the same count bits, and bad reserves header/hole/bad-page slots. The table is volatile kernel metadata rebuilt on swapon and freed on swapoff; it describes persistent swap slots but is not itself stored on disk.

Dependencies and integration points: depends on `swap.h` for cluster metadata and cluster size, XArray value encoding for shadows, PFN width macros, RCU, and atomics. It is central to `swap_state.c` cache lookup and `swapfile.c` allocation/count/free logic.

Risks and test signals: risks include bit-layout overlap between PFNs and count bits on high-physical-address systems, mistaking `xa_value` shadows for PFN markers, count underflow/overflow, reading a table after free without RCU protection, and storing bad entries where countable entries are expected. Test with large physical address configs, `SWP_TABLE_USE_PAGE` true/false, swap count overflow into extend tables, bad-page swap headers, lockdep for cluster-held mutations, and RCU/KASAN stress during swapoff.
