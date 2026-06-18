# sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/Kconfig

## Purpose
This Kconfig fragment gates Tehuti ethernet driver visibility and build selection. It defines the vendor menu `NET_VENDOR_TEHUTI`, the legacy `TEHUTI` 10G driver, and the newer `TEHUTI_TN40` TN40xx driver.

## Important APIs, Types, and Functions
The relevant configuration symbols are `NET_VENDOR_TEHUTI`, `TEHUTI`, and `TEHUTI_TN40`. `NET_VENDOR_TEHUTI` is a boolean vendor menu depending on `PCI`. `TEHUTI` is a tristate for the older `tehuti.o` PCI driver. `TEHUTI_TN40` is a tristate for the `tn40xx` module and selects `PAGE_POOL`, `FW_LOADER`, and `PHYLINK`.

## Control Flow and State
There is no runtime control flow. Build-time state determines whether Tehuti-specific questions appear and whether the legacy or TN40 module objects are compiled. The selected helper subsystems are important runtime prerequisites: TN40 RX uses page_pool, firmware loading uses `request_firmware`, and link management uses phylink.

## Dependencies and Integration Points
Both drivers depend on PCI. `TEHUTI_TN40` integrates with `tn40.c`, `tn40_mdio.c`, and `tn40_phy.c` through the Makefile module definition. The help text documents currently supported TN40xx/AQR105-based adapters and the resulting module name `tn40xx`.

## Risks and Test Signals
The main risk is stale dependency modeling: if TN40 code starts using additional subsystems, missing `select` or `depends on` entries will surface as build failures in sparse randconfig coverage. Test signals are `oldconfig/menuconfig` visibility, `m` and `y` builds for both drivers, and randconfig combinations with PCI enabled but optional firmware/phylink/page_pool settings varied.
