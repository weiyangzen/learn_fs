<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_vmcall_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_vmcall_test.c

## Purpose
This minimal nested SVM test verifies that an L2 `vmcall` instruction exits to L1 as `SVM_EXIT_VMMCALL`.

## Important APIs, Types, and Functions
The file uses `l2_guest_code()`, `l1_guest_code()`, `generic_svm_setup()`, `run_guest()`, `vcpu_alloc_svm()`, and VMCB `exit_code`.

## Control Flow, State, and Persistence
The host creates one VM, allocates SVM state, passes it to L1, and repeatedly runs until `UCALL_DONE`. L1 prepares L2, enters it, and asserts the VMCB exit code is `SVM_EXIT_VMMCALL`. State is the nested VMCB and ucall stream only.

## Dependencies and Integration Points
It requires AMD SVM support and the selftests nested SVM helper stack.

## Risks and Test Signals
The test is narrow; its risk signal is a regression in VMCALL intercept/exit-code mapping. Passing requires L1 assertion success and `GUEST_DONE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_vmcall_test.c -->
