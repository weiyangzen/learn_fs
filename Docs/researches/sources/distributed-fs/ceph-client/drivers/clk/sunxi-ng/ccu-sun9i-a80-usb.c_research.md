# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun9i-a80-usb.c

## Purpose
This provider models the A80 USB CCU block. It exposes bus gates for HCI controllers, OHCI functional gates, USB PHY/HSIC gates, and reset lines for HCI and PHY/HSIC domains.

## Important APIs, Types, And Functions
Important data includes firmware parent arrays for `hosc` and `bus`, gate descriptors such as `bus_hci0_clk`, `usb_ohci0_clk`, `usb0_phy_clk`, `usb1_hsic_clk`, `usb_hsic_clk`, the onecell clock table, reset map, descriptor, and `sun9i_a80_usb_clk_probe()`.

## Control Flow
Probe maps registers, obtains and enables the `bus` clock to access the USB CCU registers, then registers the CCU with `devm_sunxi_ccu_probe()`. On failure it disables the bus clock.

## State And Persistence
The driver has no persistent state beyond live hardware gates and resets. The bus clock remains enabled after successful probe to keep this secondary CCU accessible.

## Dependencies And Integration Points
Dependencies are sunxi-ng common/gate/reset helpers, Linux platform/clock APIs, A80 USB bindings, and firmware-named parents. It integrates with EHCI/OHCI/HCI controllers, USB PHYs, HSIC PHYs, and reset-controller consumers.

## Risks
Main risks are parent naming and register access ordering. If the `bus` clock is unavailable or disabled, the provider cannot safely touch registers. HCI and PHY reset bits share compact registers, so bit mistakes can break multiple ports.

## Test Signals
Test by probing `allwinner,sun9i-a80-usb-clks`, checking clk-summary for HCI/OHCI/PHY/HSIC clocks, enumerating USB devices on all ports, validating HSIC if present, and exercising reset lines during controller probe and suspend/resume.
