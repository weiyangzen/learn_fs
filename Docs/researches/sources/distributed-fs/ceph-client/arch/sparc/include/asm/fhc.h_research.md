<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/fhc.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/fhc.h

## Purpose
This header defines FireHose Controller register bits for SPARC platforms.

## Important APIs, Types, and Functions
It provides FHC register offsets and masks for board status, control, interrupt, reset, and environmental/platform management.

## Control Flow
Platform code maps FHC registers, decodes status, configures interrupts, and performs reset/power/environment control as needed.

## State and Persistence Behavior
State lives in FHC hardware registers.

## Dependencies and Integration Points
It integrates with SPARC64 platform setup, interrupt handling, and environmental monitoring.

## Risks
Wrong register programming can disrupt board-level interrupts or reset behavior.

## Test Signals
Boot FHC systems, verify interrupt routing, platform status reporting, and safe reset/power controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/fhc.h -->
