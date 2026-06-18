# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/Kconfig

## Purpose
Defines build options for Atheros/Qualcomm Ethernet drivers, including the platform AG71XX MAC and PCI ALX driver covered in this work item.

## Important APIs, Types, and Functions
`NET_VENDOR_ATHEROS` gates the vendor subtree and depends on `PCI || ATH79 || COMPILE_TEST`. `AG71XX` is a tristate for AR7xxx/AR9xxx built-in MACs, depends on `ATH79 || COMPILE_TEST`, selects `PHYLINK`, and implies `NET_SELFTESTS`. `ALX` is a tristate for AR816x/AR817x PCIe adapters, depends on `PCI`, and selects `CRC32` and `MDIO`. Additional ATL variants are declared but outside this source set.

## Control Flow and State
The file has build-time control only. Its symbols decide whether Makefiles descend into `ag71xx.o` or `alx/` and which networking subsystems are guaranteed available.

## Dependencies and Integration Points
Dependencies mirror implementation needs: AG71XX uses platform/OF/phylink/selftest hooks, while ALX uses PCI, MDIO ioctl plumbing, CRC multicast hashing, MSI/MSI-X, and hardware register access.

## Risks and Test Signals
Important test signals are successful allmodconfig and targeted builds with `AG71XX=m/y`, `ALX=m/y`, `NET_VENDOR_ATHEROS=n`, PCI disabled, and ATH79 disabled plus `COMPILE_TEST`. Misdeclared dependencies show up as missing symbols in these matrix builds.
