<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/Makefile -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/Makefile

Purpose: this Makefile builds the GL860 subdriver module and composes it from the bridge core plus four sensor-specific source files.

Important APIs, types, and functions: `obj-$(CONFIG_USB_GL860) += gspca_gl860.o` binds the object to the Kconfig option. `gspca_gl860-objs` lists `gl860.o`, `gl860-mi1320.o`, `gl860-ov2640.o`, `gl860-ov9655.o`, and `gl860-mi2020.o`. `ccflags-y` adds the parent GSPCA include directory so `gspca.h` is found.

Control flow: Kbuild compiles each listed source into constituent objects and links them into `gspca_gl860.o`, then into a module or built-in object depending on `CONFIG_USB_GL860`.

State and persistence: no runtime state. The source list is the authoritative link boundary for sensor helpers referenced by `gl860.c`.

Dependencies and integration points: must stay synchronized with declarations in `gl860.h` and calls from `gl860.c` to `mi1320_init_settings()`, `mi2020_init_settings()`, `ov2640_init_settings()`, and `ov9655_init_settings()`.

Risks: omitting a sensor object causes link failures; adding a source without updating this file leaves code unreachable. Test signals are successful incremental and clean Kbuilds with `CONFIG_USB_GL860=m` and expected module symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gl860/Makefile -->
