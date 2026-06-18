<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_msrs_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_msrs_test.c

## Purpose
This test validates KVM ownership and validation of VMX control MSRs and `IA32_FEATURE_CONTROL`. It checks that KVM restores owned fixed bits where appropriate and rejects unsupported feature-control bits.

## Important APIs, Types, and Functions
Important helpers are `vmx_fixed1_msr_test()`, `vmx_fixed0_msr_test()`, `vmx_fixed0and1_msr_test()`, `vmx_save_restore_msrs_test()`, `__ia32_feature_control_msr_test()`, and `ia32_feature_control_msr_test()`. It uses `vcpu_get_msr()`, `vcpu_set_msr()`, `_vcpu_set_msr()`, VMX MSR constants, `FEAT_CTL_*` bits, CPUID feature mutation helpers, and bitmap iteration macros.

## Control Flow, State, and Persistence
The test creates one vCPU without guest code. It tries clearing fixed-1 bits and setting fixed-0 bits across VMX control MSRs, expecting KVM to accept writes through selftests helpers and normalize/restore as required. It toggles feature-control bits while related CPUID features are hidden or exposed, then iterates unsupported bits and expects writes to fail. State is the vCPU's synthetic VMX MSR set and CPUID feature model.

## Dependencies and Integration Points
It requires VMX and `KVM_CAP_DISABLE_QUIRKS2`. It integrates with VMX MSR virtualization, KVM quirks around tweaking VMX control MSRs, feature-control lock semantics, and CPUID dependency enforcement.

## Risks and Test Signals
Risks include KVM allowing reserved feature-control bits, failing to preserve owned VMX capabilities, or mishandling CPUID-dependent bits. Signals are successful normalization writes and expected `_vcpu_set_msr()` failures for unsupported reserved bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_msrs_test.c -->
