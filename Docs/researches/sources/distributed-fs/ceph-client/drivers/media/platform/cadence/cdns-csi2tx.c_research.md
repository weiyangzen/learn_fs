# sources/distributed-fs/ceph-client/drivers/media/platform/cadence/cdns-csi2tx.c

## Purpose
This driver registers the Cadence MIPI CSI-2 TX controller as a V4L2 bridge subdevice. It accepts up to four input stream pads, configures CSI-2 data type/line format registers, and transmits over a CSI-2 D-PHY source pad.

## Important APIs, Types, and Functions
`struct csi2tx_priv` stores MMIO, clocks, variant D-PHY operations, media pads, active pad formats, lane capabilities, stream count, and stream reference count. `struct csi2tx_vops` selects v1.3 or v2.1 D-PHY setup. Key functions are `csi2tx_get_resources()`, `csi2tx_check_lanes()`, `csi2tx_dphy_setup()`, `csi2tx_v2_dphy_setup()`, `csi2tx_start()`, `csi2tx_stop()`, `csi2tx_s_stream()`, and pad format handlers.

## Control Flow
Probe maps registers, obtains `p_clk`, `esc_clk`, per-stream pixel clocks, reads capability registers, selects variant ops from OF compatible, initializes a source pad plus four sink stream pads, seeds sink pad formats with 1280x720 RGB888, and registers the async subdev. Pad operations enumerate only UYVY8 and RGB888 formats and reject format get/set on the multiplexed source pad. The first stream-on resets the block, enters configuration mode, initializes the internal D-PHY if variant ops exist, walks enabled sink links, programs each active stream's CSI-2 data type, bytes per line, max line number, and stream fill level, then exits configuration mode. The last stream-off asserts config and reset bits.

## State and Persistence
Runtime state is volatile. `count` reference-counts hardware start/stop across users. `pad_fmts[]` stores active sink-pad formats. Lane configuration comes from the local endpoint and is kept in `lanes[]`/`num_lanes`.

## Dependencies and Integration Points
The driver depends on V4L2 subdev/media entity APIs, OF graph/fwnode endpoint parsing, MIPI CSI-2 data type definitions, platform clocks, and OF compatibles `cdns,csi2tx`, `cdns,csi2tx-1.3`, and `cdns,csi2tx-2.1`.

## Risks and Edge Cases
The source pad is multiplexed and has no exposed format, limiting userspace visibility into mixed-stream output. Only two media-bus formats are supported. Stream data type mapping is static and comments note stream ID is not a correct general data-type selector. Pixel and escape clocks are acquired but not explicitly enabled in the visible start path, so clocking assumptions depend on integration. `count` can underflow if disable is unbalanced. The probe error path after `media_entity_pads_init()` does not explicitly clean the entity before freeing private data.

## Test Signals
Build and probe each compatible variant, validate endpoint lane rejection, inspect D-PHY register programming for v1.3 and v2.1, create enabled media links on each sink pad, stream with UYVY and RGB888 formats, verify DT/line-format registers, and test balanced/unbalanced stream enable/disable paths.
