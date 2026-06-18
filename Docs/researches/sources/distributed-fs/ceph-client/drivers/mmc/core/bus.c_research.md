# sources/distributed-fs/ceph-client/drivers/mmc/core/bus.c

## Purpose
MMC card bus driver-model integration: card allocation/registration, uevents, sysfs type, driver probe/remove/shutdown, PM callbacks, and teardown.

## Important APIs, Types, And Functions
- `mmc_bus_type` defines the `mmc` bus.
- `mmc_register_bus()`/`mmc_unregister_bus()` manage bus lifetime.
- `mmc_register_driver()`/`mmc_unregister_driver()` bind media drivers.
- `mmc_alloc_card()`, `mmc_add_card()`, and `mmc_remove_card()` manage card devices.

## Control Flow
Core init registers the bus. Protocol attach code allocates a card, fills identity/type data, and adds it. The driver core emits uevents and probes drivers such as `mmcblk`. Remove/shutdown/PM callbacks delegate to bound media driver and host `bus_ops`.

## State And Persistence
State lives in registered `struct mmc_card` devices, including present flags, OF references, debugfs roots, runtime PM, and CQE enabled state.

## Dependencies And Integration Points
Depends on Linux driver core, sysfs, PM, OF, SDIO CIS cleanup, debugfs helpers, and MMC host/card definitions. Emits `MMC_TYPE`, `SDIO_ID`, `MMC_NAME`, and `MODALIAS=mmc:block`.

## Risks And Edge Cases
Uevent modalias drives block-driver autoloading. Shutdown stops host detection before optional bus shutdown. Removal must balance OF/device refs and disable CQE.

## Test Signals
Correct card probe logs, udev variables, `mmc_block` autoload, suspend/resume callback ordering, hotplug removal, and CQE disable on remove.
