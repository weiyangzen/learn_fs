# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/phy.c

## Purpose

`phy.c` is the ath5k hardware layer for PHY and RF programming. It owns channel programming, RF-bank construction, gain and noise calibration, I/Q correction, spur mitigation, antenna selection, and transmit power table generation for AR5210/AR5211/AR5212-era Atheros radios. The code is highly hardware-specific and bridges mac80211 channel/rate concepts, EEPROM calibration data, and direct register writes through `ath5k_hw_reg_*` helpers.

## Important APIs, Types, and Functions

Externally visible entry points include `ath5k_hw_radio_revision()`, `ath5k_channel_ok()`, `ath5k_hw_chan_has_spur_noise()`, `ath5k_hw_phy_disable()`, `ath5k_hw_rfgain_opt_init()`, `ath5k_hw_gainf_calibrate()`, `ath5k_hw_init_nfcal_hist()`, `ath5k_hw_update_noise_floor()`, `ath5k_hw_phy_calibrate()`, `ath5k_hw_set_antenna_switch()`, `ath5k_hw_set_antenna_mode()`, `ath5k_hw_set_txpower_limit()`, and `ath5k_hw_phy_init()`.

Core internal helpers are grouped by hardware function. `ath5k_hw_rfb_op()` edits packed RF-bank fields described by `struct ath5k_rf_reg`; `ath5k_hw_rfregs_init()` selects RF-bank templates from `rfbuffer.h`, patches them using EEPROM fields, gain tables, bandwidth mode, and radio revision, then writes the resulting banks to hardware. Channel-specific helpers convert frequencies into radio synthesizer values for RF5110, RF5111, RF5112-class radios, and RF2425/AR2417-class radios. TX power helpers interpolate EEPROM calibration piers into PCDAC or PDADC tables and rate power indices.

The file depends heavily on `struct ath5k_hw` state: `ah_radio`, `ah_version`, `ah_mac_srev`, `ah_phy_revision`, `ah_bwmode`, `ah_current_channel`, `ah_rf_banks`, `ah_offset`, `ah_gain`, `ah_nfcal_hist`, and `ah_txpower`. EEPROM-derived inputs come from `struct ath5k_eeprom_info`, including OB/DB bias, XPD/PD gains, per-channel calibration piers, rate target powers, CTL edge powers, spur channels, and noise floor thresholds.

## Control Flow

The main initialization flow is `ath5k_hw_phy_init()`. It validates fast channel switching, optionally obtains RF bus access for a synth-only channel change, programs TX power early, writes OFDM timing and optional spur mitigation, then either finishes the fast path by starting noise-floor calibration or performs full RF initialization. The full path writes initial RF gain registers, constructs and writes RF banks, toggles 802.11b support on RF5111, sets the radio channel, enables the PHY, waits for synthesizer settle, probes ADC readiness, starts AGC/NF and optional I/Q calibration, waits for AGC completion, and restores antenna mode.

The channel path runs through `ath5k_hw_channel()`. It enforces hardware frequency range via `ath5k_channel_ok()`, chooses the radio-specific synthesizer programming routine, applies the channel-14 CCK Japan/world bit, and persists `ah_current_channel`.

Calibration has several separate loops. `ath5k_hw_phy_calibrate()` performs RF5110 full calibration or RF5111+ I/Q result harvesting, requests a PAPD gain probe when a full calibration requires thermal RF-gain tracking, and updates the noise floor if no NF calibration is already active. `ath5k_hw_update_noise_floor()` checks that hardware completed NF sampling, rejects values above EEPROM threshold, stores a rolling history, writes the median back to hardware, then starts the next NF measurement. `ath5k_hw_gainf_calibrate()` reads PAPD probe feedback, corrects CCK and RF5112A readings, validates detector-window range, and transitions RF gain state to `NEED_CHANGE` or back to `ACTIVE`.

TX power programming starts in `ath5k_hw_txpower()`. It selects PCDAC/PDADC table type by radio, reuses cached channel tables when channel and mode match, rebuilds channel power curves otherwise, writes the hardware power table, applies CTL edge limits, computes per-rate power targets, maps target powers to table indices, and writes the four rate-power registers plus optional TPC maxima.

