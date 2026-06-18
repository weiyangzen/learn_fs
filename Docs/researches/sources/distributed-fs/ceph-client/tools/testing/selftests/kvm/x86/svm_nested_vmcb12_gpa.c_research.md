<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_nested_vmcb12_gpa.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_nested_vmcb12_gpa.c

## Purpose
This harness-based nested SVM test validates handling of invalid and unmappable VMCB12 physical addresses for VMRUN, VMLOAD, VMSAVE, and nested VM-exit paths.

## Important APIs, Types, and Functions
Important helpers are `l1_vmrun()`, `l1_vmload()`, `l1_vmsave()`, `l1_vmexit()`, `unmappable_gpa()`, `test_invalid_vmcb12()`, `test_unmappable_vmcb12()`, and `test_unmappable_vmcb12_vmexit()`. It uses `KVM_ONE_VCPU_TEST_SUITE`, SVM assembly instructions, GP exception handling, `vcpu_save_state()`, `vcpu_load_state()`, and `state->nested.hdr.svm.vmcb_pa`.

## Control Flow, State, and Persistence
Invalid `-1ULL` VMCB GPA cases install a #GP handler and expect a sync from the handler. Unmappable VMCB GPA cases compute a GPA just after all VM memory regions and expect `KVM_EXIT_INTERNAL_ERROR` with emulation suberror. The VM-exit case first enters L2 with a valid VMCB, saves state while L2 has started, mutates nested-state `vmcb_pa` to an unmappable GPA, reloads state, and expects shutdown when KVM cannot map VMCB12 on nested exit. State includes VM memory-region layout and nested-state serialized VMCB GPA.

## Dependencies and Integration Points
The file depends on SVM support, selftests harness macros, KVM nested-state load validation, and KVM internal-error/shutdown exit paths.

## Risks and Test Signals
Risks include accepting invalid physical addresses, reporting the wrong exit reason, or failing late on nested VM-exit state. Signals are `SYNC_GP`, `KVM_INTERNAL_ERROR_EMULATION`, and `KVM_EXIT_SHUTDOWN` for the respective scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_nested_vmcb12_gpa.c -->
