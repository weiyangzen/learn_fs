# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/reg.h lines 7054-10717

## Scope

This chunk is the tail of the Realtek rtw89 register definition header. It is not executable code; it defines MMIO/register addresses and bit masks used by the Wi-Fi 7/BE MAC, BB wrapper, PHY, RF calibration, TX power, coexistence, and watchdog paths. Most definitions use the local `R_*` register-address convention and `B_*` bit/field-mask convention built on Linux `BIT()` and `GENMASK()`.

The range covers two broad address spaces:

- BE CMAC/WMAC and TX-power wrapper registers around `0x10800` through `0x168e4`, with C1/second-MAC aliases such as `R_BE_TB_PPDU_CTRL_C1`.
- PHY/RF/BB calibration registers from low PHY offsets through BE4 high-address aliases, ending with WiFi CPU local-domain watchdog registers `R_AX_WDT_CTRL` and `R_AX_WDT_STATUS`.

## Purpose

The definitions provide the symbolic contract between the rtw89 driver and Realtek BE hardware. They let driver code:

- initialize protocol timing, response rates, NAV behavior, RX filters, BA/CSI response memory, and BE trigger/response behavior;
- mask, enable, and dump protocol/RX/TX/PHY-interface/TX-power error interrupts;
- program BE TX power by rate, power limits, RU limits, offsets, force controls, FTM controls, and BT coexistence power hooks;
- operate PHY channel/bandwidth, EDCCA/NHM/IFS measurement, CFO compensation, BSS coloring, RF path selection, baseband gain, and packet-detection knobs;
- run RFK calibration flows including IQK, DPK, DACK, ADDCK, DRCK, TSSI, PA bias, and coefficient/LUT operations;
- access BE4/RTL8922D-specific duplicated register maps and WiFi CPU watchdog state.

## Important Register Groups

### BE PTCL/TMAC/RX DMA and Error Registers

The first block defines BE protocol control and data-path registers:

- `R_BE_TB_PPDU_CTRL`, `R_BE_AMPDU_AGG_LIMIT`, `R_BE_AGG_LEN_HT_0`, `R_BE_SPECIAL_TX_SETTING`, `R_BE_SIFS_SETTING`, `R_BE_TXRATE_CHK`, and `R_BE_TXCNT` configure trigger-based PPDU behavior, AMPDU limits, special TX modes, SIFS/CTS-to-self timing, TX rate validation, and TX counters.
- `R_BE_PTCL_PRELD_CTRL`, `R_BE_BT_PLT`, `R_BE_PTCL_BSS_COLOR_0/1`, `R_BE_PTCL_FSM_MON`, and `R_BE_PTCL_TX_CTN_SEL` configure preloading queues, BT packet-lifetime grants, BSS color fields, protocol FSM timeout thresholds, and TX-contender/busy status.
- `R_BE_PTCL_IMR_2`, `R_BE_PTCL_IMR0/1`, and `R_BE_PTCL_ISR0/1` define protocol interrupt masks/status. Composite masks such as `B_BE_PTCL_IMR0_CLR`, `B_BE_PTCL_IMR0_SET`, `B_BE_PTCL_IMR1_CLR`, and `B_BE_PTCL_IMR1_SET` are consumed by chip error-mask tables.
- `R_BE_RX_ERROR_FLAG`, `R_BE_RX_ERROR_FLAG_IMR`, `R_BE_TX_ERROR_FLAG`, `R_BE_TX_ERROR_FLAG_IMR`, plus `_1` variants define DMA/RU/FSM/zero-length error reporting for RX resource units 0-15 and TX resource units 0-15. The `_V1` masks distinguish later chip revisions.
- `R_BE_WMTX_*`, `R_BE_TRXPTCL_RESP_*`, `R_BE_MAC_LOOPBACK`, `R_BE_CLIENT_OM_CTRL`, `R_BE_WMAC_NAV_CTL`, `R_BE_RXTRIG_TEST_USER_2`, `R_BE_TRXPTCL_ERROR_INDICA_MASK`, `R_BE_TRXPTCL_ERROR_INDICA`, `R_BE_PHYINFO_ERR_IMR_V1`, and `R_BE_PHYINFO_ERR_ISR` back WMAC response, loopback, NAV, trigger-test, and error-indication flows.

