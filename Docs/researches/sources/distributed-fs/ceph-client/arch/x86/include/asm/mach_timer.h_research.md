# sources/distributed-fs/ceph-client/arch/x86/include/asm/mach_timer.h

## Purpose
Provides legacy machine-specific TSC calibration helpers using the PIT channel 2 gate and counter.

## Important APIs, Types, And Functions
Defines `CALIBRATE_TIME_MSEC`, `CALIBRATE_LATCH`, `mach_prepare_counter()`, and `mach_countup()`. The helpers program PIT channel 2 through ports `0x43`, `0x42`, and gate/speaker port `0x61`.

## Control Flow
`mach_prepare_counter()` raises the gate, disables the speaker, programs PIT channel 2 for mode 0, and loads the calibration latch. `mach_countup()` busy-loops until port `0x61` indicates terminal count, returning the loop count through an output pointer.

## State And Persistence
State is transient hardware timer programming and port state during calibration. It does not persist beyond boot-time calibration except for the resulting TSC calibration computed elsewhere.

## Dependencies And Integration Points
Depends on PIT constants and port I/O helpers. It integrates with legacy x86 TSC calibration paths and early timer setup.

## Risks And Edge Cases
Port I/O timing is hardware-sensitive. Virtualized or unusual systems may emulate the PIT poorly. Busy-loop count depends on compiler and CPU behavior, so calibration users must bound error.

## Test Signals
Boot logs reporting sane TSC frequency on 32-bit/legacy paths, PIT-emulated virtual machines, and old hardware are the primary signal.
