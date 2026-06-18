# sources/distributed-fs/ceph-client/lib/test_workqueue.c

## Purpose

`sources/distributed-fs/ceph-client/lib/test_workqueue.c` is a stress/performance benchmark for unbound workqueues. It measures `queue_work()` throughput and enqueue latency across workqueue affinity scopes. The source was read as a complete 294-line file.

## Important APIs, Types, and Functions

Module parameters are `nr_threads` and `wq_items`. Static state includes `bench_wq`, `threads_done`, `start_comp`, and `all_done_comp`. `struct thread_ctx` carries per-thread completion, work item, latency array, CPU, and item count. Important routines are `bench_work_fn`, `bench_kthread_fn`, `cmp_u64`, `set_affn_scope`, `run_bench`, and `test_workqueue_init`. The tested scopes are `cpu`, `smt`, `cache_shard`, `cache`, `numa`, and `system`.

## Control Flow

On load, `test_workqueue_init` validates `wq_items`, allocates an unbound sysfs-visible workqueue named `bench_wq`, chooses the thread count as the module parameter or online CPU count capped to online CPUs, and calls `run_bench` once per affinity scope. Each run writes the desired scope to the workqueue sysfs `affinity_scope` file, allocates contexts/tasks/latency storage, starts kthreads bound to online CPUs, releases them with `start_comp`, waits for `all_done_comp`, flushes the workqueue, stops kthreads, merges and sorts latency samples, and logs throughput plus p50/p90/p95 enqueue latency. The module then destroys the workqueue and returns `-EAGAIN` to avoid staying loaded.

## State and Persistence Behavior

The workqueue exists only during module initialization. Per-run state is heap or kvmalloc memory and is freed before the next scope. The benchmark mutates the workqueue's sysfs affinity scope during execution but destroys the workqueue afterward.

## Dependencies and Integration Points

Direct includes cover workqueue, kthread, module parameters, completions, atomics, slab, ktime, cpumask, scheduler, sort, and fs APIs. Integration points are `alloc_workqueue` with `WQ_UNBOUND | WQ_SYSFS`, `queue_work`, `flush_workqueue`, `destroy_workqueue`, `kthread_create`, `kthread_bind`, `kthread_stop`, completions, `filp_open`, `kernel_write`, and `sort`.

## Risks and Edge Cases

The benchmark depends on `/sys/bus/workqueue/devices/bench_wq/affinity_scope` being writable from kernel context. If scope writes fail, that run returns an error but `test_workqueue_init` does not stop or propagate per-scope failures. Very large `nr_threads * wq_items` can consume significant memory for latency arrays. The measured latency is enqueue-call duration, not work completion latency.

## Test Signals

Useful signals are per-scope log lines showing items/sec and p50/p90/p95 nanosecond enqueue latencies. Expected module init return is `-EAGAIN` after benchmark completion. Errors are logged for invalid item count, workqueue allocation failure, sysfs write failure, task creation failure, or allocation failure.
