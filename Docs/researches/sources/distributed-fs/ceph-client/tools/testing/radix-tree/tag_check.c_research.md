# sources/distributed-fs/ceph-client/tools/testing/radix-tree/tag_check.c

Purpose: validates radix-tree/XArray tag semantics, including set/get/clear behavior, tag copying, tag propagation when trees grow/shrink, gang lookup for tagged entries, and leak-sensitive cleanup.

Important APIs/types/functions: `__simple_checks()` and `simple_checks()` exercise single-index tag operations; `extend_checks()` and `contract_checks()` validate propagation through height changes; `gang_check()` verifies tagged gang lookup order against a side array; `do_thrash()` mutates a million-entry model with insert/delete/tag/untag chunks; `thrash_tags()`, `leak_check()`, `__leak_check()`, `single_check()`, and `tag_check()` compose the suite.

Control flow: `tag_check()` runs single, extension, contraction, leak, simple, and randomized thrasher checks with `rcu_barrier()` and allocation count diagnostics between phases. The thrasher maintains a byte array model (`NODE_ABSENT`, `NODE_PRESENT`, `NODE_TAGGED`) and repeatedly cross-checks every modeled index plus gang lookup output.

State and persistence: all test trees are local `RADIX_TREE` instances; `thrash_state` is heap allocated and freed. The only external state is the harness `nr_allocated` counter used for leak diagnostics.

Dependencies/integration: uses helpers from `test.h`, radix-tree tag APIs, `tag_tagged_items()`, `verify_tag_consistency()`, and `item_kill_tree()`.

Risks and test signals: intentionally expensive due to full scans over `THRASH_SIZE` and nested chunk combinations. Assertions catch stale tags, missing tags, double-delete behavior, and inconsistent internal tag bitmaps; allocation logs help identify leaks.
