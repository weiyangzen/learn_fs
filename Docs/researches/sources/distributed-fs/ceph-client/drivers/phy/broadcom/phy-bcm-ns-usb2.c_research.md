# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-ns-usb2.c

Purpose: Programs the Broadcom Northstar USB2 PHY PLL divider based on the reference clock.

Important APIs and types: `struct bcm_ns_usb2` stores device, reference clock, PHY, clkset syscon regmap, and base control register. The only PHY operation is `.init`.

Control flow: probe maps the control register, looks up `brcm,syscon-clkset`, gets `phy-ref-clk`, creates the PHY, and registers a simple provider. Init enables the reference clock, reads its rate, derives PLL NDIV for a 1.92 GHz USB2 PLL target using the existing or default PDIV, unlocks DMU PLL settings with `0x0000ea68`, updates the NDIV field, relocks with zero, and disables the reference clock.

State and persistence: Software does not retain state. Hardware persists the computed PLL divider in the DMU USB2 control register until reprogrammed or reset.

Dependencies and integration: It depends on the clock framework, syscon regmap, BCMA DMU bit definitions, generic PHY, and `brcm,ns-usb2-phy` binding.

Risks and test signals: A zero reference clock rate returns `-EINVAL`. The divider math assumes integer division is acceptable for all supported ref clocks. Test with supported clock rates, clkset syscon failure, clock prepare failure, and USB2 link behavior after PLL relock.
