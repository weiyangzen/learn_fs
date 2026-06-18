# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar5008_initvals.h

## Purpose

This header contains static initialization tables for AR5008/AR5416-class ath9k hardware. The arrays provide register address/value sequences for base modes, common registers, RF gain, Bank6 transmit-power-control programming, and ADDAC settings.

## Important data

- `ar5416Modes[][5]` stores mode-specific register values with columns for 5 GHz HT20, 5 GHz HT40, 2 GHz HT40, and 2 GHz HT20.
- `ar5416Common[][2]` stores register writes shared by all modes, including MAC/baseband defaults, timing, filter, queue, PHY, and chain-related registers.
- `ar5416BB_RfGain[][3]` stores 5 GHz and 2 GHz RF gain table programming values.
- `ar5416Bank6TPC[][3]` stores Bank6 transmit power control sequences for 5 GHz and 2 GHz.
- `ar5416Addac[][2]` stores common ADDAC programming values.

## Control flow and integration

There are no functions in this file. Hardware initialization code includes these tables and walks them during device reset/attach or channel/mode setup, selecting the correct column for the target band and HT width. The table shapes encode how generic init helpers interpret address and value columns.

## State and persistence behavior

The arrays are compile-time read-only data. They do not hold runtime state, but applying them programs persistent hardware register state until reset or subsequent register writes. They represent vendor-provided INI defaults that other runtime systems, including ANI, assume as baselines.

## Dependencies and risks

The header depends on includers having `u32` defined and knowing the exact array names and dimensions. Risk is high for accidental numeric edits: register addresses, repeated writes to the same address, mode columns, and band-specific values are hardware calibration data. Misaligned columns can break one band or channel width while leaving others apparently functional. Default ANI levels and calibration paths may assume these values.

## Test signals

Validation requires hardware bring-up on AR5008/AR5416-class devices across 2 GHz and 5 GHz, HT20 and HT40, plus regression checks for attach/reset success, calibration, transmit power, receive sensitivity, ANI stability, throughput, and spectral/regulatory behavior. Code review should treat diffs as table-data changes rather than algorithm changes and compare against known vendor INI sources where available.
