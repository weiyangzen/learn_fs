<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/cacheflush.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/cacheflush.h

## Purpose
This dispatcher header selects the MMU or non-MMU m68k cache flush implementation.

## Important APIs, Types, And Functions
- Includes `asm/cacheflush_no.h` when `__uClinux__` is defined.
- Includes `asm/cacheflush_mm.h` otherwise.

## Control Flow
There is no runtime control flow. Preprocessor selection chooses the cache maintenance API implementation at compile time.

## State And Persistence Behavior
No state is stored here. The selected included header defines the actual cache state manipulation behavior.

## Dependencies And Integration Points
It integrates all generic include users with either m68k MMU cache handling or m68knommu/ColdFire cache handling.

## Risks And Edge Cases
The selector uses `__uClinux__`; build environments must define it consistently for non-MMU targets or the wrong implementation will be compiled.

## Test Signals
Build both MMU and uClinux/non-MMU m68k configurations and verify cacheflush API availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/cacheflush.h -->
