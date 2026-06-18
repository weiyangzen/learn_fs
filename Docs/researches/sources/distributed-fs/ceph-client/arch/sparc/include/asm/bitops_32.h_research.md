<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/bitops_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/bitops_32.h

## Purpose
This header implements SPARC32 bit operations used by generic kernel code.

## Important APIs, Types, and Functions
It provides set/clear/change/test bit operations and scanning helpers, with endian-aware numbering and atomic variants where supported.

## Control Flow
Inline helpers compute word/bit locations and issue the required load/store or atomic sequences.

## State and Persistence Behavior
Only caller-provided bitmaps are mutated. No global state exists.

## Dependencies and Integration Points
It backs Linux bitmap APIs, scheduler flags, page flags, filesystems, and driver bitmaps on SPARC32.

## Risks
Bit numbering and endianness must match generic expectations. Non-atomic helpers must not be used where atomicity is required.

## Test Signals
Run bitmap tests, page flag stress, filesystem mount tests, and SMP bit-operation tests if available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/bitops_32.h -->