Integration examples:

- `mac_be.c` uses `R_BE_TB_PPDU_CTRL` in `tmac_init_be()` to clear `B_BE_QOSNULL_UPD_MUEDCA_EN`.
- `mac_be.c` uses `R_BE_SPECIAL_TX_SETTING`, `R_BE_WMAC_NAV_CTL`, and `R_BE_TRXPTCL_RESP_0` in `nav_ctrl_init_be()` to configure NAV behavior and force MBA duration.
- `mac_be.c` uses `R_BE_SIFS_SETTING`, `R_BE_PTCL_FSM_MON`, and `R_BE_AMPDU_AGG_LIMIT` in protocol initialization.
- `mac_be.c` polls `R_BE_PTCL_TX_CTN_SEL` and `B_BE_PTCL_BUSY` in the BE TX-idle path.
- `rtw8922a.c` and `rtw8922d.c` build chip-specific IMR tables from the `*_IMR_*_CLR/SET` macros.
- `mac_be.c` dumps `R_BE_PTCL_IMR*`, `R_BE_PTCL_ISR*`, `R_BE_RX_ERROR_FLAG*`, `R_BE_TX_ERROR_FLAG*`, and `R_BE_TRXPTCL_ERROR_INDICA*` when CMAC error indicators fire.

### Response, CSI, RX Filter, and CAM Registers

This range defines the WMAC response-format matrix:

- `R_BE_BFMEE_RESP_OPTION`, `R_BE_TRXPTCL_RESP_CSI_CTRL_0/1`, `R_BE_TRXPTCL_RESP_CSI_RRSC`, and `R_BE_TRXPTCL_RESP_CSI_RATE` drive BFee/CSI response setup.
- `R_BE_WMAC_ACK_BA_RESP_*`, `R_BE_WMAC_RX_RTS_RESP_*`, `R_BE_WMAC_RX_MURTS_RESP_*`, and `R_BE_WMAC_OTHERS_RESP_*` encode ACK/BA/RTS/MU-RTS/other response behavior for legacy, HE, and EHT puncturing modes.
- `R_BE_RCR`, `R_BE_PLCP_HDR_FLTR`, `R_BE_RXGCK_CTRL`, `R_BE_RX_FLTR_OPT`, `R_BE_CTRL_FLTR`, `R_BE_MGNT_FLTR`, `R_BE_DATA_FLTR`, `R_BE_ADDR_CAM_CTRL`, `R_BE_RESPBA_CAM_CTRL`, `R_BE_PPDU_STAT`, `R_BE_RX_SR_CTRL`, `R_BE_BSSID_SRC_CTRL`, `R_BE_CSIRPT_OPTION`, `R_BE_BSR_UPD_CTRL`, and `R_BE_DRV_INFO_OPTION` define RX filtering, CAM addressing, PPDU status, spatial reuse, BSSID source, CSI report, and driver-info options.
- `R_BE_RESP_CSI_RESERVED_PAGE` stores the reserved packet-id/page count used for CSI response buffers.
- `R_BE_RESP_IMR1`, `R_BE_RESP_IMR`, `R_BE_RX_ERR_ISR`, `R_BE_RX_ERR_IMR`, and `R_BE_RX_PLCP_EXT_OPTION_1/2` define response/RX error masks and PLCP option bits.

Integration examples:

