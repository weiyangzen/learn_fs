# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_lp.c

## Purpose

`phy_lp.c` implements the b43 LP-PHY backend for Broadcom low-power 802.11a/g hardware. It supports SSB-only LP PHY devices, 2062 and 2063 radios, 2 GHz and 5 GHz channel tables, SPROM-derived power/RSSI setup, baseband/radio initialization, RC calibration, channel tuning, antenna selection, RF kill, analog switching, TX gain and TX power-control setup, RX IQ calibration, sample/tone generation, periodic calibration, and low-level PHY/radio access.

The file is significantly more complete than LCN in some areas, but many paths still have TODO/FIXME markers, especially hardware TX power control, ACI, calibration details, and spec ambiguities.

## Important APIs, Types, and Functions

- `const struct b43_phy_operations b43_phyops_lp` wires allocation/free, prepare/init, PHY maskset, radio read/write, RF kill, analog switch, channel switch, default channel, RX antenna selection, TX-power recalc/adjust stubs, and 15/60 second periodic work.
- `b43_lpphy_op_allocate()`, `_prepare_structs()`, and `_free()` manage `struct b43_phy_lp`, setting default antenna state after zeroing.
- `b43_lpphy_op_init()` is the lifecycle entry point. It rejects non-SSB devices, reads band-specific SPROM data, initializes baseband and radio, calibrates RC, switches initially to channel 7, initializes TX power control, and runs calibration.
- `lpphy_read_band_sprom()` transfers SPROM isolation, PA, RSSI, max-power, and per-rate power-offset data into `dev->phy.lp`.
- `lpphy_table_init()`, `lpphy_baseband_rev0_1_init()`, `lpphy_baseband_rev2plus_init()`, and `lpphy_baseband_init()` upload LP tables and configure revision-specific baseband/RSSI/AFE/TR lookup state.
- `lpphy_2062_init()`, `lpphy_2063_init()`, `lpphy_radio_init()`, `lpphy_b2062_tune()`, and `lpphy_b2063_tune()` initialize and tune radio hardware. Static `b2062_chantbl` and `b2063_chantbl` provide channel-specific data.
- `lpphy_calibrate_rc()`, `lpphy_rev0_1_rc_calib()`, `lpphy_rev2plus_rc_calib()`, `lpphy_set_rc_cap()`, and `lpphy_loopback()` handle RC and loopback calibration.
- `lpphy_set_tx_power_control()`, `lpphy_tx_pctl_init_hw()`, `lpphy_tx_pctl_init_sw()`, `lpphy_tx_pctl_init()`, and `lpphy_set_tx_power_by_index()` manage TX power-control mode, table-selected gains, BB multiplier, IQ coefficients, and RF power overrides.
- `lpphy_rx_iq_cal()`, `lpphy_calc_rx_iq_comp()`, `lpphy_run_ddfs()`, `lpphy_start_tx_tone()`, `lpphy_stop_tx_tone()`, and `lpphy_papd_cal_txpwr()` implement calibration support using IQ estimates and generated tones.
- `b43_lpphy_op_switch_channel()` dispatches to the proper radio tune function, applies analog filter and gain-table updates for 2062, persists `lpphy->channel`, and writes `B43_MMIO_CHANNEL`.

## Control Flow

The common PHY layer enters through `b43_phyops_lp`. Allocation installs `dev->phy.lp`; preparation clears all LP state and sets default antenna. Init requires `B43_BUS_SSB`; otherwise it returns `-EOPNOTSUPP`. On supported hardware it reads SPROM band fields into LP state, initializes table/baseband state according to PHY revision, initializes the radio according to radio version, performs RC calibration, switches to channel 7, initializes TX power control, runs a broader calibration path, and leaves later operation to channel, RF kill, antenna, and periodic callbacks.

Baseband initialization is split by revision. Rev0/1 setup programs AFE, CRS, clipping, RSSI, TR lookup, FEM/BT flags, PAREF, PMU, and 2 GHz/5 GHz differences. Rev2+ setup uses a different register set, optionally writes board-revision and chip-specific tables, saves digital filter state, and configures AFE/RSSI registers differently.

Radio channel switching is table-driven. 2062 tuning finds a `b2062_chantbl` entry, writes tune registers, calculates PLL values from crystal frequency and `lpphy->pdiv`, calibrates VCO, and returns `-EIO` if the fallback VCO calibration still reports failure. 2063 tuning finds a `b2063_chantbl` entry, writes radio front-end values, computes PLL calibration values with fixed-point division, runs VCO calibration, and restores a saved register. Invalid channels return `-EINVAL`.

