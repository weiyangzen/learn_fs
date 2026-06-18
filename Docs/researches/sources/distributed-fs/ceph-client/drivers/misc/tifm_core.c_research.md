# sources/distributed-fs/ceph-client/drivers/misc/tifm_core.c

## Purpose
`tifm_core.c` implements the TI FlashMedia bus, adapter class, workqueue, media-device allocation, driver registration, and DMA helper APIs used by TIFM host and media drivers.

## Important APIs, Types, and Functions
Exported APIs include `tifm_alloc_adapter()`, `tifm_add_adapter()`, `tifm_remove_adapter()`, `tifm_free_adapter()`, `tifm_alloc_device()`, `tifm_free_device()`, `tifm_eject()`, `tifm_has_ms_pif()`, `tifm_map_sg()`, `tifm_unmap_sg()`, `tifm_queue_work()`, `tifm_register_driver()`, and `tifm_unregister_driver()`. Bus callbacks are `tifm_bus_match()`, `tifm_uevent()`, `tifm_device_probe()`, `tifm_device_remove()`, and optional PM callbacks. Global state includes `workqueue`, `tifm_adapter_idr`, and `tifm_adapter_lock`.

## Control Flow
`tifm_init()` creates a freezable workqueue, registers the `tifm` bus, and registers the `tifm_adapter` class. Host drivers allocate an adapter, add it to the IDR/class, and allocate/register socket devices as media appears. The bus matches socket type against a `tifm_driver` ID table, calls media driver probe/remove, and emits `TIFM_CARD_TYPE` uevents. Removing an adapter flushes pending work, unregisters all socket devices, removes the IDR entry, and deletes the adapter device.

## State and Persistence
Adapter IDs are allocated from an IDR protected by a spinlock. The workqueue persists for the module lifetime. Socket devices hold type, socket ID, event callbacks, and device-core references. State is dynamic only and disappears at driver unload or adapter removal.

## Dependencies and Integration Points
The core depends on Linux device model bus/class APIs, IDR, workqueues, PCI DMA helpers for scatter-gather mapping, and TIFM structures from `<linux/tifm.h>`. It is consumed by `tifm_7xx1.c` and media-specific MemoryStick/SD/xD drivers.

## Risks and Edge Cases
`type_show()` uses `sprintf()` without a newline and older sysfs style. `tifm_device_probe()` takes an extra reference and leaves it until remove, so probe failure must correctly drop it. DMA helpers assume the socket parent is a PCI device. Adapter removal flushes the global workqueue, affecting work for all adapters.

## Test Signals
Validate bus/class registration, media type matching and uevents, probe/remove reference balance, adapter ID allocation/removal, global workqueue flushing, DMA map/unmap through socket parent, eject delegation, and PM callback forwarding.
