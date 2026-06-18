<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_vector.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_vector.h

## Purpose
Declares guest and host vector context allocation, save/restore, and vector register get/set helpers.

## Important APIs, Types, And Functions
types `kvm_cpu_context`, `kvm_vcpu`, `kvm_one_reg`; functions/prototypes `__kvm_riscv_vector_save`, `__kvm_riscv_vector_restore`, `kvm_riscv_vcpu_vector_reset`, `kvm_riscv_vcpu_guest_vector_save`, `kvm_riscv_vcpu_guest_vector_restore`, `kvm_riscv_vcpu_host_vector_save`, `kvm_riscv_vcpu_host_vector_restore`, `kvm_riscv_vcpu_alloc_vector_context`, `kvm_riscv_vcpu_free_vector_context`, `kvm_riscv_vcpu_get_reg_vector`, `kvm_riscv_vcpu_set_reg_vector`; macros/constants `__KVM_VCPU_RISCV_VECTOR_H`.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
Direct includes are `linux/types.h`, `asm/vector.h`, `asm/kvm_host.h`. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 78 lines, 2098 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_vector.h -->
