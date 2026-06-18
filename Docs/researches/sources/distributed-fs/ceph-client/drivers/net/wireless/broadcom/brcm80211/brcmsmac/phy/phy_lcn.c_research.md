# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_lcn.c

## Purpose
`phy_lcn.c` implements the LCNPHY backend for Broadcom `brcmsmac`, mainly BCM2064 radio/LCN PHY hardware. It provides LCN-specific table access, radio/channel tuning, baseband/radio initialization, SPROM power parsing, transmit-power control, TSSI and temperature/voltage sensing, TX IQ/LO calibration, RX IQ calibration, tone generation, calibration orchestration, RX gain/power measurement, and backend callbacks installed into `struct phy_func_ptr`.

The file is hardware-programming heavy: it writes PHY tables, PHY registers, radio registers, chipcommon PLL/chip-control registers, and D11 sample/template paths.

## Important APIs, Types, and Functions
- Static hardware data: PLL/VCO constants, LCN table IDs, TX power table offsets, power-control mode constants, `chan_info_2064_lcnphy[]`, `lcnphy_radio_regs_2064[]`, CCK/OFDM digital filter tables, gain tables, IQ calibration ladders, RF register save lists, and sample-tone tables.
- Local types: `struct lcnphy_txgains`, `struct lcnphy_iq_est`, `struct lcnphy_rx_iqcomp`, `struct lcnphy_spb_tone`, `struct lcnphy_unsign16_struct`, `struct lcnphy_sfo_cfg`, and calibration/TSSI enums.
- Table helpers: `wlc_lcnphy_write_table()`, `wlc_lcnphy_read_table()`, `wlc_lcnphy_common_read_table()`, and `wlc_lcnphy_common_write_table()`.
- Gain/RF override helpers: `wlc_lcnphy_get_tx_gain()`, `wlc_lcnphy_set_tx_gain()`, `wlc_lcnphy_set_tx_gain_override()`, `wlc_lcnphy_set_pa_gain()`, `wlc_lcnphy_set_rx_gain()`, `wlc_lcnphy_rx_gain_override_enable()`, and TR switch override helpers.
- TX power and sensing: `wlc_lcnphy_tssi_setup()`, `wlc_lcnphy_tx_pwr_update_npt()`, `wlc_lcnphy_txpower_recalc_target()`, `wlc_lcnphy_tempcompensated_txpwrctrl()`, `wlc_lcnphy_set_tx_pwr_ctrl()`, `wlc_phy_txpower_recalc_target_lcnphy()`, `wlc_lcnphy_tssi2dbm()`, `wlc_lcnphy_get_tssi()`, `wlc_lcnphy_tempsense*()`, and `wlc_lcnphy_vbatsense()`.
- Calibration: RX IQ estimation/compensation through `wlc_lcnphy_rx_iq_est()`, `wlc_lcnphy_calc_rx_iq_comp()`, and `wlc_lcnphy_rx_iq_cal()`; TX IQ/LO through `wlc_lcnphy_tx_iqlo_loopback()`, `wlc_lcnphy_tx_iqlo_cal()`, `wlc_lcnphy_tx_iqlo_soft_cal_full()`, and `wlc_lcnphy_txpwrtbl_iqlo_cal()`.
- Tone/sample play: `wlc_lcnphy_start_tx_tone()`, `wlc_lcnphy_stop_tx_tone()`, `wlc_lcnphy_tx_pu()`, and `wlc_lcnphy_deaf_mode()`.
- Initialization/channel: `wlc_lcnphy_set_chanspec_tweaks()`, `wlc_lcnphy_radio_2064_channel_tune_4313()`, `wlc_lcnphy_load_tx_iir_filter()`, `wlc_lcnphy_tbl_init()`, `wlc_lcnphy_radio_init()`, `wlc_lcnphy_baseband_init()`, `wlc_phy_init_lcnphy()`, and `wlc_phy_chanspec_set_lcnphy()`.
- Attach/detach: `wlc_phy_attach_lcnphy()` allocates state, sets capabilities, installs callbacks, and reads SPROM; `wlc_phy_detach_lcnphy()` frees state.
- RX power: `wlc_lcnphy_get_receive_power()` and `wlc_lcnphy_rx_signal_power()`.

## Control Flow
Attach is called from common PHY attach. `wlc_phy_attach_lcnphy()` allocates `struct brcms_phy_lcnphy`, enables hardware power control when the board has a PA, records ALP clock, installs LCN callbacks, reads SPROM power/calibration fields, and selects TSSI-based or temperature-based power control for revision 1.

