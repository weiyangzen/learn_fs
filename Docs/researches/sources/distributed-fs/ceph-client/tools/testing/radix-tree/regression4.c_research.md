# sources/distributed-fs/ceph-client/tools/testing/radix-tree/regression4.c

Purpose: stress-tests lookup stability for an existing radix-tree entry while another thread repeatedly inserts and deletes a neighboring entry.

Important APIs/types/functions: static `worker_barrier`, `obj0`, `obj1`, and `RADIX_TREE(mt_tree)`; `reader_fn()` performs one million RCU-protected lookups of index 0; `writer_fn()` performs one million insert/delete cycles at index 1; `regression4_test()` starts both threads.

Control flow: index 0 is inserted once before the barrier. Reader and writer run concurrently; the reader aborts if `radix_tree_lookup(&mt_tree, 0)` returns anything other than `&obj0`.

State and persistence: in-memory static tree and object addresses only. The code does not delete index 0 after the test, so repeated invocations in one process may hit existing state.

Dependencies/integration: depends on pthread barriers, RCU registration, radix-tree insert/delete/lookup, and `printv()`.

Risks and test signals: abort on a wrong pointer is the main failure signal. The static tree lifetime and lack of barrier destruction are acceptable in one-shot test execution but are not reusable-test friendly.
