# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/Kconfig

Purpose: provides the menu entry and source aggregation point for Allwinner sunxi media platform drivers under the kernel media platform Kconfig tree.

Important APIs and symbols: no runtime APIs are declared. It emits a `comment "Sunxi media platform drivers"` and sources six child Kconfig files: `sun4i-csi`, `sun6i-csi`, `sun6i-mipi-csi2`, `sun8i-a83t-mipi-csi2`, `sun8i-di`, and `sun8i-rotate`.

Control flow: Kconfig evaluation enters this file from the parent media platform Kconfig and then evaluates each child driver option in order. The file itself has no conditions around child inclusion, so each child controls its own visibility and dependencies.

State and persistence: selected symbols persist only in the kernel build configuration. There is no runtime state.

Dependencies and integration points: integrates the sunxi capture, MIPI CSI-2, deinterlace, and rotation drivers into the V4L2 media platform menu. The corresponding directory Makefile builds the same child directories unconditionally through `obj-y` so child Makefiles can gate objects by config symbols.

Risks: adding a new sunxi media driver requires updating this source list or the option will be invisible in configuration. Ordering can affect menu readability but not runtime behavior.

Test signals: `menuconfig` should show all six child options when dependencies are satisfiable. `allmodconfig` and `COMPILE_TEST` builds validate that every sourced child Kconfig parses.
