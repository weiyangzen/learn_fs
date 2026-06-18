# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_n.c

## Purpose

This file implements the Broadcom b43 driver operations for IEEE 802.11n N-PHY devices. It is responsible for N-PHY allocation/init/free, PHY and radio register access, radio bring-up for Broadcom 2055/2056/2057 radios, channel setup, RF sequencing, RSSI/TSSI measurement, TX power control, TX/RX IQ and LO calibration, and revision-specific hardware workarounds.

The implementation is table- and register-driven. Most functions write PHY registers, radio registers, shared memory, or N-PHY tables through the common b43 accessors, with behavior split by `dev->phy.rev`, `phy->radio_rev`, current band, SPROM board flags, internal-vs-external PA configuration, and 20/40 MHz channel type.

## Important APIs, Types, and Functions

- `const struct b43_phy_operations b43_phyops_n`: exported operation table wiring N-PHY into the b43 core. It provides `.allocate`, `.free`, `.prepare_structs`, `.init`, `.phy_maskset`, `.radio_read`, `.radio_write`, `.software_rfkill`, `.switch_analog`, `.switch_channel`, `.get_default_chan`, and `.recalc_txpower`.
- Local calibration data types:
  - `struct nphy_txgains`: per-core TX LPF, TXGM, PGA, PAD, and IPA gain fields.
  - `struct nphy_iqcal_params`: derived TX calibration gains and correction counts used by TX IQ/LO calibration.
  - `struct nphy_iq_est`: accumulated I/Q power and product measurements from the PHY estimator.
- RF control helpers:
  - `b43_nphy_force_rf_sequence()` triggers RF sequence state-machine commands and waits for completion.
  - `b43_nphy_rf_ctl_override()`, `b43_nphy_rf_ctl_override_rev7()`, `b43_nphy_rf_ctl_override_one_to_many()`, and `b43_nphy_rf_ctl_intc_override()` manipulate RF override paths for different PHY revisions.
  - `b43_nphy_stay_in_carrier_search()` temporarily makes the receiver deaf by changing classifier and clipping state, guarded by `nphy->deaf_count`.
- Radio setup:
  - `b43_radio_2055_setup/init2055()`, `b43_radio_2056_setup/init2056()`, and `b43_radio_2057_setup/init()` upload channel or init tables and perform VCO/RC/RCCAL sequences.
  - `b43_chantab_radio_upload()`, `b43_chantab_radio_2056_upload()`, and `b43_radio_2057_chantab_upload()` translate channel-table entries into radio register writes.
- Calibration and measurement:
  - RSSI: `b43_nphy_rssi_select()`, `b43_nphy_poll_rssi()`, `b43_nphy_rssi_cal()`, and `b43_nphy_restore_rssi_cal()`.
  - TX power: `b43_nphy_tx_power_ctrl()`, `b43_nphy_tx_power_fix()`, `b43_nphy_tx_power_ctl_idle_tssi()`, `b43_nphy_tx_power_ctl_setup()`, `b43_nphy_tx_gain_table_upload()`, `b43_nphy_op_recalc_txpower()`.
  - TX/RX IQ and LO: `b43_nphy_cal_tx_iq_lo()`, `b43_nphy_cal_rx_iq()`, `b43_nphy_calc_rx_iq_comp()`, `b43_nphy_save_cal()`, `b43_nphy_restore_cal()`, `b43_nphy_reapply_tx_cal_coeffs()`.
  - Sample playback: `b43_nphy_gen_load_samples()`, `b43_nphy_load_samples()`, `b43_nphy_run_samples()`, `b43_nphy_tx_tone()`, and `b43_nphy_stop_playback()`.
- Initialization and channel entry points:
  - `b43_phy_initn()` is the main N-PHY initialization path.
  - `b43_nphy_set_channel()` chooses the right radio/channel table and calls `b43_nphy_channel_setup()`.
  - `b43_nphy_op_switch_channel()` validates requested channel numbers but ultimately uses the mac80211 chandef channel from `dev->wl->hw->conf.chandef`.

## Control Flow

Allocation and preparation start through `b43_nphy_op_allocate()` and `b43_nphy_op_prepare_structs()`. Preparation zeros `struct b43_phy_n`, sets defaults for hang avoidance, spur avoidance, gain boost, TX/RX chains, periodic calibration mode, TX power control state, internal PA flags, and cached TX power indices.

Initialization flows through `b43_nphy_op_init()` into `b43_phy_initn()`:

