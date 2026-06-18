# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_ddc.c

## Purpose
Implements the original MediaTek HDMI DDC controller as a Linux I2C adapter for EDID and HDMI sink transactions.

## Important APIs, types, and functions
- `struct mtk_hdmi_ddc` stores the I2C adapter, DDC clock, and MMIO base.
- `mtk_hdmi_ddc_xfer()` is the adapter transfer implementation.
- `mtk_hdmi_ddc_read_msg()` and `mtk_hdmi_ddc_write_msg()` perform hardware start/address/data/read/write sequences.
- `ddcm_trigger_mode()` selects a DDCM mode, triggers it, and polls completion.
- Probe registers the adapter named `mediatek-hdmi-ddc`.

## Control flow
Probe obtains the `ddc-i2c` clock and MMIO resource, enables the clock for adapter lifetime, initializes adapter metadata, and calls `i2c_add_adapter()`. Each transfer enables clock stretching and state-machine mode, rejects a busy trigger bit, writes the fixed clock divider, then executes each I2C message. Writes emit START, address byte, one payload byte, expect ACK mask `0x03`, and stop. Reads emit START, address-read byte, then read in chunks of up to 8 bytes with ACK on intermediate chunks and NACK on the final chunk, copying hardware data registers back into the caller buffer. All paths send STOP on completion or error.

## State and persistence
The adapter and enabled DDC clock persist while the platform device exists. Hardware state persists in DDCM control/data registers during a transaction. No runtime PM is used; the clock is prepared at probe and disabled at remove.

## Dependencies and integration points
Depends on Linux I2C core, platform MMIO/clock APIs, polling helpers, and the HDMI bridge's DT `ddc-i2c-bus` phandle lookup in common HDMI code. It advertises `I2C_FUNC_I2C | I2C_FUNC_SMBUS_EMUL`.

## Risks
Write support only sends address plus `msg->buf[0]`, so it is tailored to EDID offset writes rather than arbitrary long writes. Poll return from `ddcm_trigger_mode()` is ignored, which can hide timeout details. ACK bit interpretation is hardware-specific and transaction failures may appear as `-ENXIO`, `-EIO`, or `-EBUSY`. The clock is always on after probe.

## Test signals
Signals include `i2c ack err`, `ddc line is busy`, `Address NACK`, EDID reads through `drm_edid_read_ddc()`, adapter registration/removal, and repeated hotplug EDID access under marginal cable/sink conditions.
