# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_DIG.h

## Purpose

`odm_DIG.h` declares the DIG and false-alarm data structures, DIG thresholds, low-power thresholds, and the public DIG/adaptivity/false-alarm APIs. The source was read as a complete 169-line file.

## Important APIs, Types, and Functions

The header defines `struct dig_t`, `struct false_ALARM_STATISTICS`, `enum ODM_Pause_DIG_TYPE`, threshold macros such as `DM_DIG_MAX_NIC`, `DM_DIG_MIN_NIC`, `DM_DIG_FA_TH*`, `DM_DIG_BACKOFF_*`, `DM_DIG_FA_TH*_LPS`, and prototypes for all functions implemented in `odm_DIG.c`.

## Control Flow

There is no executable flow; it defines the state and constants used by the ODM watchdog and DIG implementation.

## State and Persistence Behavior

`struct dig_t` stores current and previous IGI, thresholds, bounds, false-alarm recovery state, CCK CCA threshold state, BT IGI, and media-connect flags. `struct false_ALARM_STATISTICS` stores OFDM, CCK, and aggregate counter snapshots.

## Dependencies and Integration Points

It is included by `odm.h` and `odm_precomp.h`. It integrates with `dm_odm_t`, PHY register access, false alarm counter reads, RSSI processing, and low-power DM handling.

## Risks and Edge Cases

Many fields are legacy or unused in this trimmed driver, so initialization coverage matters. Threshold constants are hardware-specific and should not be changed without RF validation.

## Test Signals

Compile coverage, initialization snapshots, and tests that verify each threshold macro's use through `odm_DIG` and `odm_DIGbyRSSI_LPS` provide useful signals.
