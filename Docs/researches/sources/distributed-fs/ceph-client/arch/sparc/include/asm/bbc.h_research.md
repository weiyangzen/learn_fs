<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/bbc.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/bbc.h

## Purpose
This header describes the BootBus Controller used on SPARC systems.

## Important APIs, Types, and Functions
It defines register offsets, control/status bit masks, and structures/constants for BBC register blocks used by platform code.

## Control Flow
Platform initialization and error/power-management paths map BBC registers and use these constants to inspect or program hardware.

## State and Persistence Behavior
State lives in the BBC hardware registers. Header constants have no state.

## Dependencies and Integration Points
It integrates with SPARC64 platform support, environmental monitoring, reset/power control, and low-level bus accessors.

## Risks
Incorrect bit definitions can break platform management or acknowledge the wrong hardware status.

## Test Signals
Boot BBC-equipped machines, inspect register dumps, exercise power/reset/environmental paths, and verify no unexpected bus errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/bbc.h -->
