# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm_precomp.h

## Purpose

`odm_precomp.h` is the consolidated include header for RTL8723BS ODM implementation files. It pulls in ODM types, common ODM state, submodules, PHY/RF calibration headers, chip HAL headers, register definitions, generated hardware images, and register configuration prototypes. The source was read as a complete 47-line file.

## Important APIs, Types, and Functions

It defines `BEAMFORMING_SUPPORT 0` and includes `odm_types.h`, `odm.h`, `odm_HWConfig.h`, `odm_RegDefine11N.h`, `odm_EdcaTurboCheck.h`, `odm_DIG.h`, `odm_DynamicBBPowerSaving.h`, `odm_DynamicTxPower.h`, `odm_CfoTracking.h`, `HalPhyRf.h`, `HalPhyRf_8723B.h`, `rtl8723b_hal.h`, `odm_interface.h`, `odm_reg.h`, generated `HalHWImg8723B_*` headers, `Hal8723BReg.h`, and `odm_RegConfig8723B.h`.

## Control Flow

There is no runtime flow.

## State and Persistence Behavior

The header owns no storage but controls the declaration environment for most ODM `.c` files.

## Dependencies and Integration Points

It is included by ODM implementation files and centralizes dependencies on generated hardware image tables and RF calibration code.

## Risks and Edge Cases

Large include aggregation can hide dependency cycles and makes compile order sensitive. `TEST_FALG___` appears to be a misspelled legacy define. Beamforming is hard-disabled.

## Test Signals

Full driver compile coverage and include-order checks are the main signals.
