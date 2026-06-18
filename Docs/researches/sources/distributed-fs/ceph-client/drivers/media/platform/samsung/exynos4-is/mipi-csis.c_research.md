# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/mipi-csis.c

## Purpose
Implements the Samsung S5P/Exynos MIPI CSI-2 receiver subdevice, including D-PHY/control register programming, format negotiation, packet-buffer capture, interrupt/error counters, runtime PM, and DT probing.

## Important APIs, Types, and Functions
Important types are `struct csis_state`, `struct csis_pix_format`, `struct csis_drvdata`, and event/pktbuf structures. Key functions include `s5pcsis_parse_dt()`, `s5pcsis_start_stream()`, `s5pcsis_stop_stream()`, pad format callbacks, `s5pcsis_s_rx_buffer()`, `s5pcsis_irq_handler()`, PM resume/suspend helpers, `s5pcsis_probe()`, and `s5pcsis_remove()`.

## Control Flow
Probe parses DT lane and clock configuration, obtains PHY/regulators/clocks/MMIO/IRQ, initializes a two-pad subdev, sets a default format, and enables runtime PM. Stream-on clears counters, resumes PM, resets hardware, programs lane count, format, resolution, settle time, alignment, wrapper clock source, enables the D-PHY/system, and unmasks interrupts. IRQ handling copies non-image packet data into a caller-supplied buffer, updates event counters, and clears interrupt sources. PM suspend stops streaming, powers off PHY/regulators, disables the gate clock, and marks suspend state.

## State and Persistence
`struct csis_state` stores active media-bus format, selected hardware format, lane/clock/settle settings, flags for powered/streaming/suspended, packet buffer pointer/length, and event counters. Hardware state is volatile and reprogrammed on stream start or resume.

## Dependencies and Integration Points
Depends on V4L2 subdev/media pads, OF graph/fwnode endpoint parsing, PHY, regulators, runtime PM, clocks, platform IRQs, and Exynos media graph registration through `media-dev.c`.

## Risks and Edge Cases
`s5pcsis_s_stream()` calls runtime resume before taking the lock; if streaming is rejected due to `ST_SUSPENDED`, it exits without a matching runtime PM put. `s5pcsis_parse_dt()` uses the first graph endpoint and derives index from port number, so malformed DT ports can misidentify receiver instances. Packet-buffer copying happens in IRQ context into an external pointer that must remain valid until completion.

## Test Signals
Validate Exynos4/5 interrupt masks, 1/2/4 lane DTs, default and explicit clock rates, all supported media-bus formats, runtime PM balance on failed stream-on, non-image packet buffer delivery, event counters under CRC/ECC/overflow injection, and suspend/resume while streaming.
