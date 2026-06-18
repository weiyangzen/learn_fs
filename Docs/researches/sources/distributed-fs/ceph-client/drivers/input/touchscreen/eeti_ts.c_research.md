# sources/distributed-fs/ceph-client/drivers/input/touchscreen/eeti_ts.c

Purpose: `eeti_ts.c` is an I2C driver for EETI touchscreen panels using the simple six-byte EETI report protocol. It reports single-touch X/Y, optional pressure, and `BTN_TOUCH`, with support for an optional attention GPIO.

Important APIs, types, and functions: `struct eeti_ts` stores the I2C client, input device, optional `attn` GPIO, touchscreen properties, mutex, and running flag. `eeti_ts_read()` receives six bytes and passes motion packets to `eeti_ts_report_event()`. `eeti_ts_report_event()` derives coordinate resolution from AD bits, normalizes coordinates to 11 bits, reports pressure if present, applies touchscreen properties, and syncs. `eeti_ts_isr()` drains events while running and while the attention GPIO remains asserted. `eeti_ts_start()`/`eeti_ts_stop()` control IRQ enablement for input open/close and PM.

Control flow: probe allocates state/input, sets ABS_X/Y/pressure ranges, parses touchscreen properties, obtains optional attention GPIO, requests a threaded IRQ, stops the device by disabling IRQ, and registers input. Open enables IRQ and optionally performs a catch-up read if the attention line is already asserted. Suspend stops the device if input is enabled and optionally enables IRQ wake; resume reverses that.

State and persistence: only `running` and the IRQ enable state persist during runtime. The mutex serializes ISR reads and start catch-up. There are no persistent settings or firmware operations.

Dependencies and integration points: it depends on I2C `i2c_master_recv()`, optional GPIO descriptor `attn`, input touchscreen properties, IRQ wake handling, and compatible `eeti,exc3000-i2c` for this older protocol path.

Risks: absent attention GPIO means the ISR reads exactly once and relies on level-triggered IRQ behavior for further data. The stop path disables IRQ after only a write memory barrier and does not wait for the threaded handler beyond IRQ core semantics. The driver cannot probe the device actively and trusts platform description.

Test signals: validate packet resolution normalization, pressure-present and pressure-absent reports, attention GPIO drain loop, open catch-up read after missed edge, suspend/resume wake IRQ behavior, and read-short/error handling.
