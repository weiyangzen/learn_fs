# sources/distributed-fs/ceph-client/drivers/phy/lantiq/Kconfig

## Purpose
Kconfig entries for Lantiq/Intel XWAY USB2 RCU PHY and VRX200/ARX300 PCIe PHY.

## Important APIs, types, and functions
Defines `PHY_LANTIQ_VRX200_PCIE` and `PHY_LANTIQ_RCU_USB2`.

## Control flow
Symbols gate object compilation. PCIe requires OF, IOMEM, and selects generic PHY plus regmap MMIO. USB2 requires OF and selects generic PHY.

## State and persistence
Build configuration only.

## Dependencies and integration points
Consumed by the Lantiq Makefile; architecture gate is `SOC_TYPE_XWAY` or `COMPILE_TEST`.

## Risks and test signals
Risk is missing dependency if drivers evolve. Test `COMPILE_TEST` and XWAY target configs.
