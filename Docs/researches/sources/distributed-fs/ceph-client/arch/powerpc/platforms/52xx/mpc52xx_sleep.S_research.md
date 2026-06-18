# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc52xx_sleep.S

## Purpose
`mpc52xx_sleep.S` contains the low-level generic MPC52xx deep-sleep code copied into SRAM and the cached wake interrupt handler.

## Important APIs, Types, and Functions
`mpc52xx_deep_sleep(sram, sdram, cdm, intr)` enables interrupts, emulates a timer interrupt to prime the cached handler, locks icache, branches to SRAM code, and returns after wake. `mpc52xx_ds_sram` puts SDRAM into self-refresh, disables the SDRAM clock, sets `MSR_POW`, then restores clocks and SDRAM. `mpc52xx_ds_cached` is the wake handler that disables emulated interrupt, acknowledges wakeup, sets a flag, and returns from interrupt. Size symbols expose copy lengths.

## Control Flow, State, and Persistence
The C PM code copies SRAM and cached sections into special execution locations. The assembly uses registers as a wake flag protocol and directly touches IMMR offsets.

## Dependencies and Integration Points
It depends on `mpc52xx_pm.c`, MPC5200 SDRAM/CDM/PIC register layout, PowerPC cache/HID0/MSR behavior, and `CONFIG_KERNEL_START`.

## Risks and Test Signals
Risks include executing from wrong memory, stale instruction cache, wake handler size exceeding saved buffer, SDRAM self-refresh sequencing, and assumptions about timer interrupt emulation. Test signals are successful wake from standby, no data corruption, restored code at low vector area, and no interrupt-controller deadlock.
