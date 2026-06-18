# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-mediatek.h

## Purpose
Defines MediaTek UFS vendor register offsets, MCQ constants, refclock controls, UniPro vendor attributes, capability flags, private clock/crypto/MCQ state structures, runtime constants, and IP version identifiers.

## Important APIs and types
Important constants include `REG_UFS_REFCLK_CTRL`, `REG_UFS_MMIO_OPT_CTRL_0`, `REG_UFS_MTK_IP_VER`, debug/probe registers, MCQ SQ/CQ offsets, `REFCLK_REQUEST`, `REFCLK_ACK`, and `REFCLK_REQ_TIMEOUT_US`. Capability flags include boost crypto, VA09 power control, AH8 disable, broken VCC, VCCQx LPM allowance, FASTAUTO power-mode change, TX skew fix, MCQ disable, RTFF MTCMOS, and broken RTC. Types include `struct ufs_mtk_crypt_cfg`, `struct ufs_mtk_clk`, `struct ufs_mtk_hw_ver`, `struct ufs_mtk_mcq_intr_info`, and `struct ufs_mtk_host`.

## Control flow and state
No executable flow. The header defines all state tracked by the MediaTek C driver: PHY/regulator/reset handles, clock scaling state, hardware version, capability bits, refclk delays, IP version, MCQ IRQs, and optional PHY device PM handle.

## Dependencies and integration points
Included by `ufs-mediatek.c` and coupled to MediaTek UFSHCI register layout, UFSHCD MCQ support, Linux PHY/regulator/reset/clock types, and firmware operations declared in `ufs-mediatek-sip.h`.

## Risks and test signals
Risks are stale IP version comparisons, bit definitions that gate critical power behavior, and fixed `UFSHCD_MAX_Q_NR` assumptions. Test signals are compile coverage with MCQ and clock scaling enabled, register dumps matching documented offsets, and runtime behavior differences across legacy and newer IP versions.
