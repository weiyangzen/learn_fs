# sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-hi3670-usb3.c

## Purpose
HiSilicon Kirin970/Hi3670 USB3.1 PHY provider. It configures USB2/USB3 clock sources, TCA Type-C adapter state, USB31 PHY CR bus access, fake VBUS, SSC, reset release, eye diagram, and TX vboost.

## Important APIs, types, and functions
- `struct hi3670_priv` stores peri/pctrl/sctrl/usb31misc regmaps and tuning values.
- CR helpers `hi3670_phy_cr_read()` and `hi3670_phy_cr_write()` bit-bang USB31 PHY control registers through `USB_MISC_CFG54/58` with ACK polling.
- `hi3670_config_phy_clock()` selects ABB or pad reference path based on `SCTRL_SCDEEPSLEEPED`.
- `hi3670_config_tca()` programs TCA interrupt, sync mode, mux, Type-C disable, TCPC valid, and VBUS override.
- `hi3670_phy_init()` performs resets, clock selection, IDDQ/test-powerdown exit, PHY/controller deassertion, stable-power flags, TCA config, SSC, fake VBUS, and tuning.

## Control flow
Probe gets three syscon phandles, parent USB31 misc regmap, optional `hisilicon,eye-diagram-param` and `hisilicon,tx-vboost-lvl`, then creates one PHY. Init runs a long regmap sequence and aborts on first failure. Exit asserts PHY reset and disables whichever reference clock path was selected.

## State and persistence
Only cached tuning values and register state. There is no persisted state. Clock-source decision is recomputed from SCTRL on init/exit.

## Dependencies and integration points
Uses generic PHY, syscon/regmap, platform OF, parent syscon layout, and USB Type-C adapter registers. DT compatible is `hisilicon,hi3670-usb-phy`.

## Risks and test signals
Risks include CR-bus timeouts, parent-node syscon assumptions, no rollback after mid-init failures, and reliance on fake VBUS/Type-C overrides. Test both ABB and pad refclock paths, USB2/USB3 enumeration, CR read/write retries, default/custom tuning, and suspend or repeated exit/init.
