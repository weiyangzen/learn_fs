# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_devlink.h

Purpose: Declares Ionic devlink and firmware update entry points.

Important APIs/types/functions: Exposes `ionic_firmware_update()`, `ionic_devlink_alloc()`, `ionic_devlink_free()`, `ionic_devlink_register()`, and `ionic_devlink_unregister()`.

State and dependencies: Includes `<net/devlink.h>` and forward-relies on Ionic LIF/device definitions in including C files. The firmware update API accepts a kernel firmware object and netlink extack for user-visible errors.

Risks and test signals: Callers must register only after the LIF/netdev is allocated and unregister before freeing embedded devlink port state. Build and runtime tests should cover devlink disabled impossible by Kconfig selection, firmware flash with invalid device state, and probe error unwind.
