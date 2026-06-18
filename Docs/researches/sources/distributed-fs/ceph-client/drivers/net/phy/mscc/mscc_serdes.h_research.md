# sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_serdes.h

Purpose: provides the small public interface and selected register offsets/bit positions for the VSC85xx 6G SerDes configuration helper.

Important APIs/types:
- `vsc85xx_sd6g_config_v2(struct phy_device *phydev)` is declared as the only callable API from this header.
- `PHY_S6G_PLL5G_CFG2_GAIN_MASK` and `PHY_S6G_PLL5G_CFG2_ENA_GAIN` support LCPLL detune/tune logic.
- DES bit-position macros and SerDes CSR offsets (`PHY_S6G_DES_CFG`, `PHY_S6G_IB_CFG0..4`, `PHY_S6G_GP_CFG`, `PHY_S6G_DFT_CFG0`, `PHY_S6G_IB_DFT_CFG2`) are used by `mscc_serdes.c` helper writers.

Control flow enabled by this header: `mscc_main.c` includes it to call the SerDes calibration function during host SerDes setup. `mscc_serdes.c` uses the register constants to construct CSR writes before committing them through the MCB helper API.

State and persistence: no software state is declared. All represented state is PHY hardware state written during SerDes calibration and retained until reset/reconfiguration.

Dependencies and integration points: depends on `struct phy_device` being visible to the including C file through `<linux/phy.h>`. The comment guard closes with `_MSCC_PHY_SERDES_H_` while the opening guard is `_MSCC_SERDES_PHY_H_`; this is only a comment mismatch, not a preprocessor issue.

Risks and edge cases:
- Only a subset of register constants is local to this header; other SerDes/MCB constants come from `mscc.h`, so changes must be coordinated across both headers.
- Because the header exposes only one high-level function, any additional SerDes mode would require expanding the API or adding mode selection inside `vsc85xx_sd6g_config_v2()`.

Test signals: compile coverage for all files including this header; run SGMII/QSGMII initialization paths; verify no include-order issue around `struct phy_device`; cross-check register offsets against the datasheet and `mscc.h`.
