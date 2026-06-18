<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/cpu.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/cpu.c

Purpose: Detects SPARC CPU/FPU/PMU identity and exposes `/proc/cpuinfo` data.

Important APIs and control flow: `manufacturer_info` tables map PSR or V9 version implementation values to CPU/FPU/PMU names. `set_cpu_and_fpu()` selects names and logs unknown implementations. `show_cpuinfo()` prints CPU, FPU, PROM, platform type, probed/online CPU counts, optional clocks, MMU/SMP/capability data, and SPARC64 parity TL1 counters. SPARC32 `cpu_type_probe()` reads PSR/FSR with temporary FPU enablement. SPARC64 `cpu_type_probe()` either maps `sun4v_chip_type` through `sun4v_cpu_probe()` or reads `%ver` for sun4u-style systems. The probe runs as an early initcall.

State, dependencies, and risks: exported per-CPU `__cpu_data`, `ncpus_probed`, `fsr_storage`, CPU/FPU/PMU name pointers, and SPARC64 parity counters persist globally. Dependencies include PROM data, PSR/FSR or `%ver`, `tlb_type`, `sun4v_chip_type`, SMP/MMU info helpers, and seq_file. Risks include incomplete CPU tables, FPU probing side effects, unknown PMU names reducing perf integration, and proc output ABI expectations. Test signals are `/proc/cpuinfo` on SPARC32, sun4u, and sun4v, unknown CPU fallback logs, FPU version detection, and parity counter updates after Cheetah+ traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/cpu.c -->
