<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear1340.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear1340.c

## Purpose
This file defines the SPEAr1340 pin controller description. SPEAr1340 has pins 0 through 251 and a two-level mux model: first pads are enabled as GPIO or peripheral, then shared peripheral pads select primary versus alternate IP. The file encodes those choices as static SPEAr pinctrl tables and registers a platform driver for `st,spear1340-pinmux`.

## Important APIs, Types, And Data
- `spear1340_pins[]` extends the common SPEAr pin ranges with PLGPIO246..251.
- First-level pad control uses `PAD_FUNCTION_EN_1..8`.
- Second-level shared-IP control uses `PAD_SHARED_IP_EN_1..2`.
- Sideband configuration registers include `PERIP_CFG`, `GMAC_CLK_CFG`, and `PCIE_SATA_CFG`.
- `pads_as_gpio` clears pad function enables to override bootloader state.
- Major functions include `fsmc`, `keyboard`, `spdif_in`, `spdif_out`, `gpt_0_1`, `pwm`, `vip`, `cam0..cam3`, `smi`, `ssp0`, `uart0`, `uart1`, `i2s`, `gmac`, `i2c0`, `i2c1`, `cec0`, `cec1`, `sdhci`, `cf`, `xd`, `clcd`, `arm_trace`, `miphy_dbg`, `pcie`, and `sata`.
- `gpio_request_endisable()` is a SoC callback that dynamically clears or sets the relevant `PAD_FUNCTION_EN_*` bit for GPIO request/release.

## Control Flow And Integration
Probe calls the shared `spear_pinctrl_probe()` with `spear1340_machdata`. During mux selection the common core walks each selected group's `spear_modemux` list and writes the specified register/mask/value triples. Many groups write both first-level pad enable registers and second-level shared-IP selectors. GMAC groups share the `GMAC_MUXREG` pad enable sequence, then select GMII, RGMII, RMII, or SGMII in `GMAC_CLK_CFG`. SDHCI, CF, and XD share MCIF pad enables and select the media mode in `PERIP_CFG`. PCIe and SATA select mutually exclusive lane mode and clocks/resets in `PCIE_SATA_CFG`.

## State And Persistence
Runtime state is held by the common SPEAr core. This file's persistent hardware impact is the programmed pad function state, shared-IP selections, GMAC mode bits, MCIF mode bits, SPDIF output enable, CLCD sleep/active pin state, and PCIe/SATA lane configuration. GPIO request persistence is mediated by `gpio_request_endisable()`, which computes the pad enable register from the pin number and toggles one bit.

## Dependencies
It depends on Linux platform/OF/init headers and local `pinctrl-spear.h`. It assumes the common SPEAr core supports the optional `gpio_request_endisable` hook and multi-register mux sequences.

## Risks And Review Notes
- The two-level mux model requires correct ordering and polarity. Some alternate functions are selected by writing zero to `PAD_SHARED_IP_EN_*`; others are selected by setting bits.
- `gpio_request_endisable()` uses `sizeof(int *)` as the register stride. This works only if it matches the intended 4-byte register spacing on all target builds; it is a notable review point.
- `pads_as_gpio` touches all pad-function enable registers and can override bootloader mux defaults. It must be used deliberately by DT states.
- `clcd_sleep_grp` intentionally disables CLCD output to avoid panel damage; display suspend/resume should validate this state.
- GMAC, MCIF, and PCIe/SATA sideband registers configure more than pin routing and can affect clocks, reset, and peripheral mode.

## Test Signals
Run build coverage for SPEAr1340 and boot with `st,spear1340-pinmux`. Use debugfs to confirm all groups/functions are registered. Test GPIO request/release on peripheral-capable pads, GMAC in all declared interface modes, SDHCI/CF/XD media selection, SPDIF out enable, CLCD active and sleep states, camera/VIP exclusivity, and PCIe versus SATA lane selection. Register readback should include both `PAD_FUNCTION_EN_*` and `PAD_SHARED_IP_EN_*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear1340.c -->
