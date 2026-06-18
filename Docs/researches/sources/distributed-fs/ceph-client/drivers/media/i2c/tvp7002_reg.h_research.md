# sources/distributed-fs/ceph-client/drivers/media/i2c/tvp7002_reg.h

## Purpose

This header defines symbolic register addresses for the TI TVP7002 digitizer. It is used by `tvp7002.c` to build default and per-timing register scripts and to read timing-detection status.

## Important APIs, Types, And Functions

The file has no functions or types. It maps register names from `TVP7002_CHIP_REV` through `TVP7002_YUV_V_R_COEF_MSBS`. Covered groups include HPLL feedback/control/phase, clamp timing, sync thresholds, input mux, RGB gain/offset, output formatter, power/ADC setup, auto level control, status registers for line and clock counts, sync widths, AVID/VBLK/FBIT timing, and YUV coefficient registers.

## Control Flow

There is no executable flow. The C driver uses these constants in fixed initialization arrays, timing-specific parameter arrays, status reads, polarity programming, stream toggling, gain control, and advanced debug access.

## State And Persistence

The header holds no state. Hardware persistence is embodied in the TVP7002's registers, while selected timing and streaming state live in `struct tvp7002`.

## Dependencies And Integration Points

The header is private to the TVP7002 driver and follows naming conventions documented in comments. It relies on no custom includes beyond what the including C file provides.

## Risks

Incorrect address definitions would affect many scripts at once. Reserved gaps are intentionally omitted or referenced numerically in `tvp7002.c`; adding symbolic names should be coordinated with the register script type tags so reserved registers are not accidentally written.

## Test Signals

Correctness is observed indirectly through successful default initialization, stable DV timing detection from line/clock status registers, proper gain writes, stream toggling via miscellaneous control, and optional advanced debug register access.
