
# sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/Makefile

Purpose: Kbuild fragment for the Kyro framebuffer driver.

Important content: `obj-$(CONFIG_FB_KYRO) += kyrofb.o` enables the module/built-in object when the config symbol is selected. `kyrofb-objs` composes the final object from `STG4000Ramdac.o`, `STG4000VTG.o`, `STG4000OverlayDevice.o`, `STG4000InitDevice.o`, and `fbdev.o`.

Control flow and integration: build order ensures the public functions declared in `STG4000Interface.h` and called from `fbdev.c` are linked into one `kyrofb` driver. The object list makes the STG4000 helper files private implementation units of the driver rather than independent modules.

State and persistence: no runtime state.

Dependencies: requires `CONFIG_FB_KYRO` and the surrounding kernel Kbuild system. All listed object names must match source files in the same directory.

Risks: missing a helper object causes link failures for RAMDAC, VTG, overlay, or core PLL symbols. Adding new Kyro helper files requires updating this list.

Test signals: `make drivers/video/fbdev/kyro/` or a kernel build with `CONFIG_FB_KYRO=m/y` should compile and link `kyrofb.o` without unresolved STG4000 symbols.
