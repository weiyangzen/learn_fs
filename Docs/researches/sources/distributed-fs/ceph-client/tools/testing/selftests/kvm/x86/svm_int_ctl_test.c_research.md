<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_int_ctl_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_int_ctl_test.c

## Purpose
This nested SVM test validates simultaneous delivery of L1 physical interrupts and L2 virtual interrupts through the VMCB `int_ctl` path. It specifically checks that with virtual interrupt masking disabled, L2 receives both the real LAPIC interrupt and the pending virtual interrupt.

## Important APIs, Types, and Functions
Key functions are `vintr_irq_handler()`, `intr_irq_handler()`, `l2_guest_code()`, and `l1_guest_code()`. It uses `generic_svm_setup()`, `run_guest()`, `struct vmcb.control.int_ctl`, `V_IRQ_MASK`, `V_INTR_PRIO_SHIFT`, `V_INTR_MASKING_MASK`, `INTERCEPT_INTR`, `INTERCEPT_VINTR`, x2APIC self-IPI, and SVM exit-code checking.

## Control Flow, State, and Persistence
L1 enables x2APIC, prepares L2, clears virtual interrupt masking and interrupt intercepts, and marks a virtual interrupt pending in the VMCB. L2 sends itself a fixed interrupt through the LAPIC and executes `sti_nop()`. The two guest handlers set globals, and L2 asserts both fired before exiting through `vmcall`. The host only runs until `UCALL_DONE` or guest abort.

## Dependencies and Integration Points
The file depends on AMD SVM support, nested SVM VMCB control semantics, LAPIC interrupt delivery, and selftests IDT exception-handler installation.

## Risks and Test Signals
Risks include priority/masking mishandling, L1 intercepting interrupts that should reach L2, or losing the V_IRQ event. Signals are both handler globals set and L1 observing `SVM_EXIT_VMMCALL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_int_ctl_test.c -->
