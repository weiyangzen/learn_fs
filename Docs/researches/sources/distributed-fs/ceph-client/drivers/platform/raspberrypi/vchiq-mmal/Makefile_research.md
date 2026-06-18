# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/Makefile

Purpose: kbuild rules for the BCM2835 MMAL-over-VCHIQ service object.

Important APIs, types, and functions: `bcm2835-mmal-vchiq-objs := mmal-vchiq.o` defines the composite object contents. `obj-$(CONFIG_BCM2835_VCHIQ_MMAL) += bcm2835-mmal-vchiq.o` includes it based on Kconfig.

Control flow: kbuild compiles and links `mmal-vchiq.o` into the named object when enabled.

State and persistence: no runtime state; build state follows `.config`.

Dependencies and integration points: depends on `CONFIG_BCM2835_VCHIQ_MMAL` and MMAL source/header files in the same directory.

Risks: the Makefile only includes `mmal-vchiq.o`; all shared structures must remain header-only or linked from that object. Missing `mmal-vchiq.c` would fail the build.

Test signals: build the directory under built-in and module configurations and inspect module/object contents.
