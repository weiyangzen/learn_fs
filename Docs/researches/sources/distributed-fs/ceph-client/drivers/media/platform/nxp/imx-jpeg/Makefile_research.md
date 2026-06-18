# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-jpeg/Makefile

Purpose: Kbuild composition for the i.MX JPEG encoder/decoder module.

Important APIs, types, and functions: `mxc-jpeg-encdec-objs := mxc-jpeg-hw.o mxc-jpeg.o` combines register helper and core V4L2 logic into one module/object. `obj-$(CONFIG_VIDEO_IMX8_JPEG) += mxc-jpeg-encdec.o` ties it to Kconfig.

Control flow: Kbuild first builds both object files, then links them into `mxc-jpeg-encdec`.

State and persistence behavior: No runtime state.

Dependencies and integration points: Must match symbols in `Kconfig` and exported function prototypes between `mxc-jpeg-hw.c`, `mxc-jpeg-hw.h`, and `mxc-jpeg.c`.

Risks: Renaming either object without updating this Makefile breaks module linkage. Function definitions in `mxc-jpeg-hw.c` are required by `mxc-jpeg.c`.

Test signals: Selecting `VIDEO_IMX8_JPEG` should produce `mxc-jpeg-encdec.ko` in module builds and link both object files in built-in builds.
