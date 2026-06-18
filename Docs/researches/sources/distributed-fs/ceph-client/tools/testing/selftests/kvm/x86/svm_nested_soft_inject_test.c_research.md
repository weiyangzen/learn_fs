<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_nested_soft_inject_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_nested_soft_inject_test.c

## Purpose
This test validates nested SVM soft interrupt, breakpoint, and NMI injection corner cases, especially interactions with next-RIP, intervening nested page-fault-like IDT changes, GIF/NMI blocking, and guest debug state.

## Important APIs, Types, and Functions
Key functions are `guest_bp_handler()`, `guest_int_handler()`, `guest_nmi_handler()`, `l2_guest_code_int()`, `l2_guest_code_nmi()`, `l1_guest_code()`, and `run_test()`. It uses `vmcb->control.event_inj`, `SVM_EVTINJ_TYPE_SOFT`, `SVM_EVTINJ_TYPE_EXEPT`, `SVM_EVTINJ_TYPE_NMI`, `next_rip`, `clgi()/stgi()`, APIC self-NMI, alternate IDT pages, and `vcpu_guest_debug_set()`.

## Control Flow, State, and Persistence
For soft interrupts, L1 injects vector 0x20 into L2, expects the handler RIP to equal the L2 entry, exits on VMMCALL, advances RIP, swaps to an alternate IDT, injects #BP with a next-RIP that skips an embedded `ud2`, and expects an HLT exit. For NMI, L1 injects an NMI, handles a VMMCALL from the NMI handler, then uses `clgi/stgi` and a self-NMI to verify nested NMI state resumes correctly. Host installs handlers, disables guest debug content, wraps execution in an alarm, and checks `UCALL_DONE`.

## Dependencies and Integration Points
It requires SVM and nRIP support. It integrates with nested SVM event injection fields, APIC NMI delivery, IDT copying, atomic guest-visible counters, and guest debug ioctls.

## Risks and Test Signals
Risks include wrong next-RIP on soft-event injection, lost NMI blocking, bad event type encoding, or hangs in NMI/GIF state. Signals include exact handler counters, expected VMMCALL/HLT exits, and final `UCALL_DONE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_nested_soft_inject_test.c -->
