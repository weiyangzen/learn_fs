# sources/distributed-fs/ceph-client/drivers/media/platform/aspeed/Kconfig

Purpose: Defines the Aspeed Video Engine media platform driver option.

Important APIs/types/functions: No C API. `VIDEO_ASPEED` is a tristate depending on `ARCH_ASPEED || COMPILE_TEST`, V4L platform drivers, and video device support, and selects vb2 DMA-contig.

Control flow and state: Controls whether the Aspeed video engine driver is built. Help text describes AST2400/AST2500 video capture and compression support.

Dependencies and integration: Paired with `aspeed/Makefile`, which builds `aspeed-video.o` when the option is enabled.

Risks: Kconfig only references AST2400/AST2500 in help; newer SoCs need option/help updates if supported elsewhere.

Test signals: Kconfig visibility on Aspeed and compile-test builds, module build with `VIDEO_ASPEED=m`, and dependency resolution for vb2 DMA-contig.
