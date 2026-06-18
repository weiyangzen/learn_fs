<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/delay_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/delay_64.h

## Purpose
This header provides SPARC64 delay helper declarations.

## Important APIs, Types, and Functions
It exposes low-level delay routines backed by tick/stick or calibrated loops.

## Control Flow
Drivers and core code call generic delay APIs that route to these SPARC64 helpers.

## State and Persistence Behavior
No header-owned state; timebase calibration persists elsewhere.

## Dependencies and Integration Points
It integrates with SPARC64 timers, generic delay APIs, and hardware drivers.

## Risks
Wrong timebase use can break device timing or boot waits.

## Test Signals
Measure udelay/mdelay accuracy and run boot/device initialization tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/delay_64.h -->
