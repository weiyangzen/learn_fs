<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vmid.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vmid.h

## Purpose
Declares guest-stage VMID bit discovery, version tracking, initialization, and update helpers.

## Important APIs, Types, And Functions
types `kvm_vmid`, `kvm`, `kvm_vcpu`; functions/prototypes `kvm_riscv_gstage_vmid_bits`, `kvm_riscv_gstage_vmid_init`, `kvm_riscv_gstage_vmid_ver_changed`, `kvm_riscv_gstage_vmid_update`; macros/constants `__RISCV_KVM_VMID_H_`.

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

Source read size: 26 lines, 654 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vmid.h -->
