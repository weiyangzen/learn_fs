# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/sun8i_a83t_mipi_csi2.h

Purpose: declares the A83T MIPI CSI-2 receiver's device, bridge, pad, and format structures.

Important APIs and types: defines driver name, sink/source pad enum, `struct sun8i_a83t_mipi_csi2_format`, `struct sun8i_a83t_mipi_csi2_bridge`, and `struct sun8i_a83t_mipi_csi2_device`.

Control flow: the controller implementation fills the device resources and bridge state; the D-PHY implementation receives the device pointer for shared regmap access.

State and persistence: bridge state stores active mbus format, parsed CSI-2 endpoint, async notifier, and bound source subdev. Device state stores three clocks, reset, regmap, and integrated PHY.

Dependencies and integration points: includes generic PHY, regmap, reset, V4L2 device, and fwnode headers. It is the private shared header between controller and D-PHY files.

Risks: adding more pads, channels, or PHY timing state requires expanding fixed-size structures. The bridge assumes one upstream source.

Test signals: compile coverage and runtime graph registration.
