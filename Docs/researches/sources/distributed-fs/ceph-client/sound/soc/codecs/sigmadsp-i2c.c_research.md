# sources/distributed-fs/ceph-client/sound/soc/codecs/sigmadsp-i2c.c

Purpose: I2C transport adapter for the shared Analog Devices SigmaDSP firmware loader. It creates a managed `sigmadsp` instance and wires it to raw 16-bit-address I2C read/write callbacks.

Important APIs and data: `sigmadsp_write_i2c()` allocates a DMA-capable buffer, stores the target address big-endian, appends payload bytes, and sends with `i2c_master_send()`. `sigmadsp_read_i2c()` sends the 16-bit address followed by an I2C read message via `i2c_transfer()`. `devm_sigmadsp_init_i2c()` calls the core `devm_sigmadsp_init()`, then fills `control_data`, `write`, and `read`.

Control flow: codec drivers call `devm_sigmadsp_init_i2c(client, ops, firmware_name)`. Firmware parsing happens in `sigmadsp.c`; this file only supplies transport. Writes return negative I2C errors but otherwise ignore short positive sends; reads require exactly two messages transferred.

State and persistence: no independent persistent state. The returned `struct sigmadsp` stores the I2C client and function pointers until devres cleanup. Firmware data/control state is owned by the core.

Dependencies and integration points: depends on Linux I2C, unaligned big-endian helpers, memory allocation, and `sigmadsp.h`. Risks include potential short-write handling weakness, allocation per firmware/control write, fixed 16-bit register addressing, and adapter requirements for combined read transfers. Test signals are firmware download over I2C, readback controls, I2C error propagation, and devres cleanup through parent codec removal.
