# sources/distributed-fs/ceph-client/drivers/pci/hotplug/shpchp.h

## Purpose
Defines the shared data structures, constants, register layout, helper functions, and prototypes for the Standard Hot Plug Controller PCI/PCI-X driver.

## Important APIs, Types, and Functions
Important types are `struct slot`, `struct event_info`, `struct controller`, packed `struct ctrl_reg`, and `enum ctrl_offsets`. The header defines event constants (`INT_*`), state constants (`STATIC_STATE`, `BLINKING*`, `POWER*`), user-facing error codes, SHPC/AMD errata register masks, and prototypes for core, control, hardware, PCI, and sysfs helpers. Inline helpers include `get_slot()`, `shpchp_find_slot()`, and AMD POGO errata save/restore functions.

## Control Flow
No standalone code runs, but the header defines the controller/slot state machine used by `shpchp_core.c` and `shpchp_ctrl.c`. AMD errata helpers temporarily mask SERR/PERR enables and clear bridge error status around slot enable.

## State and Persistence Behavior
`struct controller` persists per-HPC locks, slot list, wait queue, PCI device, MMIO mapping, SHPC offsets, bus speed metadata, and polling timer. `struct slot` persists per-slot state, cached power/presence/latch/attention status, workqueue, delayed button work, and hotplug slot object.

## Dependencies and Integration Points
Includes PCI, PCI hotplug, delay, signal, mutex, and workqueue APIs. It is consumed by all `shpchp_*` implementation files and couples them to SHPC MMIO register layout.

## Risks
Register layout and bit definitions mirror the SHPC spec and are ABI-sensitive. Slot state values drive button debounce and sysfs behavior. AMD errata helpers touch vendor-specific PCI-X bridge registers and must remain scoped to affected devices. `shpchp_find_slot()` assumes device numbers uniquely identify slots.

## Test Signals
Compile all SHPC objects, initialize controllers with multiple slot counts/orderings, exercise button/presence/latch/power-fault events, AMD POGO single-slot enable, and inspect cached status consistency.
