# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi_bridge.h

Purpose: declares the bridge subdevice data model and helper APIs for sun6i CSI.

Important APIs and types: defines bridge pad indexes, `struct sun6i_csi_bridge_format`, source tracking structs, async-subdev wrapper, and `struct sun6i_csi_bridge`. Declares helpers for dimensions, format, format lookup, setup, and cleanup.

Control flow: the platform code calls setup/cleanup. Capture code queries bridge dimensions and mbus format for link validation and hardware configuration. Bridge implementation uses the source structures for async endpoint binding.

State and persistence: stores active media-bus format, lock, subdevice, notifier, pads, parallel source, and MIPI source. Source endpoint data persists after fwnode parsing and is used during stream-time bus configuration.

Dependencies and integration points: includes V4L2 device and fwnode types and forward-declares `struct sun6i_csi_device`. It mediates between the capture object and external sensor/MIPI subdevices.

Risks: the `pads` array is declared as `[2]` rather than by the enum count macro, so future pad-count changes require careful updates. Source selection depends on stored subdev pointers matching the active remote entity.

Test signals: build coverage and runtime async binding validate the header contracts; media graph introspection should show two bridge pads and correct links.
