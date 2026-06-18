# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/s390/user_operexec.c

## Purpose
This s390x test verifies forwarding of operation exceptions to userspace for instruction zero and general user-operation-exception capabilities.

## Important APIs, Types, And Functions
It uses `KVM_CAP_S390_USER_INSTR0`, `KVM_CAP_S390_USER_OPEREXEC`, `__vm_enable_cap()`, and SIE intercept checking through `KVM_EXIT_S390_SIEIC`, `ICPT_OPEREXC`, and `ipa`. Guest snippets are raw `.word 0x0000` and `.word 0x0807`.

## Control Flow
`test_user_instr0()` enables `USER_INSTR0` after vCPU creation and expects instruction 0 to exit with operation exception and IPA 0. `test_user_operexec()` enables `USER_OPEREXEC`, checks `.word 0x0807`, then confirms the superset also forwards instruction 0. `test_user_operexec_combined()` enables both capabilities in both orders and verifies the general operation exception still exits with IPA `0x0807`. `main()` requires `USER_INSTR0`, runs all three tests, and prints pass results.

## State, Dependencies, And Integration
State is limited to per-VM capability enablement and vCPU exit state. It depends on s390 KVM user operation-exception capabilities and instruction interception.

## Risks And Test Signals
Risks include capability-order bugs, enabling-after-vCPU regressions, or IPA corruption. Signals are exact enablement success, exit reason, intercept code, and IPA assertions for all capability combinations.
