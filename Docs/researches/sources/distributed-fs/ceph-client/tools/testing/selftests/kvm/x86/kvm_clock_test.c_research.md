# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/kvm_clock_test.c

Purpose: Tests userspace adjustment of KVM clock state via `KVM_SET_CLOCK` and guest observation through the paravirtual KVM clock MSR.

Important APIs/types/functions: `struct test_case` defines base clock and realtime offset cases; `guest_main()` enables `MSR_KVM_SYSTEM_TIME_NEW` and reports pvclock cycles; `setup_clock()` writes `struct kvm_clock_data`; `handle_sync()` compares guest-observed values with host `KVM_GET_CLOCK` ranges; `enter_guest()` runs all cases.

Control flow: For each test case, the host sets KVM clock data, captures start clock, runs the guest until a sync, captures end clock, and asserts the guest pvclock value lies between start and end. Cases include zero base, positive base offset, and positive/negative realtime offsets.

State and persistence behavior: KVM clock data is VM-wide state. Guest pvclock structure is shared guest memory enabled through the KVM system-time MSR.

Dependencies and integration points: Uses KVM clock ioctls, pvclock ABI structures, realtime clock reads, and KVM paravirtual MSRs.

Risks and maintenance notes: Clock comparisons depend on monotonic ordering around `KVM_RUN`; excessive scheduling delays widen but should not invalidate the range. Flag expectations require `KVM_CLOCK_REALTIME` and `KVM_CLOCK_HOST_TSC`.

Test signals: Passing means userspace-set KVM clock state is reflected to the guest pvclock page and `KVM_GET_CLOCK` flags are correct. Failures implicate clock offset, realtime, or pvclock update regressions.
