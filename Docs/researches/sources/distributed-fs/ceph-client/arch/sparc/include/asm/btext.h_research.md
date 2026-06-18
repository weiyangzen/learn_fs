<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/btext.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/btext.h

## Purpose
This header declares early boot text-console discovery for SPARC.

## Important APIs, Types, and Functions
It declares `btext_find_display()`.

## Control Flow
Early boot code calls the function to locate a display usable for boot text output.

## State and Persistence Behavior
The header has no state; the implementation may initialize early console/display state.

## Dependencies and Integration Points
It integrates with SPARC boot console and framebuffer discovery.

## Risks
Incorrect declaration would break early console linkage; display discovery failures reduce boot diagnostics.

## Test Signals
Boot with framebuffer console enabled and verify early boot text appears on supported displays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/btext.h -->
