# sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/dw-mipi-csi2rx.c

## Purpose
Implements a V4L2 media-controller sub-device bridge for the Synopsys DesignWare MIPI CSI-2 receiver. It terminates a CSI-2 D-PHY input from a remote sensor/bridge, configures the receiver and PHY, exposes sink/source pads, and forwards stream enable/disable calls to the upstream sub-device. It supports at least Rockchip RK3568 and NXP i.MX93 through per-SoC register maps and optional callback hooks.

## Important APIs, Types, And Functions
Core state is held in `struct dw_mipi_csi2rx_device`, with MMIO base, clocks, PHY, optional reset, pad/notifier/subdev objects, bus type, lane count, and `drvdata`. `struct dw_mipi_csi2rx_drvdata` supplies register layout plus optional D-PHY reset and IPI enable callbacks. `struct dw_mipi_csi2rx_format` maps media-bus codes to bit depth and CSI-2 data type.

Register helpers `dw_mipi_csi2rx_has_reg()`, `dw_mipi_csi2rx_read()`, and `dw_mipi_csi2rx_write()` mask SoC differences. V4L2 pad ops include `enum_mbus_code`, `set_fmt`, `set_routing`, `get_frame_desc`, `enable_streams`, and `disable_streams`. Platform lifecycle is `dw_mipi_csi2rx_probe()` / `dw_mipi_csi2rx_remove()` plus runtime PM callbacks.

## Control Flow
Probe allocates the device, maps registers, fetches match data, gets all clocks, gets the MIPI PHY and optional reset, enables runtime PM, initializes the PHY, and registers a V4L2 sub-device. Registration parses endpoint 0, records D-PHY/CPHY bus metadata, installs an async notifier for the remote source, initializes two pads, finalizes subdev state, and registers the async subdev.

Streaming starts in `dw_mipi_csi2rx_enable_streams()`: stream masks are translated from source to sink, runtime PM resumes clocks/resets, `dw_mipi_csi2rx_start()` validates lanes, derives link frequency from the remote pad, configures the PHY for D-PHY, writes receiver lane/control registers, powers on the PHY, deasserts receiver resets, optionally enables i.MX93 IPI, then asks the remote source to stream. Disable reverses the remote stream, powers off the PHY, resets receiver state, masks errors when present, and drops runtime PM.

## State And Persistence
Persistent driver state is in memory only. V4L2 active state stores routing and pad formats; runtime state tracks bus type and lane count parsed from firmware. Hardware state is register programming, PHY mode/configuration, clock/reset state, and runtime PM reference count. No filesystem state is written.

## Dependencies And Integration Points
The driver integrates with Linux platform bus, OF match data, clocks, resets, generic PHY, runtime PM, V4L2 async notifier, media entity graph, fwnode endpoint parsing, and MIPI CSI-2 helpers. It requires an upstream source exposing `V4L2_CID_LINK_FREQ` or compatible link-frequency calculation and a firmware graph connection on endpoint 0.

## Risks
CPHY is explicitly unsupported. i.MX93 IPI enable currently selects `csi2->formats->csi_dt`, the first supported format, rather than the negotiated active pad format, which is a functional risk for non-default formats. Stream enable assumes a remote pad exists and that the remote entity is a V4L2 subdev. Error cleanup around `phy_power_on()` failures does not unwind previously asserted receiver reset state beyond returning the error, relying on later stop/runtime behavior. Register existence checks prevent crashes on missing registers but can hide incomplete SoC data behind one-time errors.

## Test Signals
Useful signals are successful media graph creation, async link binding to the sensor, `v4l2-compliance` subdev routing/format tests, stream-on/off with a D-PHY sensor at multiple lane counts and media-bus codes, runtime PM suspend/resume cycles, and error-path tests for missing link frequency, unsupported CPHY endpoints, absent remote pads, and invalid lane counts.
