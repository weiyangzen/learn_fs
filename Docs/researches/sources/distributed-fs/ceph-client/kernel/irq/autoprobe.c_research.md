# sources/distributed-fs/ceph-client/kernel/irq/autoprobe.c

## Purpose
`autoprobe.c` implements the legacy generic IRQ autodetection API. Drivers can enable probing, stimulate hardware, then ask which unassigned interrupt line fired.

## Important APIs, types, and functions
Public exported APIs are `probe_irq_on()`, `probe_irq_mask()`, and `probe_irq_off()`. The file uses the `probing_active` mutex, descriptor iteration helpers, `IRQS_AUTODETECT`, `IRQS_WAITING`, `IRQS_PENDING`, `irq_settings_can_probe()`, `irq_activate_and_startup()`, and `irq_shutdown_and_deactivate()`.

## Control flow
`probe_irq_on()` synchronizes async work, serializes probing, activates eligible unassigned probeable IRQs once to flush old interrupts, waits, then marks them autodetect/waiting and starts them again before waiting for spurious triggers. Lines that already triggered are shut down; low-numbered waiting lines are returned in a mask. `probe_irq_mask()` and `probe_irq_off()` scan all autodetect descriptors, determine which lines cleared `IRQS_WAITING`, shut them down, clear autodetect state, unlock the mutex, and return a bitmap or a single IRQ/negative ambiguous result.

## State and persistence
Probe state lives transiently in descriptor `istate` bits and the global `probing_active` mutex. The API mutates hardware interrupt activation state during the probe window and restores lines by shutdown/deactivation afterward.

## Dependencies and integration points
The file depends on generic IRQ descriptors, chip startup/shutdown, descriptor locking, async synchronization, and legacy driver APIs exported to modules. It assumes unassigned handlers leave triggered autodetect interrupts disabled with `IRQS_WAITING` cleared.

## Risks and test signals
Risks include races with real IRQ users, ambiguous multiple triggers, limited return masks for low IRQ numbers, drivers forgetting to call off/mask and holding the mutex, and chip callbacks that do not support probe type. Test signals include no-trigger, single-trigger, multi-trigger, longstanding-spurious filtering, `probe_irq_mask()` cleanup, and overlap attempts from multiple callers.
