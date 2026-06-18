# sources/distributed-fs/ceph-client/include/media/v4l2-mediabus.h

Purpose: declares V4L2 media-bus configuration flags, bus-specific config structs, bus type enum, and inline format conversion helpers between media-bus frame formats and pixel formats.

Important APIs/types: parallel flags describe master/slave mode, sync polarities, pixel clock edge, data polarity, field polarity, sync-on-green, and data-enable polarity. CSI-2 flags include non-continuous clock and max data lanes. `enum v4l2_mbus_csi2_cphy_line_orders_type` describes C-PHY lane wire ordering. Bus config structs cover CSI-2 lanes/polarities/line order, parallel bus width/shift, and CSI-1/CCP2 clock/strobe/lane polarity. `enum v4l2_mbus_type` enumerates unknown, parallel, BT.656, CSI-1, CCP2, CSI-2 D-PHY, CSI-2 C-PHY, DPI, and invalid. `struct v4l2_mbus_config` pairs type, link frequency, and a bus-specific union.

Control flow: subdevices report bus configuration through pad operations; bridge drivers interpret exactly one value from each mutually exclusive flag group. Format helpers copy width/height/field/colorspace/ycbcr/quantization/xfer fields between `v4l2_mbus_framefmt` and single- or multi-plane pixel formats, adding a media-bus code when converting to mbus.

State and persistence: all structures are caller-owned configuration snapshots. Inline conversion helpers mutate only the destination format struct.

Dependencies and integration: includes UAPI `linux/v4l2-mediabus.h` and bitops. It is consumed by `v4l2-fwnode.h`, subdevice pad operations, sensor/receiver bridge drivers, and format negotiation paths.

Risks: flags can encode conflicting states because mutually exclusive choices are separate bits; TODO notes a future field-based replacement. Drivers must validate one-and-only-one choice per group. Lane arrays must honor `num_data_lanes` and the maximum of 8. Format helpers intentionally do not fill stride, image size, plane layout, or pixel format, so drivers must complete those fields.

Test signals: validate conflicting flag rejection in drivers, parse/report every bus type, CSI-2 lane and polarity mapping, C-PHY line order handling, link frequency propagation, and format conversion preserving colorimetry fields while drivers fill missing pixel-layout fields.
