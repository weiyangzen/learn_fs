<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_pmu.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_pmu.c

## Purpose
`vcpu_sbi_pmu.c` implements the SBI PMU extension dispatch layer. It translates SBI calls into KVM RISC-V PMU helper operations.

## Important APIs, Types, And Functions
`kvm_sbi_ext_pmu_handler()` handles counter count/info, config-match, start, stop, firmware counter read/read-hi, snapshot shared memory, and event info. `kvm_sbi_ext_pmu_probe()` reports availability from `kvpmu->init_done`. `vcpu_sbi_ext_pmu` exports the descriptor.

## Control Flow
The handler first rejects all calls when PMU init is not done. It switches on `a6`, reconstructs 64-bit arguments from paired registers on RV32, and delegates to PMU helpers. Some perf setup failures intentionally return SBI errors to the guest without aborting KVM_RUN.

## State And Persistence
PMU state lives in `struct kvm_pmu` and perf events outside this file. This file only reads initialization state and routes requests.

## Dependencies And Integration Points
It depends on `asm/csr.h`, SBI PMU constants, and KVM PMU helpers for counters, firmware events, snapshots, and event metadata.

## Risks
RV32 argument packing is easy to break. PMU setup errors should remain guest-visible SBI failures, not userspace exits. Probe state must match actual PMU init to avoid advertising dead counters.

## Test Signals
KVM PMU selftests, guest `perf` use, RV32 high-half reads, snapshot shared-memory tests, and disabled-PMU probe tests are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_pmu.c -->