1. Apply selected chip-control tweaks for external LNA cases.
2. Initialize N-PHY tables with `b43_nphy_tables_init()`.
3. Clear RF, AFE, and override registers, reset sequence override modes, and set baseline timing/MIMO settings.
4. Configure TX/RX chain selection, PAPD/digital filters for internal PA, or external PA filters.
5. Apply broad revision-specific workarounds through `b43_nphy_workarounds()`.
6. Reset CCA, enable PHY clock, and perform RF transition sequences for older PHYs.
7. Disable TX power control, apply fixed TX gain, measure idle TSSI, set up hardware TX power tables, upload gain tables, and restore requested TX power-control state.
8. Run or restore RSSI calibration and IQ/TX calibration caches depending on band, cached chanspecs, mute state, and measurement hold state.
9. Rebuild TX power coefficients, set MAC interface delay registers, update TX LPF bandwidth, and run spur workaround for rev3+.

Channel switching enters through `b43_nphy_op_switch_channel()` and `b43_nphy_set_channel()`. The code selects a channel-table entry based on PHY revision: rev7+ uses 2057 tables, rev3-6 uses 2056 tables, and older revs use 2055 tables. It then sets the temporary `phy->channel`, applies HT40 sideband bits, runs radio setup, uploads PHY SFO/channel registers, toggles BPHY reset for band changes, updates classifier behavior for channel 14, adjusts TX power/LNA/LPF state, applies PMU spur avoidance, and resets CCA.

TX power recalculation in `b43_nphy_op_recalc_txpower()` skips work when frequency and desired limit are unchanged. Otherwise it rebuilds a `struct b43_ppr` from SPROM, regulatory, and user limits, applies a minimum, suspends the MAC, sets up TX power tables, re-enables or disables hardware power control according to `nphy->txpwrctrl`, and caches the recalculation key.

## State and Persistence Behavior

The persistent driver state lives primarily in `dev->phy.n` (`struct b43_phy_n` in `phy_n.h`). This file reads and updates many of its fields:

- Calibration caches are band-scoped. `iqcal_chanspec_2G/5G`, `rssical_chanspec_2G/5G`, `cal_cache`, and `rssical_cache` store channel identity, RX IQ coefficients, TX IQ/LO coefficients, LOFT radio registers, RSSI radio registers, and RSSI PHY scale/offset registers. `b43_nphy_save_cal()` and `b43_nphy_restore_cal()` handle IQ/TX cal state; `b43_nphy_rev3_rssi_cal()` and `b43_nphy_restore_rssi_cal()` handle RSSI state.
- TX power state includes `txpwrctrl`, `tx_pwr_idx[]`, `tx_power_offset[]`, `adj_pwr_tbl[]`, `pwr_ctl_info[]`, `tx_pwr_max_ppr`, and last recalculation frequency/limit. Disabling TX power control saves current hardware indices when possible; enabling restores them when not set to sentinel value `128`.
- Sample playback state uses `bb_mult_save` and `lpf_bw_overrode_for_sample_play` to restore modified baseband multiplier and LPF overrides in `b43_nphy_stop_playback()`.
- Calibration setup/cleanup uses temporary save arrays `tx_rx_cal_phy_saveregs[]` and `tx_rx_cal_radio_saveregs[]`, plus `rfctrl_intc1_save/rfctrl_intc2_save` for PA override.
- `deaf_count`, `classifier_state`, and `clip_state[]` implement nested carrier-search/deafening. The first enter saves classifier/clip state; the last exit restores it.
- Chain and behavior flags such as `phyrxchain`, `txrx_chain`, `hang_avoid`, `gain_boost`, `elna_gain_config`, `ipa2g_on`, `ipa5g_on`, `use_int_tx_iq_lo_cal`, `spur_avoid`, and `preamble_override` steer future init, channel, and calibration behavior.

The hardware itself is also a state store: many paths save selected PHY/radio registers, overwrite them for calibration or RF sequencing, and restore them manually. Missed cleanup would leave the radio in a non-normal mode.

## Dependencies and Integration Points

