# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/ipi.c

## Purpose
This file provides generic IPI delivery helpers for xAPIC-style APIC drivers and SMP call sites. It manages the optional IPI shorthand optimization and implements physical/logical APIC ICR writes for single, mask, all, all-but-self, and self IPIs.

## Important APIs, Types, And Functions
`apic_use_ipi_shorthand` is a static key controlling broadcast shorthand use. Boot option `no_ipi_broadcast=` sets `apic_ipi_shorthand_off`. SMP-facing functions include `apic_smt_update()`, `apic_send_IPI_allbutself()`, `native_smp_send_reschedule()`, `native_send_call_func_single_ipi()`, `native_send_call_func_ipi()`, and `apic_send_nmi_to_offline_cpu()`. Low-level helpers include `apic_mem_wait_icr_idle_timeout()`, `apic_mem_wait_icr_idle()`, `__default_send_IPI_dest_field()`, physical and logical mask senders, and shorthand senders.

## Control Flow
CPU topology changes call `apic_smt_update()` to enable shorthand only after all present CPUs have booted once and more than one CPU is online. Generic SMP reschedule/call-function paths invoke native send helpers, which choose APIC shorthand when safe or fall back to mask delivery. Driver structs in other files point their IPI callbacks at these helpers. Low-level send functions wait for ICR idle, write ICR2 for explicit destinations, then write ICR.

## State And Persistence
The persistent runtime state is the static key plus the boot option flag. Delivery uses per-CPU APIC IDs, online/present/booted-once masks, and APIC hardware ICR state.

## Dependencies And Integration Points
It depends on SMP CPU masks, `x86_cpu_to_apicid`, local APIC MMIO accessors, vector constants, and string-choice logging. It integrates with scheduler reschedule IPIs, generic call-function IPIs, NMI backtraces, APIC driver callback tables, and CPU hotplug state.

## Risks
IPI broadcast shorthand is unsafe before all present CPUs have initialized APIC state, especially for NMIs. ICR2 plus ICR writes must be protected from interruption for explicit destinations; the code uses IRQ save where needed. NMI sends use timeout waiting to avoid panic/kdump hangs.

## Test Signals
Signals include SMP boot, CPU hotplug toggling shorthand logs, scheduler reschedule IPIs, smp-call-function stress, NMI backtraces, panic stop-CPU behavior, and `no_ipi_broadcast=` boot variations.