- `mac_be.c` initializes response rates and response RRSR fields in `trxptcl_init_be()`, using `R_BE_TRXPTCL_RESP_0/1` and the chip `rrsr_cfgs`.
- `mac_be.c` resets the BA CAM through `R_BE_RESPBA_CAM_CTRL` and polls `B_BE_BACAM_RST_MASK`.
- `mac_be.c` programs `R_BE_RCR`, `R_BE_RX_FLTR_OPT`, `R_BE_PLCP_HDR_FLTR`, `R_BE_RX_PLCP_EXT_OPTION_1/2`, `R_BE_BSR_UPD_CTRL`, and `R_BE_RXGCK_CTRL` in RX filter setup.
- `mac_be.c` programs CSI reserved pages with DLE reserved-queue data in `resp_pktctl_init_be()`.
- `mac_be.c` enables BFee/CSI response behavior through `R_BE_TRXPTCL_RESP_CSI_CTRL_0/1`, `R_BE_CSIRPT_OPTION`, `R_BE_TRXPTCL_RESP_CSI_RRSC`, and `R_BE_TRXPTCL_RESP_CSI_RATE`.

### BE TX Power and BB Wrapper Registers

The `R_BE_PWR_*` block defines the MAC-side TX power wrapper and table windows:

- Control registers include `R_BE_PWR_MODULE`, `R_BE_PWR_LISTEN_PATH`, `R_BE_PWR_REF_CTRL`, `R_BE_PWR_OFST_LMTBF`, `R_BE_PWR_FORCE_LMT`, `R_BE_PWR_RATE_CTRL`, `R_BE_PWR_RATE_OFST_CTRL`, `R_BE_PWR_BOOST`, `R_BE_PWR_OFST_RULMT`, `R_BE_PWR_FORCE_MACID`, `R_BE_PWR_REG_CTRL`, `R_BE_PWR_COEX_CTRL`, `R_BE_PWR_TH`, `R_BE_PWR_RSSI_TARGET_LMT`, `R_BE_PWR_OFST_SW`, `R_BE_PWR_FTM`, and `R_BE_PWR_FTM_SS`.
- Table windows include `R_BE_PWR_BY_RATE` to `R_BE_PWR_BY_RATE_END`, `R_BE_PWR_LMT` to `R_BE_PWR_LMT_MAX`, and `R_BE_PWR_RU_LMT` to `R_BE_PWR_RU_LMT_MAX`.
- Error/status definitions include `R_BE_C0_TXPWR_IMR`, `R_BE_TXPWR_ERR_FLAG`, and `R_BE_TXPWR_ERR_IMR`, with C1 aliases.

Integration examples:

- `phy_be.c` clears table windows in `rtw89_phy_bb_wrap_tpu_set_all()` and writes by-rate/limit/RU-limit pages in the BE TX-power programming functions.
- `phy_be.c` uses `R_BE_PWR_FORCE_*`, `R_BE_PWR_COEX_CTRL`, and `R_BE_PWR_RATE_CTRL` to clear force modes during BB wrapper initialization.
- `phy_be.c` configures `R_BE_PWR_LISTEN_PATH`, `R_BE_PWR_FTM`, `R_BE_PWR_FTM_SS`, `R_BE_PWR_TH`, and `R_BE_PWR_RSSI_TARGET_LMT` for listen-path, FTM, and uplink-power behavior.
- `rtw8922a.c` and `rtw8922d.c` write `R_BE_PWR_REF_CTRL`, `R_BE_PWR_RATE_CTRL`, `R_BE_PWR_REG_CTRL`, `R_BE_PWR_COEX_CTRL`, and `R_BE_PWR_BOOST` for chip-specific power and BT grant handling.
- `debug.c` uses the table ranges for dumping BE power-by-rate, power-limit, and RU-limit windows.

### PHY, CCX, EDCCA/NHM/IFS, and Channel Registers

The middle PHY block defines baseband measurement, channel, and path-control registers:

