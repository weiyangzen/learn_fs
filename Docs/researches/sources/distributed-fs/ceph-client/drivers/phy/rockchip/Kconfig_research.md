# sources/distributed-fs/ceph-client/drivers/phy/rockchip/Kconfig

## Purpose
This Kconfig fragment declares build options for Rockchip PHY drivers under `drivers/phy/rockchip`. It controls which PHY implementations are compiled and which common kernel facilities are selected for each hardware block.

## Important APIs, Types, And Functions
The file is declarative Kconfig. Important symbols in this subset are `PHY_ROCKCHIP_DP`, `PHY_ROCKCHIP_DPHY_RX0`, `PHY_ROCKCHIP_EMMC`, `PHY_ROCKCHIP_INNO_CSIDPHY`, `PHY_ROCKCHIP_INNO_DSIDPHY`, `PHY_ROCKCHIP_INNO_HDMI`, and `PHY_ROCKCHIP_INNO_USB2`. Other folder symbols include NANENG combo, PCIe, Samsung DCPHY/HDPTX, SNPS PCIe3, TYPEC, legacy USB, and USBDP.

## Control Flow
There is no runtime control flow. During configuration, each `tristate` controls whether the corresponding object is omitted, built-in, or modular. `depends on` gates choices to Rockchip architectures, device tree, compile-test cases, clock framework, I/O memory, extcon, USB, or TYPE-C support. `select` pulls in generic PHY, MIPI D-PHY helpers, MFD syscon, reset controller, USB common, and rational arithmetic helpers as needed.

## State And Persistence
Configuration state persists in the kernel `.config`. The choices determine module names and whether downstream platform devices can bind at runtime.

## Dependencies And Integration Points
The Kconfig symbols are consumed by the Rockchip Makefile. They integrate with generic PHY subsystem availability and enforce dependencies needed by source files, such as `COMMON_CLK` for HDMI/USB2 clock providers, `EXTCON` and `USB_SUPPORT` for Innosilicon USB2, and `GENERIC_PHY_MIPI_DPHY` for DPHY drivers.

## Risks And Test Signals
Dependency mistakes appear as build failures under randconfig or missing drivers on Rockchip platforms. Compile-test coverage is uneven: some options require `ARCH_ROCKCHIP && OF`, while others allow `COMPILE_TEST`. Test signals include `make olddefconfig` symbol resolution, module names matching help text, and all selected source files building with their declared dependencies.
