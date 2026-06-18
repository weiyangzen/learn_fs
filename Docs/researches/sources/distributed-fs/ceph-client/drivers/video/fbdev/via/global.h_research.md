# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/global.h

## Purpose
`global.h` is the umbrella include for the VIA framebuffer driver. It gathers kernel headers and VIA local headers so source files share common types, register helpers, chip structures, mode tables, LCD/DVI APIs, ioctl definitions, and utility declarations.

## Important APIs, Types, And Data
The file includes fbdev, PCI, I/O, proc, console, timer, optional OLPC detection, and VIA local headers: `debug.h`, `viafbdev.h`, `chip.h`, `accel.h`, `share.h`, `dvi.h`, `viamode.h`, `hw.h`, `lcd.h`, `ioctl.h`, `via_utility.h`, `vt1636.h`, and `tblDPASetting.h`. It also provides a fallback `machine_is_olpc(x) 0` when OLPC support is not enabled.

## Control Flow
There is no direct control flow. Its include ordering controls what declarations and macros are visible to each VIA compilation unit.

## State And Persistence
No state is defined in the header itself in the viewed contents; state declarations and definitions live in included headers and `global.c`.

## Dependencies And Integration Points
This header is a major coupling point: most VIA files include it instead of selecting narrow dependencies. It integrates Linux subsystem headers with the VIA driver's private APIs and hardware tables.

## Risks
The umbrella pattern increases rebuild scope and makes dependency cycles harder to reason about, especially because `chip.h` includes `global.h`. The fallback `machine_is_olpc(x)` macro hides OLPC-specific behavior in non-OLPC builds. Header changes can have broad impact across all VIA objects.

## Test Signals
Signals include clean compilation of every VIA object, no missing declarations when local headers change, correct OLPC conditional behavior, and include-cycle changes detected by incremental builds.
