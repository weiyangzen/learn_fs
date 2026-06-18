# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_eth_path.c

## Purpose
`mtk_eth_path.c` is a small path-fabric configuration library for the MediaTek SoC Ethernet driver. It maps a requested MAC-to-PHY path, such as GMAC1 to SGMII or GMAC2 to GEPHY/2.5G PHY, onto the SoC-specific mux bits in `ethsys`, `infra`, and NETSYS registers. It keeps pin/path switching out of the phylink MAC configuration code in `mtk_eth_soc.c`.

## Important APIs, Types, and Functions
`struct mtk_eth_muxc` describes one mux controller with a name, a required capability bit, and a `set_path()` callback. `mtk_eth_path_name()` converts path capability bits to debug strings. The static mux writers are `set_mux_gdm1_to_gmac1_esw()`, `set_mux_gmac2_gmac0_to_gephy()`, `set_mux_u3_gmac2_to_qphy()`, `set_mux_gmac2_to_2p5gphy()`, `set_mux_gmac1_gmac2_to_sgmii_rgmii()`, and `set_mux_gmac12_to_gephy_sgmii()`. The dispatch table `mtk_eth_muxc[]` ties those callbacks to `MTK_ETH_MUX_*` capability bits.

The exported path setup functions are `mtk_gmac_sgmii_path_setup()`, `mtk_gmac_2p5gphy_path_setup()`, `mtk_gmac_gephy_path_setup()`, and `mtk_gmac_rgmii_path_setup()`. These are declared in `mtk_eth_soc.h` and called by `mtk_mac_config()` when phylink changes interface mode.

## Control Flow
Each public setup function derives a path bit from `mac_id` and requested interface family, validates unsupported IDs, then calls `mtk_eth_mux_setup()`. `mtk_eth_mux_setup()` first verifies that the SoC advertises the requested path capability. If the SoC has no mux fabric (`MTK_MUX` absent), it returns success because no register programming is needed. Otherwise it iterates all mux controllers, invokes only those whose capability is present, and stops on the first callback error.

Each callback is intentionally tolerant: it updates only when the requested path is relevant to that mux and logs whether it changed anything. The register programming uses `mtk_m32()` for NETSYS MAC misc registers and `regmap_update_bits()`, `regmap_clear_bits()`, or `regmap_read()`/`regmap_update_bits()` for syscon-backed `infra` and `ethsys` maps.

## State and Persistence
The persistent hardware state is the mux register state in `eth->ethsys`, `eth->infra`, and direct NETSYS MMIO registers. The file itself stores no long-lived software state beyond the static mux table. Path validity is represented by the SoC capability bitmap in `eth->soc->caps`.

## Dependencies and Integration Points
The file depends on `mtk_eth_soc.h` for capability bits, register constants, `struct mtk_eth`, and helpers such as `MTK_HAS_CAPS()` and `mtk_is_netsys_v3_or_greater()`. It integrates with phylink via `mtk_eth_soc.c`: interface transitions call these setup functions before MAC/PCS configuration proceeds. It also depends on device tree-provided syscon regmaps; paths that touch `eth->infra` require the `MTK_INFRA` capability and successful probe setup.

## Risks
The most visible risk is incorrect capability/path mapping. A SoC data table that advertises a path without its required mux controller can silently skip necessary programming or return `-EINVAL`. Several callbacks preserve existing register bits and clear only selected masks; stale bits can remain if a transition is not explicitly handled. `set_mux_gmac1_gmac2_to_sgmii_rgmii()` compares `path` against combined capability constants (`MTK_GMAC1_RGMII`, `MTK_GMAC2_RGMII`) inside cases for path-only constants; this relies on macro values and should be watched when capability definitions change. Register-map availability is also critical for `eth->infra` and `eth->ethsys`.

## Test Signals
Exercise every supported `phy-mode` for each SoC data table: RGMII/TRGMII/MII/GMII, SGMII/1000BASE-X/2500BASE-X, internal 2.5G PHY, and GEPHY. Boot logs should not report unsupported paths for valid device trees. Register traces or hardware validation should confirm expected `ETHSYS_SYSCFG0`, `INFRA_MISC2`, `USB_PHY_SWITCH_REG`, `TOP_MISC_NETSYS_PCS_MUX`, and `MTK_MAC_MISC(_V3)` values. Link tests should include interface switching through phylink restart paths.
