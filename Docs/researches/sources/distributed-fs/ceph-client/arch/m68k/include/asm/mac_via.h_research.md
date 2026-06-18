<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_via.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_via.h

## Purpose
`mac_via.h` maps the Macintosh VIA/RBV register interface and bit definitions for ADB, RTC, SCC, sound, NuBus, video, cache, power, and interrupt routing.

## Important APIs, Types, and Functions
It defines VIA/RBV base addresses, VIA1/VIA2/RBV port bits, 6522 register offsets, RBV-specific registers, monitor and interrupt-enable helper macros, globals `via1`, `via2`, `rbv_present`, `via_alt_mapping`, and APIs for L2 flush, interrupt registration/enabling/disabling, NuBus IRQ startup/shutdown, VIA1 IRQ handling, head select, and SCSI DRQ checks.

## Control Flow, State, and Persistence
The header has no implementation, but callers manipulate persistent VIA/RBV MMIO state. `IER_SET_BIT`/`IER_CLR_BIT` encode the 6522 interrupt-enable convention.

## Dependencies and Integration Points
Mac ADB, RTC, SCSI, NuBus, poweroff, video, cache flush, and IRQ code all depend on these definitions. `macints.h` maps IRQ numbers for VIA sources.

## Risks
Many bits differ by model, and comments document incomplete or conflicting sources. VIA2 may be an RBV or OSS replacement, so callers must check presence flags. Some bits control power or cache.

## Test Signals
Signals include ADB/RTC operation, VIA timer interrupts, NuBus interrupt cascade, RBV monitor detection, cache flush behavior, poweroff, and correct handling of machines without real VIA2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_via.h -->
