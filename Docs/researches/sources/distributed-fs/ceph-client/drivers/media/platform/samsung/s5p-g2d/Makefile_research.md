# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-g2d/Makefile

Purpose: build recipe for the Samsung G2D V4L2 mem2mem driver.

Important declarations: `s5p-g2d-objs := g2d.o g2d-hw.o` links the core V4L2/mem2mem driver with the hardware register helper file. `obj-$(CONFIG_VIDEO_SAMSUNG_S5P_G2D) += s5p-g2d.o` connects the aggregate object to the Kconfig option.

Control flow and integration: when the option is built-in or modular, Kbuild compiles both source files and links them into one driver object that registers the platform driver from `g2d.c`.

State and persistence: no runtime state.

Risks: adding new G2D helper files requires updating this object list. A mismatch between Kconfig symbol and object name would break builds.

Test signals: incremental build with the symbol enabled as `y` and `m`, and symbol-disabled build confirming no objects are compiled.
