<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/dlhl60d.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/dlhl60d.c

Purpose: I2C IIO driver for All Sensors DLH low-voltage digital pressure sensors, with DLHL60D and DLHL60G variants.

Important APIs, types, and functions: `struct dlh_info` stores variant name, digital offset factor, and full-scale span. `struct dlh_state` stores client, variant info, optional interrupt completion, and RX buffer. `dlh_start_capture_and_read()` sends a single-shot command, waits by IRQ or delay, and reads seven bytes. `dlh_read_raw()` exposes raw, scale, and offset. `dlh_trigger_handler()` captures active channels into an IIO buffer.

Control flow: probe checks I2C functionality, gets match data, optionally requests a rising IRQ, initializes triggered buffers, and registers the IIO device. Direct reads claim direct mode, start a conversion, read pressure and temperature, and release direct mode. Buffered capture performs the same conversion flow from the trigger handler.

State and persistence: variant constants and optional IRQ mode persist in memory. No hardware configuration persists. The shared `rx_buf` is reused for direct and triggered reads, with direct reads protected by IIO direct-mode claim.

Dependencies and integration points: depends on I2C, IIO triggered buffers, OF/I2C match data, and optional device IRQ. Uses IIO scan definitions for 24-bit big-endian pressure/temperature fields stored in 32-bit slots with shift.

Risks: `i2c_master_recv()` only checks negative errors and not short positive reads. Interrupt timeout is only 5 ms, matching conversion time tightly. `mdelay()` is used for polling mode, which busy-waits. Status must equal `0x40`; other status variants are treated as busy. Buffered path does not include a timestamp channel in the channel table.

Test signals: DLHL60D/G scale and offset math, optional IRQ and polling modes, short-read injection, status-byte error handling, direct-read busy behavior while buffer enabled, and active-channel scan ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/dlhl60d.c -->
