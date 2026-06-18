# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-mediatek-sip.h

## Purpose
Defines the MediaTek secure monitor interface used by the UFS driver for power, reset, crypto, reference clock, SRAM, MPHY, MTCMOS, and VCC selection operations.

## Important APIs, types, and functions
`MTK_SIP_UFS_CONTROL` is the SMC function ID. Command bits include `UFS_MTK_SIP_VA09_PWR_CTRL`, `UFS_MTK_SIP_DEVICE_RESET`, `UFS_MTK_SIP_CRYPTO_CTRL`, `UFS_MTK_SIP_REF_CLK_NOTIFICATION`, `UFS_MTK_SIP_SRAM_PWR_CTRL`, `UFS_MTK_SIP_GET_VCC_NUM`, `UFS_MTK_SIP_DEVICE_PWR_CTRL`, `UFS_MTK_SIP_MPHY_CTRL`, and `UFS_MTK_SIP_MTCMOS_CTRL`. `struct ufs_mtk_smc_arg` packages SMC arguments. `_ufs_mtk_smc()` calls `arm_smccc_smc()`. Convenience macros expose each operation.

## Control flow and state
The header has inline SMC dispatch only; persistent state lives in firmware or caller-provided `arm_smccc_res`. Command wrappers are synchronous firmware calls.

## Dependencies and integration points
Depends on `linux/soc/mediatek/mtk_sip_svc.h` and ARM SMCCC definitions through includers. Used by `ufs-mediatek.c` to coordinate hardware that Linux cannot directly control.

## Risks and test signals
Risks include firmware ABI mismatch, typoed comments indicating vendor-specific command semantics, and macros that require callers to pass a real `arm_smccc_res` lvalue. Test signals are nonzero `res.a0` handling in callers, successful reset/refclk/crypto operations, and boot tests across firmware revisions.
