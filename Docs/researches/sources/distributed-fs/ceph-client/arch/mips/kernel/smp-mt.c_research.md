## sources/distributed-fs/ceph-client/arch/mips/kernel/smp-mt.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/smp-mt.c` implements virtual SMP over MIPS MT VPEs and TCs. It configures thread contexts, maps each VPE to a logical CPU, and boots secondary VPEs by programming TC restart, stack, GP, status, and VPE activation registers.

### Important APIs, Types, And Functions
Key functions are `smvp_copy_vpe_config()`, `smvp_vpe_init()`, `smvp_tc_init()`, `vsmp_init_secondary()`, `vsmp_smp_finish()`, `vsmp_boot_secondary()`, `vsmp_smp_setup()`, and `vsmp_prepare_cpus()`. The exported platform operations object is `vsmp_smp_ops`.

### Control Flow
Setup disables VPEs and MT, enters MVP configuration state, reads `MVPConf0`, derives TC and VPE counts, sets `smp_num_siblings`, initializes each TC as halted/non-allocatable, deactivates nonboot VPEs, copies CP0 status/config/count/config7 to secondary VPEs, and records CPU maps. Booting a secondary disables VPE scheduling, selects the target TC, writes `smp_bootstrap` as restart PC, marks the TC active, unhalts it, enables the VPE, writes stack and GP, flushes the thread_info cache range, exits configuration state, and re-enables VPE execution.

### State, Persistence, And Dependencies
State is in MIPS MT CP0/VPE/TC registers, `cpu_data` VPE IDs, `__cpu_number_map`, `__cpu_logical_map`, `smp_num_siblings`, and optional `mt_fpu_cpumask`. Dependencies include `asm/mipsmtregs.h`, `asm/mips_mt.h`, generic MIPS IPI functions, GIC presence, FPU affinity support, and generic SMP startup.

### Integration Points
`vsmp_smp_ops` is registered by platform code and then consumed by generic `smp.c`. It uses `mips_mt_set_cpuoptions()` for MT user-accessible behavior, generic IPI senders for reschedule/call-function interrupts, and `start_secondary()` after `smp_bootstrap`.

### Risks
Programming MT configuration registers while interrupts or VPE scheduling are active can hang the system. CPU-to-TC/VPE one-to-one assumptions must match hardware. `smp_max_threads` limiting must not leave maps inconsistent. FPU affinity masks need correct enrollment for systems with fewer FPU contexts than VPEs.

### Test Signals
Test MT-capable Malta or similar systems with varying `smt=` and `nosmt`, secondary VPE boot, call-function IPIs, timer/performance interrupt masks with and without GIC, and workloads that trigger FPU affinity migration.
