## sources/distributed-fs/ceph-client/arch/arm64/kernel/cpufeature.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/cpufeature.c` is the ARM64 CPU feature
sanitization and capability engine. It records boot and secondary CPU ID register values, derives
system-wide safe feature values, advertises ELF HWCAPs to user space, enables internal CPU
capabilities, applies alternative patching, and rejects or taints CPUs whose feature set conflicts
with the finalized system view. In this imported Ceph client kernel tree it is not Ceph protocol
logic, but it is a platform contract for every filesystem, networking, page-cache, crypto, and MM
path that depends on ARM64 instruction, cache, memory-tagging, virtualization, tracing, and security
features.

### Important APIs, Types, And Functions
Key global state includes `system_cpucaps`, `boot_cpucaps`, `elf_hwcap`, `cpucap_ptrs`,
`arm64_ftr_reg_ctrel0`, the `arm64_ftr_override` instances for boot-time ID overrides, per-CPU
`this_cpu_vector`, and the optional `cpu_32bit_el0_mask`. The main table types are
`struct arm64_ftr_bits`, `struct arm64_ftr_reg`, and `struct arm64_cpu_capabilities`.

The feature-register path is built from the `ftr_*` arrays, `arm64_ftr_regs`,
`sort_ftr_regs()`, `get_arm64_ftr_reg()`, `arm64_ftr_safe_value()`, `init_cpu_ftr_reg()`,
`update_cpu_ftr_reg()`, `check_update_ftr_reg()`, `read_sanitised_ftr_reg()`, and
`__read_sysreg_by_encoding()`. The capability path centers on `arm64_features`,
`arm64_elf_hwcaps`, `compat_elf_hwcaps`, `init_cpucap_indirect_list()`,
`update_cpu_capabilities()`, `enable_cpu_capabilities()`, `verify_local_cpu_caps()`,
`check_local_cpu_capabilities()`, `setup_boot_cpu_features()`, `setup_system_features()`, and
`setup_user_features()`. User-visible emulation and reporting are handled by `do_emulate_mrs()`,
`try_emulate_mrs()`, `cpu_get_elf_hwcap*()`, `cpu_show_meltdown()`, and 32-bit EL0 sysfs support.

### Control Flow
Boot starts with CPU register snapshots from `cpuinfo.c`. `init_cpu_features()` sorts and validates
the feature-register table, initializes sanitized values from the boot CPU, applies valid override
masks, initializes SVE/SME vector length maps when available, and records optional MPAM/MTE metadata.
`setup_boot_cpu_features()` builds the indirect cpucap lookup array, checks pseudo-NMI firmware
constraints, detects boot and local capabilities, enables boot-scope CPU controls, and applies boot
alternatives.

As secondary CPUs start, `update_cpu_features()` compares their raw ID registers against the boot
CPU and folds mismatches into the safe system value according to each field's policy
(`FTR_EXACT`, `FTR_LOWER_SAFE`, `FTR_HIGHER_SAFE`, or `FTR_HIGHER_OR_ZERO_SAFE`). Strict mismatches
warn and taint the kernel with `TAINT_CPU_OUT_OF_SPEC`. Before system finalization,
`check_local_cpu_capabilities()` updates local feature/erratum capabilities; after finalization it
verifies that new CPUs match all advertised capabilities and parks or panics CPUs on conflicts.

System finalization calls `setup_system_features()`: it detects system-scope capabilities from the
sanitized ID registers, uses `stop_machine()` for non-boot CPU enable callbacks that may need real
PSTATE changes, applies alternatives globally, installs KPTI/non-global mapping effects, and runs
SVE/SME setup. `setup_user_features()` masks user-visible ID fields for errata, constructs HWCAP
bitmaps, fixes compat HWCAPs, and updates minimum signal stack sizing.

### State, Persistence, And Dependencies
All persistent state is in kernel memory: bitmap capabilities, per-CPU vectors, per-CPU or global
cpumasks for weak local features, sanitized feature-register values, static branches, sysfs
attributes, and exported HWCAP values. There is no filesystem persistence beyond sysfs/procfs
presentation. Boot parameters such as `kpti=`, `allow_mismatched_32bit_el0`, and
`irqchip.gicv3_pseudo_nmi=` mutate early policy state.

Dependencies are broad: CPU ID accessors and sysreg encodings, `asm/cpufeature.h`,
`asm/hwcap.h`, `asm/fpsimd.h`, `asm/mte.h`, KVM/hypervisor hooks, MPAM state, GICv3/GICv5
register access, Spectre/KPTI mitigation code, alternative patching, CPU hotplug, sysfs, percpu,
stop-machine, KASLR and mitigation policy, and compat AArch32 support.

### Integration Points
This file feeds `cpuinfo.c`, exception entry vectors, KVM, ptrace/sysreg emulation, ELF auxv,
`/proc/cpuinfo`, CPU hotplug, alternatives, Spectre/Meltdown reporting, SVE/SME/FPSIMD setup, MTE,
MPAM, GIC priority masking, and KPTI vector selection. Ceph client code depends on these decisions
indirectly through atomics, crypto HWCAP dispatch, page-cache coherency, networking, DMA/cache
maintenance, memory tagging, and scheduler/hotplug stability.

### Risks
Feature table mistakes are high impact: a wrong safe value can expose unsupported instructions to
user space, hide available CPU features, or permit unsafe heterogeneous CPU combinations. Missing
strictness can allow late CPU corruption; excessive strictness can prevent hotplug on valid systems.
Capability ordering matters because some entries depend on earlier caps. Override handling can
force unsafe values only if validation is wrong. KPTI, PAN, BTI, MTE, pointer authentication, GIC
priority masking, and KVM feature decisions all have security consequences. Several paths are
configuration-specific and hardware-specific, making coverage gaps likely.

### Test Signals
Useful signals are ARM64 defconfig and randconfig builds, boot on heterogeneous big.LITTLE systems,
CPU hotplug stress, KVM selftests, SVE/SME vector-length tests, MTE tests, ptrace/MRS emulation
tests, `/proc/cpuinfo` and auxv HWCAP checks, sysfs CPU register reads, Spectre/Meltdown mitigation
reporting, kdump boots, pseudo-NMI configurations, and targeted boot-parameter tests for KPTI,
feature overrides, and mismatched 32-bit EL0.
