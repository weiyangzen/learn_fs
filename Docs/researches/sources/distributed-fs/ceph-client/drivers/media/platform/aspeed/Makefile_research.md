# sources/distributed-fs/ceph-client/drivers/media/platform/aspeed/Makefile

Purpose: Connects `CONFIG_VIDEO_ASPEED` to the Aspeed video engine object in Kbuild.

Important APIs/types/functions: No C API. `obj-$(CONFIG_VIDEO_ASPEED) += aspeed-video.o`.

Control flow and state: Kbuild includes `aspeed-video.o` as built-in or module depending on the Kconfig state.

Dependencies and integration: Depends on the Aspeed Kconfig option and the corresponding implementation file in the same directory.

Risks: Object name drift causes build failure or omitted driver.

Test signals: Build with option unset, built-in, and module.
