<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/Kconfig -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/Kconfig

Purpose: Defines RISC-V KVM configuration menu entries and dependencies.

Important APIs/types/functions: Sources generic `virt/kvm/Kconfig`, declares `VIRTUALIZATION`, and config `KVM` with dependencies on MMU, OF/ACPI interrupt controllers, SBI, H extension support, and standard KVM selects.

Control flow: Kconfig dependency resolution controls whether RISC-V KVM can be enabled and which support libraries are selected.

State and persistence: Build-time configuration only.

Dependencies and integration points: Connects RISC-V virtualization to generic KVM, perf, irqchip, SBI, AIA/IMSIC, and architecture hypervisor support.

Risks: Incomplete dependencies produce build failures or runtime KVM without required interrupt/timer/hypervisor features.

Test signals: `allyesconfig`/`allmodconfig`, KVM enabled/disabled configs, guest boot under SBI/H extension, and KVM selftests.

Source read size: 40 lines, 965 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/Kconfig -->
