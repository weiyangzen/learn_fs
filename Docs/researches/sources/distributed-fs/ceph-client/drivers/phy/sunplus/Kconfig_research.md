# sources/distributed-fs/ceph-client/drivers/phy/sunplus/Kconfig

Purpose: Kconfig entry for Sunplus SP7021 USB2 PHY support.

Important APIs, types, and functions: `PHY_SUNPLUS_USB` depends on OF and `SOC_SP7021 || COMPILE_TEST`, selects `GENERIC_PHY`, and describes USB2 features including battery charger, synchronous signals, power modes, and speed support.

Control flow: build-time only.

State and persistence: none.

Dependencies and integration points: enables `phy-sunplus-usb2.o` for SP7021 USB controller consumers.

Risks: driver uses clocks, resets, and nvmem but Kconfig only selects generic PHY; compile-test should ensure implicit dependencies are adequate.

Test signals: SP7021 defconfig and compile-test builds, plus USB2 controller probe with the PHY symbol enabled.
