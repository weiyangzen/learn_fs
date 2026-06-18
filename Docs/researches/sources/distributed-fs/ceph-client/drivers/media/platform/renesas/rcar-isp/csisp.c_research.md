# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-isp/csisp.c

## Purpose
`csisp.c` implements the Renesas R-Car ISP Channel Selector as a V4L2 subdevice. The comments state the hardware can do more ISP work, but this driver only selects/filter-routes CSI-2 data types and virtual channels between a CSI-2 receiver and up to eight downstream VIN outputs.

## Important APIs, Types, And Functions
`struct rcar_isp` stores device resources, reset control, selected CSI input, `v4l2_subdev`, nine media pads, async notifier, remote source, and stream count. `struct rcar_isp_format` maps media bus codes to MIPI CSI-2 datatype and ISP processing mode. Important functions are `risp_probe()`, `risp_parse_dt()`, `risp_notify_bound()`, `risp_start()`, `risp_stop()`, `risp_enable_streams()`, `risp_disable_streams()`, and `risp_set_pad_format()`.

## Control Flow
Probe maps the channel selector register block, gets reset control, enables runtime PM, parses one of two possible sink endpoints, initializes a subdevice named `rcar-isp <dev>`, creates one sink pad plus eight source pads, finalizes subdev state, and registers it asynchronously. Binding creates an immutable enabled link from the upstream source pad to ISP sink pad 0.

Streaming starts on the first enabled source stream. `risp_start()` validates the sink pad format, resumes runtime PM, deasserts reset, selects CSI input 0 or 1, configures filter channels 4-7 so each virtual channel accepts the chosen datatype, writes the processing mode for all four VCs for that datatype, starts the ISP, then enables upstream streams. `risp_stop()` disables upstream streams, writes stop, asserts reset, and drops runtime PM. Pad format setting validates against the static table and propagates the sink format to all source pads.

## State And Persistence
Runtime state is the selected input endpoint, remote subdevice pointer/pad, active media bus format in subdev state, and `stream_count`. Register state is re-created on each stream start. There is no persistent storage. Reset and runtime PM define the hardware lifetime.

## Dependencies And Integration Points
The driver depends on platform MMIO, reset control, runtime PM, media controller, V4L2 subdev streams, async notifier/fwnode graph APIs, and MIPI CSI-2 datatype definitions. It integrates upstream with `rcar-csi2.c` on Gen4 ISP paths and downstream with `rcar-vin` in `use_isp` configurations, where VIN creates immutable links from ISP source pads to VIN nodes.

## Risks
Only one stream mask (`BIT_ULL(0)`) is accepted even though eight source pads exist, so callers must use the expected single-stream model. The format table encodes processing modes as hardware constants; incorrect datatype/procmode mapping can break capture. `stream_count` lacks explicit underflow protection. Endpoint parsing accepts the first existing endpoint among IDs 0 and 1, so DT mistakes can select the wrong CSI input. Advanced ISP functions are intentionally unsupported.

## Test Signals
Validate probe for old and generic compatibles, endpoint ID 0/1 selection, subdev node registration, immutable upstream link creation, format propagation to all pads, stream count behavior when multiple VIN links are active, correct CSI datatype filtering for RGB/YUV/RAW8/RAW10/RAW12, runtime PM/reset sequencing, and error paths when no remote or unsupported format is configured.
