# sources/distributed-fs/orangefs/src/io/flow/flow-ref.c

Purpose: maintains a linked list mapping source/destination endpoint type pairs to a flow protocol id.

Important APIs/functions: `flow_ref_new()` allocates a list head; `flow_ref_add()` allocates and appends a `flow_ref_entry`; `flow_ref_search()` scans for matching source and destination endpoints; `flow_ref_remove()` unlinks an entry; `flow_ref_cleanup()` frees entries and the head.

Control flow/state: all mappings are in heap entries linked by `quicklist`. Search precomputes `tmp_next_link` and advances through the circular list.

Dependencies/integration: used by `flow.c` initialization as `flow_mapping`, though the current `PINT_flow_post()` selects protocols by `FLOWPROTO_TYPE_QUERY` rather than endpoint mapping. This may be legacy support.

Risks/test signals: `flow_ref_remove()` unlinks but does not free the entry, so callers must free or cleanup later. `flow_ref_cleanup()` frees entries without explicit `qlist_del()`, acceptable before freeing head but fragile if extended. Tests should cover duplicate mappings, not-found search, cleanup after removals, and endpoint-pair lookup if endpoint-based routing is restored.
