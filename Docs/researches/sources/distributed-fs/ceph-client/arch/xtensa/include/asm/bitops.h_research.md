<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/bitops.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/bitops.h

## Purpose
Provides Xtensa bit operations, including optimized find-first/last bit support when the NSA instruction exists, plus generic non-atomic and little-endian helpers.

## Important APIs, Types, And Functions
Important definitions include `__cntlz`, `ffz`, `__ffs`, `fls`, `fls64`, architecture find-bit macros, and includes for generic bitops variants.

## Control Flow
Feature-dependent inline functions use `nsau` for count-leading-zero operations when present; otherwise generic helpers provide portable behavior. Atomic bit operations are mostly delegated through generic or other architecture primitives.

## State And Persistence
No persistent state; functions inspect integer words or bitmaps.

## Dependencies And Integration Points
Depends on `<linux/bitops.h>` include discipline, Xtensa core features, byteorder, barriers, and generic bitops headers.

## Risks And Edge Cases
Incorrect endianness or bit numbering would break filesystem, scheduler, and memory-management bitmaps. `ffz` is undefined for all-ones input, matching generic expectations.

## Test Signals
Build with and without `XCHAL_HAVE_NSA`, run bitmap/bitops selftests, and stress page allocator, cpumasks, and filesystem bitmaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/bitops.h -->