- Clock/reset/control: `R_UPD_P0`, `R_BBCLK`, `R_RSTB_WATCH_DOG`, `R_EMLSR`, `R_CHK_LPS_STAT`, `R_SPOOF_CG`, `R_DFS_FFT_CG`, `R_CHINFO_DATA`, `R_ANAPAR*`, `R_RFE_*`, `R_CIRST`, and SWSI/HWSI access registers.
- PHY-status and PMAC: `R_PLCP_HISTOGRAM`, `R_PHY_STS_BITMAP_*`, `R_PMAC_GNT`, `R_PMAC_RX_CFG1`, `R_PMAC_RXMOD`, `R_PMAC_TX_CTRL`, `R_PMAC_TX_PRD`, and `R_PMAC_TX_CNT`.
- CCX/noise/IFS: `R_CCX`, `R_NHM_CFG`, `R_NHM_TH*`, `R_FAHM`, `R_IFS_COUNTER`, `R_IFS_T1` through `R_IFS_T4`, `R_IFS_CLM_*`, `R_IFS_HIS`, `R_IFS_AVG_*`, `R_IFS_CCA_*`, `R_IFSCNT`, and BE4 alternatives such as `R_IFS_T1_AVG_BE4`.
- EDCCA and CCA: `R_EDCCA_RPT_*`, `R_SEG0R_EDCCA_LVL*`, `R_SEG0R_PPDU_LVL_BE*`, `R_RXCCA*`, `R_RXHE`, `R_SPOOF_ASYNC_RST`, and `R_BMODE_PDTH*`.
- Channel/bandwidth and RF path state: `R_FC0*`, `R_CHBW_MOD*`, `R_DBCC`, `R_ANT_CHBW`, `R_ANT_RX_BE4`, `R_BW_BE4`, path initial-gain registers, LNA/TIA/RXB init registers, BT-share registers, notch/5M detector registers, and BSS-color clear-map registers.
- TX filtering and coefficients: `R_TXFIR*`, `R_PCOEFF*`, `R_TX_CFR_MANUAL_EN_BE4`, `R_PATH0_TX_CFR`, and `R_PATH0_TX_POLAR_CLIPPING`.

Integration examples:

- `phy.c` maps the CCX/NHM/IFS definitions into `rtw89_ccx_regs`-style configuration used by channel-load/noise measurement.
- `phy.c` uses BSS-color clear-map registers in BSS color programming.
- Chip files such as `rtw8851b.c`, `rtw8852c.c`, and BE chip files use path, channel, EDCCA, and coefficient definitions to fill chip-info register tables for channel changes, BT coexistence, RSSI offsets, bandwidth programming, RXCCA control, and TX FIR/CFR setup.
- `phy_be.c` supplies BE and BE4 register structs for PHY status, CFO compensation, and BB wrapper behavior.

### RFK, IQK/DPK/DACK/TSSI Calibration Registers

The RF calibration block is dense and stateful:

- TSSI and TX power baseband registers include `R_TSSI_PA_K*`, `R_P0_TSSI_*`, `R_P1_TSSI_*`, `R_TSSI_THOF`, `R_TSSI_PWR_P0/P1`, `R_TSSI_MAP_OFST_P0/P1`, `R_TXAGC_REF_DBM_*`, `R_TSSI_K_*`, `R_TXPWRB*`, `R_TXPWR_RST*`, and BE4 path/table variants.
- DACK/ADDCK/DRCK registers include `R_DCOF*`, `R_DACK_S0P*`, `R_DACK_S1P*`, `R_DACK_BIAS*`, `R_DACK_DADCK*`, `R_DACK10/11`, `R_DACK1_K`, `R_DACK2_K`, `R_ADDCK0*`, `R_ADDCK1*`, `R_DRCK*`, and `R_DACKN*_CTL`.
- IQK/DPK/KIP/NCTL registers include `R_NCTL_CFG`, `R_NCTL_RPT`, `R_NCTL_N1/N2`, `R_IQK_*`, `R_TPG_*`, `R_MDPK_*`, `R_KIP_*`, `R_DPK_*`, `R_CFIR_*`, `R_DPD_*`, `R_GAPK`, coefficient LUT/register windows, and report/status registers.
- BE4 additions include OOB/DPD/QAM/RFSI compensation thresholds, override-value registers, band-edge controls, software SI data windows, KTBL controls, and thermal-compensation controls.

