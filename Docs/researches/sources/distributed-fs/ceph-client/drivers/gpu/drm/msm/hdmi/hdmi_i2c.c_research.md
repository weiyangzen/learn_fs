# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_i2c.c

## Purpose
Implements the HDMI DDC I2C adapter used for EDID and HDCP DDC transactions through MSM HDMI controller registers.

## Important APIs, types, and functions
- `struct hdmi_i2c_adapter` wraps `struct i2c_adapter`, an HDMI pointer, SW_DONE latch, and waitqueue.
- `msm_hdmi_i2c_init()` creates/registers the adapter; `msm_hdmi_i2c_destroy()` unregisters and frees it.
- `msm_hdmi_i2c_xfer()` programs up to four hardware transactions and waits for SW_DONE.
- `msm_hdmi_i2c_irq()` wakes blocked transfers when the DDC interrupt says software transfer is done.
- `init_ddc()`, `ddc_clear_irq()`, and `sw_done()` initialize and service controller status.

## Control flow
Transfers are capped at `MAX_TRANSACTIONS`. The driver resumes HDMI runtime PM, soft-resets DDC state, clears stale interrupts, writes address/data bytes into `REG_HDMI_DDC_DATA`, programs each `REG_HDMI_I2C_TRANSACTION(i)` with count, direction, start, and final stop bits, triggers `HDMI_DDC_CTRL_GO`, and waits up to `HZ/4` for `ddc_event`. It then checks NACK bits per transaction and reads back data for read messages by programming the DDC data index and discarding the first returned byte.

## State and persistence
Runtime state is the adapter object and `sw_done` latch. Hardware DDC speed, timeout, reference timer, transaction registers, data FIFO/index, SW status, HW status, and interrupt control registers are reinitialized for each transfer. No EDID cache is stored here.

## Dependencies and integration points
Depends on Linux I2C core, runtime PM, HDMI register definitions, and HDMI IRQ dispatch. HDCP code uses this adapter through normal `i2c_transfer()`, and DRM connector probing uses it for EDID.

## Risks
Only four I2C messages are supported per transfer; callers with longer compound transfers are truncated by `min()`. Timeout and NACK handling returns the number of completed messages for partial success, so callers must interpret I2C semantics correctly. The code warns if HDMI CTRL is not enabled but still proceeds. DDC FIFO indexing is sensitive to off-by-one behavior.

## Test signals
Signals include DDC timeout warnings with SW/HW/int status, EDID read success, HDCP DDC reads/writes, NACK handling, interrupt wakeups, runtime PM balance, and behavior when HDMI is disabled.
