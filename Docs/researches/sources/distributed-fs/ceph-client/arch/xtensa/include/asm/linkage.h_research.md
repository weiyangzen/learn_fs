<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/linkage.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/linkage.h

## Purpose
Defines Xtensa symbol alignment for assembly linkage.

## Important APIs, Types, And Functions
Defines `__ALIGN` and `__ALIGN_STR` as `.align 4`.

## Control Flow
No runtime flow; assembler/linkage macros use these definitions when emitting functions and symbols.

## State And Persistence
No state.

## Dependencies And Integration Points
Used by Linux linkage macros and Xtensa assembly files.

## Risks And Edge Cases
Alignment must satisfy instruction fetch and ABI expectations. Too-small alignment can hurt performance or violate entry assumptions.

## Test Signals
Compile assembly objects and inspect symbol alignment for entry points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/linkage.h -->
