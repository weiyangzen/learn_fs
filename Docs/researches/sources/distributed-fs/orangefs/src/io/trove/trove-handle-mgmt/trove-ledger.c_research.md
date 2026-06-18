## sources/distributed-fs/orangefs/src/io/trove/trove-handle-mgmt/trove-ledger.c

Purpose: Implements an opaque per-collection handle ledger composed of three extent lists: immediately free handles, recently freed handles, and overflow handles waiting for safe reuse.

Important APIs and functions: `trove_handle_ledger_init` allocates and initializes the three lists. `trove_ledger_handle_alloc`, `trove_ledger_handle_alloc_from_range`, `trove_ledger_peek_handles`, and `trove_ledger_peek_handles_from_extent` delegate allocation and preview to the free list. `trove_ledger_handle_free` places returned handles into recently-freed or overflow lists and triggers `handle_recycle` when the free list falls below cutoff and purgatory has expired. `trove_handle_ledger_addextent`, `trove_handle_remove`, `trove_handle_ledger_set_threshold`, `trove_ledger_set_timeout`, `trove_handle_ledger_get_statistics`, and `trove_handle_ledger_show` support range setup, reservation, tuning, and diagnostics.

Control flow: Initialization currently builds empty in-memory extent lists; historical on-disk load/create code is disabled. Allocation consumes only `free_list`. Freeing a handle first checks whether the recently-freed list has crossed the cutoff; if so the handle goes to `overflow_list`, otherwise it goes to `recently_freed_list`. When free handles are low, `extentlist_endured_purgatory(recently_freed, overflow)` determines whether to merge recently-freed handles back into free space, promote overflow to recently-freed, and reset overflow.

State and persistence: `struct handle_ledger` is file-private and stores list state, optional backing-store names/handles, and a `cutoff`. `trove_handle_ledger_dump` returns `-1`; the attempted bstream-backed persistence implementation remains under `#if 0`, so live state is volatile and reconstructed from configured ranges plus existing dataspaces.

Dependencies and integration points: Uses `trove-extentlist`, Trove types, `gossip`, and the higher-level handle manager. Disabled code shows intended integration with Trove bstreams and collection lookup.

Risks: Initialization leaks partially initialized ledgers if a later `extentlist_init` fails. `trove_ledger_handle_free` does not null-check `hl`. `handle_recycle` shallow-copies `overflow_list` into `recently_freed_list`, then zeroes overflow; this relies on extent-list ownership details. The delayed-reuse timestamp comparison is hard to reason about and should be verified. Statistics are only as reliable as extent-list counts/traversals. Persistence is unimplemented despite ledger fields suggesting it exists.

Test signals: Test initialization failure cleanup, allocation from empty and populated ledgers, free-list/recent/overflow transitions around cutoff, timeout zero/default behavior through the higher layer, recycle after elapsed purgatory, statistics across all three lists, and ledger show/debug output on fragmented extents.
