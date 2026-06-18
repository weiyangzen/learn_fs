# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-iop3xx.h

Purpose: private header for the IOP3xx/IXP46x I2C driver. It defines register offsets, control/status bit meanings, local constants, error codes, IO size, and the private adapter data structure consumed by `i2c-iop3xx.c`.

Important APIs, types, and functions: the header does not export callable functions. The central type is `struct i2c_algo_iop3xx_data`, containing the mapped register base, wait queue, spinlock, enabled/received status masks, logical id, and optional GPIO descriptors. Register constants cover control register operations such as reset, unit enable, SCL enable, START/STOP, NACK, and transfer byte, plus status bits for bus error, RX full, TX empty, arbitration loss, bus busy, unit busy, NACK, and read/write direction.

Control flow: this header shapes the C file's byte-level state machine. Control bits are written to `CR_OFFSET`, status bits are read/cleared through `SR_OFFSET`, and data is moved through `DBR_OFFSET`. `IOP3XX_ISR_CLEARBITS` is used during reset, while `IOP3XX_ISR_*` masks drive wait conditions and error mapping.

State and persistence: the structure fields persist per adapter. `SR_received` is an interrupt-to-waiter handoff field, while `SR_enabled` limits which status bits the IRQ handler records. Optional SCL/SDA GPIO descriptors persist only to support the GPOD clearing requirement before enabling the controller.

Dependencies and integration points: depends on Linux `wait_queue_head_t`, `spinlock_t`, `u32`, `void __iomem`, and `struct gpio_desc`. It is included only by the IOP3xx driver and is not a public kernel API.

Risks: bit definitions are hardware contract. Any mismatch in clear bits, offsets, or interrupt masks changes live bus behavior. Error codes `I2C_ERR_BERR` and `I2C_ERR_ALD` are private numeric constants that the C file negates, so callers see unusual negative values rather than standard errno for those two cases.

Test signals: compile coverage with the C file, register offset validation on real hardware or emulation, interrupt bit clear tests, error mapping for bus error and arbitration loss, and GPOD-related enable sequencing on systems that provide SCL/SDA GPIO descriptors.
