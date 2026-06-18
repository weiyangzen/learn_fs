# sources/distributed-fs/glusterfs/libglusterfs/src/async.c

Purpose: Implements GlusterFS global asynchronous worker-thread pool used when `global_threading` is enabled outside glusterd. The design minimizes queue contention with userspace-RCU wait-free queues and signal-based leader/worker coordination.

Important APIs and functions: Public APIs are `gf_async_init()`, `gf_async_fini()`, and `gf_async_adjust_threads()`, with work submission supplied by macros/types in `glusterfs/async.h`. Internal functions include signal wrappers, `gf_async_worker_create()`, `gf_async_worker_enable()`, `gf_async_leader_run()`, `gf_async_worker_run()`, `gf_async_stop_check()`, `gf_async_stop_all()`, `gf_async_join()`, `gf_async_terminate()`, and `gf_async_worker()`. Global state is `gf_async_ctrl`, static worker table `gf_async_workers`, and thread-local `gf_async_current_worker`.

Control flow: Initialization resets state, skips disabled/glusterd modes, sets max threads, initializes queues and signal masks, blocks async signals, installs safety handlers, creates spare workers, and wakes the initial leader. A leader waits for queue signals, dequeues one job, enables another worker as future leader, runs the job, then drains available work as a normal worker. Shutdown sets max threads to zero, enqueues stop propagation, synchronizes with the last worker via barrier, joins it, flushes pending signals, restores handlers, and resets state.

State and persistence: State is in-process only: worker stack, work queue, atomic packed counts for running/stopping workers, signal masks/old handlers, barrier, max-thread count, and current-worker TLS. No files are persisted.

Dependencies and integration: Depends on pthreads, POSIX signals, userspace-RCU queues/stacks, Gluster atomics, thread naming, logging/error helpers, and `glusterfs_ctx_t` command/process mode. `glusterfsd.c` initializes it from `main_start()`.

Risks: Signal-mask correctness is critical; an unblocked async signal in any thread is treated as fatal. Worker scaling relies on packed atomic counters. Shutdown intentionally processes join jobs through the same async queue, so missed stop propagation can deadlock. Static worker storage avoids early allocator issues but caps maximum concurrency.

Test signals: Needs stress tests for concurrent submission, dynamic thread adjustment, shutdown with queued work, disabled mode, signal-mask violations, and max-thread limits. In this subset there are no direct tests.