- Kernel APIs: `linux/cordic.h` for sample generation, `linux/delay.h` for `udelay()`, `msleep()`, and `usleep_range()`, `linux/slab.h` for allocations, integer helpers such as `clamp_val()`, `min_t()`, `int_sqrt()`, `hweight32()`, and bit helpers such as `fls()`.
- b43 core APIs: `b43_phy_read/write/mask/set/maskset`, `b43_radio_read/write/mask/set/maskset`, `b43_ntab_read/write[_bulk]`, `b43_mac_suspend/enable`, `b43_switch_channel`, `b43_mac_switch_freq`, `b43_mac_phy_clock_set`, MMIO helpers, shared-memory writes, debug/error logging, and status/debug helpers.
- Tables and radio definitions: `tables_nphy.h`, `radio_2055.h`, `radio_2056.h`, and `radio_2057.h` provide register IDs, init tables, channel tables, gain tables, RF override mapping tables, TX filters, LO/IQ calibration command tables, and N-PHY table accessors.
- SPROM and platform integration: SPROM board flags, FEM fields, PA coefficients, antenna/power data, chip ID/package/revision, and bus type alter radio setup and workarounds. BCMA and SSB chipcommon/PMU hooks are used for GPIO and spur-avoid PLL updates.
- mac80211/cfg80211 integration: current band and channel definition come from `dev->wl`/`phy->chandef`; channel type is obtained with `cfg80211_get_chandef_type()`, and regulatory/user power limits feed TX power recalculation.
- PPR integration: `b43_ppr_*()` functions build and clamp per-rate target power used by N-PHY power-control setup.

## Risks and Edge Cases

- Revision coverage is incomplete. Many rev19+ paths are explicit `TODO`, including RF overrides, RSSI selection/calibration, gain-control workarounds, TX power setup, channel setup, RF kill, analog switching, and TX calibration. `b43_nphy_set_channel()` returns `-ESRCH` for rev19+.
- `b43_nphy_rev3_cal_rx_iq()` returns `-1`, so RX IQ calibration for rev3+ is effectively unimplemented even though the init path may attempt it after TX IQ/LO calibration.
- Register programming is highly order-sensitive. Numerous paths depend on save/restore symmetry around RF/AFE overrides, carrier-search deafening, playback, MAC suspend windows, PHY lock bits, and chip/radio reset sequences.
- Timeouts are logged but often continue with default or zero results. RF sequence, radio RC/RCCAL, sample run, RSSI polling, and IQ local calibration timeout behavior may leave calibration degraded rather than failing init outright.
- Channel handling depends on the current `chandef` rather than the `new_channel` numeric argument after validation. Callers must keep `dev->wl->hw->conf.chandef` coherent before invoking the switch op.
- Several comments indicate deliberate divergence from specs to match Broadcom `wl`, plus placeholder conditions such as `if (0)`, `true /* TODO */`, and “TODO Enable this once we have gains configured”. Those are portability and future-maintenance risks.
- Hardware table writes use many literal offsets. Changes to table layout, PHY revision mappings, or register definitions could silently corrupt unrelated hardware state.
- Calibration caches are keyed only by band/channel frequency/channel type in selected places. Temperature, board-specific drift, PA state, or changed power-control mode may require recalibration even when cached chanspecs still match.

## Test Signals

- Build signals: compile this driver with representative `CONFIG_B43`, `CONFIG_B43_BCMA`, and `CONFIG_B43_SSB` combinations; enable `B43_DEBUG` to catch invalid PHY route access in `check_phyreg()`.
- Probe/init signals: successful N-PHY allocation, radio init, `b43_phy_initn()` completion, no `RF sequence status timeout`, `radio post init timeout`, `Radio recalibration timeout`, `Radio 0x2057 rcal/rccal timeout`, or sample-playback timeout logs.
- Channel-switch signals: switching across 2.4 GHz, 5 GHz, channel 14, HT20, HT40+, and HT40- should find channel-table entries, preserve BPHY reset state, update PMU spur avoidance on affected channels, and keep CCA/RX functional.
- TX power signals: `b43_nphy_op_recalc_txpower()` should recompute only when frequency or desired limit changes, produce sane `b43_ppr_get_max()` debug output, and preserve/restore `tx_pwr_idx[]` when hardware TX power control is toggled.
- Calibration signals: first init per band should populate RSSI and IQ calibration chanspec/cache fields; later same-band init should restore cached calibration. TX IQ/LO calibration should set `txiqlocal_coeffsvalid`; sample playback should always restore `bb_mult_save` and LPF override state.
- RF kill and analog-switch signals: with MAC suspended, blocking/unblocking RF should not leave radio power/control registers stuck off; unblock should reinitialize 2055/2056/2057 radios as appropriate and switch back to the current channel.
- Hardware behavior signals: stable association, throughput, RSSI reporting, noise floor, TX EVM/power, and MIMO chain behavior across both cores are the practical end-to-end checks for the register and table programming in this file.
