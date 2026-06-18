# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/Kconfig

Purpose: Kconfig menu for Renesas media platform drivers, grouped by V4L capture, mem2mem, and SDR devices.

Important APIs/types/functions: defines symbols for CEU, R-Car CSI-2, SuperH VOU, FCP, FDP1, JPU, VSP1, and R-Car DRIF, and sources subdirectory Kconfigs for `rcar-isp`, `rcar-vin`, `rzg2l-cru`, and `rzv2h-ivc`.

Control flow: configuration dependencies expose only applicable drivers for V4L platform, V4L mem2mem, or SDR platform builds. Symbols select needed helpers such as media controller, V4L2 subdev API, reset controller, vb2 dma-contig/vmalloc, V4L2 mem2mem, V4L2 fwnode, or async support.

State and persistence: kernel config state only.

Dependencies and integration: matches Renesas architecture gates (`ARCH_RENESAS`, `ARCH_SHMOBILE`, `ARCH_R7S72100`) with `COMPILE_TEST` escape hatches. Some mem2mem drivers depend on FCP availability or absence according to architecture.

Risks: Kconfig dependency errors can hide drivers or allow impossible link combinations. The ARM64/FCP conditions for FDP1/VSP1 are subtle and should be preserved when refactoring. Sourced subdirectories must remain in sync with the Makefile.

Test signals: `make olddefconfig`, allmodconfig, allyesconfig, and targeted configs for capture, mem2mem, and SDR symbols on Renesas and COMPILE_TEST platforms.
