# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_tsc_scaling_test.c

Purpose: Verifies nested TSC scaling when L1 and L2 run with different TSC ratios. L1's apparent frequency should remain stable while L2 observes a scaled frequency.

Important APIs/types/functions: `compare_tsc_freq()` checks a 1% tolerance; `check_tsc_freq()` measures TSC delta over a host-controlled one-second sleep; `l1_svm_code()` uses `MSR_AMD64_TSC_RATIO`; `l1_vmx_code()` uses `SECONDARY_EXEC_TSC_SCALING`, `TSC_OFFSET`, and `TSC_MULTIPLIER`; `l2_guest_code()` measures L2 frequency.

Control flow: Guest code measures L1 frequency, configures nested TSC scaling for L2, launches L2, has L2 measure its scaled frequency, then measures L1 again after L2 exits. Host ucalls perform sleeps and compare reported frequencies against expected L1 and L2 values.

State and persistence behavior: TSC scaling ratio/offset is nested VMCS/VMCB state. TSC measurements are transient. No external persistence exists.

Dependencies and integration points: Requires nested VMX or SVM with TSC scaling support, host sleep timing, and KVM TSC frequency reporting.

Risks and maintenance notes: Timing tests can be flaky on heavily loaded hosts despite 1% tolerance. VMX and SVM use different ratio encodings, so both paths require independent maintenance.

Test signals: Passing means nested TSC scaling applies to L2 without leaking into L1 before or after L2 execution. Failures indicate TSC multiplier, offset, or nested scaling isolation bugs.
