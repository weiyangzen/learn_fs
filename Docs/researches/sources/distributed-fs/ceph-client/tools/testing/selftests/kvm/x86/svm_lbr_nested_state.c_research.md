<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_lbr_nested_state.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_lbr_nested_state.c

## Purpose
This test validates last-branch-record state preservation across nested SVM save/restore, both with nested LBR virtualization enabled and disabled. It checks separation between L1 and L2 LBR state when virtual LBR is active.

## Important APIs, Types, and Functions
Important items are `struct lbr_branch`, `RECORD_AND_CHECK_BRANCH`, `CHECK_BRANCH_MSRS`, `CHECK_BRANCH_VMCB`, `l2_guest_code()`, `l1_guest_code()`, and `test_lbrv_nested_state()`. It uses `MSR_IA32_DEBUGCTLMSR`, `MSR_IA32_LASTBRANCHFROMIP`, `MSR_IA32_LASTBRANCHTOIP`, `SVM_MISC2_ENABLE_V_LBR`, `vcpu_save_state()`, and `vcpu_load_state()`.

## Control Flow, State, and Persistence
L1 records a branch into LBR MSRs, triggers a save/restore, then runs L2. L2 records its own branch, triggers another save/restore, and exits. L1 syncs once more after L2, then verifies either that L1 MSRs remain intact and L2 branch data is stored in VMCB fields when nested LBRV is enabled, or that the shared MSRs contain L2 branch data when disabled. The test runs both modes.

## Dependencies and Integration Points
It depends on SVM support and KVM LBRV enablement. It integrates with debug-control MSRs, nested VMCB save fields, and KVM x86 state serialization.

## Risks and Test Signals
Risks include lost LBR MSRs during migration, failure to copy virtual LBR fields to/from VMCB, and incorrect sharing when LBRV is off. Signals are non-zero recorded branch addresses and exact MSR/VMCB comparisons after restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_lbr_nested_state.c -->
