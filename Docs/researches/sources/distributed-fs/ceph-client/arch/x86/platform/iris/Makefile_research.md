<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/iris/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/iris/Makefile

## Purpose
Builds Eurobraille Iris platform poweroff support.

## Important APIs, Types, And Functions
`iris.o` is selected by `CONFIG_X86_RDC321X`.

## Control Flow
Kbuild links the Iris platform driver only for the configured x86 platform.

## State And Persistence
No runtime state exists in the Makefile.

## Dependencies And Integration Points
Integrates with platform driver/module infrastructure through `iris.c`.

## Risks And Edge Cases
The Kconfig dependency must match the rare hardware needing this handler; otherwise the module is unavailable or unnecessarily built.

## Test Signals
Build and module load coverage for the selected config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/iris/Makefile -->
