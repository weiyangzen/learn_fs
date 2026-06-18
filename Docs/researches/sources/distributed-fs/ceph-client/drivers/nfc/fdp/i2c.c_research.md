# sources/distributed-fs/ceph-client/drivers/nfc/fdp/i2c.c

Purpose: Implements the I2C physical layer for Intel Fields Peak NFC. It frames NCI packets with FDP length/LRC bytes, handles reset/power GPIO, reads ACPI/device properties, services IRQ-driven reads, and delegates NCI core registration to `fdp.c`.

Important APIs, types, and functions: `fdp_nci_i2c_probe()` allocates `fdp_i2c_phy`, requests threaded IRQ, maps ACPI GPIOs, reads clock/VSC properties, and calls `fdp_nci_probe()`. `fdp_nci_i2c_write()` adds/removes length+LRC framing and retries standby writes. `fdp_nci_i2c_read()` performs two-stage reads using `next_read_size`; `fdp_nci_i2c_irq_thread_fn()` passes SKBs to `nci_recv_frame()`.

Control flow: Enable/disable both pulse the power GPIO via reset. Writes prepend a 16-bit little-endian length and append XOR LRC, send via `i2c_master_send()`, retry once for `-EREMOTEIO`, and restore the original SKB. Reads first receive either a length packet or data packet, validate XOR LRC, update `next_read_size`, allocate an SKB for data packets, strip framing, and flush on desynchronization.

State and persistence behavior: Runtime state is `hard_fault`, `next_read_size`, power GPIO value, and the core `nci_dev` pointer. Clock and vendor-specific configuration are read at probe and passed to core setup; they are not persisted by the transport.

Dependencies and integration points: Uses I2C core, threaded IRQs, ACPI GPIO mappings, device properties (`clock-type`, `clock-freq`, `fw-vsc-cfg`), GPIO consumer API, NFC NCI receive path, and FDP core exported functions.

Risks: LRC/desync handling uses a broad flush read that may drop valid data. Short writes set `hard_fault` to a positive short count before returning `-EREMOTEIO`, which causes future writes to return that positive value. Property parsing of `fw-vsc-cfg` expects an embedded length and can reject or ignore malformed data. IRQ must be present.

Test signals: Probe with ACPI `INT339A`, missing IRQ/GPIO, I2C adapter lacking `I2C_FUNC_I2C`, normal read/write framing, standby retry, LRC failure resync, short writes, device property defaults and VSC arrays, remove/reset, and NCI receive delivery.
