# sources/distributed-fs/ceph-client/drivers/net/ethernet/arc/emac_rockchip.c

## Purpose
Provides the Rockchip platform glue for the generic ARC EMAC core. It adapts SoC-specific GRF register offsets, clocks, regulator handling, and RMII speed programming before delegating the network device to `arc_emac_probe()`.

## Important APIs, Types, and Functions
`struct emac_rockchip_soc_data` describes GRF offset fields and whether a divided MAC clock is needed. `struct rockchip_priv_data` embeds `struct arc_emac_priv` and adds `regmap`, regulator, and clock handles. `emac_rockchip_probe()` is the platform probe path, `emac_rockchip_remove()` unwinds it, and `emac_rockchip_set_mac_speed()` is installed as the ARC core `set_mac_speed` callback. OF matching selects RK3036, RK3066, or RK3188 data.

## Control Flow and State
Probe allocates an Ethernet device with private Rockchip state, validates RMII-only PHY mode, resolves the GRF syscon, enables `hclk`/`macref`, optionally enables the PHY regulator, writes initial 100 Mbps RMII GRF bits, sets reference clock to 50 MHz, optionally enables `macclk` at 25 MHz, then calls `arc_emac_probe()`. Removal calls the ARC core cleanup and disables resources in reverse.

## Dependencies and Integration Points
Integrates with platform bus, OF `phy-mode`, syscon/regmap for `rockchip,grf`, Linux clock framework, regulators, and the shared ARC EMAC implementation. Runtime link speed changes are propagated from the core into GRF speed bits.

## Risks and Test Signals
Risk is concentrated in resource unwind and SoC-specific GRF bit programming. Unsupported PHY modes fail early. Tests should cover probe deferral from regulator/clock/syscon, both `need_div_macclk` paths, 10/100 speed changes, and remove after partial probe. Board-level validation should verify RMII clock rates and that GRF writes use write-mask high bits correctly.
