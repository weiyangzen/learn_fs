<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_host.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_host.h

## Purpose
Defines the core RISC-V KVM VM and vCPU architecture state, request numbers, trap context, CSR state, interrupt bitmaps, and vCPU lifecycle APIs.

## Important APIs, Types, And Functions
types `kvm_vm_stat`, `kvm_vm_stat_generic`, `kvm_vcpu_stat`, `kvm_vcpu_stat_generic`, `kvm_arch_memory_slot`, `kvm_arch`, `kvm_vmid`, `kvm_guest_timer`, `kvm_aia`, `kvm_cpu_trap`, plus 22 more; functions/prototypes `kvm_arch_pmi_in_guest`, `kvm_arch_vcpu_blocking`, `kvm_arch_vcpu_unblocking`, `kvm_riscv_setup_default_irq_routing`, `__kvm_riscv_unpriv_trap`, `kvm_riscv_vcpu_unpriv_read`, `kvm_riscv_vcpu_trap_redirect`, `kvm_riscv_vcpu_exit`, `__kvm_riscv_switch_to`, `kvm_riscv_vcpu_setup_isa`, `kvm_riscv_vcpu_num_regs`, `kvm_riscv_vcpu_copy_reg_indices`, plus 13 more; macros/constants `__RISCV_KVM_HOST_H__`, `KVM_MAX_VCPUS`, `KVM_HALT_POLL_NS_DEFAULT`, `KVM_VCPU_MAX_FEATURES`, `KVM_IRQCHIP_NUM_PINS`, `KVM_REQ_SLEEP`, `KVM_REQ_VCPU_RESET`, `KVM_REQ_UPDATE_HGATP`, `KVM_REQ_FENCE_I`, `KVM_REQ_HFENCE_VVMA_ALL`, `KVM_REQ_HFENCE`, `KVM_REQ_STEAL_UPDATE`, `__KVM_HAVE_ARCH_FLUSH_REMOTE_TLBS_RANGE`, `KVM_DIRTY_LOG_MANUAL_CAPS`, plus 1 more.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself. Special attention: `struct kvm_vcpu_arch` is the aggregation point for guest context, host context, CSR state, reset state, pending interrupt bitmaps, MMIO/CSR decode data, SBI, timer, PMU, AIA, FP/vector, and memory-cache state.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
Direct includes are `linux/types.h`, `linux/kvm.h`, `linux/kvm_types.h`, `linux/spinlock.h`, `asm/hwcap.h`, `asm/kvm_aia.h`, `asm/ptrace.h`, `asm/kvm_tlb.h`, `asm/kvm_vmid.h`, `asm/kvm_vcpu_config.h`, plus 6 more. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 323 lines, 8399 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_host.h -->
