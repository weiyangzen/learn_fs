<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_nested_clear_efer_svme.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_nested_clear_efer_svme.c

## Purpose
This short nested SVM regression test verifies that clearing `EFER.SVME` from L2 causes a shutdown path instead of returning normally to L1 or corrupting host state.

## Important APIs, Types, and Functions
The test uses `l2_guest_code()`, `l1_guest_code()`, `generic_svm_setup()`, `run_guest()`, `rdmsr(MSR_EFER)`, `wrmsr(MSR_EFER)`, and `vcpu_alloc_svm()`.

## Control Flow, State, and Persistence
L1 prepares and enters L2 through generic SVM setup. L2 asserts `EFER_SVME` is initially set, clears it, and should never execute the following guest assertion. The host runs one vCPU and expects `KVM_EXIT_SHUTDOWN`. State is limited to the nested VMCB and EFER.

## Dependencies and Integration Points
It requires AMD SVM support and nested SVM execution through selftests helpers.

## Risks and Test Signals
Risks include mishandling architectural shutdown conditions or allowing illegal nested SVM state to continue. The decisive signal is `KVM_EXIT_SHUTDOWN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_nested_clear_efer_svme.c -->
