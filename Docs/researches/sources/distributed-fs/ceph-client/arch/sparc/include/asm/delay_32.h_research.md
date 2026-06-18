<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/delay_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/delay_32.h

## Purpose
This header declares/implements SPARC32 busy-wait delay helpers.

## Important APIs, Types, and Functions
It exposes `__delay`, `udelay`, and related loop-calibrated delay surfaces for SPARC32.

## Control Flow
Callers request short busy waits; helpers loop based on calibrated CPU speed.

## State and Persistence Behavior
No state is owned here beyond external calibration values used by delay code.

## Dependencies and Integration Points
It integrates with generic delay APIs, timer calibration, and drivers needing short waits.

## Risks
Incorrect calibration causes too-short hardware delays or excessive stalls.

## Test Signals
Boot delay calibration, run driver smoke tests using udelay/mdelay, and compare measured delay duration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/delay_32.h -->
