# sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_serdes.c

Purpose: implements the 6G SerDes/LCPLL calibration and configuration sequence for VSC85xx package PHYs. It provides the exported `vsc85xx_sd6g_config_v2()` routine used by `mscc_main.c` when configuring host SerDes in SGMII or QSGMII modes.

Important APIs and functions:
- `vsc85xx_sd6g_config_v2()` is the single external entry point. It orchestrates PLL detune/tune, RCPLL reset, input buffer calibration, FoJi frequency-offset calibration, mission-mode restore, MAC mode selection, and final PLL/lane reset release.
- `pll5g_detune()` and `pll5g_tune()` modify `PHY_S6G_PLL5G_CFG2` gain control around calibration.
- Helper writers such as `vsc85xx_sd6g_pll_cfg_wr()`, `vsc85xx_sd6g_common_cfg_wr()`, `vsc85xx_sd6g_des_cfg_wr()`, `vsc85xx_sd6g_ib_cfg*_wr()`, `vsc85xx_sd6g_misc_cfg_wr()`, `vsc85xx_sd6g_gp_cfg_wr()`, and DFT/PLL5G writers encode specific CSR writes.
- It uses `phy_update_mcb_s6g()` and `phy_commit_mcb_s6g()` from `mscc_main.c` to transfer CSR shadow state to/from MCB hardware.

Control flow: the sequence first selects the standard page and detunes/unlocks LCPLL. It resets RCPLL, commits base common/DES/IB configuration, starts the PLL FSM, and polls `PHY_S6G_PLL_STATUS` until calibration completes. It then releases digital reset with TX disabled, applies FoJi RX frequency offset, prepares and starts input-buffer calibration, toggles GP configuration for the required calibration cycles, polls `PHY_S6G_IB_STATUS0`, restores mission-mode IB settings, reenables TX, disables FoJi/DFT, and retunes/relocks LCPLL. Final configuration reads `MSCC_PHY_MAC_CFG_FASTLINK` to choose QSGMII or SGMII parameters, invokes the 8051 processor command for the selected MAC mode, updates LCPLL/S6G MCB state, writes final DES/IB/common settings, restarts the PLL FSM, waits for PLL completion again, releases lane reset, and commits.

State and persistence: no driver-private memory is retained by this file. Persistent state is entirely in PHY CSR/MCB hardware: PLL FSM config, common lane config, DES config, input-buffer calibration values, DFT/FoJi settings, GP toggles, MAC mode, and lane reset state. The function is intended to run during package/host-SerDes initialization with the MDIO bus already controlled by the caller.

Dependencies and integration points: includes `mscc_serdes.h` and `mscc.h`. It relies on `vsc85xx_csr_read/write()`, `phy_base_read/write()`, `phy_update_mcb_s6g()`, `phy_commit_mcb_s6g()`, and `vsc8584_cmd()` from `mscc_main.c`. It is called from `vsc8584_config_host_serdes()` and `vsc8514_config_host_serdes()`.

Risks and edge cases:
- This is a long, order-sensitive hardware recipe with many magic values from PHY characterization; small reordering or failed intermediate writes can leave the SerDes unusable.
- Poll loops use `PROC_CMD_NCOMPLETED_TIMEOUT_MS`; timeouts return `-ETIMEDOUT`, but prior hardware state is not rolled back.
- If `MSCC_PHY_MAC_CFG_FASTLINK` does not decode as QSGMII or SGMII, an error is logged but execution continues into later MCB update/configuration using the previous default variables, which may hide invalid interface setup.
- Helper `vsc85xx_sd6g_common_cfg_wr()` takes `pwd_tx` but does not encode it in the written value, which may be intentional or a stale parameter.
- The function assumes suitable locking context and package state from callers.

Test signals: boot VSC8514/VSC8584-class devices in SGMII and QSGMII modes; observe PLL and IB calibration completion; inject CSR/MCB write failures and timeouts; verify invalid MAC mode behavior; measure link bring-up and error counters after calibration; compare final register dumps to vendor reference sequences.
