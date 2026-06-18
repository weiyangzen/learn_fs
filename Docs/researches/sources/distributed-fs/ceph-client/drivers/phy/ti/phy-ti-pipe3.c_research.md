# sources/distributed-fs/ceph-client/drivers/phy/ti/phy-ti-pipe3.c

## Purpose
TI PIPE3 PHY driver for USB3, SATA, and PCIe. It programs protocol DPLL settings, RX calibration registers, control-module/syscon power bits, PCIe PCS delay, and SATA errata handling.

## APIs, Flow, And State
`struct ti_pipe3` stores PLL/RX/TX bases, clocks, control/syscon references, mode, DPLL maps, calibration settings, and SATA refclk state. Probe selects mode data by compatible, maps resources, resolves syscon/control-module helpers, obtains clocks, keeps SATA refclk on for erratum i783, creates generic PHY, powers it off, and registers provider. Init enables clocks, programs PCIe PCS delay for PCIe, otherwise wakes/programs DPLL and calibrates RX. Power-on writes clock frequency and TX/RX commands, with TX-before-RX for USB/SATA and simultaneous TX/RX for PCIe. Exit idles DPLL, waits powerdown, handles SATA soft reset, and disables clocks.

## Dependencies And Integration
Uses generic PHY, OMAP control PHY helpers, syscon/regmap, clocks, runtime PM, named platform resources, and OF match data. Consumed by USB3, SATA, and PCIe controllers.

## Risks And Tests
Some power-on regmap writes are unchecked, clock/resource rules vary by mode, and SATA intentionally holds refclk enabled. Test all compatibles, DPLL maps by sysclk rate, PLL lock/idle timeouts, PCIe PCS syscon/control paths, SATA pllreset presence, clock balancing, and protocol link training.
