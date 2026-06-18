<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/set_sregs_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/set_sregs_test.c

## Purpose
This regression test validates `KVM_SET_SREGS` enforcement for invalid `IA32_APIC_BASE`, unsupported CR4 bits, and illegal CR0 combinations. It also checks that CPUID-dependent CR4 state is honored even when userspace never calls `KVM_SET_CPUID2`.

## Important APIs, Types, and Functions
Key logic is in `calc_supported_cr4_feature_bits()`, `test_cr_bits()`, and the `TEST_INVALID_CR_BIT` macro. The test uses `struct kvm_sregs`, `_vcpu_sregs_set()`, `vcpu_sregs_get()`, feature probes such as `kvm_cpu_has()`, CPUID checks through `vcpu_cpuid_has()`, and control-register/APIC constants from `processor.h`.

## Control Flow, State, and Persistence
The first VM is barebones and avoids CPUID setup to verify KVM still rejects unsupported CR4 bits. The second VM has normal guest CPUID, attempts invalid and valid APIC base values, then sets all supported CR4 bits. For each unsupported CR4 bit and illegal CR0 bit combination, the test attempts `KVM_SET_SREGS`, expects failure, and verifies KVM left the original sregs unchanged. State is transient in the vCPU's special-register block and CPUID model.

## Dependencies and Integration Points
It integrates with x86 feature enumeration, KVM special-register validation, APIC base MSR constraints, CR0/CR4 architectural rules, and OSXSAVE/OSPKE CPUID side effects.

## Risks and Test Signals
Risks include KVM accepting unsupported features, partially modifying sregs on a failed ioctl, or failing to reflect CR4.OSXSAVE/CR4.PKE into guest CPUID. Test signals are expected `_vcpu_sregs_set()` failures and exact sregs preservation after rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/set_sregs_test.c -->