Integration examples:

- `phy_be.c` preinitializes RF/NCTL clocks and resets through `R_GOTX_IQKDPK_*`, `R_IQK_DPK_RST*`, and `R_IQK_DPK_PRST*`, using BE4 alternatives for newer chips.
- `rtw8922a_rfk.c`, `rtw8922d_rfk.c`, and older RFK implementations use the TSSI, DACK, ADDCK, DRCK, IQK, DPK, KIP, CFIR, and coefficient definitions for calibration sequencing, status polling, and result application.
- DACK state is read from result/status fields such as `B_DACK_S0P*_OK`, `B_DACK_S1P*_OK`, `B_ADDCKR*_A*`, and bias/DADCK masks, then written back through manual-control fields.
- TSSI calibration writes tracking enable/moving-average/reference-DBM/K-factor fields and controls SAR/maximum RF power through `R_P0_TXPWRB_BE`, `R_P1_TXPWRB_BE`, and BE4 equivalents.

### BE4/RTL8922D-Specific High Address Registers

The chunk adds many `_BE4` aliases in the `0x20000`, `0x24000`, `0x26000`, `0x2e000`, and `0x38000` ranges. These are used for later BE/BE4 hardware layout changes:

- `R_SYS_DBCC_BE4`, `R_EMLSR_SWITCH_BE4`, `R_CHINFO_SEG_BE4`, and `R_SEL_GNT_BT_RX*_BE4` cover DBCC, EMLSR, channel-info, and BT grant routing.
- `R_ENABLE_CCK0_BE4`, `R_RSTB_ASYNC_BE4`, `R_STS_HDR2_PARSING_BE4`, `R_TXINFO_PATH_BE4`, `R_TX_ERROR_SEL_BE4`, and `R_IMR_TX_ERROR_BE4` cover BE4 parsing/error behavior.
- BE4 EDCCA/IFS registers provide alternate measurement/report addresses.
- BE4 TSSI/TXAGC/path/channel/RX decode registers support per-path and per-table programming for newer chips.
- `R_SW_SI_*_BE4`, `R_RX_PATH*_TBL0_BE4`, `R_KTBL*_*_BE4`, and `R_TC_*_BE4` support software serial-interface access, RX path tables, calibration tables, and thermal-compensation triggers.

## Control Flow and State Behavior

Because this file is a register map, control flow is in consumers rather than here. The expected flow is:

1. Chip-specific probe selects chip operations and register configs.
2. MAC/CMAC initialization calls BE init helpers, checks MAC enablement, resolves C0/C1 addresses with `rtw89_mac_reg_by_idx()`, and writes protocol/RX/response bits.
3. PHY/BB initialization writes direct PHY registers, sets BB wrapper tables, and initializes RF/NCTL blocks.
4. Channel, bandwidth, coexistence, TX power, and calibration operations reuse these definitions to update hardware state after runtime state changes.
5. Error handling uses the composite IMR/ISR masks and error-flag definitions to enable/clear/report hardware faults.

The persistent state is almost entirely hardware-resident. Writes persist until firmware/driver reset, SER recovery, power-state transitions, channel changes, or explicit calibration reprogramming. Some calibration consumers copy hardware result fields into driver RFK state structures before later restoring them to manual fields. Table-window writes for TX power and RF coefficients persist in chip table SRAM/register windows and must be reloaded when regulatory/channel/SAR/calibration state changes.

## Dependencies

This header depends on common kernel bit helpers (`BIT`, `GENMASK`) and rtw89 register access wrappers in other files:

- MAC wrappers: `rtw89_read*()`, `rtw89_write*()`, `rtw89_write*_mask()`, `rtw89_mac_reg_by_idx()`, and `rtw89_mac_txpwr_write32*()`.
- PHY wrappers: `rtw89_phy_read32*()`, `rtw89_phy_write32*()`, and indexed PHY accessors.
- Polling helpers such as `read_poll_timeout_atomic()`.
- Chip metadata in `struct rtw89_chip_info`, `struct rtw89_rrsr_cfgs`, BB wrapper register structs, TX power tables, RFK state structs, and channel descriptors.

