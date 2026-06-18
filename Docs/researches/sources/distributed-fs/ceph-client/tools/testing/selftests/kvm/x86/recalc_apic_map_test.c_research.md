<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/recalc_apic_map_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/recalc_apic_map_test.c

## Purpose
This is a race/regression test for `kvm_recalculate_apic_map()`. It tries to widen the APIC-map recalculation window with the maximum selftests vCPU count while concurrently toggling APIC state.

## Important APIs, Types, and Functions
The test uses `race()` as a pthread loop issuing `KVM_SET_LAPIC`, and `main()` creates `KVM_MAX_VCPUS`, sets `MSR_IA32_APICBASE`, and repeatedly toggles one vCPU between x2APIC enabled and LAPIC disabled. It depends on `struct kvm_lapic_state`, `vcpu_ioctl(KVM_SET_LAPIC)`, `vcpu_set_msr()`, and APIC constants from `apic.h`.

## Control Flow, State, and Persistence
All vCPUs are first put into x2APIC mode to avoid APIC-ID aliasing. A racing thread continuously sets a zeroed LAPIC state on vCPU0, which forces APIC-map recalculation. The main thread toggles the last vCPU's APIC base between enabled x2APIC and disabled for five seconds, then cancels the worker. The only state is volatile VM/vCPU APIC state.

## Dependencies and Integration Points
It integrates with LAPIC state ioctls, APIC base MSR virtualization, x2APIC mode handling, pthread cancellation, and KVM's APIC destination map internals.

## Risks and Test Signals
The test is probabilistic and may not hit a narrow race every run, but should reliably expose crashes, use-after-free, lock inversions, or invalid APIC-map handling under stress. Passing is simply completing without assertion, hang, or kernel failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/recalc_apic_map_test.c -->
