# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-ingenic.c

## Purpose
This is the Ingenic SoC DWMAC glue layer. It programs a MAC PHY control syscon register for different Ingenic SoC families and optional RGMII TX/RX delays, then delegates datapath operation to STMMAC.

## Important APIs, Types, And Functions
- `enum ingenic_mac_version` identifies JZ4775, X1000, X1600, X1830, and X2000 variants.
- `struct ingenic_soc_info` stores version, register mask, variant `set_mode` callback, and valid PHY interface selector bitmap.
- `struct ingenic_mac` stores variant info, STMMAC platform data, device, syscon regmap, and delay values.
- Variant mode functions (`jz4775_mac_set_mode()`, `x1000_mac_set_mode()`, `x1600_mac_set_mode()`, `x1830_mac_set_mode()`, `x2000_mac_set_mode()`) compose syscon register values.
- `ingenic_set_phy_intf_sel()` validates STMMAC selector encoding against the variant bitmap and calls the variant mode function.
- `ingenic_mac_probe()` parses STMMAC resources/DT, gets `mode-reg` syscon, parses optional `tx-clk-delay-ps` and `rx-clk-delay-ps`, installs `bsp_priv` and selector callback, and probes STMMAC.

## Control Flow
At probe, the driver builds standard STMMAC platform data, allocates private state, gets match data, looks up the MAC PHY control regmap, validates optional delay properties, stores platform data and callbacks, and calls `devm_stmmac_pltfr_probe()`. During STMMAC setup, `set_phy_intf_sel` programs the syscon according to the selected interface.

## State And Persistence
State is the devm-managed `ingenic_mac` and syscon register contents. Delay values are stored in internal units after multiplying parsed picosecond values by 1000 for the X2000 formula.

## Dependencies And Integration Points
Depends on OF, syscon/regmap, STMMAC platform helpers, and variant compatibles `ingenic,jz4775-mac`, `ingenic,x1000-mac`, `ingenic,x1600-mac`, `ingenic,x1830-mac`, and `ingenic,x2000-mac`.

## Risks
- Delay property names use `tx-clk-delay-ps`/`rx-clk-delay-ps`, not the common `*-internal-delay-ps`; DT binding must match.
- X2000 delay conversion uses `(delay + 9750) / 19500 - 1` after multiplying input by 1000, which is easy to misread and should be validated against hardware units.
- Valid interface selector bitmaps differ by SoC; invalid `phy-mode` fails setup.
- The syscon offset is fixed at 0 in `regmap_update_bits()`, so `mode-reg` must expose the intended register at offset zero.

## Test Signals
Probe all compatibles, validate GMII/RGMII/RMII acceptance per SoC, test invalid and boundary delay values, inspect syscon register programming, and run STMMAC traffic with link changes.
