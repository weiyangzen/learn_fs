<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/triple_fault_event_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/triple_fault_event_test.c

## Purpose
This test validates `KVM_CAP_X86_TRIPLE_FAULT_EVENT`, including injecting a pending triple-fault event while L2 is stopped at a userspace I/O exit. It covers VMX and SVM paths.

## Important APIs, Types, and Functions
Important functions are `l2_guest_code()`, `l1_guest_code_vmx()`, and `l1_guest_code_svm()`. Host logic uses `vm_enable_cap(KVM_CAP_X86_TRIPLE_FAULT_EVENT)`, `vcpu_events_get()`, `vcpu_events_set()`, `KVM_VCPUEVENT_VALID_TRIPLE_FAULT`, `vcpu_run_complete_io()`, VMX/SVM nested helpers, and `run->immediate_exit`.

## Control Flow, State, and Persistence
L1 launches L2, which exits to L0 userspace through an `inb`. The host confirms the I/O port, reads vCPU events, marks a triple fault pending, sets `immediate_exit`, completes the I/O, and verifies the pending event remains. Resuming then should produce shutdown on SVM or a VMX L1-observed triple-fault VM-exit leading to `UCALL_DONE`. State is pending vCPU event state plus nested VMCS/VMCB execution.

## Dependencies and Integration Points
This integrates with KVM vCPU event get/set ABI, triple-fault event capability, nested VMX/SVM triple-fault handling, and KVM I/O completion.

## Risks and Test Signals
Risks include dropping pending triple-fault events across I/O completion, losing event validity flags, or mishandling nested triple-fault delivery. Signals are retained pending flags, `KVM_EXIT_SHUTDOWN` for SVM, or VMX `EXIT_REASON_TRIPLE_FAULT` observed by L1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/triple_fault_event_test.c -->
