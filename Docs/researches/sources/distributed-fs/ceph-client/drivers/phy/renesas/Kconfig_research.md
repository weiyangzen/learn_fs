# sources/distributed-fs/ceph-client/drivers/phy/renesas/Kconfig

Purpose: Declares Renesas PHY driver configuration options for Ethernet SERDES, R-Car Gen2 USB, R-Car Gen3 PCIe/USB2/USB3, and RZ/G3E USB3.

Important APIs/types/functions: Defines `PHY_R8A779F0_ETHERNET_SERDES`, `PHY_RCAR_GEN2`, `PHY_RCAR_GEN3_PCIE`, `PHY_RCAR_GEN3_USB2`, `PHY_RCAR_GEN3_USB3`, and `PHY_RZ_G3E_USB3`. All select `GENERIC_PHY`; USB2 also depends on `EXTCON || !EXTCON`, `USB_SUPPORT`, and `REGULATOR`, and selects `MULTIPLEXER` and `USB_COMMON`.

Control flow: No runtime flow. Kconfig controls object inclusion and dependency visibility.

State and persistence: No runtime state. Kernel configuration choices persist in `.config`.

Dependencies and integration points: Integrates with the Renesas PHY Makefile and architecture guard `ARCH_RENESAS || COMPILE_TEST` for most newer options. `PHY_RCAR_GEN2` and `PHY_RCAR_GEN3_PCIE` depend directly on `ARCH_RENESAS`.

Risks: Narrow dependencies reduce compile-test coverage for older Gen2/Gen3 PCIe drivers. The file notes alphabetical sorting; adding entries out of order increases maintenance churn.

Test signals: Build all Renesas PHY configs under `ARCH_RENESAS`, compile-test the options that allow it, and verify selected helper symbols for USB2.
