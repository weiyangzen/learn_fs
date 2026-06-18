<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_hdmi_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_hdmi_i2c.c

## Purpose

`sun4i_hdmi_i2c.c` exposes the HDMI controller's DDC engine as a Linux I2C adapter so EDID can be read when no external DDC bus is supplied. It hides SoC register-layout differences behind regmap fields supplied by the HDMI variant.

## Important APIs, Types, And Functions

The exported function is `sun4i_hdmi_i2c_create()`. Internal flow is split across `sun4i_hdmi_init_regmap_fields()`, `sun4i_hdmi_i2c_xfer()`, `xfer_msg()`, and `fifo_transfer()`. The `sun4i_hdmi_i2c_algorithm` advertises `master_xfer` and `I2C_FUNC_I2C | I2C_FUNC_SMBUS_EMUL`.

## Control Flow

Creation first calls `sun4i_ddc_create()` to derive `hdmi->ddc_clk`, allocates regmap fields for enable/start/reset/address/status/FIFO/byte-count/command/SDA/SCK controls, allocates an adapter, binds `hdmi` as adapter data, and registers it. Each transfer validates all messages, enables and fixes the DDC clock at 100 kHz, resets the controller, enables SDA/SCK, then processes each message. `xfer_msg()` selects FIFO direction when required, clears address and FIFO state, programs address, thresholds, byte count, and implicit read/write command, clears interrupts, starts transfer, streams FIFO chunks, waits for start to clear, and checks transfer-complete/error bits.

## State And Persistence Behavior

The adapter persists in `hdmi->i2c`; regmap fields are devm-managed. Runtime state is transient per transfer, but hardware FIFO, DDC control, interrupt-status, and line-enable registers are rewritten on each message. The DDC clock is enabled only around transfer windows.

## Dependencies And Integration Points

It depends on `struct sun4i_hdmi` variant field descriptors from `sun4i_hdmi_enc.c`, the common clock framework, I2C core, MMIO FIFO helpers, and regmap field polling. The HDMI connector uses this adapter through `drm_edid_read_ddc()`.

## Risks And Test Signals

Risks include timeout/error handling around FIFO request and transfer-complete bits, off-by-one FIFO threshold semantics across variants, rejecting zero-length or too-large messages, and assuming 100 kHz byte timing for polling delays. Test with EDID reads on sun4i/sun5i/sun6i variants, multi-message DDC transactions, injected NACK/arbitration/bus errors, FIFO boundary sizes, and cleanup via `i2c_del_adapter()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_hdmi_i2c.c -->
