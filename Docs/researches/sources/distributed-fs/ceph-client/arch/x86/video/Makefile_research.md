<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/video/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/video/Makefile

## Purpose
`video/Makefile` builds the common x86 video helper object.

## Important APIs, types, and functions
It adds `video-common.o` to `obj-y`.

## Control flow
Kbuild links the helper whenever the x86 video directory is included.

## State and persistence behavior
No runtime state exists in the Makefile.

## Dependencies and integration points
It depends on parent x86 architecture kbuild selection.

## Risks and edge cases
The risk is only omitted helper linkage for framebuffer/primary-device users.

## Test signals
Signals are successful x86 build and exported symbols from `video-common.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/video/Makefile -->
