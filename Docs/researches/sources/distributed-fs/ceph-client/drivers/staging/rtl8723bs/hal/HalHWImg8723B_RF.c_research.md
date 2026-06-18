# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalHWImg8723B_RF.c

## Purpose

`HalHWImg8723B_RF.c` embeds generated RTL8723B RF initialization data, SDIO thermal power-tracking delta swing tables, and TX power limit regulatory tables. The file was read as a complete 555-line source.

## Important APIs, Types, and Functions

Public functions are `ODM_ReadAndConfig_MP_8723B_RadioA`, `ODM_ReadAndConfig_MP_8723B_TxPowerTrack_SDIO`, `ODM_GetVersion_MP_8723B_TxPowerTrack_SDIO`, `ODM_ReadAndConfig_MP_8723B_TXPWR_LMT`, and `ODM_GetVersion_MP_8723B_TXPWR_LMT`. Static data includes `Array_MP_8723B_RadioA`, eight `gDeltaSwingTableIdx_MP_*_TxPowerTrack_SDIO_8723B` arrays, and string tuple table `Array_MP_8723B_TXPWR_LMT`. `CheckPositive` matches generated RF conditions.

## Control Flow

`ODM_ReadAndConfig_MP_8723B_RadioA` uses the generated pair interpreter to call `odm_ConfigRF_RadioA_8723B` for direct or conditionally selected entries. `ODM_ReadAndConfig_MP_8723B_TxPowerTrack_SDIO` copies embedded positive/negative delta swing tables for 2.4 GHz CCK/OFDM, path A/B, into `pDM_Odm->RFCalibrateInfo`. `ODM_ReadAndConfig_MP_8723B_TXPWR_LMT` iterates six-string tuples `(regulation, bandwidth, rate, rfPath, channel, value)` and passes them to `odm_ConfigBB_TXPWR_LMT_8723B`.

## State and Persistence Behavior

Static arrays are immutable. RadioA loading persists in RF registers. TxPowerTrack loading persists in `RFCalibrateInfo` arrays used later by `GetDeltaSwingTable_8723B` and thermal power tracking. TX power limits persist in ODM regulatory power-limit data structures populated by the config callback.

## Dependencies and Integration Points

It includes `<linux/kernel.h>` and `odm_precomp.h`; uses ODM RF/BB config callbacks, `DELTA_SWINGIDX_SIZE`, generated branch macros, and `memcpy`. It feeds `HalPhyRf.c`/`HalPhyRf_8723B.c` thermal tracking and the transmit power configuration path.

## Risks and Edge Cases

Regulatory string tables are compliance-sensitive. A tuple ordering or width mistake can misconfigure channel limits. Delta swing table sizes must match destination arrays. Conditional RF register programming is board-specific and hard to validate without hardware. Fallback behavior in calibration uses 8188E tables if channel is outside 2.4 GHz, so missing load can change thermal response.

## Test Signals

Compile coverage, RF register traces against vendor images, checksum or count checks for delta swing copies, regulatory power-limit table validation by channel/rate/bandwidth/regulation, and thermal tracking tests that confirm copied tables are selected at runtime are useful.
