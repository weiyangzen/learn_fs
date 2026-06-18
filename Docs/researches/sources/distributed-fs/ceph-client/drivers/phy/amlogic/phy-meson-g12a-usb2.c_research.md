# sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-g12a-usb2.c

Purpose: Initializes and tears down the USB2 PHY found on Meson G12A and A1 SoCs, including PLL setup, analog tuning, calibration bypass, and UTMI bus width declaration.

Important APIs and types: `enum meson_soc_id` selects G12A versus A1 tuning. `struct phy_meson_g12a_usb2_priv` stores device, regmap, xtal clock, reset, and SoC id. The `phy_ops` implement `.init` and `.exit`; mode selection is intentionally left to the UTMI bus.

Control flow: probe maps the PHY register block, records match data, creates a regmap, gets `xtal` and reset `phy`, deasserts reset, creates a generic PHY, sets bus width to 8, and registers the provider. Init enables the clock, resets the PHY, programs MPLL registers for 24 MHz to 480 MHz, applies SoC-specific analog and calibration values, tunes VBUS, disconnect threshold, and PMA update signals. Exit resets the PHY and disables the clock when reset succeeds.

State and persistence: The driver persists no dynamic link state; all hardware programming is redone on init. SoC variant data is immutable match state.

Dependencies and integration: It depends on clock/reset/regmap/generic PHY infrastructure and device-tree compatible strings `amlogic,g12a-usb2-phy` and `amlogic,a1-usb2-phy`. USB host/device controller glue consumes the PHY and handles mode externally.

Risks and test signals: PLL and analog constants are hardware-specific and not validated at runtime. A reset failure during exit leaves the clock enabled. Test G12A and A1 match data, clock enable failure rollback, PLL lock behavior on hardware, repeated init/exit, and USB high-speed enumeration with disconnect/attach threshold sensitivity.
