<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_apicv_updates_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_apicv_updates_test.c

## Purpose
This nested VMX test validates APICv inhibition and updates when APIC mode and APIC ID are changed across L1/L2 transitions. It checks that IRQ state, APIC virtualization, and TLB behavior remain coherent.

## Important APIs, Types, and Functions
Important functions are `good_ipi_handler()`, `bad_ipi_handler()`, `l2_guest_code()`, and `l1_guest_code()`. The test uses APIC register helpers, `prepare_virtualize_apic_accesses()`, VMX MSR bitmaps, APICv/APIC-access controls, ISR/EOI checks, and `vcpu_get_stat(vcpu, irq_injections)`.

## Control Flow, State, and Persistence
L1 enables xAPIC and writes a modified APIC ID to inhibit APICv, sends itself a good IPI, and verifies it is in-service. L2 first switches to x2APIC, causing KVM to restore the APIC ID and potentially uninhibit APICv. L1 then scribbles APIC access registers, verifies a bad IPI write is ignored, checks ISR state in x2APIC, EOIs, resumes L2 to switch back to xAPIC, sends another good IPI, and checks ISR/EOI again. State includes APIC mode, APIC ID, vISR/SVI-like in-service state, and KVM IRQ-injection stats.

## Dependencies and Integration Points
It requires VMX and APIC-access virtualization setup. It integrates with APICv inhibition, APIC ID virtualization, xAPIC/x2APIC transitions, APIC access page MMIO, and IRQ injection accounting.

## Risks and Test Signals
Risks include stale APICv state after L2 APIC mode changes, failure to flush L1 TLB for APIC access page changes, bad IPI delivery, or lost in-service vector propagation. Signals are exactly two guest-observed good IPIs, no bad IPI, cleared ISR after EOI, and at least two KVM IRQ injections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_apicv_updates_test.c -->
