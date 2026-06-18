# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-mediatek.c

## Purpose
Implements MediaTek UFSHCI platform support. It manages MediaTek-specific reset, PHY power, secure firmware calls, reference clock handshake, UniPro low-power mode, device quirks, regulators, clock scaling, MCQ interrupts, debug dumping, PM, and platform probe integration.

## Important APIs, types, and functions
Private state is `struct ufs_mtk_host` from the header. Initialization flows through `ufs_mtk_init()`, which parses DT capability booleans, initializes MCQ IRQ metadata, binds optional MPHY, gets reset controls, backs up MPHY state, enables UFSHCD capabilities, initializes private clocks, powers MPHY, handles RTFF MTCMOS, turns clocks on, and records IP version. Variant ops include HCE/link/power-change notifications, suspend/resume, event notification, devfreq scaling, MCQ resource setup, ESI config, and SCSI device config. Key helpers include `ufs_mtk_setup_ref_clk()`, `ufs_mtk_wait_idle_state()`, `ufs_mtk_wait_link_state()`, `ufs_mtk_mphy_power_on()`, `ufs_mtk_pre_pwr_change()`, `ufs_mtk_auto_hibern8_disable()`, `ufs_mtk_link_set_hpm()`, `ufs_mtk_link_set_lpm()`, `_ufs_mtk_clk_scale()`, and MCQ IRQ handlers.

## Control flow and state
Probe first creates device links to reset/PHY providers when present, then calls `ufshcd_pltfrm_init()` with MediaTek vops and forces device regulator LPM off. HCE pre-change resets host unless UniPro LPM is active, enables crypto, disables AH8 if configured, and applies IP-version-specific MMIO settings. Link pre-change disables UniPro LPM, disables LCC and deep stall, and sets selected debug OMC bits; post-link enables UniPro clock gating. Power-change pre-stage temporarily disables AH8, may use FASTAUTO transition, configures adaptation, and post-stage restores AHIT. Suspend/resume sequences UniPro LPM/HPM, MPHY power, SRAM power, regulator LPM, MTCMOS, and clock scaling.

## Dependencies and integration points
Depends on UFSHCD platform/core, MediaTek SIP firmware ABI, reset framework, regulators, clock framework, PHY framework, OF device links, Linux tracepoints, MCQ core APIs, block multiqueue CPU mappings, and UFS device quirk infrastructure.

## Risks and test signals
Risks include firmware ABI failures, refclk ack timeout, AH8/link-state races, static AHIT backup during power change, optional reset pointers used in reset sequence, MCQ IRQ topology assumptions, regulator LPM policy for broken VCC devices, and resume returning success after recovery to avoid I/O hangs. Test signals include successful boot on MT8183/MT8195 compatibles, refclk ack transitions, UIC error tracepoints, MCQ queue interrupts and affinity, clock scaling parent changes plus vcore requests, suspend/resume under runtime and system PM, and device-specific quirk application for Samsung, Micron, SK hynix, Toshiba, and UFS 5.0 devices.
