# sources/distributed-fs/ceph-client/arch/x86/kvm/svm/hyperv.c

## Purpose
`hyperv.c` provides the SVM-specific implementation for injecting a Hyper-V enlightened synthetic VM exit after an L2 TLB flush hypercall. It is small but important glue between KVM's Hyper-V emulation and SVM nested virtualization.

## Important APIs, types, and functions
- `svm_hv_inject_synthetic_vmexit_post_tlb_flush(struct kvm_vcpu *vcpu)` is the sole exported function in this file.
- It uses `to_svm()` to access the SVM vCPU, writes VMCB exit fields, asserts `HV_SVM_EXITCODE_ENL == SVM_EXIT_SW`, and calls `nested_svm_vmexit()`.

## Control flow
The function is called after L0 handles an enlightened L2 TLB flush hypercall that should be reported to L1 as a Hyper-V synthetic exit. It writes the software-defined exit code into `exit_code`, sets `exit_info_1` to `HV_SVM_ENL_EXITCODE_TRAP_AFTER_FLUSH`, clears `exit_info_2`, and immediately routes through the generic nested SVM VM-exit path.

## State and persistence behavior
It mutates only the active VMCB control exit fields for the vCPU and relies on `nested_svm_vmexit()` to persist the result back into vmcb12, leave guest mode, and restore L1 state. No independent allocation or long-lived state is kept here.

## Dependencies and integration points
The file depends on `hyperv.h` for Hyper-V/SVM constants and on nested SVM support for `nested_svm_vmexit()`. Its caller is selected through Hyper-V nested operations and the SVM nested ops table. It is compiled only when the corresponding Hyper-V support is enabled through the declarations in `hyperv.h`.

## Risks and edge cases
The function assumes the vCPU is currently in nested guest mode and that `svm->vmcb` refers to the L2-running VMCB. Calling it outside that context would synthesize an exit into the wrong state. The build-time assertion protects against mismatch between the Hyper-V software exit encoding and AMD's reserved software exit code.

## Test signals
Signals are Hyper-V-on-KVM nested tests that issue L2 TLB flush hypercalls with enlightened VMCB enabled, then verify L1 observes `HV_SVM_EXITCODE_ENL` and `HV_SVM_ENL_EXITCODE_TRAP_AFTER_FLUSH`. Nested migration tests should confirm no persistent state beyond vmcb12 exit fields is needed.
