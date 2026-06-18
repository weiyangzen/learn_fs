# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/jornada720.h

## Purpose
This SA-1100 machine header collects board or SoC constants for `jornada720` users: GPIO assignments, IRQ lines, register offsets, memory windows, and helper declarations consumed by legacy board files and companion drivers.

## Important APIs, Types, and Functions
- Register/constant macro families: `BRIGHTNESSOFF`(1), `CONTRASTOFF`(1), `ERRORCODE`(1), `GETBATTERYDATA`(1), `GETBRIGHTNESS`(1), `GETCONTRAST`(1), `GETSCANKEYCODE`(1), `GETTOUCHSAMPLES`(1); examples: `GETBATTERYDATA`, `GETSCANKEYCODE`, `GETTOUCHSAMPLES`, `GETCONTRAST`, `SETCONTRAST`, `GETBRIGHTNESS`, `SETBRIGHTNESS`, `CONTRASTOFF`, `BRIGHTNESSOFF`, `PWMOFF`, `TXDUMMY`, `ERRORCODE`.

## Control Flow
There is no runtime control flow in this header. Including C files expand its macros into direct memory-mapped register accesses, IRQ-number calculations, board tests, and timing constants at compile time.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Dependencies are limited to compile-time inclusion by adjacent platform code.

## Risks
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.

## Research Notes
- Read coverage: full file (810 bytes, 29 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.
