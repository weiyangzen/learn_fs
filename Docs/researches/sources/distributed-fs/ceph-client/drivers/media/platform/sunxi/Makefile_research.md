# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/Makefile

Purpose: delegates sunxi media platform builds to the six child driver directories.

Important APIs and entries: `obj-y` includes `sun4i-csi/`, `sun6i-csi/`, `sun6i-mipi-csi2/`, `sun8i-a83t-mipi-csi2/`, `sun8i-di/`, and `sun8i-rotate/`.

Control flow: kbuild descends into each child directory during media platform builds. The actual object selection is controlled by each child Makefile through its Kconfig symbol.

State and persistence: no runtime state. Build output is determined by child `obj-$(CONFIG_...)` entries.

Dependencies and integration points: mirrors the top-level sunxi Kconfig sourcing and keeps all child drivers reachable from the platform media build.

Risks: if a child directory is removed or renamed without updating this Makefile, kbuild traversal fails. If a child Kconfig is added without a matching Makefile descent, the option can be selected without producing objects.

Test signals: kernel build coverage for `drivers/media/platform/sunxi/` with each child driver enabled and disabled.
