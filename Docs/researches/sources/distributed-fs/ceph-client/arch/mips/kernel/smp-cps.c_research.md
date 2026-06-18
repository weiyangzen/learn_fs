## sources/distributed-fs/ceph-client/arch/mips/kernel/smp-cps.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/smp-cps.c` implements SMP support for MIPS Coherent Processing System machines. It discovers cluster/core/VPE topology, allocates and installs reset vectors, boots cores and VPEs through CM/CPC/GIC hardware, maintains per-cluster boot configuration, and supports hotplug and kexec shutdown.

### Important APIs, Types, And Functions
Important state includes `core_entry_reg`, `cps_vec_pa`, and `mips_cps_cluster_bootcfg`. Setup functions include `power_up_other_cluster()`, `core_vpe_count()`, `mips_cps_build_core_entry()`, `check_64bit_reset()`, `allocate_cps_vecs()`, `setup_cps_vecs()`, `cps_smp_setup()`, and `cps_prepare_cpus()`. Boot and runtime functions include `init_cluster_l2()`, `boot_core()`, `remote_vpe_boot()`, `cps_boot_secondary()`, `cps_init_secondary()`, and `cps_smp_finish()`. Hotplug/kexec functions include `cps_cpu_disable()`, `play_dead()`, `wait_for_sibling_halt()`, `cps_cleanup_dead_cpu()`, and `cps_kexec_nonboot_cpu()`. Registration is via `register_cps_smp_ops()` and `mips_cps_smp_in_use()`.

### Control Flow
Early setup reads CPS topology, powers up clusters when needed, records cluster/core/VPE IDs into `cpu_data`, sets coherent CCA, initializes core 0, allocates BEV reset vectors, and writes BEV base on CM3+ systems. Preparation validates coherent CCA and dcache aliasing constraints, builds vector code and exception copies, allocates per-cluster/core/VPE boot configuration, and marks boot CPU state. Booting a CPU fills `vpe_boot_config` with `smp_bootstrap`, stack, and GP, then either resets a powered-down core, asks a sibling CPU to boot a VPE, or boots a local VPE. Hotplug subtracts the VPE from the live mask, marks the CPU offline, then either halts a VPE or power-gates the whole core; cleanup waits for the observed halt or power state.

### State, Persistence, And Dependencies
State lives in CM/CPC/GIC registers, reset vector memory allocated by memblock, `cluster_boot_config` and nested core/VPE arrays, core power bitmaps, atomic VPE masks, CPU topology fields, and the `__cpu_primary_thread_mask`. Dependencies include `asm/mips-cps.h`, `asm/pm-cps.h`, `asm/uasm.h`, `asm/mips_mt.h`, `asm/bcache.h`, GIC interrupts, memblock, hotplug, and the generic MIPS SMP ops interface.

### Integration Points
The file provides `cps_smp_ops` to `register_smp_ops()`, uses generic IPI senders from `smp.c`, consumes `smp_max_threads` and topology maps from generic SMP code, and calls CPS PM support for power gating. It must align with exception-vector handling in `traps.c` because reset vectors copy TLB/cache/general exception stubs.

### Risks
Hardware sequencing is the main risk: reset vector physical address limits, 64-bit reset base support, CM/CPC locking, VP run/stop ordering, L2 state machine initialization, and cross-cluster register mirroring must be exact. Allocation failure disables SMP by clearing present CPUs, so partial allocation cleanup must be correct. Hotplug races with re-online and sibling power-down are explicitly handled but sensitive to shared globals `cpu_death` and `cpu_death_sibling`.

### Test Signals
Use CPS systems with multiple clusters, multiple cores, multiple VPEs, CM2 versus CM3/CM3.5, CPC present and absent, GIC present checks, CCA mismatch, dcache aliasing, CPU hotplug under load, kexec, FPU affinity on MT systems, and reset vector allocation above and below KSEG1 limits.
