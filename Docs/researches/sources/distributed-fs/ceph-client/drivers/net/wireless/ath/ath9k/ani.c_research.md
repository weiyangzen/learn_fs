# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ani.c

## Purpose

This file implements ath9k Adaptive Noise Immunity for hardware. ANI observes PHY error counters and listen time, then raises or lowers OFDM and CCK noise-immunity levels by programming hardware controls such as spur immunity, FIR first step, OFDM weak signal detection, and MRC CCK.

## Important APIs, tables, and functions

- `ofdm_level_table[]` maps OFDM immunity levels to spur immunity, FIR step, and weak-signal-detection state.
- `cck_level_table[]` maps CCK immunity levels to FIR step and MRC CCK state.
- `ath9k_hw_ani_init()` initializes thresholds, default levels, poll period, counters, and MIB counter collection.
- `ath9k_ani_reset()` restores default or historical levels on reset/channel change and restarts counters.
- `ath9k_hw_ani_monitor()` is exported and performs periodic counter analysis, raising or lowering immunity.
- `ath9k_enable_mib_counters()` and `ath9k_hw_disable_mib_counters()` configure and freeze/clear MIB counters.

## Control flow

Initialization chooses old or new trigger thresholds based on chip revision, sets default ANI state, restarts counters, and enables MIB counters. Reset chooses either default levels for scanning/AP-style operation or historical levels for station/adhoc operation, applies OFDM and CCK levels, and restarts PHY error counters.

Monitoring first updates cycle/listen counters. If listen time is non-positive, ANI restarts and records the anomaly. Otherwise it accumulates listen time, updates MIB stats, reads PHY error counters, derives OFDM and CCK error rates per second, and compares them with high/low thresholds once `listenTime > aniperiod`. Low OFDM and CCK error rates lower one immunity side per turn. High OFDM error rates raise OFDM immunity and mark the next lowering turn for CCK; high CCK error rates raise CCK immunity and mark the next lowering turn for OFDM. Any adjustment restarts counters.

## State and persistence behavior

All state is in `ah->ani`, `ah->stats`, `ah->ah_mibStats`, and `ah->config`. The driver remembers current immunity levels, OFDM/CCK turn selection, listen time, previous counter values, and stats. Nothing persists across driver unload. ANI level choices can be restored across channel changes while the same `ath_hw` instance lives.

## Dependencies and integration points

The file depends on register definitions and helper macros from `hw.h` and `hw-ops.h`, chip revision predicates, `ath9k_hw_ani_control()`, cycle counter helpers, MIB/PHY error registers, and cfg80211 opmode constants. It is built into `ath9k_hw.o` and called by reset, channel, and periodic maintenance paths elsewhere in ath9k.

## Risks

Incorrect threshold tuning can reduce sensitivity or allow high false-detect rates. Register writes depend on chip family behavior; there are explicit exceptions for AR9100, pre-AR9300, AR9485, AR9565, and AR9561. Counter wrap or listen-time anomalies can distort rates. The level tables must keep default entries aligned with INI programming, as noted by the sanity-check comment.

## Test signals

Observe ANI debug logs under clean and noisy RF conditions, verify `ast_ani_*` stats change as expected, compare packet loss/throughput while forcing OFDM or CCK interference, test scan/AP/station resets, validate chip-family exceptions, and confirm no regressions in MIB counter accounting across suspend/reset/channel changes.
