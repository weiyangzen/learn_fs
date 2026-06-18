# File Research: sources/block-storage/kvdo/vdo/uds-threads.c

This file implements UDS kernel thread wrappers, once-only initialization, barriers, and scheduler yielding. A static hlist tracks live UDS kernel threads so `uds_thread_exit()` can complete the correct completion object.

Thread lifecycle:
- `uds_create_thread()` allocates `struct thread`, starts a `kthread_run()` wrapper, and derives thread names with colon-prefix inheritance from the current thread name.
- `thread_starter()` records the task, registers allocation tracking, invokes the caller thread function, unregisters, and completes `thread_done`.
- `uds_join_threads()` waits interruptibly until completion, removes the thread from the live hlist, and frees it.
- `uds_thread_exit()` locates the current thread, unregisters allocation tracking, and exits with the appropriate kernel API depending on `module_put_and_kthread_exit`.

Synchronization:
- `perform_once()` uses atomic compare/exchange states `NOT_DONE`, `IN_PROGRESS`, and `COMPLETE`, yielding while another thread initializes.
- `uds_initialize_barrier()`, `uds_enter_barrier()`, and destroy implement a reusable semaphore-based rendezvous; exactly one arriving thread is flagged as winner/last.
- `uds_get_thread_id()`, `uds_get_num_cores()`, and `uds_yield_scheduler()` wrap kernel primitives.
