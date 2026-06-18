# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/sis_accel.c

## Purpose

`sis_accel.c` implements the fbdev 2D acceleration hooks for SiS 300 and 315/310-series engines. It accelerates solid rectangle fills, screen-to-screen copies, and synchronization by translating fbdev operations into SiS MMIO command sequences defined in `sis_accel.h`, while falling back to generic `cfb_*` helpers when acceleration is unavailable.

## Important APIs, Types, And Functions

- ROP lookup tables: `sisALUConv` for source/destination ROPs, `sisPatALUConv` for pattern-as-source ROPs, and `myrops` to map fbdev fill ROPs.
- 300-series internal routines under `CONFIG_FB_SIS_300`: `SiS300Sync`, `SiS300SetupForScreenToScreenCopy`, `SiS300SubsequentScreenToScreenCopy`, `SiS300SetupForSolidFill`, and `SiS300SubsequentSolidFillRect`.
- 315-series routines under `CONFIG_FB_SIS_315`: `SiS310Sync`, `SiS310SetupForScreenToScreenCopy`, `SiS310SubsequentScreenToScreenCopy`, `SiS310SetupForSolidFill`, and `SiS310SubsequentSolidFillRect`.
- Exported/internal entry points: `sisfb_initaccel`, `sisfb_syncaccel`, `fbcon_sis_sync`, `fbcon_sis_fillrect`, and `fbcon_sis_copyarea`.

## Control Flow

`fbcon_sis_fillrect` and `fbcon_sis_copyarea` first reject inactive fbdev state, disabled acceleration, bad engine state, zero-size operations, and out-of-bounds rectangles. They clip dimensions to virtual resolution, derive color or copy direction, choose the 300 or 315 path from `ivideo->sisvga_engine`, program setup registers, trigger the command, and finally call `sisfb_syncaccel`. The 300 copy path computes explicit X/Y direction flags. The 315 copy path relies on hardware direction detection but adjusts source and destination base addresses together when overlapping areas exceed the 2048-line coordinate range.

## State And Persistence

The functions mutate `struct sis_video_info` acceleration fields such as `CommandReg` and `cmdqueuelength`, read geometry and color state from `fb_info`, and write persistent hardware command/register state through MMIO. They do not allocate memory. `sisfb_initaccel` initializes the optional acceleration spinlock only when `SISFB_USE_SPINLOCKS` is enabled.

## Dependencies And Integration Points

- Includes Linux module/kernel/fb/io headers plus `sis.h` and `sis_accel.h`.
- Registered through `sis_main.c` fb ops as `fb_fillrect`, `fb_copyarea`, and sync callback.
- Falls back to `cfb_fillrect` and `cfb_copyarea` when acceleration is disabled or engine status is bad.
- Depends on `ivideo->DstColor`, `video_linelength`, `video_offset`, `SiS310_AccelDepth`, `mmio_vbase`, `cmdqueuelength`, and `engineok` set up elsewhere.

## Risks

- Busy-wait sync macros can hang if hardware never reports idle.
- Coordinate/base adjustments for large virtual screens are hardware-specific and easy to regress, especially around overlapping blits.
- Spinlock protection is compiled out by default; concurrent framebuffer operations rely on higher-level serialization or hardware tolerance.
- ROP indexes assume caller-provided fbdev ROP values stay in range.

## Test Signals

- Compare accelerated and `cfb_*` fallback output for fills and overlapping copies at 8, 16, and 32 bpp.
- Test virtual y resolutions above 2048 to cover base-address compensation.
- Exercise both 300 and 315 paths with acceleration enabled/disabled and engineok true/false.
- Use stress tests for console scrolling and rectangle fills while checking for hangs in `sisfb_syncaccel`.
