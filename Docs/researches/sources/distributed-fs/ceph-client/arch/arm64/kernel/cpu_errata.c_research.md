<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/cpu_errata.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/cpu_errata.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/cpu_errata.c` describes arm64 CPU errata detection and mitigation capabilities across vendor MIDR ranges, feature traps, speculative execution workarounds, PMU/TRBE/TLBI issues, SME workarounds, and implementation-defined target overrides. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `CAP_MIDR_RANGE`, `CAP_MIDR_ALL_VERSIONS`, `MIDR_FIXED`, `ERRATA_MIDR_RANGE`, `CAP_MIDR_RANGE_LIST`, `ERRATA_MIDR_REV_RANGE`, `ERRATA_MIDR_REV`, `ERRATA_MIDR_ALL_VERSIONS`, `ERRATA_MIDR_RANGE_LIST`; types: `target_impl_cpu`, `midr_range`, `arm64_cpu_capabilities`, `arm64_midr_revidr`; functions/prototypes/exports: `cpu_errata_set_target_impl`, `is_midr_in_range`, `is_midr_in_range_list`, `__is_affected_midr_range`, `is_affected_midr_range`, `is_affected_midr_range_list`, `is_kryo_midr`, `has_mismatched_cache_type`, `early_arm_si_l1_workaround_4311569_cfg`, `need_arm_si_l1_workaround_4311569`, `cpu_enable_trap_ctr_access`, `has_cortex_a76_erratum_1463225`, `cpu_enable_cache_maint_trap`, `needs_tx2_tvm_workaround`, `has_neoverse_n1_erratum_1542419`, `has_impdef_pmuv3`, `cpu_enable_impdef_pmuv3_traps`, `has_sme_dvmsync_erratum`, `cpu_enable_sme_dvmsync`. The file is 973 lines / 27462 bytes. Direct includes are `linux/arm-smccc.h`, `linux/types.h`, `linux/cpu.h`, `asm/cpu.h`, `asm/cputype.h`, `asm/cpufeature.h`, `asm/fpsimd.h`, `asm/kvm_asm.h`, `asm/smp_plat.h`.

### Control Flow
Capability matching compares current CPU MIDR values against ranges/lists, optional SMCCC/firmware state, and config gates; enable callbacks install traps, static keys, or system-register settings when a workaround applies.

### State, Persistence, And Dependencies
Notable global/static state symbols are `target_impl_cpu_num`, `cpu_errata_set_target_impl`, `i`, `is_midr_in_range_list`, `__maybe_unused`, `midr`, `scope`, `model`, `has_mismatched_cache_type`, `mask`, `sys`, `ctr_raw`, `__init`, `need_arm_si_l1_workaround_4311569`, `enable_uct_trap`, `has_cortex_a76_erratum_1463225`, `has_dic`, `range`, and 25 more. Target-implementation override pointers, static keys, and final CPU capability bits persist after boot and CPU hotplug. Some mitigations change per-CPU system registers. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Incorrect MIDR ranges or missing enable callbacks can leave affected CPUs vulnerable or impose unnecessary traps/performance costs on unaffected systems.

### Test Signals
Build with errata configs, boot affected and unaffected CPU models, inspect mitigation logs/capability bits, run KVM/perf/TRBE/TLBI/SME tests, and validate CPU hotplug reapplication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/cpu_errata.c -->
