# sources/distributed-fs/ceph-client/drivers/video/fbdev/Makefile

## Purpose
This Makefile maps fbdev `CONFIG_*` symbols to object files and subdirectories. It is the Kbuild companion to the Kconfig menu, ensuring that selected legacy framebuffer drivers and helper libraries are compiled into built-in objects or modules.

## Important APIs, Types, and Functions
The main interface is Kbuild's `obj-y` and `obj-$(CONFIG_...)` syntax. `obj-y += core/` always descends into the fbdev core directory. Relevant mappings for this work item are `obj-$(CONFIG_FB_ACORN) += acornfb.o`, `obj-$(CONFIG_FB_AMIGA) += amifb.o c2p_planar.o`, `obj-$(CONFIG_FB_ARC) += arcfb.o`, `obj-$(CONFIG_FB_ARK) += arkfb.o`, and `obj-$(CONFIG_FB_ASILIANT) += asiliantfb.o`. The file also adds helper objects such as `macmodes.o`, `sbuslib.o`, and `wmt_ge_rops.o` when their symbols are enabled.

## Control Flow
Kbuild evaluates the Makefile after configuration. Built-in `y` objects are linked into the kernel or parent built-in archive; module `m` objects are compiled into modules where the symbol permits modules. Hardware-specific drivers are listed first, platform and fallback drivers later, and the virtual test framebuffer is last. Subdirectories such as `matrox/`, `aty/`, `sis/`, `via/`, `geode/`, `mmp/`, `omap/`, `omap2/`, and `mb862xx/` are entered based on fixed or conditional object assignments.

## State and Persistence
The Makefile holds no runtime state. Its persistent effect is build output: generated `.o`, `.ko`, built-in archives, and dependency files. The `CONFIG_FB_AMIGA` mapping persists an important linkage relation by always adding `c2p_planar.o` with `amifb.o`, because `amifb.c` calls `c2p_planar()` for multi-bit image blits.

## Dependencies and Integration Points
This file integrates directly with `Kconfig` symbols and with the source files in the same directory. It is also an integration point for shared helper subdirectories and vendor subtrees. Driver code assumes the correct helper selections from Kconfig; the Makefile assumes those helpers and source files are present under the same kernel tree.

## Risks and Edge Cases
Misaligning the Makefile with Kconfig breaks builds either by omitting required companion objects or by compiling code when dependencies are not met. The Amiga driver is a concrete example: dropping `c2p_planar.o` would break `amifb_imageblit()` for non-1bpp image expansion. Shared subdirectory entries such as unconditional `obj-y += omap/ omap2/` rely on each subdirectory's own Kconfig/Makefile logic to avoid unwanted objects. Duplicated helper object inclusion, such as `macmodes.o` on multiple Apple/ATI lines, is intentional Kbuild behavior but should be reviewed if moving helpers.

## Test Signals
Check `make drivers/video/fbdev/` or targeted builds with the relevant configs set. Inspect generated module names: `amifb`, `arcfb`, `arkfb` where tristate allows modules, and built-in object presence for bool-only `acornfb` and `asiliantfb`. Link-time success with `CONFIG_FB_AMIGA` verifies the `c2p_planar.o` companion. `make W=1` can catch stale object references after source renames.
