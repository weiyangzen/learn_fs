## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/Kconfig

Purpose: Kconfig menu entries for aQuantia/Marvell Ethernet drivers.

Important APIs/types: defines `NET_VENDOR_AQUANTIA` vendor menu bool and `AQTION` tristate driver option. `AQTION` depends on PCI and on either MACsec support being enabled or MACsec being disabled (`MACSEC || MACSEC=n`) so the driver can reference optional MACsec integration safely.

Control flow: no runtime control flow; controls visibility and build selection. When vendor support is enabled, `AQTION` exposes the Atlantic AQtion driver.

State and persistence: Kconfig state persists in kernel build configuration only.

Dependencies/integration: tied to `drivers/net/ethernet/aquantia/Makefile`, which descends into `atlantic/` when `CONFIG_AQTION` is selected.

Risks: dependency changes can accidentally hide the driver, build it without required PCI support, or break optional MACsec combinations.

Test signals: `make menuconfig` visibility, builds for `AQTION=m/y`, and builds with `MACSEC=y`, `MACSEC=m`, and `MACSEC=n` where valid.
