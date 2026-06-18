# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/thread-utils.c

## Purpose
`thread-utils.c` provides VDO kernel-thread creation and joining helpers with naming, allocation tracking registration, and a completion-based join path.

## Important APIs, Types, And Functions
Private `struct thread` stores the function, data, hlist link, task pointer, and done completion. `vdo_initialize_threads_mutex()` initializes global thread list locking. `vdo_create_thread()` allocates a wrapper and starts `kthread_run()`. `vdo_join_threads()` waits for completion, removes the wrapper from the global list, and frees it. `thread_starter()` is the kthread entry trampoline.

## Control Flow
Creation allocates a wrapper, derives a thread name using colon-prefix inheritance from `current->comm` when appropriate, starts the kthread, and returns the wrapper. The starter records `current`, links the wrapper under a mutex, registers the thread as an allocating thread, calls the supplied function, unregisters, completes `thread_done`, and exits. Join waits interruptibly, sleeping briefly on interruptions, then unlinks and frees.

## State And Persistence
Global state is `thread_list` plus `thread_mutex`. Per-thread state is transient and freed by join. No persistent metadata is written.

## Dependencies And Integration Points
The file depends on Linux kthreads, completions, mutexes, delays, current task state, VDO memory allocation, logging, and allocation-thread registration from the broader VDO/UDS infrastructure.

## Risks
Every successful create needs a join to free the wrapper. The global `thread_list` is maintained but not exposed here, so future users must preserve mutex discipline. Name-prefix logic depends on colon conventions. If `kthread_run()` fails, the function returns raw `PTR_ERR()` rather than a VDO status.

## Test Signals
Tests should cover create failure, naming with and without colon prefixes, function invocation with data, allocating-thread registration lifecycle, interrupted join waiting, and memory cleanup after join.
