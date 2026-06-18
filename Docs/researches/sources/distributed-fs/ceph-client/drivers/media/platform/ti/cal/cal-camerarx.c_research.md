# sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal-camerarx.c

## Purpose
Implements the CameraRx CSI-2 receiver/PHY subdevice for the TI CAL driver. It parses CSI-2 endpoint wiring, configures lane mapping, D-PHY timings, power/reset/interrupt state, forwards streaming to the upstream sensor, exposes sink/source V4L2 subdev pads, and passes frame descriptors for routed CSI-2 streams.

## Important APIs, Types, And Functions
The file operates on `struct cal_camerarx` and the parent `struct cal_dev` from `cal.h`. Register accessors are `camerarx_read()` and `camerarx_write()`. Hardware management helpers include `cal_camerarx_get_ext_link_freq()`, `cal_camerarx_lane_config()`, `cal_camerarx_enable()`, `cal_camerarx_disable()`, `cal_camerarx_config()`, `cal_camerarx_power()`, `cal_camerarx_wait_reset()`, `cal_camerarx_wait_stop_state()`, IRQ enable/disable helpers, PPI enable/disable helpers, `cal_camerarx_start()`, and `cal_camerarx_stop()`. Exported integration functions include `cal_camerarx_i913_errata()`, `cal_camerarx_get_phy_from_entity()`, `cal_camerarx_create()`, and `cal_camerarx_destroy()`.

V4L2 pad ops implement stream enable/disable, media-bus code and frame-size enumeration, format get/set, routing set/init, and frame descriptor retrieval.

## Control Flow
Creation allocates a CameraRx instance, maps the per-instance MMIO resource, initializes syscon regmap fields, parses the OF graph endpoint for CSI-2 lane data and remote source nodes, initializes a stream-capable V4L2 subdev with one sink and multiple source pads, finalizes state, and registers it with the parent V4L2 device.

Stream enable resolves the routed sink stream, then `cal_camerarx_start()` handles first-stream hardware initialization. It gets external link frequency from the source, powers the source, enables CAL CSI-2 error interrupts, configures lane positions/polarities, enables CAMERARX clocks/lanes, deasserts complex I/O reset, writes D-PHY timing registers, programs stop-state timing, forces RX mode, powers the PHY, starts the source stream, waits for reset completion and stop state, then enables the PPI. Additional enabled streams only propagate enable to the source and increment `enable_count`.

Stream disable decrements `enable_count`; if other streams remain, only the corresponding source stream is disabled. For the last stream, it disables PPI and interrupts, powers down complex I/O, asserts reset, disables CAMERARX, disables the source stream, and powers the source off.

## State And Persistence
State includes endpoint lane configuration, source endpoint/node pointers, source subdev/pad, active routing/format state in V4L2 subdev state, register field handles, MMIO base/resource, virtual-channel lock, and `enable_count`. Hardware state includes CAL complex I/O lane config, D-PHY timing/power/reset, CSI-2 PPI, and IRQ masks. No persistent storage is used.

## Dependencies And Integration Points
Depends on parent CAL core register helpers and data tables, syscon regmap fields, platform resources named `cal_rx_core0`/`cal_rx_core1`, OF graph and V4L2 fwnode endpoint parsing, V4L2 subdev streams/routing APIs, media entity validation, upstream source subdevices that provide link frequency and optional frame descriptors, and CAL format tables.

## Risks
Multistream link-frequency fallback deliberately rejects pixel-rate-only sources by passing zero bpp, so sources need `V4L2_CID_LINK_FREQ` for multistream. `enable_count` protects first/last hardware transitions but must stay balanced with all stream enable/disable paths. Endpoint parsing assumes at least one valid data lane before formatting the `data_lanes` debug string. Hardware waits log timeout errors but do not always abort after timeout. The frame descriptor path requires the upstream descriptor to be CSI-2 and contain the routed stream.

## Test Signals
Validate media graph creation, subdev routing, stream enable/disable on single and multiple streams, lane polarity/position programming from DT, link-frequency handling, D-PHY timing values across frequencies, error IRQ reporting, stop-state/reset wait logs, frame descriptor propagation, i913 errata application on affected SoCs, and `v4l2-compliance` for stream-aware subdev operations.
