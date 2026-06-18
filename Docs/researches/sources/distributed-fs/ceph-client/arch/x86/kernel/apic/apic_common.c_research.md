# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/apic_common.c

## Purpose
This file contains small common helpers shared by APIC driver implementations. It abstracts basic APIC ID calculation and logical destination register initialization so 32-bit, xAPIC, x2APIC, flat, physical, and specialized backends can reuse consistent mappings.

## Important APIs, Types, And Functions
`apic_default_calc_apicid(cpu)` returns `per_cpu(x86_cpu_to_apicid, cpu)` for physical destination mode. `apic_flat_calc_apicid(cpu)` returns `1U << cpu` for classic flat logical mode. `default_cpu_present_to_apicid(mps_cpu)` exports a KVM-visible helper that maps a present Linux CPU number to the recorded APIC ID or `BAD_APICID`. `default_init_apic_ldr()` programs `APIC_DFR` to flat mode and writes a per-CPU logical APIC ID into `APIC_LDR`.

## Control Flow
APIC driver structs install these helpers in their callback tables. During local APIC setup, `setup_local_APIC()` calls `apic->init_apic_ldr()` when present, which for logical flat drivers routes here. Vector and MSI code calls `apic->calc_dest_apicid()` to convert a target CPU into the destination ID encoded into an interrupt message or route entry.

## State And Persistence
The file does not own persistent structures. It reads per-CPU `x86_cpu_to_apicid`, `cpu_present()`, and `nr_cpu_ids`, and it mutates APIC hardware registers `APIC_DFR` and `APIC_LDR` through the active APIC accessors.

## Dependencies And Integration Points
It depends on `asm/apic.h`, per-CPU topology state, and local APIC register read/write callbacks. It integrates with APIC backend definitions in `probe_32.c`, `apic_flat_64.c`, `x2apic_*`, and platform-specific drivers such as Numachip.

## Risks
The logic is small, but the destination ID calculation must match the backend's destination mode. Using flat logical IDs on a physical-mode APIC, or vice versa, would route IPIs/MSIs incorrectly. `default_init_apic_ldr()` assumes classic flat xAPIC semantics and is unsuitable for x2APIC cluster/physical drivers.

## Test Signals
Confirm APIC driver selection logs, successful SMP boot, IPI delivery, and correct `/proc/interrupts` distribution. For flat logical mode, inspect APIC debug dumps for expected DFR/LDR values.
