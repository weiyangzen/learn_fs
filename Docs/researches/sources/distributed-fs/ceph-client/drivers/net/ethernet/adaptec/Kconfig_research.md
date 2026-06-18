# sources/distributed-fs/ceph-client/drivers/net/ethernet/adaptec/Kconfig

Purpose: this vendor Kconfig file declares the Adaptec Ethernet menu and the Starfire/DuraLAN PCI adapter driver option.

Important APIs, types, and functions: `config NET_VENDOR_ADAPTEC` is a boolean vendor gate, defaults to `y`, and depends on `PCI`. `config ADAPTEC_STARFIRE` is a tristate depending on `PCI`, selecting `CRC32` and `MII`, with help text describing Adaptec Starfire/DuraLAN 64-bit PCI boards and module name `starfire`.

Control flow: the top-level Ethernet Kconfig sources this file under `if ETHERNET`. If PCI is unavailable or the vendor gate is off, `ADAPTEC_STARFIRE` is hidden. When enabled, `adaptec/Makefile` builds `starfire.o`.

State and persistence: only Kconfig state in `.config`; no runtime state.

Dependencies and integration points: integrates with `drivers/net/ethernet/Kconfig`, the parent Ethernet Makefile, `adaptec/Makefile`, and `starfire.c`. The `CRC32` and `MII` selections reflect library requirements of the driver.

Risks: the vendor gate defaulting to `y` exposes the menu broadly on PCI systems, so driver dependencies must be accurate. Removing selected helper libraries would break link/build. Help text distinguishes older 32-bit boards that use the tulip driver; incorrect user selection may bind unsupported hardware only if PCI IDs overlap in the driver.

Test signals: Kconfig parsing with and without PCI, `CONFIG_ADAPTEC_STARFIRE=m/y` builds, selected `CRC32` and `MII` symbols, and module output named `starfire`.
