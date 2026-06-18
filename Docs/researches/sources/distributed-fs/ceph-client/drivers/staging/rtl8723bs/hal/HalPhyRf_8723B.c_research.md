# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalPhyRf_8723B.c

## Purpose

`HalPhyRf_8723B.c` implements RTL8723B-specific Tx power tracking, IQ calibration (IQK), LC calibration (LCK), and IQC restore/application logic. The file was read as a complete 1796-line source.

## Important APIs, Types, and Functions

Public APIs are `ODM_TxPwrTrackSetPwr_8723B`, `ConfigureTxpowerTrack_8723B`, `ODM_SetIQCbyRFpath`, `PHY_IQCalibrate_8723B`, and `PHY_LCCalibrate_8723B`. Important internals include `setIqkMatrix_8723B`, `setCCKFilterCoefficient`, `GetDeltaSwingTable_8723B`, path calibration helpers `phy_PathA_IQK_8723B`, `phy_PathA_RxIQK8723B`, `phy_PathB_IQK_8723B`, `phy_PathB_RxIQK8723B`, matrix fillers `_PHY_PathAFillIQKMatrix8723B` and `_PHY_PathBFillIQKMatrix8723B`, save/reload helpers for ADDA/MAC/BB registers, `phy_SimularityCompare_8723B`, `phy_IQCalibrate_8723B`, and `phy_LCCalibrate_8723B`.

## Control Flow

Power tracking chooses limits based on current or forced data rate, then applies TXAGC, BBSWING, or MIX_MODE. MIX_MODE uses BB swing until limits are exceeded, then records remnant OFDM/CCK indexes and refreshes Tx power index sections. IQK checks calibration ability and in-progress flags, optionally restores saved IQC/LOK data, otherwise performs up to three calibration candidates, each saving/restoring MAC/BB/ADDA state, programming IQK tones and RF modes, switching antenna paths/GNT_BT, running one-shot TX/RX IQK for path A and optionally path B, validating result registers, comparing candidate similarity, filling IQC matrices, saving recoverable backup registers, restoring GNT_BT and RF mode, and applying IQC for the selected RF path in 2-antenna mode. LCK waits for scans to finish, marks LCK in progress, pauses traffic or continuous TX, toggles RF LC calibration bit, handles an SDIO/package-specific channel 10 workaround, and restores traffic/RF state.

## State and Persistence Behavior

The code mutates `pDM_Odm->RFCalibrateInfo`: IQK in-progress flags, LCK in-progress flags, LOK values, IQC register/value arrays, IQK result registers, backup/recover arrays, thermal power tracking indexes, remnant swing indexes, and TxAGC modify flags. It writes persistent BB/RF/MAC hardware state for IQ imbalance, CCK coefficients, RF modes, PA/LNA calibration modes, TX power indexes, queue pause state, and LC calibration state.

## Dependencies and Integration Points

It includes `<drv_types.h>` and `odm_precomp.h`, and depends on `HalPhyRf.h`, generated RF power tracking tables from `HalHWImg8723B_RF.c`, ODM register constants, `PHY_SetBBReg`, `PHY_QueryBBReg`, `PHY_SetRFReg`, `PHY_QueryRFReg`, `PHY_SetTxPowerIndexByRateSection`, `rtw_read8`, `rtw_write8`, `rtw_write32`, `mdelay`, rate macros, and swing tables.

## Risks and Edge Cases

Calibration is timing- and hardware-state-sensitive. Early returns in `PHY_IQCalibrate_8723B` after successful restore leave `bIQKInProgress` set because the flag is set before the restore block and not cleared on that return path. `ODM_CheckPowerStatus` always returns true, so callers do not get real power-state protection. Many register constants assume 8723B path mapping and can disrupt BT coexistence if interrupted. Candidate selection uses register similarity heuristics; failed candidates fall back to defaults and may degrade RF quality. LCK blocks in 50 ms increments up to 2 seconds while scan is in progress.

## Test Signals

Hardware IQK/LCK result traces, tests for restore/recovery paths, checks that in-progress flags clear after every exit path, Tx power tracking tests for CCK/OFDM/HT rates, scan/LCK interaction tests, and RF throughput/EVM/regulatory validation after calibration are important signals.
