# sources/distributed-fs/ceph-client/drivers/nfc/pn533/i2c.c

Purpose: Implements the PN532/PN533 I2C transport frontend for the shared PN533 core.

Important APIs and functions: `struct pn533_i2c_phy` stores I2C client, common `pn533` pointer, abort flag, and hard fault. PHY ops are `pn533_i2c_send_frame()`, `pn533_i2c_send_ack()`, and `pn533_i2c_abort_cmd()`. IRQ/read/probe functions are `pn533_i2c_read()`, `pn533_i2c_irq_thread_fn()`, `pn533_i2c_probe()`, and `pn533_i2c_remove()`.

Control flow: Probe checks I2C support, allocates PHY state, initializes common PN533 as a PN532 request/ACK/response device, allocates an NFC device with no Type B protocols, requests a shared falling IRQ, finalizes setup by querying/configuring the chip, and registers NFC. Send writes the fully framed SKB with a standby retry. IRQ reads a maximum-size frame prefixed by a READY byte, trims to the parsed PN533 frame size, and passes it to `pn533_recv_frame()` unless the command was locally aborted. Abort sends a PN533 ACK and completes the current command with `-ENOENT`.

State and persistence: Runtime state includes `aborted`, `hard_fault`, and the common PN533 command queues/work. No durable persistence.

Dependencies and integration points: Uses Linux I2C/IRQ, OF match aliases for `nxp,pn532`, and shared PN533 frame parsing/command completion.

Risks: The read path pulls a fixed maximum frame and relies on READY plus frame-size parsing. Fatal I2C errors set hard fault permanently. Aborted frames are dropped to avoid completing cancelled commands. Test signals include READY bit absent, standby retry, abort while command pending, hard fault, IRQ sharing, setup failure unwind, and device-tree compatible coverage.
