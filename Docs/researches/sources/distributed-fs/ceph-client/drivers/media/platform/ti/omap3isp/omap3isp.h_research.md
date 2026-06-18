# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/omap3isp.h

## Purpose
Defines board/firmware-facing bus configuration structures for the OMAP3 ISP input interfaces: parallel, CCP2/CSI1, and CSI2.

## Important APIs, Types, and Functions
Important declarations are `enum isp_interface_type`, `struct isp_parallel_cfg`, lane/mode constants, `struct isp_csiphy_lane`, `struct isp_csiphy_lanes_cfg`, `struct isp_ccp2_cfg`, `struct isp_csi2_cfg`, and `struct isp_bus_cfg`. There are no functions.

## Control Flow
No control flow is present. The ISP driver consumes `struct isp_bus_cfg` to determine interface type and interpret the matching union member.

## State and Persistence
Instances of these structures describe static platform/firmware configuration such as lane positions, polarities, data-lane shift, clock/sync polarities, BT.656 mode, CRC enable, and VP clock configuration. The header itself has no state.

## Dependencies and Integration Points
This header is included by ISP platform or sensor-connection code. It bridges board descriptions to the ISP receiver modules, especially parallel, CCP2, and CSI2 PHY setup.

## Risks and Edge Cases
Bitfield widths encode hardware-limited values; callers must validate lane positions, lane counts, and interface enum/union consistency. The comment notes the named union is retained for older GCC initializer compatibility.

## Test Signals
Build platform data/users, verify device-tree or board conversion populates the right interface type, test parallel polarity and lane-shift variants, and validate CSI/CCP2 lane mapping with sensors on each supported PHY.
