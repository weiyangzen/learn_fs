# sources/distributed-fs/ceph-client/arch/m68k/sun3x/time.h

## Purpose

declares local interfaces for `sources/distributed-fs/ceph-client/arch/m68k/sun3x` so nearby m68k
machine or MMU files can share prototypes without exposing them globally

## Important APIs, Types, and Functions

Source read size: 19 lines, 433 bytes. Declared functions: `sun3x_hwclk`. Key macros/defines:
`SUN3X_TIME_H`. Types visible in this file: `mostek_dt`. External symbols referenced/declared:
`sun3x_hwclk`.

## Control Flow and Behavior

the header provides board or subsystem function prototypes, forward declarations, and include guards
consumed by adjacent C files

## State and Persistence

state is compile-time only, though the declared functions usually manipulate machine interrupt,
timer, PROM, or MMU state

## Dependencies and Integration Points

integrates local machine files with arch/m68k setup, machdep callbacks, and low-level assembly entry
points

## Risks and Test Signals

prototype drift causes build failures or wrong calling conventions; the platform defconfig build is
the first signal