Calibration paths suspend or deafen receive behavior as needed, save old overrides/gains/TX power mode, run loopback or IQ estimation, and restore state. `lpphy_calibration()` is also the 60-second periodic hook; it turns off TX power control, optionally runs workarounds/full calibration, restores digital filters for rev2+, runs RX IQ calibration, and re-enables the MAC.

## State and Persistence

`struct b43_phy_lp` is the primary runtime state. It persists under `dev->phy.lp` until free and is reset by `prepare_structs()`. Important fields populated from SPROM include transmit isolation, max TX power by band, per-rate max power arrays, PA coefficients, RSSI offsets/calibration values, and BX architecture. Runtime/calibration fields include `txpctl_mode`, TSSI index/NPT/count, target TX frequency, TX power index override, `rc_cap`, `full_calib_chan`, best IQ-local coefficients, saved digital filter state, CRS disable reference flags, PLL divider `pdiv`, current channel, active antenna, and active TX tone frequency.

The file has many local save/restore blocks around calibration. `lpphy_pr41573_workaround()` is especially stateful: it saves a 256-entry TX power table region, power-control mode, override index, TSSI fields, reruns partial init/calibration/RF state, restores the table and channel, restores antenna and RC cap, and writes the saved TX power-control mode back.

Hardware state is programmed through PHY/radio registers and LP tables. There is no persistent storage beyond SPROM input and volatile driver memory. Several header fields have FIXME comments about initial values; callers must ensure init paths populate them before depending on them.

## Dependencies and Integration Points

The file includes `b43.h`, `main.h`, `phy_lp.h`, `phy_common.h`, `tables_lpphy.h`, Linux `cordic`, and Linux `slab`. It depends on SSB chipcommon/PMU helpers, SPROM data, b43 PHY/radio/table accessors, MAC suspend/enable, host flags, MMIO channel writes, dummy transmission, mac80211 band state, and LP table upload helpers such as `lpphy_rev0_1_table_init()`, `lpphy_rev2plus_table_init()`, `lpphy_init_tx_gain_table()`, `b2062_upload_init_table()`, and `b2063_upload_init_table()`.

The exported operation table is consumed by common PHY dispatch for LP PHY devices. The implementation is tightly coupled to `phy_lp.h` register constants and `struct b43_phy_lp`, and it shares generic PHY operation expectations with the other b43 PHY backends.

## Risks and Edge Cases

- Init is SSB-only. Any BCMA LP device fails with `-EOPNOTSUPP`.
- Many TODO/FIXME comments remain: incomplete prepare state, cached host-flag write concern, PMU recalibration, channel 14 analog filter uncertainty, hardware TX power-control capability disabled behind `if (0)`, missing NPT/offset/target-power work, missing ACI init, and empty TX-power recalc/adjust/15-second work.
- Some calculations rely on crystal frequency and PMU capability. The code warns if PMU capability or crystal frequency is absent but still uses derived values.
- Calibration loops can sleep/poll for long periods. Timeout behavior is limited and can leave partially restored radio state if not carefully audited.
- `lpphy_start_tx_tone()` has an explicit FIXME about negative frequency semantics and warns if sample count exceeds 63.
- Static channel tables are large and hardware ABI sensitive. Missing channel entries return `-EINVAL`; bad entries can misprogram PLL/radio state.
- `lpphy_calc_rx_iq_comp()` performs integer fixed-point math and square root on values derived from hardware accumulators; divide-by-zero and sign/overflow assumptions should be treated carefully.
- TX power-control mode writes include a suspicious `((u16)lpphy->tssi_npt << 16)` expression that shifts out of a 16-bit value before maskset semantics, matching a TODO-heavy area.

## Test Signals

Validation should include SSB LP devices with 2062 and 2063 radios, rev0/1 and rev2+ PHY revisions, both 2 GHz and 5 GHz channel tables, invalid channel rejection, VCO calibration fallback on 2062, RC calibration completion, channel field persistence, antenna selection on rev0/1, RF kill on/off, and periodic 60-second calibration. Memory-failure testing should cover `b43_lpphy_op_allocate()` and `lpphy_pr41573_workaround()` allocation failure. Hardware logs should be checked for `B43_WARN_ON` hits, channel 7 init-switch failures, and unexpected TX power-control mode warnings.
