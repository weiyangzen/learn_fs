# sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/Kconfig

Purpose: Kconfig menu for Mucse Ethernet devices. It gates visibility of Mucse-specific drivers behind `NET_VENDOR_MUCSE` and defines the `MGBE` tristate for the rnpgbe PCIe 1GbE adapter driver.

Important symbols: `NET_VENDOR_MUCSE` is a vendor-menu boolean defaulting to `y`. `MGBE` is a tristate depending on `PCI`; when built as a module, the module name is `rnpgbe`.

Control flow: configuration-only. If the vendor option is disabled, the `MGBE` prompt is hidden and the Makefiles will not include rnpgbe objects.

State and persistence: persistent effect is the generated kernel `.config`, which controls compilation and module availability.

Dependencies and integration: integrated from the broader Ethernet vendor Kconfig tree. The help text points to `Documentation/networking/device_drivers/ethernet/mucse/rnpgbe.rst`.

Risks: `MGBE` has no explicit dependency on firmware mailbox support beyond PCI, so compile-time coverage must catch missing includes. The vendor default of `y` exposes the driver prompt broadly.

Test signals: Kconfig olddefconfig/menuconfig coverage for built-in, module, and disabled modes; verify `CONFIG_MGBE=m` builds `rnpgbe.ko`.
