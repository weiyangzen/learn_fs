<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_tlb.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_tlb.h

## Purpose
Declares KVM hypervisor fence/TLB request types and local/remote guest-stage and virtual-address flush helpers.

## Important APIs, Types, And Functions
types `kvm_riscv_hfence_type`, `kvm_riscv_hfence`, `kvm_vcpu`, `kvm`; functions/prototypes `kvm_riscv_local_hfence_gvma_vmid_gpa`, `kvm_riscv_local_hfence_gvma_vmid_all`, `kvm_riscv_local_hfence_gvma_gpa`, `kvm_riscv_local_hfence_gvma_all`, `kvm_riscv_local_hfence_vvma_asid_gva`, `kvm_riscv_local_hfence_vvma_asid_all`, `kvm_riscv_local_hfence_vvma_gva`, `kvm_riscv_local_hfence_vvma_all`, `kvm_riscv_local_tlb_sanitize`, `kvm_riscv_tlb_flush_process`, `kvm_riscv_fence_i_process`, `kvm_riscv_hfence_vvma_all_process`, plus 8 more; macros/constants `__RISCV_KVM_TLB_H_`, `KVM_RISCV_VCPU_MAX_HFENCE`, `KVM_RISCV_GSTAGE_TLB_MIN_ORDER`.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
Direct includes are `linux/kvm_types.h`. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 85 lines, 2865 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_tlb.h -->
