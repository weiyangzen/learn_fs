# sources/distributed-fs/ceph-client/drivers/phy/intel/phy-intel-lgm-combo.c

## Purpose
Intel Lightning Mountain ComboPHY provider. It supports two internal PHY lanes, selectable PCIe/XPCS/SATA mode, optional dual-lane aggregation, clock/refclk gating, resets, and XPCS RX adaptation calibration.

## Important APIs, types, and functions
- `struct intel_combo_phy` stores shared clocks, resets, app/core MMIO, syscfg/hsiocfg regmaps, mode, aggregation, init count, and mutex.
- `struct intel_cbphy_iphy` stores per-lane PHY and app reset.
- `intel_cbphy_fwnode_parse()` reads clocks/resets, named resources, `intel,syscfg`, `intel,hsio`, `intel,phy-mode`, and optional `intel,aggregation`.
- `intel_cbphy_init()/exit()` serialize shared power and per-lane enable/disable with `init_cnt`.
- `intel_cbphy_calibrate()` triggers XPCS RX adaptation and polls ACK.

## Control flow
Probe parses resources and creates one or two PHYs depending on aggregation. Init powers the shared core on first user, sets mode, enables the requested lane (and lane 1 too in dual-lane mode), deasserts app reset, and enables PCIe pad refclk if needed. Exit decrements `init_cnt`, disables refclk, powers off lanes, and shuts down shared clocks/resets when count reaches zero.

## State and persistence
State is in `init_cnt`, selected mode/aggregation, MMIO/regmap registers, and reset/clock enable state. No persistence. Mutex protects shared init count and mode programming.

## Dependencies and integration points
Uses generic PHY, common clock, reset controls, regmap/syscon references via fwnode, OF xlate, and `dt-bindings/phy/phy.h`. Consumers pass lane ID in the PHY phandle.

## Risks and test signals
Risks include `init_cnt--` underflow if exit is unbalanced, error path disabling shared clock even when another lane is active, unsupported dual-lane SATA, and calibration only meaningful for XPCS. Test PCIe/XPCS/SATA modes, single/dual lane phandles, concurrent lane users, calibration success/timeout, and remove cleanup.
