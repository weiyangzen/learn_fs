<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/phy.c

## Purpose
`phy.c` is the central PHY-layer implementation for the Realtek `rtw89` wireless driver. It configures baseband and RF tables, exposes RF register access helpers, programs transmit-power tables and limits, handles PHY-related firmware C2H events, drives RF calibration waits, and runs dynamic PHY management loops such as rate adaptation setup, CFO tracking, thermal/RSSI/stat tracking, noise and IFS channel-load monitoring, DIG, antenna/path diversity, UL trigger-based waveform control, PHY status parsing, RFK table parsing, TSSI helper setup, channel index encoding, and EDCCA tracking.

The file is not a standalone algorithm module. It is glue between mac80211 station/vif state, chip-specific `rtw89_chip_info` and `rtw89_phy_gen_def` callbacks/tables, firmware H2C/C2H commands, efuse/ACPI/regulatory data, and low-level MAC/BB/RF registers.

## Important APIs, Types, And Functions
- Rate adaptation: `rtw89_phy_ra_update_sta_link()`, `rtw89_phy_ra_update_sta()`, `rtw89_phy_ra_update()`, `rtw89_phy_ra_assoc()`, `rtw89_phy_rate_pattern_vif()`, `rtw89_phy_ra_recalc_agg_limit()`. These build `struct rtw89_ra_info` from mac80211 `ieee80211_link_sta` capabilities and send `rtw89_fw_h2c_ra()`.
- Rate masks: `get_mcs_ra_mask()`, `get_he_ra_mask()`, `get_eht_ra_mask()`, `rtw89_phy_ra_mask_rssi()`, `rtw89_phy_ra_mask_cfg()`, and `rtw89_phy_ra_mask_recover()` compose CCK/OFDM/HT/VHT/HE/EHT masks, RSSI floors, configured bitrate masks, and chip TX-NSS limits.
- Channel subband helpers: `rtw89_phy_get_txsc()` and `rtw89_phy_get_txsb()` calculate TX subchannel/subband indexes for narrower transmissions within 40/80/160/320 MHz channel contexts.
- RF access: `rtw89_phy_read_rf()`, `rtw89_phy_read_rf_v1()`, `_v2()`, `_v3()`, `rtw89_phy_write_rf()`, `rtw89_phy_write_rf_v1()`, `_v2()`, `_v3()` implement direct and indirect SWSI/HWSI RF register access with polling and mask handling.
- Register table initialization: `rtw89_phy_init_bb_reg()`, `rtw89_phy_init_bb_afe()`, `rtw89_phy_init_rf_reg()`, `rtw89_phy_init_rf_nctl()`, and `rtw89_phy_init_reg()` load PHY tables selected by RFE/CV conditions and firmware elements when available.
- PHY-indexed register helpers: `rtw89_phy_write32_idx()`, `_set()`, `_clr()`, `rtw89_phy_read32_idx()`, and `rtw89_phy_set_phy_regs()` apply DBCC PHY1 register offsets through `rtw89_phy0_phy1_offset()`.
- Antenna gain and TX power: `rtw89_phy_ant_gain_init()`, `rtw89_phy_ant_gain_pwr_offset()`, `rtw89_print_ant_gain()`, `rtw89_phy_load_txpwr_byrate()`, `rtw89_phy_read_txpwr_byrate()`, `rtw89_phy_read_txpwr_limit()`, `rtw89_phy_read_txpwr_limit_ru()`, and the AX `set_txpwr_*` implementations program by-rate, offset, channel-width, RU, SAR, TPE, and directional-antenna constrained limits.
- Firmware C2H handling: `rtw89_phy_c2h_handle()` dispatches RA reports, dynamic management reports, RFK logs, and RFK report state completions through class/function handler tables. `rtw89_phy_c2h_chk_atomic()` declares which events are handled atomically.
- RFK wait APIs: `rtw89_phy_rfk_pre_ntfy_and_wait()`, `rtw89_phy_rfk_tssi_and_wait()`, `rtw89_phy_rfk_iqk_and_wait()`, `rtw89_phy_rfk_dpk_and_wait()`, `rtw89_phy_rfk_txgapk_and_wait()`, `rtw89_phy_rfk_dack_and_wait()`, `rtw89_phy_rfk_rxdck_and_wait()`, `rtw89_phy_rfk_txiqk_and_wait()`, and `rtw89_phy_rfk_cim3k_and_wait()` wrap firmware H2C commands with completion-based report waiting.
- TSSI helpers: `rtw89_phy_rfk_tssi_fill_fwcmd_efuse_to_de()` and `rtw89_phy_rfk_tssi_fill_fwcmd_tmeter_tbl()` translate efuse TSSI/thermal tables into firmware command fields, including 6 GHz group handling and chip-specific RTL8922A layout.
- Dynamic tracking: `rtw89_phy_dm_init()`, `rtw89_phy_dm_reinit()`, `rtw89_phy_dm_init_data()`, `rtw89_phy_stat_track()`, `rtw89_phy_cfo_track()`, `rtw89_phy_env_monitor_track()`, `rtw89_phy_nhm_trigger()`, `rtw89_phy_dig()`, `rtw89_phy_tx_path_div_track()`, `rtw89_phy_antdiv_track()`, and `rtw89_phy_edcca_track()` are watchdog-style periodic entry points.
- RFK cache/table helpers: `rtw89_rfk_chan_lookup()` selects reusable or replaceable RFK channel-cache slots. `rtw89_rfk_parser()` executes RFK table opcodes for RF writes, BB masked writes, set/clear, and microsecond delays.
- Misc exported integration helpers: `rtw89_phy_set_bss_color()`, `rtw89_phy_tssi_ctrl_set_bandedge_cfg()`, `rtw89_encode_chan_idx()`, `rtw89_decode_chan_idx()`, `rtw89_phy_config_edcca()`, `rtw89_phy_get_kpath()`, and `rtw89_phy_get_syn_sel()`.
- Generation definition: `rtw89_phy_gen_ax` binds AX-generation register maps and implementation callbacks for CCX, PHY status, CFO, PHY1 offsets, BB gain parsing, RF NCTL preinit, and TX-power programming.

