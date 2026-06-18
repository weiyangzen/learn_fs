# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/s390/resets.c

## Purpose
This s390x test verifies normal, initial, and clear vCPU reset semantics: which CPU registers and pending interrupts are cleared, initialized, or preserved.

## Important APIs, Types, And Functions
It uses `KVM_S390_NORMAL_RESET`, `KVM_S390_INITIAL_RESET`, `KVM_S390_CLEAR_RESET`, `KVM_S390_GET_IRQ_STATE`, `KVM_S390_SET_IRQ_STATE`, `KVM_CAP_S390_VCPU_RESETS`, and one-reg reads for `KVM_REG_S390_*` fields. Guest assembly dirties control registers, FPC, GPRs, FPRs, access registers, and exits via `diag 0x501`.

## Control Flow
Each reset test creates a VM with a nonzero vCPU ID, runs guest dirtying code, injects an emergency IRQ, performs the reset ioctl, and checks expected post-reset state. `assert_normal()` checks IRQ and pfault-token clearing. `assert_initial()` checks CR, PSW, timer, prefix-related values, FPC, and one-reg initial state. `assert_clear()` additionally verifies GPR, ACR, FPR, and vector register zeroing. Tests that need `KVM_CAP_S390_VCPU_RESETS` are skipped if unavailable.

## State, Dependencies, And Integration
State includes `buf` for IRQ state exchange, zero-reference storage, the vCPU sync-reg area, and guest-dirtied architectural state. There is no persistent state. Integration points are s390 reset ioctls, sync regs, interrupt state ioctls, and one-reg ABI.

## Risks And Test Signals
Risks are partial reset regressions that clear too much or too little, especially sync-reg discrepancies versus ioctl getters. Signals are exact field assertions for each reset class and kselftest pass/skip lines for initial, normal, and clear reset.
