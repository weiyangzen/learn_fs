# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mcu_mpc8349emitx.c

## Purpose
`mcu_mpc8349emitx.c` is an I2C driver for the MCU on MPC8349E-mITX-compatible boards, providing power-management, shutdown, GPIO expander, and status sysfs functions.

## Important APIs, Types, and Functions
The driver binds to I2C ID `"mcu-mpc8349emitx"` and OF compatible `"fsl,mcu-mpc8349emitx"`. Probe allocates an MCU state object, initializes GPIO-chip support, exposes a `status` device attribute, starts a shutdown-monitor thread, and may install `pm_power_off`. Remove stops the thread, removes sysfs, clears global power-off state if owned, unregisters GPIOs, and frees memory.

## Control Flow, State, and Persistence
Persistent state includes the per-client `struct mcu`, global `glob_mcu`, global `shutdown_thread`, and `pm_power_off` hook. MCU register state lives on the external I2C device.

## Dependencies and Integration Points
It integrates I2C core, optional gpiolib-style expander support, sysfs, kernel thread/freezer behavior, and board power-off handling.

## Risks and Test Signals
Risks include global singleton behavior, shutdown thread lifetime, I2C errors during poweroff/status reads, and GPIO numbering/semantics. Test signals are driver bind/unbind, sysfs status reads, GPIO line operation, clean remove, shutdown/poweroff action, and thread stop under module unload.
