<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/tsc_msrs_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/tsc_msrs_test.c

## Purpose
This test validates interactions between `MSR_IA32_TSC`, `MSR_IA32_TSC_ADJUST`, and host-side TSC offsetting. It checks both guest and host MSR writes.

## Important APIs, Types, and Functions
Important elements are `guest_code()`, `run_vcpu()`, `rounded_rdmsr()`, `rounded_host_rdmsr()`, `vcpu_get_msr()`, and `vcpu_set_msr()`. The test uses kselftest result reporting with a five-stage plan.

## Control Flow, State, and Persistence
The guest starts from zeroed rounded TSC/TSC_ADJUST, writes TSC, writes TSC_ADJUST, observes a host-applied TSC offset, writes TSC_ADJUST again, and finally writes TSC. The host mirrors each stage, sets a host-side TSC offset through `MSR_IA32_TSC`, verifies host writes to TSC_ADJUST do not modify TSC, and restores expected values. Rounding masks natural TSC progression. State is vCPU TSC offset and TSC_ADJUST MSR state.

## Dependencies and Integration Points
It integrates with KVM MSR virtualization for TSC/TSC_ADJUST, guest ucall stage sequencing, and kselftest TAP-style reporting.

## Risks and Test Signals
Risks include conflating guest writes with host offset writes, corrupting TSC_ADJUST, or time drift exceeding rounding tolerance. Signals are exact rounded MSR equality at each stage and five kselftest passes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/tsc_msrs_test.c -->
