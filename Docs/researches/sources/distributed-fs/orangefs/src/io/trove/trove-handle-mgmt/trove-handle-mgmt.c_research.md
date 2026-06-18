## sources/distributed-fs/orangefs/src/io/trove/trove-handle-mgmt/trove-handle-mgmt.c

Purpose: Provides the process-level Trove handle allocator facade. It maps collection IDs to per-collection handle ledgers, initializes valid handle ranges, removes handles already present on disk, allocates/free/peeks handles, and returns free-handle statistics.

Important APIs and functions: `trove_handle_mgmt_initialize` creates the global collection-to-ledger hash. `trove_set_handle_ranges` parses a configured handle range string, creates or finds the collection ledger, maps all extents into it, then calls `trove_check_handle_ranges` to iterate existing dataspace handles and remove them from the free pool. `trove_set_handle_timeout` updates delayed reuse. `trove_handle_alloc`, `trove_handle_alloc_from_range`, `trove_handle_peek`, `trove_handle_peek_from_range`, `trove_handle_set_used`, `trove_handle_free`, `trove_handle_get_statistics`, and `trove_handle_mgmt_finalize` form the allocator API.

Control flow: All public operations take `trove_handle_mutex`. Range setup converts `handle_range_str` with `PINT_create_extent_list`, adds each `PVFS_handle_extent` to the ledger, sets the reuse cutoff to roughly one quarter of total handles, then synchronously drains `trove_dspace_iterate_handles` operations through `trove_dspace_test` so allocated-on-disk handles are removed from the free ledger. Allocation and peek paths search the hash table, require `have_valid_ranges == 1`, and delegate to `trove-ledger.c`.

State and persistence: Global state is `s_fsid_to_ledger_table`, a quickhash table keyed by `TROVE_coll_id`. Each entry stores the collection ID, whether configured ranges are valid, and a `struct handle_ledger *`. The allocator itself is memory-resident; persistence comes indirectly from scanning existing Trove dataspaces during range setup.

Dependencies and integration points: Integrates `quickhash`, `gen-locks`, `extent-utils`, `trove-ledger`, and public Trove dataspace iteration/test APIs. DBPF dataspace creation/removal calls `trove_handle_alloc*`, `trove_handle_set_used`, and `trove_handle_free`.

Risks: APIs assume `trove_handle_mgmt_initialize` succeeded; `finalize` dereferences the global table without a null guard. Error paths in `trove_set_handle_ranges` can return while holding no extent-list cleanup for the parsed list. Range verification is expensive and synchronous, so setup cost scales with existing handles. Error conventions mix `-TROVE_*`, `-PVFS_*`, and `-1`. The single global mutex is simple but serializes all collection allocations. If extent-list counts drift, statistics and recycle thresholds returned here drift too.

Test signals: Exercise blank filesystem setup, invalid/out-of-range on-disk handles, duplicate `trove_set_handle_ranges`, allocation before ranges are set, range-constrained allocation across multiple extents, peeking consistency, set-used/free interactions, timeout changes, stats, and finalize/reinitialize cycles.
