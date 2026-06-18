# sources/distributed-fs/ceph-client/drivers/phy/ti/phy-am654-serdes.c

## Purpose
AM654x SERDES generic PHY and clock provider. It programs PCIe or USB3 SERDES recipes, arbitrates the lane-function mux, exposes PHY reset/init/power operations, and registers three SERDES reference-clock mux outputs.

## APIs, Flow, And State
Main state is `struct serdes_am654`, with the MMIO `regmap`, `regmap_field` array, mux control, current PHY type, busy flag, and clock provider data. `serdes_am654_xlate()` translates PHY phandles, rejects concurrent use with `busy`, selects the mux lane function, and records `PHY_TYPE_PCIE` or `PHY_TYPE_USB3`. `serdes_am654_init()` dispatches to `serdes_am654_pcie_init()` or `serdes_am654_usb3_init()`. Power-on enables PLL, enables TX/RX, and polls `CMU_OK_I_0`; power-off disables TX/RX and PLL. Clock mux operations map a shared clock-select register through a static 16-entry table.

## Dependencies And Integration
Uses generic PHY, common clock, mux consumer, regmap/regmap-field, platform MMIO, runtime PM, syscon clock-select phandle parsing, and DT binding PHY type IDs. It registers both an OF PHY provider and an OF clock provider.

## Risks And Tests
Risks include a single `busy` flag limiting sharing, USB3 register recipe writes that do not propagate errors, limited rollback on power-on failure, and reliance on a complete clock mux table. Test signals: probe with three output clocks, PCIe/USB3 init, PLL and CMU polling, clock parent switching, xlate `-EBUSY`, mux deselect on release, and provider cleanup on remove.