The definitions must remain aligned with hardware manuals and chip-ID/revision assumptions in `rtw8922a.c`, `rtw8922d.c`, `mac_be.c`, `phy_be.c`, and RFK implementation files.

## Integration Points

- `mac_be.c`: BE CMAC/TMAC/PTCL/RX/CSI/BFee initialization, TX idle polling, TX power address validation, and CMAC error dumps.
- `phy_be.c`: BE PHY status/CFO/CCX/BB wrapper register configs, RF/NCTL preinit, TX power table programming, FTM/listen-path/force-control setup, and BE4 RFSI/band-edge logic.
- `rtw8922a.c` and `rtw8922d.c`: chip-specific error IMR tables, RRSR configs, TX power reference/boost/coexistence programming, SAR max writes, and TSSI K-factor handling.
- `rtw8922*_rfk.c` and older `rtw8852*_rfk.c`: DACK/IQK/DPK/TSSI calibration sequences and status polling.
- `debug.c`: register-range dumps for BE TX power tables.
- Chip data files: channel/bandwidth, EDCCA, BSS color, BT coexistence, RSSI, TX filter, and path-control mappings.

## Risks and Edge Cases

- Address aliases are revision-sensitive. Many registers have C1 aliases and BE4 variants; using a base address without `rtw89_mac_reg_by_idx()` or the correct BE4 symbol can write the wrong MAC/PHY instance.
- Composite IMR masks encode policy, not only bit layout. Incorrect `*_CLR`, `*_SET`, or `_V1` selection can leave serious DMA/RU/FSM errors masked or cause noisy interrupts.
- Several aliases share the same address with different field names, for example OOB/DPD threshold registers. Consumers must use the mask matching the intended hardware mode.
- Table windows have strict sizes and ordering. TX-power by-rate/limit/RU-limit loops assume consecutive 32-bit registers and struct sizes checked with `BUILD_BUG_ON()` in consumers.
- Calibration sequencing is timing-sensitive. DACK/ADDCK/DRCK/IQK/DPK definitions include kick, reset, ready, and result fields; missed polling or wrong manual/auto selection can leave RF paths miscalibrated.
- Some status macros are used for error diagnostics only. If renamed or removed without updating dumps, SER triage loses observability.
- Register names mix generations (`AX`, `BE`, `BE4`, `V1`) and paths (`P0/P1`, `S0/S1`, C0/C1). Reviewers need to verify both generation and path before reusing a symbol.

## Test and Validation Signals

Useful validation for changes touching this range:

- Build coverage for all enabled rtw89 chips, especially RTL8922A/RTL8922D and BE4 paths, to catch missing/renamed macros.
- Boot/probe smoke tests with both MAC instances where supported, checking that CMAC init completes and `tx_idle_poll_band_be()` does not timeout.
- SER/error-injection or debug-trigger tests that verify IMR/ISR/error dump paths print the expected PTCL, DMA, PHYINFO, TRXPTCL, and TXPWR registers.
- RX/TX functional tests across legacy/HE/EHT rates, puncturing modes, AMPDU aggregation, BA/CSI/BFee response, and NAV/CTS-to-self behavior.
- Regulatory/SAR/TX-power tests that verify by-rate, limit, RU-limit, offset, BT coexistence, and forced-power controls are reflected in hardware.
- Channel/bandwidth switch tests across 20/40/80/160/320 MHz and DBCC/EMLSR modes, watching EDCCA/NHM/IFS counters and PHY status parsing.
- RFK validation after cold boot, resume, channel switch, and SER recovery: DACK/ADDCK/DRCK/IQK/DPK/TSSI status bits should complete, and EVM/RSSI/TSSI telemetry should remain in range.
