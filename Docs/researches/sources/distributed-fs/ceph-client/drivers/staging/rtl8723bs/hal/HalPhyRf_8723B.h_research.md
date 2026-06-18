# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalPhyRf_8723B.h

## Purpose

`HalPhyRf_8723B.h` declares RTL8723B-specific RF calibration and Tx power tracking APIs and calibration constants. The file was read as a complete 68-line header.

## Important APIs, Types, and Functions

Constants include `IQK_DELAY_TIME_8723B`, `IQK_DEFERRED_TIME_8723B`, `index_mapping_NUM_8723B`, `AVG_THERMAL_NUM_8723B`, and `RF_T_METER_8723B`. It declares `ConfigureTxpowerTrack_8723B`, `ODM_TxPwrTrackSetPwr_8723B`, `PHY_IQCalibrate_8723B`, `ODM_SetIQCbyRFpath`, `PHY_LCCalibrate_8723B`, `PHY_DigitalPredistortion_8723B`, and several underscored calibration helper prototypes.

## Control Flow

No executable flow is present. The declarations are consumed by the generic RF tracking file and the wider PHY/HAL code to trigger 8723B-specific tracking and calibration flows.

## State and Persistence Behavior

The header owns no state. Declared functions mutate ODM RF calibration state and hardware registers in the implementation.

## Dependencies and Integration Points

It depends on `struct txpwrtrack_cfg`, `struct dm_odm_t`, and `struct adapter` from surrounding headers. It integrates `HalPhyRf.c` with the 8723B implementation and exposes calibration hooks to other HAL code.

## Risks and Edge Cases

Several underscored helper prototypes do not match the static helper names/visibility in the implementation (`_8723B` suffix differences and static definitions), indicating stale declarations or unused legacy API surface. `PHY_DigitalPredistortion_8723B` is declared here but not implemented in the researched C file, so link coverage depends on other build exclusions or dead declarations.

## Test Signals

Compile/link coverage, symbol reachability checks for declared calibration helpers, and direct tests for public calibration functions are useful.
