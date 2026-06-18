# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-rzv2m.c

Purpose: Renesas RZ/V2M I2C master platform driver. It provides a synchronous completion-based I2C adapter with 7-bit and 10-bit addressing, standard/fast-mode timing setup, runtime PM, and shared reset deassertion.

Important APIs/types/functions: `struct rzv2m_i2c_priv` holds MMIO base, adapter, clock, selected bus mode, completion, and precomputed low/high width registers. `bitrate_configs` encodes low-period ratio and max data hold time for 100 kHz and 400 kHz. Main routines are `rzv2m_i2c_clock_calculate()`, `rzv2m_i2c_init()`, `rzv2m_i2c_write_with_ack()`, `rzv2m_i2c_read_with_ack()`, `rzv2m_i2c_send_address()`, `rzv2m_i2c_xfer_msg()`, `rzv2m_i2c_xfer()`, probe/remove, and suspend/resume.

Control flow: probe maps resources, gets clock/reset/IRQ, deasserts shared reset, registers the TIA interrupt completion handler, calculates timing, enables runtime PM, initializes hardware, and registers a numbered adapter. `rzv2m_i2c_xfer()` resumes runtime PM, rejects a busy bus via `IICB0SSBS`, then sends each message with START, address bytes, data send/receive, and STOP only on the last message. Writes wait for completion and require ACK. Reads manipulate `IICB0SLWT` and `IICB0SLAC` so the final byte receives NACK and a 9th-clock completion.

State and persistence: transfer state is minimal and stack-driven; completion `msg_tia_done` serializes byte progress. Timing values persist in `iicb0wl/iicb0wh` and are recalculated on resume. Runtime PM autosuspend is used after transfers. Reset is shared and only deasserted because it affects non-Linux hardware.

Dependencies/integration: I2C core, firmware timing parser, platform MMIO/IRQ, clk framework, runtime PM, reset controller, `readl_poll_timeout()`, and numbered adapter registration. Functionality excludes SMBus quick and advertises 10-bit address support.

Risks: only exact 100 kHz and 400 kHz firmware frequencies are accepted. Multi-message transfer issues START for each message and STOP only at the end, which may or may not match repeated-start expectations depending on hardware behavior. Timeout or non-NACK errors reinitialize the controller. Shared reset cannot be asserted for recovery. `rzv2m_i2c_disable()` resumes PM only to clear enable, so PM failures block removal/suspend cleanup.

Test signals: 7-bit write/read, 10-bit address high/low bytes, final-byte NACK behavior, multi-message transfer without intermediate STOP, busy-bus `-EAGAIN`, NACK stop handling, timeout reinitialization, invalid timing rejection, runtime PM resume failure, suspend disable/resume reinitialize, and no-zero-length quirk enforcement.
