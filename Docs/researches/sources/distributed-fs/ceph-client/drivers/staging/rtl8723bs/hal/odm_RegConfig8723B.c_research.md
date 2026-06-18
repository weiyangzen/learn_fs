# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_RegConfig8723B.c

## Purpose

`odm_RegConfig8723B.c` applies generated RTL8723B MAC, BB, RF, PHY register-page, and TX power-limit table entries. It is the low-level bridge between Realtek header tables and hardware register writes or HAL power-table storage. The source was read as a complete 177-line file.

## Important APIs, Types, and Functions

Public functions are `odm_ConfigRFReg_8723B`, `odm_ConfigRF_RadioA_8723B`, `odm_ConfigMAC_8723B`, `odm_ConfigBB_AGC_8723B`, `odm_ConfigBB_PHY_REG_PG_8723B`, `odm_ConfigBB_PHY_8723B`, and `odm_ConfigBB_TXPWR_LMT_8723B`.

## Control Flow

RF config handles special delay pseudo-addresses, writes RF registers, delays between writes, and retries problematic RF registers `0xb6` and `0xb2` with readback verification; the `0xb2` retry also retriggers LCK through RF register `0x18`. MAC config writes one byte. BB AGC/PHY config writes BB registers or interprets delay pseudo-addresses. PHY register-page entries are stored into TX power-by-rate tables instead of immediately written. TX power-limit entries are passed to `PHY_SetTxPowerLimit`.

## State and Persistence Behavior

Hardware register writes persist until reset or later table/application writes. PHY register-page and TX power-limit entries persist in `hal_com_data` arrays and are consumed when setting channel/rate power.

## Dependencies and Integration Points

It depends on `PHY_SetRFReg`, `PHY_QueryRFReg`, `PHY_SetBBReg`, `PHY_StoreTxPowerByRate`, `PHY_SetTxPowerLimit`, delay APIs, and generated header readers from `HalHWImg8723B_*`. It is called by `odm_HWConfig.c` dispatchers.

## Risks and Edge Cases

Retry loops are bounded but silent on failure. Delay pseudo-addresses must match generated table conventions. RF path support is effectively path A for this chipset. Incorrect table values can directly program bad RF/BB hardware state or bad power limits.

## Test Signals

Register-write trace tests for normal entries, delay entries, `0xb6` retry, `0xb2` retry/LCK, PHY_REG_PG storage, and TX power-limit forwarding are useful. Hardware bring-up logs should match Realtek reference table order.
