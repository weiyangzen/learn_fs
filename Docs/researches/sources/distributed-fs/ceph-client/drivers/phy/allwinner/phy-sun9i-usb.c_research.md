# sources/distributed-fs/ceph-client/drivers/phy/allwinner/phy-sun9i-usb.c

Purpose: Allwinner sun9i A80 USB PHY driver for individual USB2 host PHYs, including optional HSIC mode.

Important APIs, types, and functions: `struct sun9i_usb_phy` stores the generic PHY, PMU MMIO, reset, main clock, optional HSIC 12 MHz clock, and `enum usb_phy_interface` type. `sun9i_usb_phy_passby` toggles AHB burst, alignment, ULPI bypass, and HSIC-specific PMU bits. PHY ops are init and exit.

Control flow: probe reads PHY interface mode from DT. HSIC mode acquires `hsic_480M`, `hsic_12M`, and `hsic` reset; non-HSIC mode acquires `phy` clock and reset. It maps PMU resource 0, creates the PHY, stores driver data, and registers a simple provider. Init enables clocks, deasserts reset, and enables passby. Exit disables passby, asserts reset, and disables clocks.

State and persistence: runtime state is clock/reset state, PMU passby bits, and PHY type. No persistent storage.

Dependencies and integration: generic PHY, USB OF mode helper, clock/reset frameworks, platform MMIO, and compatible `allwinner,sun9i-a80-usb-phy`.

Risks: HSIC clock/reset names differ from regular PHY names, so DT binding errors lead to probe failure. `clk_disable_unprepare` is called on `hsic_clk` in exit even for non-HSIC mode; because the field is zeroed by `devm_kzalloc`, this relies on common clock helpers tolerating NULL. Test signals include regular and HSIC DT nodes, init failure unwinding at each clock/reset stage, and host controller enumeration after passby enable.
