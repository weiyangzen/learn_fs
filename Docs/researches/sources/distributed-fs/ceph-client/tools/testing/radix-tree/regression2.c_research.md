# sources/distributed-fs/ceph-client/tools/testing/radix-tree/regression2.c

Purpose: verifies that range tag copying does not leave a false root tag that can make tagged gang lookup spin forever after tree extension and deletion.

Important APIs/types/functions: defines page-cache tag aliases for `XA_MARK_0..2`, a static `RADIX_TREE(mt_tree)`, local `struct page`, `page_alloc()`, and `regression2_test()`.

Control flow: fills one radix-tree chunk, tags the last slot dirty, copies dirty-to-towrite tags over a range that excludes the dirty item, inserts a new item to extend tree height, clears the original dirty tag, deletes the original chunk, then calls `radix_tree_gang_lookup_tag_slot()` for `PAGECACHE_TAG_TOWRITE`. The lookup must return rather than loop.

State and persistence: `page_count` monotonically labels heap pages; all inserted pages are freed with `radix_tree_delete()`. No persistent state.

Dependencies/integration: uses `tag_tagged_items()` from `test.c` and radix-tree tag APIs; exported as `regression2_test()`.

Risks and test signals: any stale root/internal tag can hang the test. The comments note `start` must not be zero for the reproducer. Final `BUG_ON(!radix_tree_empty())` validates cleanup.
