# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/apic_numachip.c

## Purpose
This file implements APIC backends for Numascale NumaConnect and NumaConnect2 systems. These systems need nonstandard APIC ID extraction and remote IPI delivery through Numachip local CSR registers when targets are outside the local APIC ID segment.

## Important APIs, Types, And Functions
Global `numachip_system` records detected generation. `numachip1_get_apic_id()` and `numachip2_get_apic_id()` derive extended APIC IDs from AMD node/MMIO configuration MSRs. `numachip1_apic_icr_write()` and `numachip2_apic_icr_write()` write generation-specific CSR interrupt generation registers. `numachip_wakeup_secondary()` sends INIT/SIPI through the CSR path. IPI helpers choose local APIC delivery when the target is local to the Numachip segment and CSR delivery otherwise. Two `struct apic` drivers, `apic_numachip1` and `apic_numachip2`, register with OEM MADT checks.

## Control Flow
ACPI MADT OEM matching sets `numachip_system`. The early initcall `numachip_system_init()` maps LCSR space, selects the CSR writer, installs CPU topology fixups, and overrides PCI arch initialization. APIC probing then selects the matching driver. During IPI delivery, `numachip_send_IPI_one()` compares local and destination APIC IDs; local targets use standard physical ICR writes, remote targets use the Numachip CSR generator.

## State And Persistence
The persistent state is the generation flag and the selected `numachip_apic_icr_write` function pointer. CPU topology is adjusted through `x86_cpuinit.fixup_cpu_id`, setting LLC and package IDs based on node topology. LCSR mappings persist for the kernel lifetime.

## Dependencies And Integration Points
It depends on Numachip CSR/MSR definitions, AMD topology MSRs, early extra UC mappings, APIC common helpers, native APIC MMIO accessors, and x86 PCI init hooks. It integrates with APIC driver selection through MADT OEM IDs `NUMASC/NCONNECT` and `NUMASC/NCONECT2`.

## Risks
Wrong generation detection or CSR formatting would break remote IPIs and AP startup. Topology fixups influence scheduler/cache/package decisions. The local-vs-remote decision depends on `NUMACHIP_LAPIC_BITS`; mismatch with hardware APIC ID layout can route interrupts incorrectly. The driver assumes CSR space is mapped before remote IPI use.

## Test Signals
Boot logs should identify NumaConnect generation and APIC routing. Validate AP startup, remote IPI delivery, NMI delivery, CPU topology/package IDs, PCI init behavior, and interrupt distribution across remote nodes.
