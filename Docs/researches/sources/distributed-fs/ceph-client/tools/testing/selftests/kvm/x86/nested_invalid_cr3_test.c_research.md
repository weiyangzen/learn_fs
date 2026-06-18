# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_invalid_cr3_test.c

Purpose: Verifies that L1 cannot enter L2 with an invalid CR3 and can successfully enter L2 after restoring a valid CR3.

Important APIs/types/functions: `l2_guest_code()` exits by `vmcall`; `l1_svm_code()` corrupts/restores `vmcb->save.cr3`; `l1_vmx_code()` corrupts/restores `GUEST_CR3`; `l1_guest_code()` selects VMX or SVM. It uses `SVM_EXIT_ERR`, `EXIT_REASON_FAILED_VMENTRY`, and `EXIT_REASON_INVALID_STATE`.

Control flow: L1 prepares nested state, saves the original CR3, writes `-1ull` as invalid CR3, tries to run L2, and asserts failed entry. It then restores CR3, launches L2 again, and asserts a normal VMCALL/VMMCALL exit.

State and persistence behavior: Only nested CR3 state is mutated and restored. No persistence beyond the VM.

Dependencies and integration points: Requires nested VMX/SVM and KVM's nested entry validation for guest CR3.

Risks and maintenance notes: Invalid CR3 validation can vary with paging mode and address-width support; using all ones is meant to be universally invalid. Expected VMX/SVM exit codes must remain architecture-correct.

Test signals: Passing means KVM rejects invalid nested CR3 at entry and does not poison subsequent valid entry. Failures indicate nested entry validation or state recovery bugs.
