# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/apic_flat_64.c

## Purpose
This is the default 64-bit physical-flat xAPIC driver. It provides a `struct apic` backend for systems using memory-mapped APIC registers and physical destination mode, and it is the initial global `apic` pointer on x86-64 before probing may switch to another driver.

## Important APIs, Types, And Functions
`physflat_get_apic_id()` extracts the 8-bit APIC ID from the APIC ID register. `physflat_probe()` and `physflat_acpi_madt_oem_check()` always accept, making this a safe fallback. The `apic_physflat` driver sets physical destination mode, `max_apic_id = 0xFE`, physical IPI helpers, native MMIO read/write/EOI, native ICR access, and memory-mode ICR wait functions. `apic_driver(apic_physflat)` registers it, and `struct apic *apic` is initialized to it.

## Control Flow
During `x86_64_probe_apic()`, this driver can be selected if no more specific x2APIC or platform driver wins. Once installed, generic APIC calls are static-call patched by `init.c`, so IPI, register access, and EOI operations dispatch to the physical-flat callbacks.

## State And Persistence
The file owns no dynamic state except the global `apic` pointer default. The driver struct is `__ro_after_init`, so callback configuration becomes read-only after initialization.

## Dependencies And Integration Points
It depends on shared helpers from `apic_common.c` and `ipi.c`, native APIC MMIO accessors from the architecture APIC layer, and the APIC driver linker section. It integrates with local APIC setup, vector allocation, MSI composition, and SMP IPI delivery through `struct apic`.

## Risks
Because `probe()` always succeeds, driver ordering matters: this fallback must not preempt more specific drivers. Its 8-bit destination limit means it is unsuitable for systems requiring x2APIC extended IDs unless another driver replaces it. Incorrect fallback use could cap CPU enumeration or misroute interrupts on large systems.

## Test Signals
Boot logs should show `Switched APIC routing to: physical flat` when this driver is selected. SMP bring-up, IPIs, timer interrupts, and MSI affinity changes validate the callbacks.
