# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/Makefile

## Purpose
This Makefile descends unconditionally into the OMAP2 omapfb subdirectory for fbdev display support.

## Important APIs, Types, And Functions
- `obj-y += omapfb/` adds the subdirectory to the build traversal.

## Control Flow
The kernel build system evaluates the nested Makefile, where actual object inclusion is controlled by configuration symbols.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
It integrates `drivers/video/fbdev/omap2/omapfb` with the parent fbdev build.

## Risks
Because descent is unconditional, nested Makefiles must correctly gate objects by config to avoid unwanted builds.

## Test Signals
Kernel build logs should enter the `omapfb/` subdirectory and include objects only when relevant configs are enabled.
