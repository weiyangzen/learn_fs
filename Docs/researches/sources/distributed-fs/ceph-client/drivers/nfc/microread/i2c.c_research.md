# sources/distributed-fs/ceph-client/drivers/nfc/microread/i2c.c

Purpose: Implements the I2C transport for Inside Secure Microread HCI NFC chips using SHDLC framing. It adds/removes length and XOR CRC bytes, handles threaded IRQ reads, tracks hard I2C faults, and registers the shared Microread HCI core.

Important APIs, types, and functions: `struct microread_i2c_phy` stores the I2C client, HCI device, and `hard_fault`. `microread_i2c_write()` frames and sends SKBs with standby retry; `microread_i2c_read()` reads length plus payload, validates size and CRC, and strips framing; `microread_i2c_irq_thread_fn()` forwards frames to `nfc_hci_recv_frame()`; `microread_i2c_probe()` registers IRQ and calls `microread_probe()`.

Control flow: Probe allocates PHY state, binds client data, requests a rising-edge threaded IRQ, then registers the HCI core with `LLC_SHDLC_NAME` and I2C framing sizes. Writes delay for chip timing, push length, append XOR CRC, send over I2C, retry `-EREMOTEIO`, restore the SKB, and return 0 or error. IRQ reads validate the length byte, receive the rest, check CRC, strip length/tail, and pass the frame upward. Hard I2C failure stores `-EREMOTEIO` and reports a NULL frame to HCI.

State and persistence behavior: Runtime state is the `hard_fault` latch and HCI device pointer. There is no persistent configuration or firmware state.

Dependencies and integration points: Uses I2C, threaded IRQs, NFC HCI, NFC LLC SHDLC, SKB helpers, and the exported Microread core API.

Risks: Length/CRC errors trigger flush reads that may desynchronize if device timing differs. `hard_fault` permanently blocks future writes until reprobe. Probe does not explicitly validate `client->irq > 0`, relying on `request_threaded_irq` failure. Fixed payload limit of 29 bytes must match the chip/LLC contract.

Test signals: I2C probe/remove, missing/invalid IRQ, normal read/write frames, CRC and length faults, standby retry, hard-fault propagation, SHDLC LLC registration, and remove while IRQ activity is possible.
