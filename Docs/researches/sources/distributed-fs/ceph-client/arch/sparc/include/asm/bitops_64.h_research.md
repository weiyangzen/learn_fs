<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/bitops_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/bitops_64.h

## Purpose
This header implements SPARC64 bit operations and optimized scanning helpers.

## Important APIs, Types, and Functions
It provides atomic and non-atomic bit set/clear/change/test helpers plus `ffz`/find-bit style primitives, using SPARC64 word operations.

## Control Flow
Helpers calculate the target word, apply masks, and use atomic primitives where required.

## State and Persistence Behavior
State is limited to caller-owned bitmaps.

## Dependencies and Integration Points
It integrates with generic bitops, page flags, cpumasks, nodemasks, locks, and driver bitmaps.

## Risks
Endian bit numbering, alignment, and memory ordering are the main correctness hazards.

## Test Signals
Run lib/bitmap tests, cpumask/nodemask smoke tests, lock bitops users, and SMP stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/bitops_64.h -->
