# sources/distributed-fs/ceph-client/drivers/memory/emif.h

## Purpose
`emif.h` is the private register, bitfield, timing, and SRAM-PM contract header for the TI EMIF driver and related low-level assembly/SRAM code.

## Important APIs, Types, And Functions
The header defines EMIF driver limits such as `EMIF_MAX_NUM_FREQUENCIES`, voltage and timing derating constants, low-power timeout defaults, ZQ calibration constants, temperature polling defaults, PHY magic values, and register offsets for the EMIF MMIO block. It also defines masks and shifts for SDRAM configuration, refresh, timing, power management, LPDDR2 mode register access, interrupts, ZQ, temperature alert, OCP error logs, leveling, and PHY control registers.

The central data type is `struct emif_regs`, which caches frequency-specific shadow register values used for initialization, derating, and DVFS/PM. The header also declares SRAM-related objects and functions: `ti_emif_sram`, `ti_emif_sram_sz`, `ti_emif_pm_sram_data`, `ti_emif_regs_amx3`, and PM routines such as `ti_emif_save_context()`, `ti_emif_restore_context()`, `ti_emif_enter_sr()`, and `ti_emif_exit_sr()`.

## Control Flow
The header has no runtime control flow by itself. Its definitions drive `emif.c` register writes and low-level suspend/resume assembly generated through `emif-asm-offsets.c`.

## State And Persistence
`struct emif_regs` models cached shadow state for several frequencies and temperature derating variants. External SRAM symbols represent persistent low-power code/data areas that survive or operate during EMIF self-refresh transitions.

## Dependencies And Integration Points
The header is consumed by the EMIF platform driver, TI SRAM PM code, and assembly offset generation. It is tightly coupled to `linux/ti-emif-sram.h`, platform data structures, JEDEC timing types, and hardware-specific EMIF 4D/4D5 register layouts.

## Risks
Bitfield constants must exactly match hardware documentation; mistakes can corrupt SDRAM timings or power-management behavior. Magic PHY values are opaque and board/SoC sensitive. The header exposes low-level PM symbols, so structure layout changes require offset-regeneration and suspend/resume validation.

## Test Signals
Compile coverage with EMIF, SRAM PM, and assembly-offset generation enabled is the first signal. Runtime validation includes SDRAM stability during frequency changes, self-refresh entry/exit, context save/restore, and temperature derating.
