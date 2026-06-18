<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/Makefile

Purpose: connects selected staging Kconfig symbols to subdirectory builds.

Important APIs/types/functions: `obj-y += media/` always descends into media staging, while other entries are conditional on symbols such as `CONFIG_FB_TFT`, `CONFIG_XIL_AXIS_FIFO`, `CONFIG_GREYBUS`, and `CONFIG_BCM2835_VCHIQ`.

Control flow: kbuild evaluates `obj-*` variables and descends into enabled subdirectories during kernel or module builds.

State and persistence: no runtime state; build outputs depend on `.config`.

Dependencies and integration: pairs with top-level staging Kconfig and each subdirectory Makefile. It integrates FBTFT and axis-fifo into the build when their symbols are selected.

Risks: symbol/path mismatch silently omits drivers or breaks builds. The unconditional `media/` descent relies on that subdirectory handling its own inner config filtering.

Test signals: compile with each staging symbol enabled as built-in and module, especially `CONFIG_FB_TFT=m` and `CONFIG_XIL_AXIS_FIFO=m`, and verify expected objects are produced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/Makefile -->
