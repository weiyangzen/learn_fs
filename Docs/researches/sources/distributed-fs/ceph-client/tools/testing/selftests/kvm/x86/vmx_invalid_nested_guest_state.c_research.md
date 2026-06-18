<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_invalid_nested_guest_state.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_invalid_nested_guest_state.c

## Purpose
This nested VMX test verifies that if userspace makes L2 guest state invalid while L2 is stopped at an I/O exit, KVM reports the condition to L1 as a triple-fault VM-exit rather than trying unsupported invalid-state emulation for L2.

## Important APIs, Types, and Functions
Key functions are `l2_guest_code()` and `l1_guest_code()`. Host logic uses `vcpu_sregs_get()`, `vcpu_sregs_set()`, `struct kvm_sregs.tr.unusable`, VMX setup helpers, and `KVM_EXIT_IO` validation.

## Control Flow, State, and Persistence
L1 launches L2, which exits to L0 userspace through an `inb` at a fixed port. The host confirms the I/O exit, marks TR unusable in vCPU sregs, and resumes. L1 expects VMX exit reason `EXIT_REASON_TRIPLE_FAULT` and signals done. State is nested VMCS state, L2 special registers, and one userspace I/O exit.

## Dependencies and Integration Points
It requires VMX and the selftests VMX helper framework. It integrates with KVM nested guest-state validation and triple-fault injection into L1.

## Risks and Test Signals
Risks include attempting invalid-state emulation for L2, wrong VM-exit reason, or state corruption after userspace changes sregs. Passing signal is L1 `UCALL_DONE` after reading `EXIT_REASON_TRIPLE_FAULT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_invalid_nested_guest_state.c -->
