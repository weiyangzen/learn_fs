# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/reg_aic.h

## Purpose
`reg_aic.h` defines AR9003 adaptive interference cancellation register addresses and bit fields. It covers AIC control/status registers for both PHY chains, SRAM address/data windows, and a small set of Bluetooth coexistence PHY registers used to calibrate and monitor interference cancellation when WLAN and Bluetooth share RF resources.

## Important APIs, types, and constants
The file exports register offsets such as `AR_PHY_AIC_CTRL_0_B0`, `AR_PHY_AIC_STAT_0_B0`, `AR_PHY_AIC_SRAM_ADDR_B0`, and their B1-chain equivalents. Field masks and shifts describe monitor enable, calibration enable/reset, WLAN frequency, BT TX power thresholds, standby attenuation, RSSI min/max, radio delay, calibration convergence controls, monitor status, measurement counts, SRAM validity, attenuation entries, and isolation estimates.

## Control flow and integration
There is no executable code. AIC calibration and Bluetooth coexistence code uses these constants with PHY register read/modify/write helpers. The B0/B1 naming makes chain-specific programming explicit, while SRAM access macros support iterating over calibration entries through address/data registers.

## State and persistence behavior
All state is hardware-resident calibration and monitor state. Calibration status bits such as active/done/error reflect current hardware progress. SRAM fields hold AIC correction entries until cleared, recalibrated, or reset. The header does not persist anything in software.

## Dependencies
The offsets depend on `AR_SM_BASE`, `AR_SM1_BASE`, and `AR_AGC_BASE` from ath9k PHY register headers. Consumers must use the companion mask/shift macros consistently with `REG_RMW_FIELD`-style helpers.

## Risks
Risks center on incorrect chain selection, stale AIC SRAM contents, and misinterpreting signed/attenuation fields as plain unsigned values. Calibration done/error bits must be polled carefully to avoid enabling ineffective cancellation or blocking coexistence setup.

## Test signals
Relevant signals include successful AIC calibration completion, no calibration timeout/error bits, sane SRAM valid entries, improved coexistence throughput under Bluetooth activity, and no regression on devices without AIC support.