Key state structures used here include `struct rtw89_dev`, `struct rtw89_chip_info`, `struct rtw89_phy_gen_def`, `struct rtw89_bb_ctx`, `struct rtw89_sta_link`, `struct rtw89_vif_link`, `struct rtw89_ra_info`, `struct rtw89_ra_report`, `struct rtw89_cfo_tracking_info`, `struct rtw89_env_monitor_info`, `struct rtw89_dig_info`, `struct rtw89_phy_stat`, `struct rtw89_antdiv_info`, `struct rtw89_tssi_info`, `struct rtw89_edcca_bak`, and RFK/TX-power table structs supplied by chip data and firmware elements.

## Control Flow
Initialization is table-driven and chip-driven. `rtw89_phy_init_bb_reg()` chooses firmware-provided BB tables when present, otherwise chip built-ins, applies conditional table rows using `rtw89_phy_init_reg()`, initializes the TX-power unit, parses BB gain tables, and resets BB. `rtw89_phy_init_rf_reg()` walks each RF path table, optionally stores RF register data for firmware H2C without MMIO, and pushes stored pages through `rtw89_fw_h2c_rf_reg()`. `rtw89_phy_dm_init()` then initializes statistics, chip BB hardware, CCX/IFS/NHM monitoring, PHY status bitmaps, DIG, CFO, BB wrappers, EDCCA, channel info, UL-TB info, antenna diversity, RFE GPIO, RFK hardware/NCTL/RFK state, TX power control, power trim, and TX/RX path configuration.

Rate adaptation starts from association or mac80211 rate-change notifications. The driver dereferences link station state under RCU, computes supported modes and masks from EHT/HE/VHT/HT/legacy capabilities, restricts them by band, TX NSS, RSSI floor, configured bitrate mask, fixed rate-pattern requests, GI/LTF, LDPC/STBC, DCM, ER, and channel width, then sends the resulting `struct rtw89_ra_info` to firmware. Firmware RA status reports come back as C2H, are decoded into `struct rate_info`, update `rtwsta_link->ra_report`, tune max A-MSDU aggregation, and can trigger `ieee80211_sta_recalc_aggregates()`.

