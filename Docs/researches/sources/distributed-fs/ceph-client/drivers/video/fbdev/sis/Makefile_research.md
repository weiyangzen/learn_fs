# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/Makefile

## Purpose
This Makefile is the kbuild glue for the SiS framebuffer driver directory. It builds the `sisfb` composite object when `CONFIG_FB_SIS` is enabled.

## Important APIs, types, and functions
There are no C APIs in this file. The relevant kbuild declarations are `obj-$(CONFIG_FB_SIS) += sisfb.o` and `sisfb-objs := sis_main.o sis_accel.o init.o init301.o initextlfb.o`. These lines define both the config-controlled object and its component compilation units.

## Control flow
Kbuild evaluates `CONFIG_FB_SIS`; if enabled as built-in or module, it compiles the listed objects and links them into `sisfb.o`. Conditional content inside those objects, such as inclusion of `300vtbl.h` or `310vtbl.h`, is controlled by C preprocessor symbols like `CONFIG_FB_SIS_300` and `CONFIG_FB_SIS_315` rather than by this Makefile.

## State and persistence
The file has no runtime state. Its only state is build graph state derived from `.config`, deciding whether the SiS framebuffer code is present and whether it is built-in or modular.

## Dependencies and integration points
It integrates the fbdev Kconfig symbol `CONFIG_FB_SIS` with the SiS driver sources. The component list ties the top-level fbdev driver (`sis_main.o`), acceleration (`sis_accel.o`), CRT1 init (`init.o`), CRT2/bridge init (`init301.o`), and external-LFB init support (`initextlfb.o`) into one driver.

## Risks and test signals
Risks are missing object components, stale file names, or a mismatch between Kconfig suboptions and conditionally compiled code in the listed objects. Test signals include `CONFIG_FB_SIS=y`, `CONFIG_FB_SIS=m`, 300-only and 315-only config builds, `make W=1` for the directory, and module load/link checks confirming that all referenced init and acceleration symbols resolve.
