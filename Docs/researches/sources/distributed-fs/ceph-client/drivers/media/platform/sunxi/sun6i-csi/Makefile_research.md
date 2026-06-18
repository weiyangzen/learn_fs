# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/Makefile

Purpose: links the sun6i CSI driver from platform, bridge, and capture components.

Important APIs and entries: `sun6i-csi-y` includes `sun6i_csi.o`, `sun6i_csi_bridge.o`, and `sun6i_csi_capture.o`; `obj-$(CONFIG_VIDEO_SUN6I_CSI)` builds `sun6i-csi.o`.

Control flow: kbuild creates a single composite module or built-in object when `VIDEO_SUN6I_CSI` is enabled.

State and persistence: no runtime state.

Dependencies and integration points: maps the Kconfig symbol to the implementation split used by the driver headers.

Risks: source/object list drift can omit a major subsystem because bridge and capture are not separately selectable.

Test signals: module builds with all three objects linked and no undefined references between the components.
