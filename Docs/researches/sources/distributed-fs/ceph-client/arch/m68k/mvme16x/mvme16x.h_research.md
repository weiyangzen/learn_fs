# sources/distributed-fs/ceph-client/arch/m68k/mvme16x/mvme16x.h

## Purpose

declares local interfaces for `sources/distributed-fs/ceph-client/arch/m68k/mvme16x` so nearby m68k
machine or MMU files can share prototypes without exposing them globally

## Important APIs, Types, and Functions

Source read size: 6 lines, 155 bytes. Declared functions: `mvme16x_cons_write`. Types visible in
this file: `console`.

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
