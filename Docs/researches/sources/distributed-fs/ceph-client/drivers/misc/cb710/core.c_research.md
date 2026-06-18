# sources/distributed-fs/ceph-client/drivers/misc/cb710/core.c

Purpose: implements the ENE CB710/CB720 PCI card-reader core. It configures PCI hardware, creates platform devices for detected media slots, routes shared IRQs to child slot handlers, and exports helper functions for child drivers.

Important APIs, types, and functions: `cb710_pci_update_config_reg()` updates a PCI config dword and is exported. `cb710_set_irq_handler()` installs per-slot IRQ callbacks under `chip->irq_lock` and is exported. `cb710_probe()` and `cb710_remove_one()` are the PCI lifecycle. `cb710_register_slot()` and `cb710_unregister_slot()` create/remove platform devices such as `cb710-mmc`, `cb710-ms`, and `cb710-sm`. `cb710_irq_handler()` fans the shared PCI IRQ out across registered slots.

Control flow: probe first applies hardware-specific PCI config writes, reads config register `0x48` to discover enabled slot bits, allocates a variable-sized `struct cb710_chip`, enables the PCI device with managed resources, maps BAR 0, requests the IRQ, allocates a platform id through `ida`, and registers platform slot devices for MMC, MemoryStick, and SmartMedia based on hardware mask bits. Remove unregisters slots in reverse order and frees the ID. Suspend frees the IRQ and resume requests it again.

State and persistence: `struct cb710_chip` holds mapped I/O base, slot array, slot count, slot mask, platform id, IRQ lock, and debug reference counts. `struct cb710_slot` holds per-slot I/O base, platform device, and child IRQ handler. Hardware state is partly persisted in PCI config registers touched by `cb710_pci_configure()`.

Dependencies and integration points: depends on PCI, platform devices, IDA, spinlocks, `linux/cb710.h`, and child slot drivers that bind to the registered platform devices and call `cb710_set_irq_handler()`. IRQ sharing is cooperative: children provide callbacks that return whether they handled an interrupt.

Risks: slot registration error paths unwind only previously registered slots; mistakes can leave platform devices registered or IDs leaked. Shared IRQ dispatch runs under a spinlock, so child IRQ handlers must be fast and cannot sleep. The driver uses magic PCI config values derived from a Windows driver, so hardware variants may be fragile. Debug assumption blocks use `BUG_ON()` for reference mismatches.

Test signals: probe on CB710/CB720 hardware with each slot mask combination, platform child device binding, shared IRQ delivery to MMC/MS/SM handlers, suspend/resume IRQ re-registration, remove/unbind cleanup, and debug-assumption builds.
