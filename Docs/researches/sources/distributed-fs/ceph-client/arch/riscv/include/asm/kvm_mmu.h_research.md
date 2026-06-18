<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_mmu.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_mmu.h

## Purpose
Declares RISC-V KVM MMU map/ioremap/page-table allocation and HGATP update hooks.

## Important APIs, Types, And Functions
types `kvm`, `kvm_vcpu`, `kvm_memory_slot`, `kvm_gstage_mapping`; functions/prototypes `kvm_riscv_mmu_ioremap`, `kvm_riscv_mmu_iounmap`, `kvm_riscv_mmu_map`, `kvm_riscv_mmu_alloc_pgd`, `kvm_riscv_mmu_free_pgd`, `kvm_riscv_mmu_update_hgatp`; macros/constants `__RISCV_KVM_MMU_H_`.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
Direct includes are `asm/kvm_gstage.h`. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 21 lines, 721 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_mmu.h -->
