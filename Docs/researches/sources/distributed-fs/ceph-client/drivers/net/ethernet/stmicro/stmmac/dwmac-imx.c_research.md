# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-imx.c

## Purpose
This file is the NXP i.MX8/i.MX9 DWMAC EQOS glue layer. It configures SoC interface-mode syscon registers, TX and memory clocks, RMII reference-clock selection, speed-specific TX clock handling, i.MX93 reset quirks, and STMMAC platform flags.

## Important APIs, Types, And Functions
- `struct imx_dwmac_ops` holds variant flags, DMA address width, whether RGMII TX clock is auto-adjusted, and callbacks for reset, interface mode, and speed fixups.
- `struct imx_priv_data` stores device, TX/memory clocks, syscon regmap/offset, RMII reference-clock source, MMIO base, ops, and platform data.
- `imx8mp_set_intf_mode()`, `imx8dxl_set_intf_mode()`, and `imx93_set_intf_mode()` program interface selection differently by SoC.
- `imx_dwmac_clks_config()` enables/disables memory and TX clocks.
- `imx_set_phy_intf_sel()` validates STMMAC PHY interface selector values before calling variant mode setup.
- `imx_dwmac_fix_speed()` and `imx93_dwmac_fix_speed()` handle speed-dependent TX clock and i.MX93 fixed-link RGMII reprogramming.
- `imx_dwmac_mx93_reset()` performs DMA software reset and writes RMII speed reset bits for RMII mode.
- `imx_dwmac_parse_dt()` parses clocks, `snps,rmii_refclk_ext`, and `intf_mode` syscon phandle where required.
- `imx_dwmac_probe()` installs platform callbacks, enables clocks, sets queue TBS defaults, and calls `stmmac_pltfr_probe()`.

## Control Flow
Probe gets resources and standard DT STMMAC config, allocates private state, selects variant ops by compatible, parses clocks/syscon, copies variant flags, enables TBS on TX queues except queue 0, sets host DMA width, installs `set_phy_intf_sel`, clock config, `bsp_priv`, speed/clock callbacks, and optional reset quirk, then enables clocks and probes STMMAC. On probe failure it disables clocks.

## State And Persistence
State persists in `imx_priv_data`, STMMAC platform data, enabled clocks, syscon interface registers, and MMIO MAC control registers for i.MX93 speed/reset workarounds.

## Dependencies And Integration Points
Uses OF compatibles `nxp,imx8mp-dwmac-eqos`, `nxp,imx8dxl-dwmac-eqos`, and `nxp,imx93-dwmac-eqos`; depends on syscon/regmap, clocks, STMMAC platform core, PHY interface encodings, and platform PM ops.

## Risks
- `imx8dxl_set_intf_mode()` is a stub, so SCU-dependent configuration must happen elsewhere.
- i.MX93 fixed-link speed workaround temporarily disables interface bits and rewrites MAC control; incorrect ordering can disrupt traffic.
- Clock enablement is done before `stmmac_pltfr_probe()` and disabled only on immediate probe failure; later lifecycle relies on STMMAC callbacks.
- Queue TBS defaults are forced for all nonzero TX queues and may surprise DT queue configurations.

## Test Signals
Probe each compatible, validate `intf_mode` phandle handling, RMII external/internal reference clock cases, TX rate changes for 10/100/1000 RGMII, i.MX93 fixed-link mode changes and reset, suspend/resume, and STMMAC traffic with queue features.
