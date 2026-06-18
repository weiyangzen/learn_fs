# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-hisi.c

## Purpose
Implements HiSilicon Hi3660/Hi3670 UFS platform variant support. It powers and clocks the UFS subsystem, initializes SoC sysctrl state, applies vendor UniPro/MPHY tuning, negotiates power mode, and manages suspend/resume reference clock behavior.

## Important APIs, types, and functions
`ufs_hisi_init_common()` allocates `struct ufs_hisi_host`, gets reset control, sets PM levels, and maps sysctrl resource 1. `ufs_hisi_clk_init()` and `ufs_hisi_soc_init()` sequence reference clocks, isolation, PSW power, reset, and device reset controls. `ufs_hisi_link_startup_pre_change()` writes many vendor MIBs, checks TX FSM hibern8 through `ufs_hisi_check_hibern8()`, disables AH8/LCC, and closes Mk2 extension support. `ufs_hisi_pwr_change_pre_change()` programs SaveConfigTime, sync lengths, and UniPro timeout values. Variant ops are separate for Hi3660 and Hi3670; Hi3670 sets `UFS_HISI_CAP_PHY10nm`.

## Control flow and state
Probe matches compatible data and calls `ufshcd_pltfrm_init()`. Init performs sysctrl and reset setup before link startup. Runtime state is in `struct ufs_hisi_host`, including sysctrl MMIO, reset control, capability flags, and `in_suspend`. System sleep suspend disables reference clock and records suspend state; resume restores override and ref clock.

## Dependencies and integration points
Depends on UFSHCD platform core, reset framework, OF resource layout, UniPro DME helpers, and sysctrl register macros from `ufs-hisi.h`.

## Risks and test signals
Risks are unverified DME writes, hard-coded magic MIBs, resource index dependence, and suspend behavior differing between runtime and system PM. Test signals include hibern8 FSM check passing on both lanes, link startup with AH8 disabled, Hi3670 10 nm branch behavior, correct sysctrl register transitions, and suspend/resume without reference-clock loss.
