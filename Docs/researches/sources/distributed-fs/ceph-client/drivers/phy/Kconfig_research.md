# sources/distributed-fs/ceph-client/drivers/phy/Kconfig

Purpose: top-level Linux PHY subsystem Kconfig menu. It defines core PHY framework options, a few root-level PHY drivers, common-property KUnit support, and includes all vendor PHY submenus.

Important APIs, types, and functions: this is declarative Kconfig rather than C. Key symbols are `PHY_COMMON_PROPS`, `PHY_COMMON_PROPS_TEST`, `GENERIC_PHY`, `GENERIC_PHY_MIPI_DPHY`, and root drivers such as `PHY_AIROHA_PCIE`, `PHY_CAN_TRANSCEIVER`, `PHY_GOOGLE_USB`, `USB_LGM_PHY`, `PHY_LPC18XX_USB_OTG`, `PHY_NXP_PTN3222`, `PHY_PISTACHIO_USB`, `PHY_SNPS_EUSB2`, and `PHY_XGENE`.

Control flow: Kconfig evaluation presents `menu "PHY Subsystem"`, resolves dependencies such as `OF`, architecture gates, `USB_SUPPORT`, `RESET_CONTROLLER`, or `TYPEC`, applies `select GENERIC_PHY`/other support libraries, and recursively sources vendor files from `drivers/phy/allwinner/Kconfig` through `drivers/phy/xilinx/Kconfig`.

State and persistence: generated build configuration persists in `.config`; this file itself has no runtime state. Defaults such as `PHY_COMMON_PROPS_TEST default KUNIT_ALL_TESTS` influence test builds.

Dependencies and integration: integrates with kernel Kconfig, PHY core, DT binding helper code, USB, regulator, MFD/syscon, and numerous vendor directories. It is paired with `drivers/phy/Makefile`, where enabled symbols map to objects and subdirectories.

Risks: incorrect `select` entries can force incompatible support code into builds; missing `depends on` can break compile-test coverage or real architecture builds. Vendor submenu inclusion order affects menu organization but not runtime. Test signals include `olddefconfig`, `allyesconfig`, `allmodconfig`, architecture-specific builds, and KUnit execution for common PHY properties.
