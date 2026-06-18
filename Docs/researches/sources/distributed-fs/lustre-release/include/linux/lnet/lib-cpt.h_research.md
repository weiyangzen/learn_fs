# sources/distributed-fs/lustre-release/include/linux/lnet/lib-cpt.h

Purpose: CPU partition table abstraction for Lustre/LNet. It maps CPUs/NUMA nodes into configurable CPU partitions and provides allocation, affinity, and iteration helpers.

Important APIs/types: under `CONFIG_SMP`, it declares `struct cfs_cpt_table *cfs_cpt_tab`, table allocation/free/print/distance APIs, CPU/node mask accessors, CPU/node-to-CPT mapping, bind functions, CPU/node set/unset operations, core include/exclude helpers, and CPU subsystem init/fini. Non-SMP builds provide inline single-partition stubs. Allocation helpers include `cfs_cpt_malloc`, `cfs_cpt_vzalloc`, `cfs_page_cpt_alloc`, and `cfs_mem_cache_cpt_alloc`. `cfs_cpt_bind_workqueue()` allocates an unbound workqueue and applies a CPT cpumask.

Control flow: modules use CPT tables to choose locality for locks, memory, workqueues, and network processing. Pattern/module parameters `cpu_npartitions` and `cpu_pattern` drive global layout outside this header.

State and persistence: runtime state is in CPT tables and module parameters; nothing persists across reboot/module unload.

Dependencies/integration: depends on Linux CPU, cpuset, topology, slab/vmalloc, NUMA node APIs, and Lustre compatibility workqueue wrappers. LNet uses it for `ln_cpt_table`, per-CPT locks, counters, and queues.

Risks and test signals: workqueue affinity must be updated under `cpus_read_lock`; allocation helpers rely on `cfs_cpt_spread_node()` returning valid NUMA nodes. Non-SMP stubs should preserve semantics. Test signals are pattern parsing, hotplug/online CPU behavior, NUMA distance output, per-CPT memory placement, and workqueue cpumask application.
