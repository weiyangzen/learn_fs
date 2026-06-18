# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-hisi.h

## Purpose
Defines HiSilicon UFS sysctrl offsets, bit masks, UFS host register constants, capability flags, private state, and helper macros for sysctrl MMIO access.

## Important APIs and types
`struct ufs_hisi_host` stores the UFSHCD pointer, sysctrl base, reset control, caps, and suspend flag. Macros `ufs_sys_ctrl_writel()`, `ufs_sys_ctrl_readl()`, `ufs_sys_ctrl_set_bits()`, and `ufs_sys_ctrl_clr_bits()` implement register access. Constants cover PSW power, PHY isolation, clock gating bypass, reset, reference clock, device reset, MPHY TX FSM, AHIT mask, and `UFS_HISI_CAP_PHY10nm`.

## Control flow and state
No executable flow beyond inline-like macros. The header defines persistent state consumed by `ufs-hisi.c`, especially capability and suspend bookkeeping.

## Dependencies and integration points
Requires Linux MMIO helpers and UFSHCD/reset types via includers. It is coupled to the sysctrl resource mapped by the C file and to Hi3660/Hi3670 hardware register layout.

## Risks and test signals
Risks are wrong bit masks or register offsets causing unsafe power/reset sequencing. Because bit helpers read-modify-write without locks, callers must ensure appropriate serialization. Test signals are correct sysctrl values during init/suspend/resume and compile coverage of all macro users.
