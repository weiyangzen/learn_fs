<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/dcu.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/dcu.h

## Purpose
This header defines SPARC64 Data Cache Unit control bits.

## Important APIs, Types, and Functions
It defines `DCU_*` flags for physical/virtual cache enable, store merging, RAW bypass, prefetch, write cache, watchpoint masks/enables, DMMU/IMMU, D-cache, and I-cache enable.

## Control Flow
Low-level CPU/MMU code uses these masks when enabling caches/MMUs or configuring watchpoints.

## State and Persistence Behavior
State lives in the DCU control register.

## Dependencies and Integration Points
It integrates with boot CPU setup, MMU enable, cache control, and debugging/watchpoint facilities.

## Risks
Misprogramming DCU can disable caches/MMUs or corrupt memory ordering during boot.

## Test Signals
Boot SPARC64 systems, validate cache/MMU enable state, run memory stress and watchpoint tests where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/dcu.h -->
