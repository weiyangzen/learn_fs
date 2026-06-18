<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cpu-info.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cpu-info.h

**Purpose:** Defines the runtime CPU descriptor structures and helpers for MIPS.

**Important APIs/types/functions:** `struct cache_desc`, `struct guest_info`, and `struct cpuinfo_mips` hold ASID, features, FPU/MSA IDs, CPU type, TLB/cache descriptors, package/global topology, watch registers, write-combine CCA, HTW state, guest capabilities, and optional Loongson CPUCFG data. Helpers include `cpu_cluster`, `cpu_core`, `cpu_vpe_id`, `cpus_are_siblings`, `cpu_asid_inc`, `cpu_asid_mask`, and notifier registration.

**Control flow:** CPU probe populates `cpu_data[]`; feature macros and proc code read it. Topology helpers decode `globalnumber`.

**State, dependencies, integration:** `cpu_data[]`, `current_cpu_data`, `raw_current_cpu_data`, and `boot_cpu_data` are global CPU state used across architecture code.

**Risks and test signals:** Alignment and field correctness affect per-CPU cacheline sharing and all feature tests. Test CPU probe/report, proc cpuinfo notifiers, topology decoding, ASID masks, and watch register exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cpu-info.h -->
