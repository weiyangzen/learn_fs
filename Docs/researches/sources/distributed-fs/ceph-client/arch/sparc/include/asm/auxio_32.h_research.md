<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/auxio_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/auxio_32.h

## Purpose
This header defines SPARC32 AUXIO register bits and helper macros for floppy, link-test, LED, and power-control functions.

## Important APIs, Types, and Functions
It defines AUXIO bit masks such as `AUXIO_FLPY_DENS`, `AUXIO_FLPY_DCHG`, `AUXIO_FLPY_DSEL`, `AUXIO_LINK_TEST`, `AUXIO_FLPY_TCNT`, `AUXIO_FLPY_EJCT`, `AUXIO_LED`, and power bits. It declares `set_auxio()`, `get_auxio()`, and `auxio_power_register`, and provides `auxio_set_lte()`/`auxio_set_led()` macros.

## Control Flow
Drivers call the helpers/macros to set or clear AUXIO bits. The macros convert high-level on/off requests into `set_auxio(bits_on, bits_off)` operations.

## State and Persistence Behavior
State lives in platform AUXIO hardware registers. Writes persist until hardware changes or later writes; the header itself stores no state.

## Dependencies and Integration Points
It depends on SPARC32 virtual-address constants and I/O types. It integrates with floppy, LED, link-test, and power-management drivers.

## Risks
AUXIO registers contain write-one/reserved bits and platform-specific interpretations, so incorrect masks can affect floppy motor control, LEDs, or power state.

## Test Signals
On sun4m/sun4c-style systems, test LED toggling, floppy operations, link-test controls, and power-failure/off register handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/auxio_32.h -->
