# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/sysfs.c

`sysfs.c` exposes b43 sysfs controls, currently the `interference` attribute for G-PHY interference mitigation.

`get_integer()` parses up to ten bytes of decimal input. `b43_attr_interfmode_show()` requires `CAP_NET_ADMIN`, locks `wldev->wl->mutex`, rejects non-G PHY with `-ENOSYS`, and emits the current `wldev->phy.g->interfmode`. `b43_attr_interfmode_store()` requires the same capability, maps input 0-3 to `B43_INTERFMODE_*`, locks, and invokes `wldev->phy.ops->interf_mitigation()` when present. `DEVICE_ATTR(interference, 0644, ...)` defines the attribute; `b43_sysfs_register()` and `b43_sysfs_unregister()` create and remove it.

State persists in driver PHY state and whatever hardware changes the mitigation operation performs. Dependencies include Linux capability/sysfs APIs, b43 device conversion helpers, `main.h`, and `phy_common.h`. Registration is tied to device initialization and teardown.

Risks include loose parsing via `simple_strtol()`, show documenting only modes 0-2 while store accepts mode 3, and lifecycle mismatches during device removal. Tests should cover privileged/unprivileged access, valid and invalid input, G-PHY versus non-G-PHY devices, and sysfs removal on teardown.
