# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/antenna.c

## Purpose

This file implements ath9k antenna diversity and LNA combining decisions for chips with ant-div support, especially AR9285 and AR9485/AR9565/AR9331-style EEPROM layouts. It observes received packet RSSI and antenna-selection metadata, decides when alternate antenna/LNA configurations are better, and writes updated hardware ant-div configuration.

## Important APIs and functions

- `ath_ant_comb_scan()` is the public entry point called with `struct ath_softc` and `struct ath_rx_status` for RX samples.
- `ath_is_alt_ant_ratio_better()` evaluates whether alternate antenna usage and RSSI justify preference changes.
- `ath_ant_div_comb_alt_check()` applies group-specific decision rules for switching main and alternate LNA settings.
- `ath_lnaconf_alt_good_scan()`, `ath_select_ant_div_from_quick_scan()`, and `ath_ant_set_alt_ratio()` manage multi-step quick scans when the alternate path looks promising.
- `ath_ant_div_conf_fast_divbias()` maps main/alt LNA combinations and diversity groups to hardware `fast_div_bias` values.
- `ath_ant_try_scan()`, `ath_ant_try_switch()`, and `ath_ant_short_scan_check()` implement scan-state progression and early termination.

## Control flow

Each RX sample extracts current and main antenna configuration from `rs_rssi_ctl[2]` and reads main/alt RSSI from control chains 0 and 1. Positive RSSI samples increment packet counts, RSSI totals, main/alt receive counters, and debug stats. The function waits until enough packets are sampled, an aggregate ends, or a short-scan condition fires. It then computes alternate receive ratio and average RSSI, reads current hardware ant-div config, and updates the ant-comb state machine.

Every `ATH_ANT_DIV_COMB_MAX_COUNT` windows, a high alternate ratio starts an alternate-good quick scan; otherwise the scan starts with simpler alternate LNA swapping. During scans the code cycles through LNA1, LNA2, LNA1+LNA2, and LNA1-LNA2 combinations, records RSSI for each, selects the best main and alternate config, adjusts fast-div bias, writes the config with `ath9k_hw_antdiv_comb_conf_set()`, records debug stats, and resets sample counters.

## State and persistence behavior

State lives in `sc->ant_comb`: scan flags, quick-scan count, RSSI totals for LNA variants, alternate ratios, threshold choices, packet counters, scan start time, and optional fast-div bias override. Hardware state is persisted in ant-div registers until changed again or reset. No disk state exists.

## Dependencies and integration points

The file depends on `ath9k.h`, `struct ath_rx_status`, `struct ath_hw_antcomb_conf`, ant-div constants/macros, jiffies timing, hardware get/set helpers, and debug statistic helpers. It integrates with RX processing and the hardware layer that reads EEPROM-derived ant-div capabilities.

## Risks

The algorithm is sensitive to RSSI sample quality, packet count thresholds, aggregate handling, and group-specific magic constants. Bad thresholds can cause oscillation, poor diversity choice, or reduced sensitivity. RSSI values of zero or negative are ignored for totals, so unusual hardware reporting can starve decisions. Fast-div bias tables are dense hardware knowledge and easy to regress. Timing and counter reset behavior matters for short scans.

## Test signals

Useful tests include RX diversity debug stats, controlled RF tests with known stronger LNA paths, mobility tests that force main/alt changes, low-RSSI and high-RSSI threshold cases, short-scan timeout and packet-count cases, aggregate traffic behavior, and per-chip EEPROM ant-div configuration validation.