Dynamic management is periodic and per active BB where needed. Statistics update thermal EWMAs, thermal protection level, RSSI minima, and packet counters. Environment monitoring reads the previous IFS-CLM result, releases CCX racing state, programs the next measurement, and triggers hardware counters. DIG consumes RSSI and false-alarm ratios to adjust AGC gain indexes and dynamic packet-detection thresholds. EDCCA derives thresholds from minimum RSSI and writes EDCCA/PPDU thresholds unless disabled. CFO tracking uses RX PHY parsed CFO samples, throughput state, timer mode, crystal-cap bounds, and DCFO compensation registers to adjust XTAL SI or chip registers. Antenna/path diversity collects per-path RSSI/EVM samples, schedules delayed training work, then switches hardware antenna selection and firmware TX path tables.

Firmware C2H control flow is table-dispatched by class/function. RA reports update station state; DM reports log LPS and scan data; RFK log packets parse nested run/report chunks; RFK report state sets `rtwdev->rfk_wait` and completes waiters. RFK wait APIs prepare the wait state, send one H2C, then block on completion unless SER handling forces a fixed delay path.

## State And Persistence
Most state is runtime-only under `struct rtw89_dev` and its per-BB, per-vif-link, and per-sta-link children. The file persists no data to disk.

Persistent hardware/device inputs are efuse values, ACPI antenna-gain data, firmware elements, chip tables, regulatory/SAR/TPE state, and current mac80211 channel/vif/sta configuration. The code transforms those inputs into hardware registers and firmware commands.

Important mutable runtime state includes RA reports and masks in station links, RSSI/thermal EWMAs, current TX/RX antenna selections, CFO sample accumulators and crystal-cap bounds, CCX/NHM/IFS monitor histories, DIG gain/threshold state, EDCCA scan backups, TSSI thermal and trim values, UL-TB defaults, RFK wait completion state, and NHM report lists allocated per supported band/channel by `rtw89_phy_dm_init_data()`.

Several functions intentionally save and restore transient state. `rtw89_phy_config_edcca()` backs up EDCCA thresholds while scanning and restores them after scan. RFK wait state is reset before each calibration. Antenna diversity uses delayed-work state to alternate training and decision periods. CFO statistics are cleared after each CFO management cycle. RF register configuration is cached into page-sized H2C buffers while tables are applied.

## Dependencies And Integration Points
- mac80211/cfg80211: station iteration, RCU link dereferences, bitrate masks, `rate_info`, HE/EHT capability structs, aggregation recalculation, vif association state, and wiphy delayed work.
- Firmware interface: many H2C functions in `fw.c` and C2H event payloads in `fw.h` are required for RA, RF table upload, RFK, MCC DIG, TX duty, TX path, and calibration commands.
- Chip abstraction: `rtwdev->chip`, `chip->ops`, `chip->phy_def`, `chip->mac_def`, register maps, RF path counts, TX NSS, feature flags, and per-generation callbacks decide most register addresses and algorithms.
- Register definitions: `reg.h` supplies BB/RF/MAC addresses and masks; this file performs numerous raw `rtw89_phy_write32*()`, `rtw89_write32*()`, and `rtw89_mac_txpwr_write32*()` accesses.
- Channel and regulatory layers: `chan.h`, `sar.h`, regulatory 6 GHz TPE, and RFE parameters feed antenna gain, TX-power limits, RU limits, subband mapping, and channel index encoding.
- Power-save, coexistence, debug, MAC, TX/RX, and utility layers: this code leaves PS before CFO delayed work, notifies BT coexistence on RSSI changes, emits debug categories for PHY/RA/TXPWR/RFK/TSSI/CFO/DIG/EDCCA, uses MAC register indexing, and consumes RX PHY PPDU parsed data.
- ACPI and efuse: ACPI RTAG controls directional antenna-gain offsets; efuse gives RFE type, XTAL cap, TSSI trims, and thermal defaults.

