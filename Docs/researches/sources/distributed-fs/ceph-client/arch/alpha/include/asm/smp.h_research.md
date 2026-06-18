<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/smp.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/smp.h

**Purpose:** Defines Alpha SMP CPU identity helpers, per-CPU `cpuinfo_alpha`, IPI hooks, and raw CPU-number access.

**Important APIs/types/functions:** `__hard_smp_processor_id`, `hard_smp_processor_id`, `raw_smp_processor_id`, `struct cpuinfo_alpha`, `cpu_data`, `smp_num_cpus`, call-function IPI hooks, and `NO_PROC_ID`.

**Control flow:** The hard CPU id comes from `PAL_whami`; scheduler and low-level code use `current_thread_info()->cpu` for raw logical CPU id. SMP builds store ASN, machine-check, profiling, and IPI counters in cacheline-aligned `cpu_data`.

**State and persistence behavior:** Persistent per-CPU runtime state includes last ASN, ASN locks, IPI counts, profiling counters, and machine-check flags.

**Dependencies and integration points:** Depends on PAL calls, cpumasks, IRQ headers, thread_info, and generic SMP call-function code.

**Risks:** The Cabrio WHAMI comment signals platform quirks. Incorrect CPU id mapping breaks per-CPU state, ASN tracking, and IPI targeting.

**Test signals:** SMP boot, CPU hotplug where supported, IPI tests, per-CPU ASN stress, and machine-check flag handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/smp.h -->
