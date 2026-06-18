# sources/distributed-fs/ceph-client/drivers/phy/amlogic/Makefile

Purpose: kbuild object mapping for Amlogic/Meson PHY drivers.

Important APIs, types, and functions: maps Meson Kconfig symbols to objects: `phy-meson8-hdmi-tx.o`, `phy-meson8b-usb2.o`, `phy-meson-gxl-usb2.o`, `phy-meson-g12a-usb2.o`, `phy-meson-g12a-usb3-pcie.o`, `phy-meson-g12a-mipi-dphy-analog.o`, `phy-meson-axg-pcie.o`, `phy-meson-axg-mipi-pcie-analog.o`, and `phy-meson-axg-mipi-dphy.o`.

Control flow: when the parent Makefile descends into `amlogic/`, kbuild includes each object based on its `CONFIG_PHY_*` value.

State and persistence: no runtime state; only build outputs according to `.config`.

Dependencies and integration: paired with `drivers/phy/amlogic/Kconfig` and the Meson source files in the same directory.

Risks: symbol/object drift is the main risk. Combo PHYs and analog/digital MIPI split drivers require all relevant objects to be selectable together through Kconfig. Test signals include `make drivers/phy/amlogic/`, `allmodconfig`, and ensuring selected options produce expected built-in or module artifacts.
