# sources/distributed-fs/ceph-client/tools/testing/radix-tree/regression1.c

Purpose: reproduces a historical radix-tree RCU lookup deadlock where a reader loops on a stale slot after tree contraction and deletion of the zero-index item.

Important APIs/types/functions: defines a local `struct page` with mutex, RCU head, refcount, and index; `page_alloc()`, `page_free()`, and `page_rcu_free()` model page lifecycle; `find_get_pages()` mimics page-cache lookup using `XA_STATE`, `xas_for_each()`, `xas_retry()`, `xas_reload()`, and `xas_reset()`; `regression1_fn()` drives reader/writer threads; `regression1_test()` starts and joins them.

Control flow: two threads synchronize on a barrier. The serial thread repeatedly inserts pages at indexes 0 and 1, deletes index 1 causing contraction, then deletes index 0 and queues both pages for RCU freeing. The other thread repeatedly calls `find_get_pages()` under RCU, retrying when the page moved or has zero count. Completion without hanging is the expected signal.

State and persistence: uses static `RADIX_TREE(mt_tree, GFP_KERNEL)`, a pthread barrier, and a heap thread array. Page objects are heap allocated and released after RCU grace periods; no persistent output.

Dependencies/integration: uses Linux radix-tree/XArray APIs, pthreads, userspace RCU shims, and `printv()` from the harness. It is invoked via `regression1_test()`.

Risks and test signals: the test can be long due to 1,000,000 writer loops and 100,000,000 reader loops. It is intentionally race-sensitive; hang indicates the regression, while normal completion plus RCU cleanup indicates pass.
