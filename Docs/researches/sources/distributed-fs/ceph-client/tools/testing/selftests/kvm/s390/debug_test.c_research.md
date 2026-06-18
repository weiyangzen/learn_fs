# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/s390/debug_test.c

## Purpose
This s390x test validates KVM guest debugging single-step behavior across program and supervisor-call interruptions, including cases where KVM or userspace emulation handles the intercepted instruction.

## Important APIs, Types, And Functions
It uses `KVM_GUESTDBG_ENABLE | KVM_GUESTDBG_SINGLESTEP` through `vcpu_guest_debug_set()`, s390 lowcore new-PSW slots, `KVM_S390_IRQ` injection, and SIE intercept checks. Guest snippets are raw assembly for division program interruption, DIAG, ISKE, LCTL, and SVC.

## Control Flow
`test_step_int_1()` creates a VM, writes a new PSW in lowcore pointing to `int_handler`, dirties register 2, enables single-step, and runs once. `test_step_int()` expects a `KVM_EXIT_DEBUG` at the handler PSW. DIAG-specific testing first expects a `KVM_EXIT_S390_SIEIC` for DIAG, injects a program interrupt, reruns, and then expects debug at the handler. `main()` runs all five testdefs and reports each pass.

## State, Dependencies, And Integration
The test mutates guest lowcore, vCPU registers, and debug control state. There is no persistence. It depends on s390 instruction interception, lowcore layout, and selftests helpers in `sie.h`.

## Risks And Test Signals
Risks are regressions where single-step state is lost during KVM emulation, userspace DIAG handling, or CPUSTAT_KSS handling. Signals are exact exit reasons, SIE intercept codes, DIAG IPA/IPB checks, and final PSW mask/address equality with the installed handler PSW.
