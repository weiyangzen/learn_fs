<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_sbi.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_sbi.h

## Purpose
Declares KVM SBI extension dispatch, reset handling, SBI register exposure, and extension context state.

## Important APIs, Types, And Functions
types `kvm_riscv_sbi_ext_status`, `kvm_vcpu_sbi_context`, `kvm_vcpu_sbi_return`, `kvm_cpu_trap`, `kvm_vcpu_sbi_extension`, `kvm_vcpu`, `kvm_run`, `kvm_one_reg`; functions/prototypes `kvm_riscv_vcpu_sbi_forward_handler`, `kvm_riscv_vcpu_sbi_system_reset`, `kvm_riscv_vcpu_sbi_request_reset`, `kvm_riscv_vcpu_sbi_load_reset_state`, `kvm_riscv_vcpu_sbi_return`, `kvm_riscv_vcpu_reg_indices_sbi_ext`, `kvm_riscv_vcpu_set_reg_sbi_ext`, `kvm_riscv_vcpu_get_reg_sbi_ext`, `kvm_riscv_vcpu_reg_indices_sbi`, `kvm_riscv_vcpu_set_reg_sbi`, `kvm_riscv_vcpu_get_reg_sbi`, `kvm_riscv_vcpu_sbi_ecall`, plus 18 more; macros/constants `__RISCV_KVM_VCPU_SBI_H__`, `KVM_SBI_IMPID`, `KVM_SBI_VERSION_MAJOR`, `KVM_SBI_VERSION_MINOR`.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
It has no direct includes. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 117 lines, 4416 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_sbi.h -->
