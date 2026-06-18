# sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-imx8mq-usb.c

## Purpose
NXP i.MX8MQ/i.MX8MP/i.MX95 USB PHY provider for the Linux generic PHY framework. It initializes USB2/USB3 PHY control registers, powers the PHY with clocks and a `vbus` regulator, applies board-tunable electrical parameters, and optionally registers an i.MX95 Type-C orientation switch for the TCA/XBar block.

## Important APIs, types, and functions
- `struct imx8mq_usb_phy` stores the generic PHY, primary and optional alternate clocks, MMIO base, regulator, optional TCA block, and all parsed tuning values.
- `struct tca_blk` owns Type-C switch state, TCA MMIO base, mutex, and current orientation.
- `imx8mq_usb_phy_init()` is the i.MX8MQ init sequence: assert reset/ATE reset, enable reference SSP, enable TX, then deassert reset.
- `imx8mp_usb_phy_init()` extends init with FSEL/SSC/OTG-disable setup, tuning writes, and optional TCA initialization for i.MX8MP/i.MX95.
- `imx8mq_phy_power_on()` and `imx8mq_phy_power_off()` manage `vbus`, `phy`/`alt` clocks, and RX termination override.
- Tuning helpers translate DT properties such as `fsl,phy-tx-vref-tune-percent`, `fsl,phy-tx-rise-tune-percent`, and `fsl,phy-pcs-tx-swing-full-percent` into packed register fields.

## Control flow
Probe allocates state, gets clocks, maps the primary MMIO resource, selects `phy_ops` from compatible data, creates one generic PHY, gets the `vbus` regulator, optionally maps/registers the TCA switch, parses tuning data, and registers an OF PHY provider. Consumers call `power_on()` before `init()`: power enables the supply and clocks; init programs PHY control fields and deasserts reset. Type-C orientation changes temporarily enable the PHY clock, update TCA mux bits under a mutex, then disable the clock again.

## State and persistence
State is runtime-only in MMIO registers, regulator/clock enable counts, cached tuning fields, and cached Type-C orientation. There is no persistent storage. The TCA mutex protects orientation updates; generic PHY core serialization protects normal PHY ops.

## Dependencies and integration points
Depends on `GENERIC_PHY`, clk, regulator, platform MMIO, OF match data, and `linux/usb/typec_mux.h`. Integrates with USB controller nodes through OF PHY phandles and with Type-C mux users via `typec_switch_register()`. The optional second MMIO resource is i.MX95-specific TCA/XBar control.

## Risks and test signals
Risks include clock/regulator leak on partial `power_on()` failure after regulator enable, SoC-specific tuning conversion mistakes, optional TCA switch registration returning `NULL` instead of an errno on registration failure, and race-prone expectations between Type-C orientation changes and PHY power state. Test by probing all compatibles, exercising suspend/off/on cycles, verifying Type-C normal/reverse/none transitions, checking USB2/USB3 enumeration, and confirming tuning fields with register dumps.
