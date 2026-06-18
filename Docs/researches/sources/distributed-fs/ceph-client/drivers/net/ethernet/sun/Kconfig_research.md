# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/Kconfig

Purpose: Kconfig menu for Sun Ethernet drivers.

Important symbols: `NET_VENDOR_SUN` gates the menu and defaults to yes when SUN3, SBUS, PCI, or SUN_LDOMS is available. Child tristates are `HAPPYMEAL`, `SUNBMAC`, `SUNQE`, `SUNGEM`, `CASSINI`, `SUNVNET_COMMON`, `SUNVNET`, `LDMVSW`, and `NIU`. Several physical NICs select `CRC32`. Logical-domain virtual networking depends on `SUN_LDOMS` and `INET`, with `SUNVNET` and `LDMVSW` depending on `SUNVNET_COMMON`.

Control flow: Kconfig exposes the vendor menu only on relevant buses/architectures. Selected symbols drive kbuild object inclusion through the sibling Makefile.

State and persistence: persistent state is kernel `.config` selection. The vendor bool does not build code directly; it controls prompt visibility.

Dependencies and integration: integrates with the Linux network driver Kconfig tree and maps help text to modules such as `sunhme`, `sunbmac`, and `sunqe`.

Risks and test signals: dependency errors can hide valid drivers or expose unbuildable options. Test with `olddefconfig`, allmodconfig, and symbol visibility on SBUS/PCI/SUN_LDOMS configurations.
