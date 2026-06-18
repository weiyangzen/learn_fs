# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_devlink.h

## Purpose
Declares the funeth driver's devlink lifecycle API. The header is intentionally small: it exposes allocation, free, registration, and unregistration helpers so `funeth_main.c` can bind a PCI-backed `struct fun_ethdev`/`struct fun_dev` instance to Linux devlink before netdev ports are registered.

## APIs and Types
Exports `fun_devlink_alloc(struct device *dev)`, `fun_devlink_free(struct devlink *devlink)`, `fun_devlink_register(struct devlink *devlink)`, and `fun_devlink_unregister(struct devlink *devlink)`. It depends only on `<net/devlink.h>` and forward usage of `struct device` from included kernel headers.

## Control Flow and Integration
The header is consumed by the funeth probe/remove path. Probe allocates devlink first, retrieves the driver-private `fun_ethdev` via `devlink_priv()`, initializes the core PCI/admin device, creates netdev ports, restarts service work, and then registers devlink. Remove reverses that order by unregistering devlink before SR-IOV teardown, service stop, port destruction, device disable, and devlink free.

## State and Persistence
This header owns no persistent state itself. Its API implies devlink lifetime must dominate all devlink port objects attached to per-port netdevs. Incorrect lifetime ordering can leave registered `devlink_port` objects referring to freed private data.

## Dependencies and Risks
The implementation is elsewhere; this contract assumes allocation returns a devlink whose private area is sized for `struct fun_ethdev`. Risk centers on ordering: `fun_devlink_free()` must not run while registered ports or netdevices still reference the devlink. Test signals include PCI probe/remove with devlink visible under `devlink dev`, hot-unplug, and failure injection at each probe unwind label.
