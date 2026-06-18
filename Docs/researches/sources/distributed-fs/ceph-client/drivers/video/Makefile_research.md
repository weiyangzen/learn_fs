# sources/distributed-fs/ceph-client/drivers/video/Makefile

## Purpose
This Makefile maps top-level video Kconfig symbols to built objects and subdirectories. It is the build glue for aperture helpers, screen info, STI, VGA state, command-line video helpers, HDMI, console, logo, backlight, fbdev, and videomode helpers.

## Important APIs, types, and functions
The file uses standard kbuild variables: `obj-$(CONFIG_...)`, composite object lists such as `screen_info-y`, and conditional `ifeq ($(CONFIG_OF),y)` inclusion. Notable mappings include `CONFIG_APERTURE_HELPERS -> aperture.o`, `CONFIG_VIDEO -> cmdline.o nomodeset.o`, unconditional descent into `backlight/` and `fbdev/`, and `CONFIG_VIDEOMODE_HELPERS` objects.

## Control flow
Kbuild evaluates config variables, adds matching objects or directories, and descends into subdirectories as needed. `backlight/` and `fbdev/` are always visited so their own Makefiles can decide object inclusion from their local symbols.

## State and persistence
The file has no runtime state. Its state is build graph state derived from `.config`.

## Dependencies and integration points
It integrates the symbols declared in `drivers/video/Kconfig` with compiled C sources. The `CONFIG_OF` branch adds device-tree timing conversion helpers only when OF support is built.

## Risks and test signals
Risks are stale symbol/object names, unconditional subdirectory descent interacting with missing dependencies, and OF helper omissions. Test signals include kbuild for minimal configs, `CONFIG_OF=n` with `VIDEOMODE_HELPERS=y`, modular backlight/fbdev builds, and `make W=1` for orphaned objects.
