# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/probe_32.c

## Purpose
This file provides the generic 32-bit APIC driver and APIC probe layer. It supplies a default logical-flat APIC backend for up to classic xAPIC-era systems and handles the `apic=` command-line driver override.

## Important APIs, Types, And Functions
`default_get_apic_id()` extracts a 4-bit or 8-bit APIC ID depending on xAPIC/extended APIC ID support. `probe_default()` always succeeds as the fallback. `apic_default` is a logical-destination `struct apic` using `default_init_apic_ldr()`, flat APIC ID calculation, logical IPI mask helpers, native MMIO accessors, and ICR wait functions. The global `apic` pointer is initialized to `apic_default`. `parse_apic()` scans the APIC driver linker section for a named driver and installs it. `x86_32_probe_apic()` probes registered drivers unless the command line already selected one.

## Control Flow
Early `apic=` parsing can select a specific driver by name. Later, `x86_32_probe_apic()` iterates `__apicdrivers` and installs the first driver whose `probe()` succeeds. If no driver is found, it panics because APIC-enabled operation cannot proceed without callbacks.

## State And Persistence
`cmdline_apic` records whether a user-selected driver was installed. The `apic` pointer and driver struct become stable after probing and static-call update.

## Dependencies And Integration Points
It depends on APIC driver section ordering, native APIC MMIO helpers, shared logical-flat helpers, Xen/ACPI/IO-APIC headers, and the static-call update path in `init.c`. It integrates with early command-line parsing and 32-bit APIC setup.

## Risks
The default driver always succeeds, so ordering with more specialized 32-bit drivers matters. Command-line driver names must match exactly. Wrong APIC ID width selection could break systems with extended APIC IDs or old non-xAPIC hardware.

## Test Signals
Boot 32-bit kernels with default APIC selection and with explicit `apic=<driver>`. Validate APIC ID extraction, logical IPIs, SMP bring-up, and early panic absence.
