# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_DIG.c

## Purpose

`odm_DIG.c` implements dynamic initial gain (DIG), false-alarm statistics, NHM/adaptivity, EDCCA threshold control, low-power DIG, and CCK packet-detect threshold tuning for RTL8723BS. The source was read as a complete 813-line file.

## Important APIs, Types, and Functions

Important functions are `odm_NHMCounterStatisticsInit`, `odm_NHMCounterStatistics`, `odm_GetNHMCounterStatistics`, `odm_NHMCounterStatisticsReset`, `odm_NHMBBInit`, `odm_NHMBB`, `odm_SearchPwdBLowerBound`, `odm_AdaptivityInit`, `odm_Adaptivity`, `ODM_Write_DIG`, `odm_DigAbort`, `odm_DIGInit`, `odm_DIG`, `odm_DIGbyRSSI_LPS`, `odm_FalseAlarmCounterStatistics`, `odm_FAThresholdCheck`, `odm_ForbiddenIGICheck`, `odm_CCKPacketDetectionThresh`, and `ODM_Write_CCK_CCA_Thres`.

## Control Flow

Initialization configures NHM counters and adaptivity defaults, reads the current IGI from hardware, and sets DIG thresholds/bounds. Each watchdog pass reads false-alarm counters and NHM, then `odm_DIG` decides whether to abort due to disabled support, scanning, or disabled initial gain. It computes RSSI-based gain bounds, adjusts for BT and antenna diversity, updates forbidden IGI for excessive false alarms, selects false-alarm thresholds, moves current IGI up or down, clamps it, applies adaptivity limits, and writes IGI registers. Adaptivity can search for a lower EDCCA bound by polling report bits and then writes OFDM ECCA thresholds. CCK PD tuning writes `ODM_REG(CCK_CCA)` based on RSSI and CCK false alarms.

## State and Persistence Behavior

State is stored in `dm_odm_t->DM_DigTable`, `FalseAlmCnt`, NHM/adaptivity fields, RSSI fields, and hardware registers for IGI, NHM, false-alarm counters, EDCCA thresholds, and CCK CCA threshold. Values persist until the next watchdog, reset, or mode transition.

## Dependencies and Integration Points

It depends on register macros from `odm_RegDefine11N.h`/`Hal8723BReg.h`, PHY BB register access, traffic byte counters hooked into `dm_odm_t`, RSSI values from `odm_HWConfig.c`/RSSI monitor, support flags from `rtl8723b_dm.c`, and watchdog sequencing in `odm.c`.

## Risks and Edge Cases

`odm_NHMBB` dereferences traffic counter pointers and assumes common-info hooks are installed. False-alarm counters are held/read but not visibly reset for OFDM in this function, so reset behavior depends on hardware side effects or external code. `odm_SearchPwdBLowerBound` uses blocking delays and a loop that can affect watchdog latency. Several threshold constants are magic values tied to Realtek calibration. LPS DIG uses `RSSI_Min` and can underflow before clamping if state is bad.

## Test Signals

Signals include register-trace tests for DIG writes, false-alarm counter decoding tests, linked/unlinked first-connect/first-disconnect behavior, adaptivity threshold tests for BW20/BW40 and RSSI hysteresis, excessive false-alarm forbidden-IGI recovery, LPS DIG bounds, CCK PD threshold selection, and tests with disabled support flags or scan-in-progress.
