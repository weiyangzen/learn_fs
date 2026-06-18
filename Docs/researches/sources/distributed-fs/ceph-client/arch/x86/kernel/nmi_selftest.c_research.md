# sources/distributed-fs/ceph-client/arch/x86/kernel/nmi_selftest.c

## Purpose
Provides an init-time NMI IPI selftest that checks whether local and remote APIC-delivered NMI vectors reach the registered local NMI handler on online CPUs.

## APIs, Types, And Functions
The file is centered on `nmi_selftest()`. Support state includes `nmi_fail`, `nmi_ipi_mask`, testcase counters, and unexpected unknown/failure counters. It installs `nmi_unk_cb()` on `NMI_UNKNOWN` and `test_nmi_ipi_callback()` on `NMI_LOCAL`.

## Control Flow
`nmi_selftest()` registers an unknown-NMI trap handler, runs `remote_ipi()` and `local_ipi()` through `dotest()`, unregisters the handler, and prints a summary. `remote_ipi()` sends NMIs to all online CPUs except the current CPU; `local_ipi()` sends one to the current CPU. `test_nmi_ipi()` registers the local handler with `NMI_FLAG_FIRST`, issues `__apic_send_IPI_mask(mask, NMI_VECTOR)`, waits up to one second for the callback to clear all CPUs from the mask, and unregisters the handler.

## State And Persistence
All state is `__initdata`, so it disappears after init. The selftest mutates the shared NMI handler registry only during the test window. Its persistent output is only printk diagnostics.

## Dependencies And Integration
Depends on APIC IPI delivery, `register_nmi_handler()`, `unregister_nmi_handler()`, online CPU masks, and `udelay()`. It validates the handler infrastructure implemented in `nmi.c` and the APIC NMI vector path.

## Risks And Test Signals
The test can time out on broken APIC/NMI routing or if CPUs fail to service NMIs. A failure disables debugging according to the printed message. Because it runs at init and uses NMI handler registration, ordering and unregister cleanup matter. Test signals are the printed per-case `ok`, `FAILED`, or `TIMEOUT` lines and the final pass/fail summary.
