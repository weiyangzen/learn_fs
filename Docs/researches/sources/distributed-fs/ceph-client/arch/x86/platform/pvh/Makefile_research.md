<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/pvh/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/pvh/Makefile

## Purpose
Builds x86 PVH guest entry and initialization support.

## Important APIs, Types, And Functions
`head.o` is marked non-standard and KASAN is disabled. `enlighten.o` and `head.o` are selected by `CONFIG_PVH`.

## Control Flow
Kbuild links the assembly entry and C boot-parameter setup only when PVH support is configured.

## State And Persistence
No runtime state is stored in the Makefile.

## Dependencies And Integration Points
Integrates with Xen/HVM PVH boot ABI and x86 early boot.

## Risks And Edge Cases
Instrumentation must be disabled for early entry code because it runs before normal runtime setup.

## Test Signals
PVH config builds and boots under Xen PVH are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/pvh/Makefile -->
