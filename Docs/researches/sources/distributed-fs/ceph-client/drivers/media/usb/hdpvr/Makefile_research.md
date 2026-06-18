<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/Makefile

Purpose: Kbuild composition for the HD-PVR driver.

Important APIs/types/functions: `hdpvr-objs` combines `hdpvr-control.o`, `hdpvr-core.o`, `hdpvr-video.o`, and `hdpvr-i2c.o`; `obj-$(CONFIG_VIDEO_HDPVR) += hdpvr.o` links them as the selected module or built-in object.

Control flow: Kbuild folds all listed objects into the single `hdpvr` driver. Optional I2C code is guarded inside `hdpvr-i2c.c`, so the object is always compiled but may contain no symbols when I2C is disabled.

State and persistence: no runtime state. It controls build artifacts only.

Dependencies and integration: pairs with `hdpvr/Kconfig` and the parent media USB build.

Risks: object ordering is conventional; missing any object causes unresolved driver entry points declared in `hdpvr.h`. Always compiling `hdpvr-i2c.o` relies on the preprocessor guard being correct.

Test signals: compile with `CONFIG_VIDEO_HDPVR=y`, `m`, and disabled; inspect `hdpvr.o` symbol resolution for control/video/I2C functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/Makefile -->
