# sources/distributed-fs/ceph-client/arch/x86/include/asm/mpspec.h

## Purpose
Declares x86 Intel MultiProcessor Specification parser state, bus/IRQ capacity constants, APIC identity globals, and helper accessors.

## Important APIs, Types, And Functions
Defines `MAX_MP_BUSSES` and `MAX_IRQ_SOURCES` by architecture/config, declares `pic_mode`, optional `mp_bus_id_to_type`, `mp_bus_not_pci`, `boot_cpu_physical_apicid`, `boot_cpu_apic_version`, `smp_found_config`, MP parser functions, `phys_cpu_present_map`, `reset_phys_cpu_present_map()`, and `copy_phys_cpu_present_map()`.

## Control Flow
Early boot parser functions locate and parse MP tables when `CONFIG_X86_MPPARSE` is enabled; otherwise they become no-ops. Helper functions reset or copy the physical APIC present bitmap.

## State And Persistence
State is boot-time topology and interrupt-routing metadata retained in globals after parsing. It is not durable beyond boot.

## Dependencies And Integration Points
Depends on MP table structures, x86 init hooks, APIC definitions, EISA support, and local APIC config. It integrates with SMP bring-up, IOAPIC routing, and legacy firmware table parsing.

## Risks And Edge Cases
Capacity constants must cover old large 32-bit Summit/generic systems and 64-bit PCI IRQ source counts. Incorrect APIC present maps affect CPU discovery. Disabled parser stubs must keep call sites simple.

## Test Signals
Boot on MP-table-only systems, ACPI-disabled configurations, 32-bit large bus configs, SMP CPU discovery logs, and IOAPIC IRQ routing tests provide signal.
