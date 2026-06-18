# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_reg.h

## Purpose

`odm_reg.h` defines a secondary set of ODM MAC/BB/RF register addresses and one bitmap used by legacy or shared ODM code. The source was read as a complete 91-line file.

## Important APIs, Types, and Functions

Macros include `ODM_BB_RESET`, `RF_T_METER_OLD`, `RF_T_METER_NEW`, EDCA registers, TX pause, BB page 8/A/C/D/E addresses, RF gain/channel registers, PSD/path-diversity registers, and `BIT_FA_RESET`.

## Control Flow

There is no executable flow.

## State and Persistence Behavior

The macros name hardware state; actual persistence is in device registers.

## Dependencies and Integration Points

It is included by `odm_precomp.h` and used by ODM/RF calibration code that references legacy macro names rather than the `ODM_REG(..._11N)` indirection.

## Risks and Edge Cases

Duplication with `odm_RegDefine11N.h` can drift. Some registers refer to features only partially present in this driver, such as path diversity and PSD.

## Test Signals

Compile coverage and hardware register trace comparisons for callers using these legacy names are useful.
