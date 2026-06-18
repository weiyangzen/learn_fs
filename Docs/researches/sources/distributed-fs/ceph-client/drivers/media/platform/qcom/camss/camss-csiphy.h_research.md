
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csiphy.h

## Purpose
Defines the private CSIPHY contract shared by common CSIPHY code, SoC resource tables, and hardware-version implementations.

## Important APIs, Types, and Functions
Pad constants define one sink and one source pad. `struct csiphy_lane`, `csiphy_lanes_cfg`, `csiphy_csi2_cfg`, and `csiphy_config` carry CSI-2 lane and target CSID configuration. `struct csiphy_format_info` and `csiphy_formats` describe accepted media-bus codes and bpp. `struct csiphy_hw_ops` is the version-specific vtable for lane mask, HW version, reset, lane enable/disable, ISR, and init. `struct csiphy_device` stores CAMSS ownership, subdev/media pads, MMIO, IRQ, clocks, regulators, formats, resource pointer, and hardware register metadata.

## Control Flow
The header shapes initialization by letting resource tables provide `csiphy_subdev_resources` with an id, ops, and format list. Common code initializes `csiphy_device`, calls `hw_ops->init()`, then dispatches power and stream transitions through the vtable.

## State and Persistence
All state is in `struct csiphy_device` and related config structs. Hardware register metadata is held in `struct csiphy_device_regs`; no on-disk persistence exists.

## Dependencies and Integration Points
Depends on Linux clk/interrupt/media/V4L2 headers and forward declarations from CAMSS. It exposes `msm_csiphy_subdev_init/register/unregister` to the top-level CAMSS driver and extern declarations for available format sets and `csiphy_ops_2ph_1_0`/`csiphy_ops_3ph_1_0`.

## Risks and Test Signals
This header is a cross-file ABI; field ordering and enum values affect all CSIPHY implementations. Tests are compile-time coverage of all SoC resource tables plus runtime validation that lane config, formats, IRQ, clocks, and subdev pads line up with the media graph.
