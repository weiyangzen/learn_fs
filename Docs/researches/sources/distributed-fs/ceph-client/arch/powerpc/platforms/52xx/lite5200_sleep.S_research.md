# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/lite5200_sleep.S

## Purpose
`lite5200_sleep.S` contains the low-level Lite5200 suspend-to-RAM assembly path used by `lite5200_pm.c`.

## Important APIs, Types, and Functions
The exported entry is `lite5200_low_power(sram, mbar)`. The file saves and restores core registers, BATs, segment registers, SPRGs, debug registers, and timebase state through local helper routines. It programs SDRAM self-refresh, wakeup behavior for the helper MCU/U-Boot path, cache state, and resumes back into the C restore path.

## Control Flow, State, and Persistence
It stores CPU state in a static `registers` area and executes critical code with MMU/cache assumptions tailored to MPC5200. It temporarily relies on SRAM/MBAR mappings supplied by the C PM layer.

## Dependencies and Integration Points
It depends on MPC5200 SDRAM/CDM/GPIO register offsets, PowerPC SPR names, `CONFIG_KERNEL_START`, and the C-side saved SRAM/register buffers.

## Risks and Test Signals
Risks are high because register ordering, cache flushing, BAT restoration, and wake-vector setup must be exact. Test signals are reliable resume from `PM_SUSPEND_MEM`, restored timebase and debug registers, stable MMU mappings after resume, and no corruption of early RAM/SRAM contents.
