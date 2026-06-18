<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xapic_tpr_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xapic_tpr_test.c

## Purpose
This test validates APIC Task Priority Register behavior in both xAPIC and x2APIC modes, including synchronization between LAPIC TPR, PPR, and CR8 and interrupt masking/unmasking based on priority.

## Important APIs, Types, and Functions
Important functions are `tpr_guest_code()`, `tpr_guest_irq_queue()`, `tpr_guest_check_tpr_ppr_cr8_equal()`, `test_tpr_check_tpr_zero()`, `test_tpr_check_tpr_cr8_equal()`, `test_tpr_set_tpr_for_irq()`, and `test_tpr()`. It uses atomic guest counters, xAPIC/x2APIC EOI handlers, `KVM_GET_LAPIC`, `KVM_SET_LAPIC`, `vcpu_sregs_get()`, and APIC priority macros.

## Control Flow, State, and Persistence
For each APIC mode, the guest disables interrupts, enables APIC, verifies reset TPR is zero and equals PPR/CR8, queues a self-IPI, verifies it is masked by IF=0, enables interrupts and observes delivery, syncs to host to raise TPR enough to mask the next IRQ, then syncs again to lower TPR and observes pending IRQ delivery. Host services syncs by editing LAPIC TPR through `KVM_SET_LAPIC` and checks CR8/TPR equality. State is APIC mode flag, guest interrupt counter, LAPIC TPR/PPR, CR8, and pending self-IPI.

## Dependencies and Integration Points
It integrates with LAPIC state ioctls, CR8/sregs ABI, xAPIC MMIO mapping, x2APIC MSR mode, interrupt priority masking, and APIC EOI.

## Risks and Test Signals
Risks include TPR/CR8 divergence, wrong PPR computation, pending IRQ lost while masked, or mode-specific APIC behavior differences. Signals are guest counter transitions 0 to 1 to 2 and host assertions that CR8 equals LAPIC TPR at every sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xapic_tpr_test.c -->
