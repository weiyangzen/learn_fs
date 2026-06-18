<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_aia.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_aia.h

## Purpose
Declares KVM Advanced Interrupt Architecture VM/vCPU state and IMSIC/APLIC helper interfaces.

## Important APIs, Types, And Functions
types `kvm_aia`, `kvm_vcpu_aia_csr`, `kvm_vcpu_aia`, `kvm_device_ops`, `kvm_vcpu`, `kvm`, `kvm_msi`; functions/prototypes `kvm_riscv_vcpu_aia_imsic_has_interrupt`, `kvm_riscv_vcpu_aia_imsic_load`, `kvm_riscv_vcpu_aia_imsic_put`, `kvm_riscv_vcpu_aia_imsic_release`, `kvm_riscv_vcpu_aia_imsic_update`, `kvm_riscv_vcpu_aia_imsic_rmw`, `kvm_riscv_aia_imsic_rw_attr`, `kvm_riscv_aia_imsic_has_attr`, `kvm_riscv_vcpu_aia_imsic_reset`, `kvm_riscv_vcpu_aia_imsic_inject`, `kvm_riscv_vcpu_aia_imsic_init`, `kvm_riscv_vcpu_aia_imsic_cleanup`, plus 34 more; macros/constants `__KVM_RISCV_AIA_H`, `KVM_RISCV_AIA_UNDEF_ADDR`, `kvm_riscv_aia_initialized(k) ((k)->arch.aia.initialized)`, `irqchip_in_kernel(k) ((k)->arch.aia.in_kernel)`, `kvm_riscv_aia_available()`, `KVM_RISCV_AIA_IMSIC_TOPEI`, `KVM_RISCV_VCPU_AIA_CSR_FUNCS`.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself. Special attention: AIA state bridges in-kernel irqchip mode, IMSIC guest files, APLIC attributes, MSI injection, and static-key detection of hardware support.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
Direct includes are `linux/jump_label.h`, `linux/kvm_types.h`, `asm/csr.h`. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 173 lines, 5579 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_aia.h -->
