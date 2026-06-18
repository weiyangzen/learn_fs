# sources/distributed-fs/ceph-client/io_uring/slist.h

Purpose: provides minimal singly-linked list helpers for io_uring work queues.

Important APIs/types/functions: macros and inlines include `__wq_list_for_each`, `wq_list_for_each`, `wq_list_empty()`, `INIT_WQ_LIST()`, `wq_list_add_after()`, `wq_list_add_tail()`, `wq_list_cut()`, `wq_stack_add_head()`, `wq_list_del()`, `wq_stack_extract()`, and `wq_next_work()`.

Control flow: helpers maintain `first` and `last` pointers for queue lists, plus stack-style operations using `node->next`. `wq_list_empty()` uses `READ_ONCE()` for concurrent visibility.

State and persistence: manipulates in-memory `io_wq_work_node`/`io_wq_work_list` links only. No persistence.

Dependencies/integration: depends on `io_uring_types.h` work-node definitions and is used by io-wq/completion batching code.

Risks/test signals: misuse can corrupt queue ordering or leave `last` stale. Tests are indirect through io-wq scheduling, cancellation, and completion batching under KASAN/lockdep.
