# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/module.c

## Purpose
`module.c` is the PCI and module lifecycle for the IBM ASM service processor driver. It enables the RSA PCI device, allocates `service_processor` state, registers interrupts/input/filesystem hooks, sends initial service-processor state, and cleans everything up on removal and module exit.

## Important APIs, Types, and Functions
Primary functions are `ibmasm_init_one()`, `ibmasm_remove_one()`, `ibmasm_init()`, and `ibmasm_exit()`. The file defines `ibmasm_debug`, module parameter metadata, `ibmasm_pci_table`, and `ibmasm_driver`.

## Control Flow
Module init registers the PCI driver, then registers ibmasmfs and panic notifier. Probe enables PCI, requests BAR regions, allocates and initializes `service_processor`, allocates event and heartbeat resources, maps BAR0, requests the shared IRQ, enables SP interrupts, registers remote input devices, sends driver VPD and OS-up dot commands, adds the service processor to ibmasmfs, and optionally registers UART. Remove unregisters UART, sends OS-down, exits heartbeat, disables/free IRQ, frees remote input, unmaps BAR, releases events, frees the service processor, releases PCI regions, and disables the device.

## State and Persistence
Per-device state is held in `struct service_processor` and stored as PCI drvdata. Loading sends persistent service-processor-visible OS-up and VPD state; removal sends OS-down. The global debug flag persists as a module parameter while loaded.

## Dependencies and Integration Points
It coordinates all ibmasm modules, PCI core, low-level register helpers, remote input, ibmasmfs, panic notifier, and optional UART.

## Risks and Edge Cases
PCI driver registration occurs before filesystem registration; a probe could call `ibmasmfs_add_sp()` before successful fs registration. `ibmasm_remove_one()` does not remove `sp->node` from the ibmasmfs service-processor list, leaving stale references. Error unwind is layered but must remain in exact reverse initialization order.

## Test Signals
Test probe success and each failure label, module load/unload, PCI hot-remove, OS-up/down command failures, panic notifier lifecycle, remote input failure unwind, and ibmasmfs mounting before/after devices appear.
