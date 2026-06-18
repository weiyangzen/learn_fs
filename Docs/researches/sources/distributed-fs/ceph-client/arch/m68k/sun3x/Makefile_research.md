# sources/distributed-fs/ceph-client/arch/m68k/sun3x/Makefile

## Purpose

selects the object files built for `sources/distributed-fs/ceph-client/arch/m68k/sun3x`, the m68k
platform area that supports Sun-3x machines, including PROM vectors, DVMA/IOMMU setup, RTC/time
handling, model reporting, and reset paths

## Important APIs, Types, and Functions

Source read size: 6 lines, 139 bytes. Build selections: `obj-y -> config.o time.o dvma.o prom.o`.

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