## Risks And Edge Cases
- RF access depends on tight polling timeouts and chip-generation-specific SWSI/HWSI semantics. Busy hardware, unplug handling, invalid RF paths, or wrong `RTW89_RF_ADDR_ADSEL_MASK` routing can return `INV_RF_DATA` or silently leave RF state unchanged.
- Conditional PHY table parsing is sensitive to RFE/CV matching. A malformed table can select the wrong headline, skip required branches, or warn and return before critical CR loads.
- Many arrays are indexed by band, bandwidth, RF path, NSS, channel index, RU, regulatory domain, and 6 GHz power type. The code has guards for some invalid bands/BWs/channels, but table shape mismatches or unsupported channels can degrade to index 0 or zero limits.
- RA mask construction combines peer capability, configured masks, RSSI floors, chip NSS, and fixed patterns. A bad mask can fall back through recovery logic, but may still over-restrict rates, disable EHT MCS12/13 via `hal.no_mcs_12_13`, or mismatch chip-generation hardware rate encoding.
- Dynamic management loops share state from RX parsing, station iteration, and delayed work. They rely on wiphy locking in work callbacks and RCU for link dereferences; missing lock context would be a correctness risk.
- CFO multi-station TP-based averaging has placeholder throughput weighting (`cfo_khz_all_tp_wgt` is not populated per station), so behavior falls back through tolerance windows and unweighted averages in practice.
- Antenna diversity can divide by zero if EVM is requested with no OFDM/non-legacy packets in a stats window; the local `phy_div()` helper returns 0, which may bias decisions.
- EDCCA and DIG thresholds are hardware-sensitive. Incorrect RSSI unit conversion, false-alarm thresholds, or scan restore sequencing can produce poor sensitivity, spurious CCA busy, or missed packets.
- RFK waits depend on firmware C2H completion. SER handling deliberately uses a fixed half-delay instead of waiting for events, which avoids deadlock but can mask calibration failures.
- Several paths branch on specific chip IDs/CVs (`RTL8852A`, `RTL8851B`, `RTL8852B`, `RTL8852C`, `RTL8922A`, `RTL8922D`). Adding a chip generation requires careful updates to register maps, report formats, RF access, EHT support, TSSI layout, and PHY status bitmaps.

## Test Signals
- Build coverage: the driver should compile with `W=1`-style kernel warnings clean for all enabled rtw89 chip objects that reference exported symbols from this file.
- Probe/init signals: successful device probe should complete BB/RF/NCTL/DM initialization without `invalid PHY package`, RF H2C page overflow, NCTL poll failure, unsupported RF path, or AFE poll warnings.
- Association signals: on joining APs across 2.4/5/6 GHz and HT/VHT/HE/EHT modes, RA H2C debug should show sane mode, bandwidth, NSS, GI/LTF, LDPC/STBC, and nonzero RA masks; C2H RA reports should update `ra_report->bit_rate` and aggregation limits.
- Regulatory/TX-power signals: TX power debug should show by-rate and limit programming for 20/40/80/160 MHz, RU limits, SAR/TPE clamping, and antenna-gain offsets only when ACPI/regulatory/RFE conditions allow.
- RFK signals: IQK/DPK/DACK/RXDCK/TSSI/TXGAPK/TXIQK/CIM3K wait APIs should receive `RTW89_RFK_STATE_OK` C2H reports within expected timeouts, and RFK log lengths should match their report structs.
- Dynamic tracking signals: watchdog traces should show thermal EWMA updates, CFO sample reset after compensation, IFS-CLM/NHM ready reports, DIG gain/PD threshold changes tied to RSSI/false alarms, EDCCA thresholds tied to RSSI, and no repeated busy/poll failures.
- Multi-BB/DBCC/MLO signals: PHY1 register accesses should receive correct offsets, active-BB iteration should configure both PHYs where expected, and `rtw89_phy_get_kpath()`/`rtw89_phy_get_syn_sel()` should choose RF paths matching MLO DBCC mode.
- Scan and recovery signals: EDCCA scan backup/restore should leave thresholds unchanged after scan, PS exit before CFO timer work should succeed, and SER paths should avoid hanging RFK waits.
- Runtime health signals: throughput, RSSI stability, low retry rate, correct channel noise reports, no firmware unsupported C2H spam, no repeated thermal duty throttling under normal temperatures, and stable antenna/path selection after training.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/phy.c -->
