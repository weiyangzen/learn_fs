<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/virt.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/virt.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/virt.h` defines arm64 hypervisor-stub calls, boot exception-level state, and helpers for KVM/VHE/nVHE/protected-KVM mode detection. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM__VIRT_H`, `HVC_SET_VECTORS`, `HVC_SOFT_RESTART`, `HVC_RESET_VECTORS`, `HVC_FINALISE_EL2`, `HVC_GET_ICH_VTR_EL2`, `HVC_STUB_HCALL_NR`, `HVC_STUB_ERR`, `BOOT_CPU_MODE_EL1`, `BOOT_CPU_MODE_EL2`, `BOOT_CPU_FLAG_E2H`, `ARM64_VECTOR_TABLE_LEN`; functions/prototypes/exports: `is_pkvm_initialized`, `pkvm_force_reclaim_guest_page`, `is_hyp_mode_available`, `is_hyp_mode_mismatched`, `is_kernel_in_hyp_mode`, `has_vhe`, `is_protected_kvm_enabled`, `has_hvhe`, `is_hyp_nvhe`. The file is 180 lines / 4650 bytes. Direct includes are `asm/ptrace.h`, `asm/sections.h`, `asm/sysreg.h`, `asm/cpufeature.h`.

### Control Flow
Early boot records `__boot_cpu_mode`; KVM and low-level restart code use HVC stub numbers for vector setup, soft restart, EL2 finalization, and capability probes. Inline helpers branch on static keys, current EL, and final CPU capabilities.

### State, Persistence, And Dependencies
Notable global/static state symbols are `is_kvm_arm_initialised`, `pkvm_force_reclaim_guest_page`. `__boot_cpu_mode` and the protected-KVM static key are durable kernel state after boot. Helpers also read CPU system registers and final capability bitmaps. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Mixed EL boot, incorrect HVC numbers, or wrong VHE/nVHE tests can break KVM initialization, CPU restart, or protected-mode assumptions.

### Test Signals
Boot EL1 and EL2 configurations, run KVM selftests for VHE/nVHE/protected KVM, and validate CPU hotplug/restart vector reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/virt.h -->
