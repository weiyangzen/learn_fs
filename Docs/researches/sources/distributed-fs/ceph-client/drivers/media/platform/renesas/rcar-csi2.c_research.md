# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-csi2.c

## Purpose
`rcar-csi2.c` is the Renesas R-Car MIPI CSI-2 receiver V4L2 subdevice driver. It receives one CSI-2 input from an upstream sensor/bridge, configures SoC-specific D-PHY or C-PHY hardware, and exposes one or more source pads to downstream VIN or ISP blocks. Gen3 variants generally route virtual channels directly to VIN output channels, while newer ISP-oriented variants expose one source pad and leave per-channel fanout to the ISP/VIN graph.

## Important APIs, Types, And Functions
The central state object is `struct rcar_csi2`, holding device resources, `v4l2_subdev`, pads, async notifier, remote subdevice, lane configuration, C-PHY line order, virtual-channel routing, and `stream_count`. `struct rcar_csi2_info` is the SoC capability table: register layout, PHTW initialization hook, post-PHY hook, receiver-start hook, standby hook, hsfreq tables, number of channels, `use_isp`, and D-PHY/C-PHY support flags. `struct rcar_csi2_format` maps media bus codes to MIPI CSI-2 data types and bits per pixel.

Key entry points are `rcsi2_probe()`, `rcsi2_remove()`, `rcsi2_enable_streams()`, `rcsi2_disable_streams()`, `rcsi2_set_pad_format()`, `rcsi2_irq()`, and `rcsi2_irq_thread()`. Hardware helpers include `rcsi2_start_receiver_gen3()`, `rcsi2_start_receiver_v4h()`, `rcsi2_start_receiver_v4m()`, PHTW writers, `rcsi2_calc_mbps()`, `rcsi2_get_active_lanes()`, and PHY wait/calibration routines.

## Control Flow
Probe allocates private state, selects the matching `rcar_csi2_info` from DT and optionally an H3 ES2 soc revision override, maps registers, requests a threaded IRQ, gets reset control, parses endpoint/lane properties, registers an async notifier for the upstream source, initializes media pads, enables runtime PM, finalizes state, and registers the subdevice. Async bound handling finds the upstream source pad and creates an immutable enabled link into CSI-2 sink pad 0.

Streaming starts through pad `.enable_streams`. The first stream increments from zero via `rcsi2_start()`: runtime PM resumes, reset deasserts, the SoC-specific receiver routine configures VCDT/field detection/lane swap/PHY PLL/PHTW/PHY mode, waits for stop state or calibration, then enables upstream streaming. Stop asserts reset, enters standby, and disables upstream streaming. `stream_count` lets multiple downstream source pads share one physical receiver. Link setup for VIN mode maps enabled source pad links to `channel_vc[]`, enforcing one downstream route per VC.

## State And Persistence
Persistent runtime state is in memory only: active remote pointer/pad, lane count and swaps from fwnode, C-PHY mode/line order, virtual-channel to output-channel mapping, and stream count. Hardware state lives in MMIO registers and is reprogrammed on every stream start or IRQ restart. Runtime PM and reset control gate register access and PHY state. No filesystem or NVRAM state exists.

## Dependencies And Integration Points
The driver depends on V4L2 subdev state, media controller links, V4L2 fwnode endpoint parsing, MIPI CSI-2 data type definitions, runtime PM, reset controller, IRQ handling, and SoC match data. It integrates upstream with sensors/bridges that provide link frequency or pixel-rate metadata and downstream with R-Car VIN or R-Car ISP. Correct DT endpoint bus type, lane count, data-lanes order, and optional C-PHY line orders are critical.

## Risks
The PHY setup contains many SoC-specific magic values and timing tables; wrong match data, link frequency, or lane count can fail calibration or silently corrupt capture. `stream_count` has no explicit underflow guard beyond caller correctness. The threaded IRQ restarts receiver on transfer errors while streams are active, so restart ordering and active-state locking are important. Routing depends on downstream video devices carrying valid `renesas,id`. Gen4 C-PHY/D-PHY register sequences are particularly hardware-sensitive.

## Test Signals
Useful validation signals include successful subdevice registration, media graph links, `dev_info` lane count, link-frequency negotiation, stream start/stop on all supported SoCs, virtual-channel routing to VIN nodes, ISP path operation for `use_isp` variants, IRQ error restart behavior, and timeout/error logs from PHTW, LP-11, PHY calibration, or unsupported PHY speed paths.
