<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/Makefile -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/Makefile

Purpose: defines how the Intel 810/815 framebuffer driver objects are built based on Kconfig options.

Important APIs, types, and functions: `obj-$(CONFIG_FB_I810) += i810fb.o` selects the composite object. `i810fb-objs` always includes `i810_main.o` and `i810_accel.o`. It conditionally adds `i810_gtf.o` when `CONFIG_FB_I810_GTF` is enabled, otherwise `i810_dvt.o`. It conditionally adds `i810-i2c.o` when `CONFIG_FB_I810_I2C` is enabled.

Control flow: build-time control decides whether runtime mode timing comes from GTF or DVT code and whether DDC/I2C support is compiled into the i810fb object.

State and persistence: no runtime state. The file persists build composition and therefore the available code paths in the module/built-in driver.

Dependencies and integration points: integrates with Linux kbuild and Kconfig symbols for `CONFIG_FB_I810`, `CONFIG_FB_I810_GTF`, and `CONFIG_FB_I810_I2C`. The `i810-i2c.c` file in this work item is included only through the I2C conditional.

Risks: misconfigured Kconfig combinations change available EDID and timing behavior. The file assumes object names remain stable; renames in source files must be reflected here.

Test signals: build matrix with `CONFIG_FB_I810` off/on, GTF on/off, and I2C on/off; verify `i810fb.o` links with the expected object list in each configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/Makefile -->
