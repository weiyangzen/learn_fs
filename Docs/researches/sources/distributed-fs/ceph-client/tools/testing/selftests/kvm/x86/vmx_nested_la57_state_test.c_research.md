<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_nested_la57_state_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_nested_la57_state_test.c

## Purpose
This test validates nested VMX state save/restore when L1 uses 5-level paging and L2 uses 4-level paging. It targets canonical-address checks around state whose validity depends on CR4.LA57.

## Important APIs, Types, and Functions
Important functions are `l2_guest_code()`, `l1_guest_code()`, and `guest_code()`. The test uses `LA57_GS_BASE`, `MSR_GS_BASE`, `GUEST_CR3`, `GUEST_CR4`, `X86_CR4_LA57`, `vcpu_save_state()`, `vcpu_load_state()`, and `virt_map()` of the PML5 page.

## Control Flow, State, and Persistence
L1 writes GS_BASE to a value canonical only with LA57 enabled, prepares VMX, points L2 CR3 at L1's first PML4, clears L2 CR4.LA57, and launches L2. L2 syncs with host while active, causing host save/release/recreate/load of vCPU state, then resumes and exits via VMCALL. State includes L1 5-level page tables, L2 4-level CR3/CR4, nested VMCS, and GS_BASE.

## Dependencies and Integration Points
It requires VMX, LA57 support, and `KVM_CAP_NESTED_STATE`. It integrates with KVM canonical-address modeling, nested VMX state serialization, and page-table identity mapping.

## Risks and Test Signals
Risks include checking L1 state with L2 LA57 rules, rejecting valid GS_BASE on restore, or corrupting nested CR3/CR4 state. Signals are successful restore while L2 is active and final `UCALL_DONE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_nested_la57_state_test.c -->
