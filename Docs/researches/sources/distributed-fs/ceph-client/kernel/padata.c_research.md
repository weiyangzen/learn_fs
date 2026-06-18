<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/padata.c -->
# sources/distributed-fs/ceph-client/kernel/padata.c

Purpose: Implements padata, a generic facility for parallel processing with ordered serialization callbacks, plus an init-time multithreaded job runner used to split large boot-time work across CPUs.

Important APIs/types/functions: exported APIs include `padata_do_parallel()`, `padata_do_serial()`, `padata_do_multithreaded()`, `padata_set_cpumask()`, `padata_alloc()`, `padata_free()`, `padata_alloc_shell()`, `padata_free_shell()`, and `padata_init()`. Key types are `struct padata_instance`, `struct padata_shell`, `struct parallel_data`, `struct padata_priv`, `struct padata_work`, and `struct padata_mt_job_state`.

Control flow: `padata_do_parallel()` validates instance flags and callback CPU under RCU-bh, takes a `parallel_data` ref, assigns a sequence number under the global work lock, allocates a bounded work item, and either queues parallel work or runs it inline if the work pool is exhausted. Parallel callbacks must later call `padata_do_serial()`, which inserts completed objects into a per-CPU reorder list unless it is the next expected sequence. `padata_reorder()` advances sequence order and queues serial callbacks on the selected callback CPU's serial workqueue. Serial workers drain local lists and drop `parallel_data` references in batches. Multithreaded init jobs allocate helper work items, compute aligned chunks, queue helpers across nodes if requested, and let the caller's thread participate.

State and persistence: `parallel_data` contains per-cpu reorder and serial queues, cpumasks, sequence counters, processed cursor, and a refcount. Instances own parallel/serial workqueues, cpumasks, flags (`PADATA_INIT`, `PADATA_RESET`, `PADATA_INVALID`), a shell list, kobject sysfs state, and optional CPU hotplug node. A global fixed-size `padata_works` pool bounds outstanding queued work.

Dependencies/integration: Integrates with workqueues, CPU masks, RCU-bh, CPU hotplug callbacks, sysfs kobjects, cpus read lock, mutexes/spinlocks, and kernel init jobs. Sysfs exposes `serial_cpumask` and `parallel_cpumask`.

Risks: Every object accepted by `padata_do_parallel()` must eventually call `padata_do_serial()` or the `parallel_data` refcount and ordering stream stall. Sequence wrap handling depends on CPU hash/cursor consistency. Cpumask changes replace `parallel_data` under RCU while old work may still reference it. CPU hotplug can mark an instance invalid and stop it. The fixed work pool forces inline execution under load, so callers must tolerate synchronous parallel callbacks.

Test signals: ordered serialization under out-of-order parallel completion, work-pool exhaustion inline fallback, cpumask sysfs changes, CPU online/offline replacement, invalid empty masks, shell allocation/free while work is outstanding, sequence wrap behavior, multithreaded chunk alignment and NUMA-aware dispatch, and sanitizer/lockdep coverage for refcount and lock ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/padata.c -->
