# sources/distributed-fs/ceph-client/drivers/phy/socionext/Kconfig

Purpose: Kconfig menu entries for Socionext UniPhier PHY drivers: USB2, USB3, PCIe, and AHCI.

Important APIs, types, and functions: declares `PHY_UNIPHIER_USB2`, `PHY_UNIPHIER_USB3`, `PHY_UNIPHIER_PCIE`, and `PHY_UNIPHIER_AHCI`. All depend on UniPhier or compile-test, OF, and MMIO support; all select `GENERIC_PHY`; USB2 also selects `MFD_SYSCON`. PCIe defaults to `PCIE_UNIPHIER`; AHCI defaults to `SATA_AHCI_PLATFORM`.

Control flow: not executable, but it determines which object files appear in the build and which framework dependencies are enabled. `PHY_UNIPHIER_USB3` builds both HS and SS PHY drivers through the Makefile.

State and persistence: no runtime state. Configuration state affects built modules and automatic defaults when matching controller drivers are enabled.

Dependencies and integration points: ties these drivers to generic PHY consumers in UniPhier USB, PCIe, and SATA/AHCI controller stacks. Help text documents SoC coverage and the special Pro4 USB2-versus-USB3-HS PHY selection.

Risks: defaulting PCIe/AHCI PHYs from controller symbols can surprise minimal builds. USB3 symbol controls two separate object files, so partial HS/SS build selection is not possible.

Test signals: `allyesconfig`, `allmodconfig`, and compile-test builds; dependency checks that syscon support is present for USB2; controller smoke tests with matching PHY symbols built-in and modular.
