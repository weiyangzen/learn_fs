<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/padata.h -->
# sources/distributed-fs/ceph-client/include/linux/padata.h

## Purpose
This header declares the padata parallelization framework, which runs work in parallel on selected CPUs and optionally serializes completion in sequence order. It also declares a multithreaded job interface.

## Important APIs, types, and functions
Core structs are `padata_priv` for a job, `padata_list`, `padata_serial_queue`, `padata_cpumask`, `parallel_data`, `padata_shell`, `padata_mt_job`, and `padata_instance`. Flags and CPU-mask types include `PADATA_CPU_SERIAL`, `PADATA_CPU_PARALLEL`, `PADATA_INIT`, `PADATA_RESET`, and `PADATA_INVALID`. APIs under `CONFIG_PADATA` include `padata_init()`, `padata_alloc()/free()`, shell alloc/free, `padata_do_parallel()`, `padata_do_serial()`, `padata_do_multithreaded()`, and `padata_set_cpumask()`.

## Control flow
Clients allocate an instance and shell, initialize `padata_priv` with parallel and serial callbacks, and submit through `padata_do_parallel()`. The framework assigns sequence numbers and parallel CPUs, then serializes completion on callback CPUs through reorder and serial queues before `padata_do_serial()`. Cpumasks can be changed by replacing `parallel_data` under RCU. Multithreaded jobs split a range into chunks, optionally NUMA-aware. Without `CONFIG_PADATA`, only `padata_do_multithreaded()` remains as a direct single-threaded call over the entire range.

## State and persistence
Persistent runtime state includes workqueues, per-CPU reorder/serial queues, cpumasks, sequence counters, processed counters, shell RCU pointers, kobject state, hotplug node, mutex, flags, and refcounts.

## Dependencies and integration points
It depends on refcounting, compiler/RCU annotations, workqueues, spinlocks, lists, kobjects, cpumasks, CPU hotplug, and module init. It is used by parallel crypto/IPsec and other bulk processing paths.

## Risks and test signals
Risks include sequence reorder deadlocks, cpumask replacement races, refcount leaks, CPU hotplug interactions, callback CPU invalidation, workqueue teardown ordering, and disabled-config changing parallelism semantics. Test ordered completion under out-of-order parallel work, cpumask changes while jobs run, CPU hotplug, padata instance free with in-flight jobs, multithreaded chunk alignment/min sizes, and `!CONFIG_PADATA` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/padata.h -->
