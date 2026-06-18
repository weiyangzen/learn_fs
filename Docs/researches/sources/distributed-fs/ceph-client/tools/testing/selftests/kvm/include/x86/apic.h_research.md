# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/apic.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/apic.h

Purpose: x86 APIC/x2APIC helper definitions for KVM selftests. It exposes APIC MSRs, MMIO register offsets, bit masks, and guest helpers to enable/disable APIC modes and read/write APIC registers.

Important APIs/types/functions: `APIC_DEFAULT_GPA`, `MSR_IA32_APICBASE` fields, xAPIC/x2APIC register offsets, ICR/LVT masks, `apic_disable`, `xapic_enable`, `x2apic_enable`, `get_bsp_flag`, `xapic_read_reg`, `xapic_write_reg`, `x2apic_read_reg`, `x2apic_write_reg_safe`, `x2apic_write_reg`, and `x2apic_write_reg_fault`.

Control flow and state: guest tests manipulate APIC base MSR and APIC registers either through MMIO at the default APIC GPA or through x2APIC MSRs. Safe write helpers capture fault vectors to validate negative cases.

Dependencies and integration: depends on `x86/processor.h` for MSR/fault helpers and `ucall_common.h` for guest assertions. It integrates with interrupt, APIC virtualization, x2APIC, and nested APIC tests.

Risks: APIC mode transitions are stateful and can affect later guest code. x2APIC MSR access must be feature-gated. Fault expectations rely on `wrmsr_safe` exception fixup working correctly.

Test signals: APIC/x2APIC selftests validate register access, interrupt delivery, faulting writes, and APIC base transitions.
