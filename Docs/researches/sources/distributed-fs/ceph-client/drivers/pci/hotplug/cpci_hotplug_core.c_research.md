<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpci_hotplug_core.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpci_hotplug_core.c

## Purpose
Implements the CompactPCI hotplug core. It registers CompactPCI slots with the PCI hotplug core, owns a single platform controller, handles ENUM events via interrupt or polling thread, tracks insertion/extraction state, and delegates PCI configuration to CPCI PCI helper functions.

## Important APIs, Types, and Functions
Exports `cpci_hp_register_controller()`, `cpci_hp_unregister_controller()`, `cpci_hp_register_bus()`, `cpci_hp_unregister_bus()`, `cpci_hp_start()`, `cpci_hp_stop()`, and `cpci_hotplug_init()`. Important internal functions include hotplug slot ops, `init_slots()`, `check_slots()`, `event_thread()`, `poll_thread()`, `cpci_hp_intr()`, `cpci_start_thread()`, and `cleanup_slots()`.

## Control Flow
A board driver registers the controller, registers slots for a bus range, and starts the subsystem. Start initializes cold-inserted slots, starts either an IRQ-driven event thread or polling thread, and enables ENUM interrupts if present. The IRQ handler validates shared IRQ ownership, disables ENUM interrupt, and wakes the thread. The worker calls `check_slots()`, which clears INS bits, configures inserted slots, detects extraction requests, waits for userspace extraction handling, handles improper removals, and re-enables interrupts when stable.

## State and Persistence
Global state includes `slot_list`, `slots`, `extracting`, `controller`, `cpci_thread`, `thread_finished`, and `cpci_debug`. Slot state tracks latch/adapter status, extraction in progress, and a cached `pci_dev` reference. No persistent storage is used.

## Dependencies and Integration Points
Depends on PCI hotplug core, kthreads, IRQ APIs, semaphores, atomic counters, and CPCI PCI helper routines. Board drivers such as `cpcihp_generic` provide controller operations and bus ranges.

## Risks and Edge Cases
Only one controller is supported. IRQ callbacks are required only in interrupt mode; polling uses `query_enum()`. `thread_finished` is a plain int shared with worker lifecycle. Improper removal is detected by HS CSR reads returning `0xffff`. `enable_slot()` hotplug op is a no-op because insertion is handled by ENUM processing. Cleanup must stop the thread before freeing slots/controller IRQs.

## Test Signals
Run controller registration failures, slot registration ranges, cold insertion clearing, insertion and extraction flows, improper removal, shared IRQ filtering, polling mode, stop/unregister while extraction is pending, and sysfs hotplug disable operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpci_hotplug_core.c -->
