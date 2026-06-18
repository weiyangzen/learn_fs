<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/dcr.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/dcr.h

## Purpose
This header defines UltraSPARC Dispatch Control Register bits.

## Important APIs, Types, and Functions
It defines `DCR_*` flags for cache parity, branch prediction, return prediction, instruction dispatch, IRQ FP operation, and multiscalar dispatch controls.

## Control Flow
CPU setup or errata code reads/modifies DCR using these masks.

## State and Persistence Behavior
State is in the CPU DCR register and persists until changed or reset.

## Dependencies and Integration Points
It integrates with SPARC64 CPU initialization and performance/errata handling.

## Risks
Wrong bit programming can disable prediction/cache features or expose parity behavior incorrectly.

## Test Signals
Boot UltraSPARC variants, inspect DCR programming, and run performance/regression tests around CPU feature setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/dcr.h -->
