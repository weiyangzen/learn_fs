# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/lite5200_pm.c

## Purpose
`lite5200_pm.c` implements Lite5200 platform suspend operations. It delegates standby to generic MPC52xx deep sleep and implements suspend-to-RAM with Lite5200-specific register save/restore and assembly low-power entry.

## Important APIs, Types, and Functions
`lite5200_pm_init()` installs `lite5200_pm_ops`. `lite5200_pm_begin()` records target state. `lite5200_pm_prepare()` maps IMMR and derives CDM, PIC, GPIO, PCI, SDMA, XLB, SRAM, and MBAR pointers for `PM_SUSPEND_MEM`. `lite5200_save_regs()` and `lite5200_restore_regs()` preserve hardware blocks not bound to normal devices. `lite5200_pm_enter()` saves state, enables FP state preservation, calls `lite5200_low_power()`, restores state, and unmaps registers.

## Control Flow, State, and Persistence
Global mapped pointers, saved register structs, `spci`, and `lite5200_pm_target_state` hold suspend state across low-power entry. SRAM contents are saved in `saved_sram` from generic PM code.

## Dependencies and Integration Points
It depends on `lite5200_sleep.S`, common MPC52xx PM helpers, IMMR layout, BestComm/SDMA registers, and PowerPC FP context handling.

## Risks and Test Signals
Risks include incomplete register save/restore, fixed IMMR offsets, ioremap failures, no cleanup on some prepare failures, and subtle FP/SRAM interactions. Test signals are repeated standby and mem suspend cycles, PCI/BestComm/GPIO functionality after resume, wake event behavior, and no SRAM corruption.
