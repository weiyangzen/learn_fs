# sources/distributed-fs/ceph-client/drivers/media/platform/cadence/cdns-csi2rx.c

## Purpose
This driver registers the Cadence MIPI CSI-2 RX controller as a V4L2 media bridge subdevice. It receives CSI-2 data from a remote source, configures lane mapping and stream output interfaces, optionally configures an external D-PHY, counts protocol/error IRQs, and forwards streaming to the upstream sensor or bridge.

## Important APIs, Types, and Functions
`struct csi2rx_priv` stores clocks, resets, MMIO, optional D-PHY, lane/stream capabilities, pixel-per-clock settings, error counters, media pads, source subdevice, and a stream reference count. Important functions are `csi2rx_get_resources()`, `csi2rx_parse_dt()`, `csi2rx_configure_ext_dphy()`, `csi2rx_start()`, `csi2rx_stop()`, `csi2rx_s_stream()`, `csi2rx_set_fmt()`, `cdns_csi2rx_negotiate_ppc()`, `csi2rx_irq_handler()`, and async bind/probe/remove helpers.

## Control Flow
Probe maps registers, obtains `sys_clk`, `p_clk`, per-stream pixel clocks, optional resets, optional external D-PHY, reads device capability registers, parses CSI-2 endpoint lane mapping, sets up the async notifier, initializes a five-pad bridge subdev, optionally requests `error_irq`, finalizes subdev state, and registers the subdev. Stream-on is reference-counted. The first user enables the P clock, resets the controller and streams, configures error IRQ masks, writes static lane mapping, enables D-PHY lanes and external D-PHY timing, enables each stream pixel clock/reset, configures FIFO mode and pixels-per-clock, maps VC0 to each stream, enables system clock/reset, then calls upstream `s_stream(true)`. Stream-off by the last user stops streams, polls readiness, asserts resets, disables clocks, calls upstream `s_stream(false)`, and powers off D-PHY.

## State and Persistence
Runtime state is volatile. `count` protects shared hardware enablement across multiple source pads. `events[]` accumulates error IRQ counts until driver removal and is reported by `.log_status`. Active subdev formats live in V4L2 subdev state; `num_pixels[]` stores negotiated stream PPC register encodings.

## Dependencies and Integration Points
The driver uses V4L2 subdev/media entity APIs, V4L2 async notifier, fwnode endpoint parsing, media links, clocks, resets, generic PHY MIPI D-PHY helpers, and exported `cdns_csi2rx_negotiate_ppc()` for downstream users such as `j721e-csi2rx`.

## Risks and Edge Cases
Internal D-PHY is explicitly unsupported. The lane mapping fallback loop computes an unused physical lane but writes `i + 1`, so lane-map assumptions should be checked carefully when changing this area. All streams are enabled together and statically select VC0, limiting multi-VC flexibility. `csi2rx_s_stream(false)` decrements `count` without underflow protection. External D-PHY link frequency depends on upstream pad link-frequency data. Optional error IRQ absence removes hardware error visibility.

## Test Signals
Test DT parsing for invalid bus type, lane counts, and lane IDs; probe with external D-PHY and no/internal D-PHY cases; stream through linked sensors; inspect stream clocks/resets; call `.log_status` after CRC/ECC/FIFO errors; validate PPC negotiation; and run media graph link validation with all source pads.
