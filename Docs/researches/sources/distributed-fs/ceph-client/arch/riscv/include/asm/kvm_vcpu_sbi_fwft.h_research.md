<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_sbi_fwft.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_sbi_fwft.h

## Purpose
Defines KVM SBI FWFT feature configuration state.

## Important APIs, Types, And Functions
types `kvm_sbi_fwft_feature`, `kvm_sbi_fwft_config`, `kvm_sbi_fwft`; macros/constants `__KVM_VCPU_RISCV_FWFT_H`, `vcpu_to_fwft(vcpu) (&(vcpu)->arch.fwft_context)`.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
Direct includes are `asm/sbi.h`. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 34 lines, 663 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_sbi_fwft.h -->
