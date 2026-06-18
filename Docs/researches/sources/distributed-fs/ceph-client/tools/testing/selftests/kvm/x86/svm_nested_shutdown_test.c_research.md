<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_nested_shutdown_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_nested_shutdown_test.c

## Purpose
This nested SVM test verifies that an unintercepted L2 shutdown does not crash KVM and is surfaced as `KVM_EXIT_SHUTDOWN`.

## Important APIs, Types, and Functions
Important functions are `l2_guest_code()` and `l1_guest_code()`. The test uses `generic_svm_setup()`, `run_guest()`, `vmcb->control.intercept`, `INTERCEPT_SHUTDOWN`, and guest IDT entry manipulation.

## Control Flow, State, and Persistence
L2 executes `ud2`. L1 clears the shutdown intercept and marks the #UD, #NP, and #DF IDT entries not-present so injection cascades through faults to shutdown. The host expects `KVM_EXIT_SHUTDOWN` from `KVM_RUN`. State is volatile in guest IDT descriptors and the nested VMCB.

## Dependencies and Integration Points
The file integrates with AMD nested SVM exception injection, IDT descriptor validity, shutdown intercept control, and KVM shutdown exits.

## Risks and Test Signals
Risks include host crashes from recursive exception handling or incorrect interception of shutdown. Passing is the expected shutdown exit and no guest return to L1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_nested_shutdown_test.c -->
