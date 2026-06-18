# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/adi/Kconfig

Purpose: this Kconfig fragment introduces the Analog Devices Ethernet vendor menu and the ADIN1110/ADIN2111 MAC-PHY driver option. It controls whether the ADI subtree appears in networking driver configuration and whether `adin1110.c` can be built.

Important APIs, types, and functions: the relevant symbols are `NET_VENDOR_ADI` and `ADIN1110`. `NET_VENDOR_ADI` is a boolean vendor gate, defaults to `y`, and depends on `SPI`. `ADIN1110` is a tristate prompt for "Analog Devices ADIN1110 MAC-PHY", depends on `SPI && NET_SWITCHDEV`, and selects `CRC8` and `PHYLIB`.

Control flow: Kconfig first offers the vendor gate. If `NET_VENDOR_ADI` is enabled, the nested `ADIN1110` option becomes visible. Selecting the driver as built-in or module causes the matching Makefile to include `adin1110.o` through `CONFIG_ADIN1110`.

State and persistence: there is no runtime state. Persistence is the kernel build configuration recorded in `.config`, which determines whether ADI questions are skipped and whether the driver is omitted, built in, or built as a module.

Dependencies and integration points: the file integrates with the kernel networking drivers Kconfig hierarchy. Its dependency on `SPI` reflects the MAC-PHY transport, `NET_SWITCHDEV` reflects the driver's bridge/FDB offload hooks, `CRC8` supports optional SPI/data CRC handling, and `PHYLIB` supports the internal ADIN1100 PHY instances exposed through an MDIO bus.

Risks: the vendor gate depends on `SPI`, so all ADI Ethernet options are hidden on builds without SPI even if a future ADI Ethernet driver did not use SPI. `ADIN1110` selects switchdev and phylib dependencies indirectly but does not express OF/GPIO/regulator dependencies because those are optional or provided by broader kernel APIs. Configuration testing should verify module builds when `NET_SWITCHDEV` is available.

Test signals: expected signals are `CONFIG_NET_VENDOR_ADI=y` making the vendor menu visible, `CONFIG_ADIN1110=m` producing `adin1110.ko`, successful dependency resolution for `CRC8` and `PHYLIB`, and absence of the option when `SPI` or `NET_SWITCHDEV` is unavailable.
