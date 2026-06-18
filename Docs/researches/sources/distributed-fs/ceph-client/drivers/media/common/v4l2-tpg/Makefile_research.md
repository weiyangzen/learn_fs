<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/v4l2-tpg/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/common/v4l2-tpg/Makefile

## Purpose
The Makefile builds the common V4L2 test pattern generator composite object.

## Important APIs, Types, and Functions
It defines `v4l2-tpg-objs := v4l2-tpg-core.o v4l2-tpg-colors.o` and adds `v4l2-tpg.o` to `obj-*` based on `CONFIG_VIDEO_V4L2_TPG`.

## Control Flow
When Kconfig enables `VIDEO_V4L2_TPG`, kbuild compiles the core and colors objects and links them into the `v4l2-tpg` object, either built-in or as a module according to the symbol value.

## State and Persistence Behavior
There is no runtime state. Build output depends entirely on the kernel configuration.

## Dependencies and Integration Points
This file integrates with kbuild and the `v4l2-tpg` source files in the same directory. It is paired with the directory Kconfig symbol.

## Risks and Test Signals
Any source file rename or split must update `v4l2-tpg-objs`. Test signals include successful `make M=drivers/media/common/v4l2-tpg` style builds and correct link inclusion when drivers select `VIDEO_V4L2_TPG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/v4l2-tpg/Makefile -->
