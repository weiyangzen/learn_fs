# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-sysinfo.c

## Purpose
Owns and exposes the global Octeon system-information structure populated by boot code.

## Important APIs, Types, And Functions
The sole API is exported `cvmx_sysinfo_get()`, returning the static `struct cvmx_sysinfo sysinfo`.

## Control Flow
There is no local initialization. Callers retrieve the singleton pointer and read or populate board type, clocks, core masks, and related bootloader facts.

## State, Persistence, And Dependencies
`sysinfo` is static kernel memory and persists for the kernel lifetime. Correctness depends on earlier platform setup filling it before consumers run.

## Integration Points
Board helpers, packet helpers, JTAG, SPI, model timing, and simulation paths read sysinfo fields.

## Risks
The getter returns a mutable pointer, so any caller can alter global platform facts. Uninitialized fields cause wrong board paths or invalid delay calculations.

## Test Signals
Verify expected board type/clock after boot, stable pointer identity, and helper behavior when sysinfo fields are initialized in harnesses.
