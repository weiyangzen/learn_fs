# sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/i2c.c

Purpose: Implements the Marvell NCI-over-I2C transport, wiring I2C probe/remove, IRQ-driven reads, writes, device-tree parsing, and common Marvell NCI registration.

Important APIs and functions: `struct nfcmrvl_i2c_drv_data` stores the I2C client, device, and common private pointer. Key helpers are `nfcmrvl_i2c_read()`, `nfcmrvl_i2c_int_irq_thread_fn()`, `nfcmrvl_i2c_nci_send()`, `nfcmrvl_i2c_parse_dt()`, `nfcmrvl_i2c_probe()`, and `nfcmrvl_i2c_remove()`. `i2c_ops` implements `nfcmrvl_if_ops`.

Control flow: Probe verifies `I2C_FUNC_I2C`, allocates transport state, finds platform data or OF properties, requests the IRQ, registers the common NCI device as `NFCMRVL_PHY_I2C`, and enables firmware download support. The threaded IRQ reads an NCI control header followed by payload, then passes the SKB to `nfcmrvl_nci_recv_frame()`. Send writes the entire SKB with a standby retry on `-EREMOTEIO`.

State and persistence: Tracks `NFCMRVL_PHY_ERROR` in common flags after fatal remote I/O and stores IRQ polarity/number in platform data. No durable persistence exists.

Dependencies and integration points: Uses Linux I2C, OF IRQ parsing, NCI header sizing, common Marvell registration, and the firmware downloader through `support_fw_dnld`.

Risks: Header `plen` is trusted for allocation and second read. Partial sends become `-EREMOTEIO`; fatal receive errors block future traffic until open/reset clears the common PHY error flag. Test signals include DT/platform probe, rising/falling IRQ selection, standby retry, bad payload length, fatal I2C error, firmware download over I2C, and remove while interrupts are active.
