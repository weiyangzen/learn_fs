<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xapic_state_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xapic_state_test.c

## Purpose
This test validates xAPIC/x2APIC LAPIC state behavior for ICR writes and APIC ID transitions. It checks reserved bits, readback semantics, destination encodings, and KVM's xAPIC/x2APIC APIC_ID formatting ABI.

## Important APIs, Types, and Functions
Important data is `struct xapic_vcpu`. Key functions are `xapic_guest_code()`, `x2apic_guest_code()`, `____test_icr()`, `__test_icr()`, `test_icr()`, `test_apic_id()`, and `test_x2apic_id()`. It uses `KVM_GET_LAPIC`, `KVM_SET_LAPIC`, `MSR_IA32_APICBASE`, `KVM_CAP_X2APIC_API`, xAPIC/x2APIC register helpers, and APIC ICR constants.

## Control Flow, State, and Persistence
The x2APIC guest reads values from IRR, writes them to ICR, and expects faults for reserved x2APIC bits. The xAPIC guest writes split ICR2/ICR and syncs the value. Host code stuffs arbitrary ICR values into IRR via `KVM_SET_LAPIC`, runs the guest, reads ICR back, and compares expected masks while accounting for AMD AVIC errata. Additional tests toggle APICBASE between xAPIC and x2APIC and verify APIC_ID formatting, then try to set x2APIC ID through LAPIC state and expect KVM to ignore it. State is LAPIC register image, APICBASE mode, CPUID x2APIC exposure, and AVIC behavior.

## Dependencies and Integration Points
It integrates with KVM LAPIC get/set ioctls, xAPIC and x2APIC register semantics, APICBASE transitions, `KVM_X2APIC_API_USE_32BIT_IDS`, and AMD AVIC quirks.

## Risks and Test Signals
Risks include accepting reserved x2APIC ICR bits, preserving illegal APIC IDs, incorrect BUSY bit behavior, or mishandling ICR destination fields. Signals are exact ICR readbacks under mode-specific masks and APIC_ID matching vCPU ID in both modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xapic_state_test.c -->
