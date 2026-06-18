<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_driver.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_driver.c

## Purpose
`eeh_driver.c` orchestrates EEH recovery after events are dequeued. It notifies PCI drivers through `pci_error_handlers`, decides whether MMIO/DMA thaw or reset is required, performs hotplug fallback for EEH-unaware devices, handles permanent failure removal, and scans special platform-wide errors.

## Important APIs, Types, And Functions
Key public functions are `eeh_pe_reset_and_recover()`, `eeh_handle_normal_event()`, and `eeh_handle_special_event()`. Helpers include result priority/merge functions, `eeh_edev_actionable()`, driver module ref helpers, IRQ disable/enable, `eeh_pe_report()`, report callbacks for `error_detected`, `mmio_enabled`, `slot_reset`, `resume`, and permanent failure, virtual-function add/remove helpers, `eeh_reset_device()`, `eeh_pe_cleanup()`, and slot presence/attention helpers.

## Control Flow
Normal recovery locks PCI rescan/remove, finds the affected bus, verifies devices remain present, logs location and saved stack trace, clears stale no-handler flags, increments freeze counters, notifies drivers of frozen I/O, waits for PE state, collects temporary logs, then follows the aggregate driver result. No EEH-aware drivers triggers full hotplug reset. `CAN_RECOVER` tries MMIO and DMA thaw plus optional `mmio_enabled`. `NEED_RESET` performs reset without full hotplug, restores state, calls `slot_reset`, and resumes. Failure collects permanent logs, marks devices permanently failed, removes VFs or the bus, and marks PE removed. Special events loop through platform `next_error()`, purge duplicate events, handle frozen/fenced PEs as normal events, and remove dead PHBs/IOCs.

## State And Persistence
Runtime state includes PE recovery/isolation/removed/keep bits, device `in_error`, `EEH_DEV_NO_HANDLER`, `EEH_DEV_DISCONNECTED`, IRQ-disabled mode bits, removed VF lists, freeze counters, and PCI device error states. No persistent storage exists.

## Dependencies And Integration Points
It integrates with EEH core APIs, event thread, PCI error recovery callbacks, PCI hotplug, SR-IOV, IRQ core, RTAS/platform logging, rescan/remove locking, and hotplug slot attention LEDs.

## Risks
This file has high race risk around device removal, driver unload, and PE tree mutation; module refs and device locks mitigate that. Recovery result merging is conservative and can escalate. Blocking config access and restoring BARs must respect restricted PEs. Freeze-count policy can permanently remove noisy hardware.

## Test Signals
Signals include injected EEH recovery for aware and unaware drivers, `mmio_enabled`/`slot_reset`/`resume` callback ordering, hotplug remove/add fallback, VF removal/re-add, permanent failure behavior after `eeh_max_freezes`, dead PHB/IOC special events, and absence of rescan/remove lock deadlocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_driver.c -->
