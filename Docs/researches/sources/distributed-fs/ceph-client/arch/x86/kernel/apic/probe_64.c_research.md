# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/probe_64.c

## Purpose
This file implements the 64-bit APIC probe layer. It enables interrupt remapping/x2APIC preparation, selects the best registered APIC backend, and supports ACPI MADT OEM-driven driver selection.

## Important APIs, Types, And Functions
`x86_64_probe_apic()` calls `enable_IR_x2apic()` and then iterates the APIC driver linker section, installing the first driver whose `probe()` callback succeeds. `default_acpi_madt_oem_check(oem_id, oem_table_id)` iterates drivers and installs the first whose OEM check matches.

## Control Flow
During APIC mode initialization, 64-bit setup invokes `x86_64_probe_apic()`. IRQ remapping and x2APIC state are prepared before driver probing so x2APIC drivers can observe `x2apic_mode`. Firmware parsing can call `default_acpi_madt_oem_check()` earlier to select platform-specific drivers such as Numachip or Secure AVIC.

## State And Persistence
The file owns no state directly. It mutates the global `apic` driver through `apic_install_driver()` and relies on global x2APIC/IRQ-remapping state from `apic.c`.

## Dependencies And Integration Points
It integrates APIC driver registration, ACPI MADT OEM matching, IRQ remapping setup, x2APIC enablement, and the static-call APIC dispatch path. Driver ordering determines fallback behavior.

## Risks
If `enable_IR_x2apic()` fails or changes mode unexpectedly, x2APIC-capable drivers may not probe. If no driver probe succeeds, the code silently leaves the existing default driver rather than explicitly panicking, so correctness relies on the default initialized in `apic_flat_64.c`.

## Test Signals
Boot logs for IRQ remapping/x2APIC enablement and `Switched APIC routing to:` identify selection. Test MADT OEM platform drivers, x2APIC physical/cluster modes, IRQ remapping failure fallback, and default physical-flat fallback.
