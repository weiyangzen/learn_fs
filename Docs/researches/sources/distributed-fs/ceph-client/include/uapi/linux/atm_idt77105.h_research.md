<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm_idt77105.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atm_idt77105.h

## Purpose
Defines IDT77105 ATM PHY driver-specific statistics structure and ioctls.

## Important APIs, Types, And Functions
`struct idt77105_stats` reports symbol errors, transmitted cells, received cells, and receive HEC errors. `IDT77105_GETSTAT` reads stats; `IDT77105_GETSTATZ` reads and zeros stats.

## Control Flow
Utilities issue PHY-private ioctls via `atmif_sioc`; the driver copies current counters to userspace and optionally resets them for the zeroing variant.

## State And Persistence
Counters are live driver/hardware statistics. `GETSTATZ` mutates them by clearing after read.

## Dependencies And Integration Points
Depends on Linux types, ATM ioctl ranges, and ATM device definitions. Integrates with IDT77105 PHY diagnostics.

## Risks And Edge Cases
Read-and-zero races, counter wrap, and invalid userspace buffer pointers are the main risks.

## Test Signals
Stats read tests, zeroing behavior, counter increment under traffic/errors, and malformed ioctl buffer rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atm_idt77105.h -->
