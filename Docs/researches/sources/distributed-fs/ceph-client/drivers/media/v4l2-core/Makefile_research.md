# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/Makefile

## Purpose
This Makefile maps V4L2 core Kconfig symbols to built objects. It assembles the main `videodev` object, the `tuner` object, and optional helper modules such as async notifier, CCI, fwnode, codec helpers, flash LED support, media-controller support, SPI/I2C support, tracepoints, and mem2mem.

## Important build rules
The file adds include paths for DVB frontends and tuners because `tuner-core.c` dynamically attaches tuner frontend implementations. `tuner-objs := tuner-core.o` defines the tuner module body. `videodev-objs` combines core V4L2 files including device, ioctl, fh, event, subdev, common, and controls code. Conditional `videodev-$(CONFIG_*)` entries add compat ioctl, media controller, SPI, trace, and I2C support. Top-level `obj-$(CONFIG_*)` lines build individual helper modules and the main `videodev.o`.

## Control flow
Build flow is Kbuild-driven. If `CONFIG_VIDEO_DEV` is enabled, `videodev.o` is built from the base and conditional `videodev-*` object lists. If `CONFIG_VIDEO_TUNER` is enabled, `tuner.o` is built from `tuner-core.o`. Optional helpers are compiled independently according to their Kconfig symbols.

## State and persistence behavior
The file has no runtime state. Its persistent effect is the kernel build graph and module composition. Object ordering in `videodev-objs` can matter for readability and, in rare cases, initialization/link behavior.

## Dependencies and integration points
The Makefile is tightly coupled to the local Kconfig names and source file names. It integrates V4L2 core with media controller, tracepoints, I2C/SPI helper code, codec helpers, async registration, fwnode parsing, CCI helpers, and tuner support.

## Risks and edge cases
Adding a source file without a matching Kconfig rule can leave symbols undefined or code unreachable. Removing or renaming entries can break module builds only for specific configurations. The comments require conditional lists to remain alphabetically sorted by Kconfig name; violating that makes maintenance harder and may fail style review.

## Test signals
Run representative `make M=drivers/media/v4l2-core` builds for built-in and modular combinations of VIDEO_DEV, VIDEO_TUNER, V4L2_ASYNC, V4L2_CCI, MEDIA_CONTROLLER, CONFIG_COMPAT, CONFIG_SPI, CONFIG_VIDEO_V4L2_I2C, and CONFIG_TRACEPOINTS. Link errors are the primary signal.
