# sources/distributed-fs/ceph-client/drivers/phy/nuvoton/phy-ma35d1-usb2.c

Purpose: This driver exposes the Nuvoton MA35D1 USB2 PHY as a generic PHY. It controls the PHY clock and programs a syscon register to reset the PHY, leave suspend, and poll for the 60 MHz UTMI clock-stable bit.

Important APIs/types/functions: `struct ma35_usb_phy` stores the clock, device, and system-controller regmap. Register constants define `MA35_SYS_REG_USBPMISCR`, `PHY0POR`, `PHY0SUSPEND`, `PHY0COMN`, and `PHY0DEVCKSTB`. PHY ops are `ma35_usb_phy_power_on()` and `ma35_usb_phy_power_off()`, registered via `ma35_usb_phy_ops`. Probe maps the syscon from `nuvoton,sys`, obtains clock index 0, creates the PHY, and registers `of_phy_simple_xlate`.

Control flow: On power-on, the driver enables the clock, reads `USBPMISCR`, and if the PHY is already in operation mode it only polls `PHY0DEVCKSTB`. Otherwise it asserts POR while setting suspend/operation bits, delays 20 microseconds, clears POR while leaving operation mode set, then polls for the UTMI clock to become stable. Timeout disables the clock and returns an error. Power-off only disables the clock.

State and persistence: Runtime state is minimal: clock enable count and hardware bits in the system register. There is no cached power state and no explicit suspend bit programming on power-off; the PHY register state may remain operational while its clock is disabled, depending on hardware behavior.

Dependencies and integration points: It depends on OF, syscon regmap, clock framework, platform devices, and generic PHY. Device-tree must provide compatible `nuvoton,ma35d1-usb2-phy`, a `nuvoton,sys` phandle, and a clock.

Risks: `regmap_read()` return values are not checked before using `val`, so bus errors may be treated as register contents. Only `-ETIMEDOUT` from the final poll disables the clock; other poll errors would currently return success unless they happen to equal timeout behavior. `of_clk_get()` is not devm-managed, so long-lived probe-failure paths after clock acquisition should be reviewed for clock reference cleanup.

Test signals: Probe should fail clearly when `nuvoton,sys` or the clock is missing. Runtime tests should verify clock enable/disable balance, `PHY0DEVCKSTB` polling, USB enumeration after repeated PHY power cycles, and timeout behavior when the stable bit never asserts.
