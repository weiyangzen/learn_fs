# sources/distributed-fs/ceph-client/drivers/pci/hotplug/shpchp_core.c

## Purpose
Registers the SHPC PCI driver, probes SHPC-capable bridges, initializes controller and slot objects, exposes hotplug slot callbacks, and tears controllers down on remove.

## Important APIs, Types, and Functions
Key functions are `shpc_probe()`, `shpc_remove()`, `init_slots()`, `cleanup_slots()`, and hotplug callbacks for attention, enable, disable, power, attention, latch, and adapter status. Module parameters are `shpchp_poll_mode` and `shpchp_poll_time`.

## Control Flow
Probe filters for SHPC capability or AMD Golam, declines devices controlled by firmware/ACPI, allocates a controller, calls `shpc_init()` for hardware/MMIO/IRQ setup, registers per-slot hotplug entries, creates the controller sysfs resource file, and marks the PCI device SHPC-managed. Slot initialization allocates one `struct slot` per hardware slot, creates a per-slot workqueue, initializes delayed button work and locks, registers with the PCI hotplug core, caches initial status, and links the slot to the controller. Remove clears management state, removes sysfs, releases hardware resources, and frees the controller.

## State and Persistence Behavior
Persistent state includes module parameters, `pdev->shpc_managed`, controller MMIO/IRQ/timer resources, per-slot workqueues and cached status, and hotplug registration. Hardware state is initialized in `shpc_init()` and masked during release.

## Dependencies and Integration Points
Depends on PCI driver core, PCI hotplug registration, ACPI hotplug ownership checks, SHPC hardware setup in `shpchp_hpc.c`, slot operation logic in `shpchp_ctrl.c`, and resource reporting in `shpchp_sysfs.c`.

## Risks
Failure paths must avoid double cleanup because `shpchp_release_ctlr()` already calls `cleanup_slots()`. Per-slot workqueues and delayed work must be canceled before free. Capability detection includes device-specific exceptions. Firmware-controlled hotplug must not be claimed by this driver.

## Test Signals
Probe/remove SHPC and non-SHPC bridges, ACPI ownership refusal, polling and interrupt modes, multi-slot registration, sysfs file creation failure, status cache fallback, and module parameter changes.
