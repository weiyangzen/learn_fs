<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/apic.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/apic.c

## Purpose
`apic.c` contains guest-side x86 APIC mode helpers for KVM selftests. It can disable the local APIC, enable xAPIC, and enable x2APIC while ensuring the software-enable bit is set in the spurious interrupt vector register.

## Important APIs, Types, and Functions
The public functions are `apic_disable()`, `xapic_enable()`, and `x2apic_enable()`. They operate on `MSR_IA32_APICBASE`, `MSR_IA32_APICBASE_ENABLE`, `MSR_IA32_APICBASE_EXTD`, `APIC_SPIV`, and `APIC_SPIV_APIC_ENABLED` through `rdmsr()`, `wrmsr()`, `xapic_read_reg()`, `xapic_write_reg()`, `x2apic_read_reg()`, and `x2apic_write_reg()`.

## Control Flow
`xapic_enable()` follows SDM sequencing: if already in x2APIC, it first disables APIC, then enables xAPIC; if APIC is disabled, it sets the enable bit. Both enable helpers then set the APIC software-enable bit in SPIV.

## State and Persistence
The functions mutate guest CPU MSR and local APIC state. The state persists for the running vCPU until reset or explicit reconfiguration.

## Dependencies and Integration Points
The file depends on `apic.h` and x86 guest register/MSR helpers. It integrates with tests that need deterministic local interrupt controller state before injecting or receiving timer, IPI, or APIC-related events.

## Risks and Test Signals
Risks include invalid APIC mode transitions, failing to set SPIV software enable, and writing xAPIC registers while still in x2APIC. Test signals are indirect: interrupt delivery tests should receive expected vectors and should not fail due to a disabled local APIC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/apic.c -->
