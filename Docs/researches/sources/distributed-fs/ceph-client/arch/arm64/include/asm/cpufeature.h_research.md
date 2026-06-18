## sources/distributed-fs/ceph-client/arch/arm64/include/asm/cpufeature.h

Purpose: central arm64 CPU feature and erratum capability interface. It describes feature-register sanitization, capability detection scopes, late-CPU conflict rules, HWCAP exposure, and many high-level feature predicates.

Important APIs/types/functions: defines `enum ftr_type`, `struct arm64_ftr_bits`, `struct arm64_ftr_override`, `struct arm64_ftr_reg`, and `struct arm64_cpu_capabilities`. Exports capability scope/type flags, `system_cpucaps`, `boot_cpucaps`, `cpus_have_cap`, final-cap helpers, `read_sanitised_ftr_reg`, ID field extractors, feature setup/check routines, HWCAP getters, system support predicates for FPSIMD/SVE/SME/PAN/PAuth/MTE/BTI/GCS/LPA2/MPAM/PMU, override helpers, and feature-specific CPU probes.

Control flow: boot stores raw ID registers, computes safe system values, finalizes boot and system capabilities, patches alternatives, then validates late CPUs against finalized capability state. Helpers choose local CPU registers or sanitized system registers depending on scope.

State and persistence: global bitmaps hold detected boot/system capabilities; `arm64_ftr_reg` records sanitized and user-visible register values; override structures persist command-line or early override decisions.

Dependencies and integration: integrates alternatives, hwcap/ELF, KVM, scheduler CPU hotplug, errata, sysreg access, and userspace ABI exposure.

Risks: incorrect safe-value rules or late-CPU flags can enable features unsupported by some CPUs, hide ABI features, or miss errata workarounds. Test signals are heterogeneous CPU boot, CPU hotplug rejection paths, `/proc/cpuinfo` and auxv HWCAP checks, KVM ID register tests, alternative patch verification, and erratum-specific regression tests.
