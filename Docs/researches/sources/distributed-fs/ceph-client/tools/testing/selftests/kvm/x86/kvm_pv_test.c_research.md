# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/kvm_pv_test.c

Purpose: Tests KVM paravirtual MSR and hypercall behavior, including feature disablement and PV unhalt behavior.

Important APIs/types/functions: `struct msr_data` and `struct hcall_data` define KVM PV MSRs and hypercalls; `test_msr()` and `test_hcall()` run guest-side access attempts; `guest_main()` executes the matrix; `enter_guest()` handles ucalls; `test_pv_unhalt()` tests paravirtual halt/wakeup behavior. It uses KVM paravirt constants such as `KVM_FEATURE_PV_UNHALT`, `KVM_HC_KICK_CPU`, and `KVM_HC_SCHED_YIELD`.

Control flow: The guest iterates supported PV MSRs and hypercalls, reporting progress through special ucalls. The host validates guest assertions and logs names. The PV unhalt section creates vCPU conditions that should be woken by KVM's PV halt mechanism.

State and persistence behavior: PV MSR values and feature exposure are vCPU state. Hypercall effects are transient. No external persistence exists.

Dependencies and integration points: Depends on KVM paravirtual CPUID leaves, KVM-specific MSRs, hypercall instruction handling, and APIC/vCPU wakeup paths.

Risks and maintenance notes: PV feature behavior is ABI-sensitive for Linux guests. The test matrix must evolve with new KVM PV MSRs/hypercalls. Wakeup timing can be scheduler-sensitive.

Test signals: Passing means PV MSRs/hypercalls are accessible and fault as expected under the exposed feature set, and PV unhalt wakeup behavior works. Failures point to KVM paravirt ABI regressions.
