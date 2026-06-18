# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-mipi-csi2/sun6i_mipi_csi2.h

Purpose: declares the A31 MIPI CSI-2 receiver device, bridge, pad, and format data structures.

Important APIs and types: defines the driver name, sink/source pad enum, `struct sun6i_mipi_csi2_format`, `struct sun6i_mipi_csi2_bridge`, and `struct sun6i_mipi_csi2_device`.

Control flow: the implementation stores subdev, pads, endpoint, notifier, active mbus format, and source subdev in the bridge structure; platform resource setup fills the device structure.

State and persistence: active endpoint lane data and mbus format persist after setup and format negotiation; source subdev persists after async binding.

Dependencies and integration points: includes PHY, regmap, reset, V4L2 device, and V4L2 fwnode headers. It is private to the driver source.

Risks: no public functions are declared, so all behavior is confined to one C file. Future multi-source or multi-channel support would require expanding the bridge state model.

Test signals: compile coverage and runtime subdev registration validate structure use.
