# sources/distributed-fs/ceph-client/drivers/net/ethernet/silan/Kconfig

Purpose: defines configuration entries for Silan Ethernet devices.

Important symbols: `NET_VENDOR_SILAN` gates the vendor menu and depends on PCI. `SC92031` is a tristate Silan SC92031 PCI Fast Ethernet driver that depends on PCI and selects CRC32.

Integration and state: controls compilation of `sc92031.o` through the Silan Makefile. No runtime state.

Risks and tests: incorrect dependencies can expose the driver on unsupported systems or miss CRC helpers. Test PCI-enabled and disabled config builds and module build for `SC92031=m`.
