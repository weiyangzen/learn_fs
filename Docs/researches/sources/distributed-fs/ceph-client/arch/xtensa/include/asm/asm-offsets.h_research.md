<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/asm-offsets.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/asm-offsets.h

## Purpose
Thin include wrapper exposing generated assembly offsets to Xtensa assembly headers.

## Important APIs, Types, And Functions
Includes `<generated/asm-offsets.h>`.

## Control Flow
At compile time, assembly sources include this file to consume constants generated from C structure layouts.

## State And Persistence
No runtime state. Persistent build artifact is the generated offsets header.

## Dependencies And Integration Points
Depends on the kernel's asm-offset generation step and is used by assembly macros such as user access and current-task lookup.

## Risks And Edge Cases
Build ordering must ensure generated offsets exist before assembly preprocessing. Stale offsets would corrupt low-level structure access.

## Test Signals
Clean Xtensa builds and changes to thread/task structures that regenerate offsets successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/asm-offsets.h -->
