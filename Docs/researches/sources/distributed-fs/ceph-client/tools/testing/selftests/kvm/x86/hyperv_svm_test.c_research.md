# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_svm_test.c

Purpose: Tests Hyper-V enlightenments for nested SVM, including enlightened MSR bitmap behavior and nested direct TLB flush hypercalls on AMD virtualization.

Important APIs/types/functions: `rdmsr_from_l2()` forces L2 exits through `RDMSR`; `l2_guest_code()` performs `VMMCALL`, MSR reads, and Hyper-V flush calls; `guest_code()` sets up SVM VMCB and Hyper-V test pages. It uses `generic_svm_setup()`, Hyper-V VP assist/partition assist pages, clean-field controls, and direct hypercall feature bits.

Control flow: The guest enables Hyper-V synthetic MSRs, initializes nested SVM, launches L2, and validates expected L2 exits. It toggles intercept bits and clean-field notifications to ensure KVM observes or ignores MSR bitmap changes correctly. It then tests direct handling versus synthetic exit behavior for Hyper-V nested TLB flush.

State and persistence behavior: State lives in the SVM VMCB, MSR permission map, Hyper-V assist pages, and partition assist page. No state is persisted beyond one VM run.

Dependencies and integration points: Requires SVM, Hyper-V nested enlightenment support, selftest SVM utilities, and KVM's AMD nested virtualization implementation.

Risks and maintenance notes: Like the eVMCS test, this is sensitive to clean-field semantics and assumes broad GPR clobbering around L2 exits. AMD-specific exit codes and VMCB fields must remain aligned with KVM headers.

Test signals: Passing means nested SVM honors Hyper-V MSR-bitmap and direct-flush enlightenments. Failures indicate AMD nested Hyper-V enlightenment regressions.
