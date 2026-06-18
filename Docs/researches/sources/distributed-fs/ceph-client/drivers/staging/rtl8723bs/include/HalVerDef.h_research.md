# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/HalVerDef.h

Purpose: this header defines the HAL chip-version data model for RTL8723B and macros for classifying chip type, cut version, vendor, and ROM version.

Important APIs/types/macros: enums include `hal_ic_type_e` with `CHIP_8723B`, `hal_chip_type_e` (`TEST_CHIP`, `NORMAL_CHIP`, `FPGA`), `hal_cut_version_e` from A through K, and `hal_vendor_e` (`TSMC`, `UMC`, `SMIC`). `struct hal_version` stores IC type, chip type, cut, vendor, and `ROMVer`. Getter macros extract each field and predicate macros such as `IS_NORMAL_CHIP`, `IS_A_CUT`, and `IS_CHIP_VENDOR_TSMC` classify versions.

Control flow and integration: `rtl8723b_hal_init.c` fills `hal_com_data.VersionID` in `ReadChipVersion8723B` from `REG_SYS_CFG`, `REG_GPIO_OUTSTS`, and multi-function registers. Later init logic uses `IS_NORMAL_CHIP` to select ARFR values and other chip-dependent behavior.

State and persistence: the header defines only type shape. Runtime state persists in `hal_com_data.VersionID`.

Dependencies: relies on `ROM_VERSION_MASK` and `BIT` definitions from included contexts. It is included by `hal_com.h` and therefore widely available.

Risks and test signals: spelling of `GET_CVID_MANUFACTUER` is legacy and should not be “fixed” without updating call sites. Any new chip cut or vendor requires enum and predicate updates. Tests should confirm chip-version dumping and normal/test chip paths on real or mocked register values.
