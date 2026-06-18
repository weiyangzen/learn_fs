# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_ddc_v2.c

## Purpose
Implements the HDMI v2 DDC controller as a Linux I2C adapter backed by the parent HDMI register map. It supports EDID/SCDC-style offset writes followed by reads, FIFO-based data movement, bus recovery, and HDCP polling disablement around foreground DDC transfers.

## Important APIs, types, and functions
- `struct mtk_hdmi_ddc` stores device, parent regmap, clock, and I2C adapter.
- `mtk_hdmi_ddc_v2_xfer()` implements adapter transfers and carries the last offset write into following reads.
- `mtk_ddcm_read_hdmi()` and `mtk_ddcm_write_hdmi()` program the DDC command engine.
- `mtk_ddc_check_and_rise_low_bus()` detects low bus/no-ACK and clocks SCL to recover.
- Probe registers the devm-managed adapter named `mediatek-hdmi-ddc-v2`.

## Control flow
Probe obtains the parent HDMI regmap, enables the unnamed DDC clock, enables runtime PM, takes a runtime reference, and registers the I2C adapter. Transfers validate message buffers. Writes pass `buf[0]` as the DDC offset and remaining bytes as payload; one-byte writes to EDID or SCDC slave addresses update the saved offset. Reads use that saved offset because the hardware emits the offset write internally as part of the read command.

Read flow clears FIFO, chooses 16-byte chunks, selects EDID-slower or normal delay counts, handles segment-address flow control for `0x51..0x53`, emits sequential/enhanced read commands, polls `DDC_I2C_IN_PROG`, checks no-ACK/low-bus status, then drains each byte through `SI2C_CTRL` read/confirm cycles. Write flow fills a 16-byte FIFO when payload exists, emits a sequential write command, polls completion, and rechecks bus status.

## State and persistence
Adapter and clock state persist for device lifetime. Runtime PM is enabled and a reference is taken at probe. Transfer-local state includes the saved offset in `mtk_hdmi_ddc_v2_xfer()`. Hardware state includes DDC delay count, FIFO contents, HDCP poll-disable bit, command status, and SCDC segment field.

## Dependencies and integration points
Depends on the parent HDMI v2 regmap, HDMI v2 register definitions, Linux I2C/PM runtime/clock APIs, DRM EDID constants, and SCDC I2C address behavior. The HDMI common probe later obtains this adapter through the connector's `ddc-i2c-bus`.

## Risks
The offset variable is local to one `master_xfer()` call, so clients must use normal combined write-then-read messages. A write with `msg->len == 0` would underflow `msg->len - 1` before lower-level validation. Debug reads in no-ACK handling are currently unused. Probe takes a runtime PM reference without an obvious paired put, intentionally or not keeping the block active.

## Test signals
Signals include EDID reads, SCDC reads/writes for scrambling, no-ACK errors, DDC I2C timeout logs, invalid read count warnings, FIFO chunk boundaries above 16 bytes, segment reads, and behavior across HDMI controller reset during EDID reads.
