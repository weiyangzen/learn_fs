<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_timer.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_timer.h

## Purpose
Declares guest timer and per-vCPU timer state, register accessors, synchronization, and pending-event helpers.

## Important APIs, Types, And Functions
types `kvm_guest_timer`, `kvm_vcpu_timer`, `hrtimer`, `kvm_vcpu`, `kvm_one_reg`, `kvm`; functions/prototypes `kvm_riscv_vcpu_timer_next_event`, `kvm_riscv_vcpu_get_reg_timer`, `kvm_riscv_vcpu_set_reg_timer`, `kvm_riscv_vcpu_timer_init`, `kvm_riscv_vcpu_timer_deinit`, `kvm_riscv_vcpu_timer_reset`, `kvm_riscv_vcpu_timer_restore`, `kvm_riscv_guest_timer_init`, `kvm_riscv_vcpu_timer_sync`, `kvm_riscv_vcpu_timer_save`, `kvm_riscv_vcpu_timer_pending`; macros/constants `__KVM_VCPU_RISCV_TIMER_H`.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
Direct includes are `linux/hrtimer.h`. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 52 lines, 1595 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_timer.h -->
