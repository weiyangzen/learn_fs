<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/Kconfig

Purpose: defines the build-time configuration surface for MDIO helper modules, MDIO controller drivers, MDIO-over-transport libraries, and MDIO bus multiplexers under `PHYLIB`.

Important APIs/types/functions: Kconfig symbols include helper accessors `FWNODE_MDIO`, `OF_MDIO`, `ACPI_MDIO`; bus controllers such as `MDIO_AIROHA`, `MDIO_ASPEED`, `MDIO_BCM_IPROC`, `MDIO_IPQ4019`, `MDIO_REALTEK_RTL9300`; library symbols `MDIO_BITBANG`, `MDIO_I2C`, `MDIO_REGMAP`, `MDIO_CAVIUM`; and mux symbols `MDIO_BUS_MUX*`.

Control flow: the file gates all definitions under `if PHYLIB`. Several symbols are silent libraries selected by concrete drivers (`MDIO_CAVIUM`, `MDIO_BUS_MUX`), while others are user-visible tristate choices. Dependencies express architecture, OF/ACPI, HAS_IOMEM, COMMON_CLK, PCI, USB, GPIOLIB, REGMAP, and MUX subsystem requirements.

State and persistence: Kconfig state persists in kernel build configuration. Selected symbols determine which object files are built and which helper APIs are available to other drivers.

Dependencies/integration: integrates with `drivers/net/mdio/Makefile`, phylib, OpenFirmware/ACPI discovery layers, and platform-specific SoC options. Defaults are conservative except for architecture defaults such as Broadcom iProc and Meson mux modules.

Risks and test signals: risks are missing `select` dependencies for helper libraries, overbroad `COMPILE_TEST`, link failures from silent symbols, and configuration combinations that compile a driver without required firmware APIs. Test signals are `allmodconfig`, `allyesconfig`, architecture defconfigs, and randconfig coverage for each dependency branch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/Kconfig -->