Initialization in `wlc_phy_init_lcnphy()` resets calibration counters, toggles AFE clocks, loads PHY tables, initializes baseband and BCM2064 radio, initializes TX power control for 2.4 GHz, applies the current chanspec, writes chipcommon controls, snapshots AGC temperature state, enables TX power control, sets default noise samples, and runs PHY-init calibration.

Channel changes record the chanspec, apply PLL/spur/channel tweaks, tune BCM2064 from the channel table, wait for settling, toggle AFE powerdown, write SFO config values, load CCK/OFDM filters, tweak RF override bits, and rerun TSSI setup when applicable.

Power control has three paths. TSSI hardware control builds a TSSI-to-dBm table from PA coefficients, estimates idle TSSI, writes target power, and enables hardware control. Temperature-based control computes a compensated gain index from raw/measured temperature and board power data. Manual/off control disables power control and programs gain, BB multiplier, IQ, LO, and RF power values for a selected table index.

Periodic calibration suspends MAC if needed, enters deaf mode, calibrates TX IQ/LO and RX IQ, refreshes TSSI tables when enabled, restores previous TX power mode/index, exits deaf mode, and resumes MAC. Watchdog calibration uses counter and temperature-delta thresholds for temperature-based mode.

RX signal power measures digital power at a selected or searched gain index, converts power to approximate dB, adjusts for gain mismatch, input-power offset, gain-index correction, frequency, and temperature, then clears RX gain override.

## State and Persistence Behavior
LCN-specific state is in `struct brcms_phy_lcnphy` via `pi->u.pi_lcnphy`. Key fields include current/override TX power index, calibration counter/temperature/channel, raw temperature, measured power, RSSI/TSSI parameters, SROM MCS offsets, IQ/LO calibration results, gain-table offsets, spur/bandedge state, noise sample count, and TSSI NPT counters.

Common `struct brcms_phy` fields used heavily include `hwpwrctrl`, `hwpwrctrl_capable`, `temppwrctrl_capable`, `txpa_2g[]`, `tx_srom_max_rate_2g[]`, `tx_power_min`, `tx_power_offset[]`, `radio_chanspec`, `xtalfreq`, `phy_lastcal`, `phy_forcecal`, and board flags. State is runtime-only and reconstructed after attach/init.

## Dependencies and Integration Points
- Linux kernel delay, CORDIC, and utility helpers.
- Broadcom chipcommon/PMU APIs for PLL and chip control.
- D11 registers for MAC control, sample capture, template/sample play, and PHY status.
- Common PHY helpers from `phy_cmn.c` and structures/constants from `phy_hal.h`, `phy_int.h`, `phy_lcn.h`, `phy_radio.h`, `phytbl_lcn.h`, and `phy_qmath.h`.
- Backend callbacks are consumed by `phy_cmn.c`.

## Risks and Edge Cases
- `wlc_phy_chanspec_set_lcnphy()` indexes `lcnphy_sfo_cfg[channel - 1]` without validating channel range.
- Calibration routines allocate with `GFP_ATOMIC` and may silently skip work on allocation failure.
- Save/restore-heavy calibration paths can leave hardware in loopback, deaf, override, or power-control-off state if cleanup is missed.
- `wlc_lcnphy_rx_iq_cal()` appears to restore `0x44c` from a value read out of `0x44d`, which may be a register-save bug.
- `wlc_lcnphy_tx_iqlo_loopback_cleanup()` uses a zero mask expression that clears all of `0x44c`.
- `wlc_lcnphy_start_tx_tone()` writes a fixed `data_buf[64]` using a computed sample count; unsupported tone frequencies could overflow the local buffer.
- RX gain search can return an edge gain index that later indexes gain tables; boundary behavior needs hardware tests.
- Sensor setup temporarily forces high TX power indices and disables power control, making restore correctness important.

## Test Signals
- Attach/init matrix across LCN revisions and board flags: no PA, FEM, FEM BT, external LNA, and temperature option variants.
- Channel tests for channels 1-14, channel 14 filter selection, PLL/spur modes, and invalid channel rejection.
- TX power tests for TSSI hardware, temperature-based, manual/off, user/regulatory target changes, MCS20 offsets, and FEM/non-FEM tables.
- Calibration tests for TX IQ/LO table updates, RX IQ coefficients, MAC suspend/resume, deaf mode, tone start/stop, and power-control restoration.
- Sensor tests for temp/voltage mode 0 and mode 1 with register restoration.
- RX power tests for gain-index search boundaries, frequency correction, temperature correction, and noise sample count.
