# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/Makefile

## Purpose
This Makefile builds the OMAP2+ fbdev core, VRFB helper, DSS subdirectory, and display subdirectory.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_OMAP2_VRFB) += vrfb.o`
- `obj-y += dss/` and `obj-y += displays/`
- `obj-$(CONFIG_FB_OMAP2) += omap2fb.o`
- `omap2fb-y := omapfb-main.o omapfb-sysfs.o omapfb-ioctl.o`

## Control Flow
The build descends into DSS and displays regardless of `FB_OMAP2`, with each nested object gated by its own config. The main fbdev object links three implementation files when `CONFIG_FB_OMAP2` is set.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
It binds Kconfig symbols to object files and links the fbdev core from multiple compilation units.

## Risks
Unconditional subdirectory descent relies on child Makefiles to avoid building disabled drivers. Adding a new core file requires updating `omap2fb-y`.

## Test Signals
Build tests should confirm `omap2fb.o` contains main/sysfs/ioctl objects and display modules are compiled only under matching config symbols.
