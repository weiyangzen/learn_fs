# sources/distributed-fs/ceph-client/drivers/media/i2c/lt6911uxe.c

## Purpose
`lt6911uxe.c` is a V4L2 subdevice driver for the Lontium LT6911UXE HDMI-to-MIPI CSI-2 bridge. It detects HDMI timing changes through an HPD IRQ, exposes DV timing and pad-format operations, controls CSI-2 TX streaming, and reports a pixel-rate control derived from the detected mode.

## Important APIs, Types, And Functions
`struct lt6911uxe` holds the subdev, source pad, control handler, pixel-rate control, current DV timings, current mode, CCI/regmap, reset GPIO, and HPD IRQ GPIO. Important functions include `get_pixel_rate()`, `lt6911uxe_get_detected_timings()`, `lt6911uxe_s_dv_timings()`, `lt6911uxe_g_dv_timings()`, `lt6911uxe_query_dv_timings()`, `lt6911uxe_status_update()`, `lt6911uxe_init_controls()`, `lt6911uxe_enable_streams()`, `lt6911uxe_disable_streams()`, `lt6911uxe_set_format()`, `lt6911uxe_get_mbus_config()`, `lt6911uxe_fwnode_parse()`, `lt6911uxe_identify_module()`, `lt6911uxe_threaded_irq_fn()`, probe, and remove.

## Control Flow
Probe creates a paged CCI regmap, initializes the subdev, obtains reset and HPD GPIOs, requires exactly four CSI-2 data lanes from firmware, identifies the chip by temporarily enabling I2C access, creates the pixel-rate control, initializes the source pad/media entity, enables runtime PM, finalizes the subdev state, requests a threaded HPD IRQ on both edges, and registers as a sensor subdev. The IRQ handler reads event/status registers; on video-ready it validates clocks, totals, active size, max 60 fps, and YUV422 8-bit MIPI format, then updates `cur_mode`, raises a source-change event, and refreshes the active pad format. Video-disappear disables MIPI TX and clears mode dimensions. Stream enable resumes runtime PM and writes `REG_MIPI_TX_CTRL = 1`; disable writes zero and drops runtime PM.

## State And Persistence
`cur_mode`, `timings`, and the pixel-rate control are cached in memory and updated from hardware interrupts or pad operations. No nonvolatile state exists. Runtime PM state controls whether the device is active for streaming. Active subdev state locks protect timing/format access.

## Dependencies And Integration Points
The driver uses ACPI matching (`INTC10C5`), GPIO descriptors, IRQs, runtime PM, V4L2 CCI register helpers, V4L2 DV timings, source-change events, fwnode CSI-2 parsing, media entity pads, and async sensor subdev registration.

## Risks
`get_pixel_rate()` divides by lane count and assumes firmware parsing has already populated lanes; early control initialization depends on that ordering. The driver only supports four lanes and YUV422 8-bit, rejecting other valid hardware possibilities. IRQ status updates can fail on transient invalid clocks/totals and leave stale cached timings. Remove must match the IRQ dev_id and runtime PM cleanup sequence. EDID is intentionally unsupported because the chip requires flash updates.

## Test Signals
Tests should cover missing GPIOs/endpoints, non-four-lane firmware rejection, chip-ID mismatch, IRQ ready/disappear/default events, invalid timing register values, pixel-rate range updates after format changes, stream enable/disable runtime PM balancing, source-change event delivery, and DV timing validation against the 4Kp30 cap.
