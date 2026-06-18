# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/sis_accel.h

## Purpose

`sis_accel.h` defines the MMIO register map, command flags, synchronization macros, command queue accounting, and public prototypes for the SiS fbdev 2D acceleration engine. It is paired with `sis_accel.c` and abstracts the differences between the older 300 engine register layout and the 315/310 layout.

## Important APIs, Types, And Functions

- Optional critical-section macros: `CRITBEGIN`, `CRITEND`, and `CRITFLAGS`, controlled by `SISFB_USE_SPINLOCKS`.
- Command constants for blit, color expansion, lines, trapezoid fill, transparent blit, alpha/3D/Z/gradient commands, source selectors, pattern flags, 300-series direction flags, clipping, transparency, and color expansion subfunctions.
- 315 register addresses such as `SRC_ADDR`, `SRC_PITCH`, `DST_ADDR`, `DST_PITCH`, `RECT_WIDTH`, `RECT_HEIGHT`, `PAT_FGCOLOR`, `COMMAND_READY`, and `FIRE_TRIGGER`.
- 300 register helper address macros `BR(x)` and `PBR(x)`.
- Idle macros `SiS300Idle` and `SiS310Idle`.
- Setup/fire macros for source/destination base, pitch, coordinates, rectangle size, colors, transparency keys, mono patterns, clipping, ROP, command flags, and command dispatch for both 300 and 310 engines.
- Function prototypes for `sisfb_initaccel`, `sisfb_syncaccel`, `fbcon_sis_sync`, `fbcon_sis_fillrect`, and `fbcon_sis_copyarea`.

## Control Flow

The macros implement inline command sequencing. Each setup macro checks `CmdQueLen`, calls the relevant idle macro when the queue is exhausted, writes one or more MMIO registers, and decrements `CmdQueLen`. `SiS300DoCMD` writes the command and trigger through the 300 register block; `SiS310DoCMD` writes `COMMAND_READY` and `FIRE_TRIGGER`. Idle macros poll status registers multiple times before resetting queue accounting.

## State And Persistence

The macros mutate `ivideo->cmdqueuelength` through `CmdQueLen`, update `ivideo->CommandReg`, and write MMIO registers under `ivideo->mmio_vbase`. Hardware command queue state persists in the graphics engine until commands complete. Optional spinlocks protect register sequences only if the header-level feature flag is enabled.

## Dependencies And Integration Points

- Requires `struct sis_video_info` and MMIO macros from `sis.h`.
- Used directly by `sis_accel.c`.
- Uses `Q_STATUS` from `sis.h` for 315 idle polling.
- Exposes fbdev acceleration hooks consumed by `sis.h` and registered by `sis_main.c`.

## Risks

- Macros evaluate arguments directly and have statement-like side effects, so callers must avoid expressions with side effects.
- Busy-wait loops have no timeout and can wedge the caller if MMIO status is invalid or hardware is hung.
- Queue length accounting is manual and must match the number of MMIO writes per macro.
- Without spinlocks, interleaved callers could corrupt command sequences if higher-level fbdev locking is insufficient.

## Test Signals

- Compile with and without `SISFB_USE_SPINLOCKS` to validate macro declarations.
- Run accelerated fills/copies while instrumenting MMIO writes to ensure queue decrement and idle refresh behavior matches expected command counts.
- Force small command queue lengths to exercise idle paths.
- Compare 300 and 315 register sequences for equivalent fill/copy operations.
