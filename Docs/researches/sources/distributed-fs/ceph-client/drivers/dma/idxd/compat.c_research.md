# sources/distributed-fs/ceph-client/drivers/dma/idxd/compat.c

## Purpose
`compat.c` provides a legacy `dsa` driver facade with custom bind/unbind attributes that redirect devices to the real IDXD subdrivers.

## Important APIs, Types, And Functions
Important pieces are `bind_store`, `unbind_store`, `DRIVER_ATTR_IGNORE_LOCKDEP`, compatibility attribute groups, and `dsa_drv`.

## Control Flow
The compat driver matches no device types. A sysfs bind write finds a device by name, chooses `idxd`, `dmaengine`, or `user` based on device/WQ type, and attaches that alternate driver. Unbind detaches the current driver.

## State And Persistence Behavior
It changes driver-core binding state only and adds writable driver attributes while suppressing default bind attrs.

## Dependencies And Integration Points
It depends on the dsa bus, driver-core attach/detach helpers, and IDXD type helpers.

## Risks And Test Signals
The code references `device_driver_detach()` externally and relies on WQ type being configured before bind. Test sysfs bind/unbind redirection without lockdep warnings.
