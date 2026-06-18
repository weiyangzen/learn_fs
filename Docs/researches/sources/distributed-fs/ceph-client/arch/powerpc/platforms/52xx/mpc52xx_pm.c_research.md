# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc52xx_pm.c

## Purpose
`mpc52xx_pm.c` implements generic MPC52xx standby/deep-sleep suspend and board callback hooks for wakeup and resume finishing.

## Important APIs, Types, and Functions
`mpc52xx_pm_init()` installs `mpc52xx_pm_ops`. `mpc52xx_pm_prepare()` maps IMMR, derives SDRAM/CDM/PIC/GPIO/SRAM pointers, and calls board `board_suspend_prepare`. `mpc52xx_set_wakeup_gpio()` configures a wakeup GPIO input and interrupt level. `mpc52xx_pm_enter()` saves SRAM and a temporary low-memory IRQ handler, copies `mpc52xx_ds_sram` into SRAM, configures sleep clocks, enters `mpc52xx_deep_sleep()`, then restores state. `mpc52xx_pm_finish()` calls board resume callback and unmaps IMMR.

## Control Flow, State, and Persistence
Global pointers and `saved_sram` hold suspend state. Board callbacks are stored in exported `mpc52xx_suspend`. The code temporarily overwrites code at `CONFIG_KERNEL_START + 0x500` with the cached wake handler and restores it after wake.

## Dependencies and Integration Points
It depends on `mpc52xx_sleep.S`, board files assigning wake callbacks, PowerPC timebase/HID0/MSR control, and fixed MPC5200 IMMR offsets.

## Risks and Test Signals
Risks include invasive low-memory handler replacement, SRAM size assumptions, missing board wake callback, cache/icache coherency, and interrupt masking restoration. Test signals are standby suspend/resume, wake GPIO behavior, restored SRAM contents, stable interrupts after resume, and repeated cycles on Lite5200/Efika.
