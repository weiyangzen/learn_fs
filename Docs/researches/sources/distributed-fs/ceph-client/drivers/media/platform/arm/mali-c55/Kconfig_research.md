# sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/Kconfig

Purpose: Defines the `VIDEO_MALI_C55` tristate option for the Arm Mali-C55 ISP platform driver.

Important APIs/types/functions: No runtime API. The option depends on supported architectures or `COMPILE_TEST`, V4L platform drivers, video device support, and OF. It selects MIPI D-PHY PHY support, Media Controller, V4L2 fwnode/subdev APIs, V4L2 ISP helpers, and vb2 DMA-contig/vmalloc support.

Control flow and state: Kconfig controls whether `mali-c55.o` is built in, built as a module, or omitted. The help text declares module name `mali-c55`.

Dependencies and integration: Enables the source files listed in the subdirectory Makefile and depends on V4L2/media infrastructure used throughout the driver.

Risks: Missing selected dependencies would surface as compile/link failures. Architecture gating may hide the driver from relevant non-listed platforms unless `COMPILE_TEST` is used.

Test signals: Kconfig dependency resolution, compile-test builds, module build/install, and allmodconfig coverage.
