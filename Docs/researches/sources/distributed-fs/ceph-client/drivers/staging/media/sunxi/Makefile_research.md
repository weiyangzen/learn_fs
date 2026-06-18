# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/Makefile

Purpose: dispatches builds into Allwinner sunxi staging media subdirectories.

Important APIs/types: `obj-$(CONFIG_VIDEO_SUNXI_CEDRUS) += cedrus/` and `obj-$(CONFIG_VIDEO_SUN6I_ISP) += sun6i-isp/`.

Control flow: kbuild descends into each subdirectory only when the corresponding config is enabled.

State and persistence: build graph only.

Dependencies/integration: tied to child Kconfig symbols defined under the same tree.

Risks: none beyond stale symbol names causing a driver to stop building.

Test signals: `make M=drivers/staging/media/sunxi` with each symbol enabled should enter the expected subdirectory.
