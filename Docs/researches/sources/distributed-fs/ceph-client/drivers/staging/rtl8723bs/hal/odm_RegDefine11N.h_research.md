# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_RegDefine11N.h

## Purpose

`odm_RegDefine11N.h` defines ODM register addresses and bit masks for 802.11n-generation Realtek PHY/RF/MAC blocks used by RTL8723BS dynamic-management code. The source was read as a complete 162-line file.

## Important APIs, Types, and Functions

The header defines RF registers (`ODM_REG_RF_MODE_11N`, `ODM_REG_CHNBW_11N`, thermal meter registers), BB page 8/A/B/C/D/E registers for DIG, false alarms, CCK CCA, ATC, IQK, TXAGC, and MAC registers for EDCA, TX pause, RSSI monitor, and antenna training. It also defines bit masks such as `ODM_BIT_IGI_11N`, `ODM_BIT_CCK_RPT_FORMAT_11N`, `ODM_BIT_BB_RX_PATH_11N`, and `ODM_BIT_BB_ATC_11N`.

## Control Flow

There is no executable flow; macros are resolved through `ODM_REG()` and `ODM_BIT()` in ODM implementation files.

## State and Persistence Behavior

The macros name hardware state locations. State is held in hardware registers when read/written by ODM code.

## Dependencies and Integration Points

It is included by `odm_precomp.h` and used by DIG, CFO tracking, NHM/adaptivity, PHY parsing, EDCA, and register configuration paths.

## Risks and Edge Cases

Address or bit-mask mistakes cause silent hardware misconfiguration. `ODM_REG_PSD_DATA_11N` is defined twice with the same value. The header is specific to 11n register naming and must match `odm_interface.h` macro expansion.

## Test Signals

Register trace comparison, compile coverage for every `ODM_REG/ODM_BIT` use, and hardware smoke tests for DIG/FA/CFO/EDCA behavior are the main signals.