## State and Persistence Behavior

This file mutates persistent driver state stored in `struct ath5k_hw`, not filesystem state. RF bank memory is allocated lazily with `kmalloc_array()` and reused across resets. Channel table setup is cached through `ah_txpower.txp_setup`, `txp_offset`, `txp_min_idx`, `txp_pd_table`, and related temporary arrays. Calibration state persists in `ah_cal_mask`, `ah_iq_cal_needed`, `ah_noise_floor`, `ah_nfcal_hist`, and `ah_gain.g_state`/`g_step_idx`/threshold fields. Antenna mode and selected antennas persist in `ah_ant_mode`, `ah_def_ant`, and `ah_tx_ant`.

Register writes are stateful hardware side effects. Many operations rely on prior reset state or EEPROM initialization: `ath5k_hw_phy_init()` explicitly assumes a warm reset state, and RF/TX power paths assume EEPROM calibration arrays and capability ranges are populated.

## Dependencies and Integration Points

The file includes Linux delay, allocation, sort, and unaligned access helpers, plus local ath5k headers `ath5k.h`, `reg.h`, `rfbuffer.h`, `rfgain.h`, and `../regd.h`. It integrates with mac80211 types such as `struct ieee80211_channel`, `enum nl80211_band`, `struct ieee80211_supported_band`, and `struct ieee80211_rate`. Regulatory limiting uses `ath5k_hw_regulatory()` and `ath_regd_get_band_ctl()`.

Register definitions from `reg.h` are central: PHY activation, AGC/NF/IQ, RF buffer controls, spur masks, antenna registers, TX power registers, QCU/DCU timing, PCU station bits, and EEPROM access fields are all programmed here. EEPROM parsing and capability setup happen elsewhere but are consumed throughout. Reset code calls `ath5k_hw_phy_init()`, periodic calibration code calls `ath5k_hw_phy_calibrate()` and `ath5k_hw_gainf_calibrate()`, and driver txpower/antenna controls call the exported setters.

## Risks and Edge Cases

The code encodes reverse-engineered radio behavior and many chip-family special cases. Incorrect radio revision checks, bandwidth assumptions, or EEPROM indexes can produce invalid RF-bank values or bad transmit power. `ath5k_hw_rfb_op()` performs bit packing across RF banks; malformed `ath5k_rf_reg` metadata or offsets can silently corrupt RF programming, although there is a boundary check for column, length, and bit range.

Calibration risk is high because several routines deliberately interrupt or alter PHY/RF operation. NF calibration may leave the previous value if hardware does not complete, AGC may time out in noisy environments, and I/Q calibration returns normal non-fatal failures when traffic is insufficient. TX power code must avoid divide-by-zero, table underflow/overflow, negative power offsets, and out-of-bounds PCDAC/PDADC values; the implementation has clamps and extrapolation guards but remains sensitive to malformed EEPROM data.

Fast channel switching risks stale state because it bypasses most RF setup and only starts NF calibration. It must only be used when modulation mode does not change and RF bus grant succeeds. Channel programming comments warn that unsupported frequencies may damage hardware, so callers must honor `ath5k_channel_ok()` and regulatory paths above this layer.

## Test Signals

Useful runtime signals are kernel logs under `ATH5K_DEBUG_CALIBRATE` and `ATH5K_DEBUG_TXPOWER`, calibration timeout messages, noise floor values, I/Q correction values, gain step transitions, and channel out-of-range errors. Hardware validation should cover AR5210, AR5211, AR5212, RF5110/5111/5112/2413/2316/5413/2317/2425 combinations where available, with 2 GHz, 5 GHz, 11b, 11g, 11a, turbo, half-rate, and quarter-rate modes. Behavioral tests should verify reset/channel-change success, txpower limits, rate power table contents, beacon/traffic continuity after calibration, antenna mode effects, and operation on channels with EEPROM spur entries.
