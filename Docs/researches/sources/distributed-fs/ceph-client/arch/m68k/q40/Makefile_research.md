# sources/distributed-fs/ceph-client/arch/m68k/q40/Makefile

## Purpose

selects the object files built for `sources/distributed-fs/ceph-client/arch/m68k/q40`, the m68k
platform area that configures the Q40/Q60 machine family: boot model reporting,
keyboard/IDE/RTC/sound/timer hooks, interrupts, reset, and platform devices

## Important APIs, Types, and Functions

Source read size: 6 lines, 126 bytes. Build selections: `obj-y -> config.o q40ints.o`.

## Control Flow and Behavior

Kbuild object variables include the platform's configuration, interrupt, PROM, DVMA, or helper
objects when the corresponding CONFIG symbol is enabled

## State and Persistence

there is no runtime state; the persistent effect is linked object coverage in vmlinux

## Dependencies and Integration Points

integrates with arch/m68k top-level Makefile/Kconfig.machine and the machine's machdep hook
implementation

## Risks and Test Signals

missing objects produce unresolved hooks or silently absent platform support; platform defconfig
builds are the main test signal
