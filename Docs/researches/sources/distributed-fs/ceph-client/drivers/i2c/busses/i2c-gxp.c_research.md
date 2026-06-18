# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-gxp.c

Purpose: HPE GXP platform I2C controller driver supporting interrupt-driven master transfers and optional I2C slave mode. It uses per-engine MMIO registers plus a shared syscon interrupt status/enable block.

Important APIs/types/functions: `struct gxp_i2c_drvdata` holds device/MMIO state, `i2c_timings`, engine number, completion, current message pointers, transfer state, and optional slave client. Important functions are `gxp_i2c_start()`, `gxp_i2c_master_xfer()`, `gxp_i2c_restart()`, address/data ACK handlers, `gxp_i2c_slave_irq_handler()`, `gxp_i2c_irq_handler()`, `gxp_i2c_init()`, `gxp_i2c_probe()`, and slave register/unregister hooks when `CONFIG_I2C_SLAVE` is enabled.

Control flow: probe obtains the global syscon map from `hpe,sysreg`, maps the local engine, derives the engine index from the mapped address, requests a shared IRQ, initializes timing/filter registers, enables the global interrupt bit, and registers an adapter. Master transfers set the current message queue, start with address/RW, and wait for completion. The ISR validates the engine bit in global status, handles errors, dispatches slave events when present, or advances the master address/read/write state machine byte by byte.

State and persistence: transfer state is tracked in `state`, `curr_msg`, `msgs_remaining`, `buf`, `buf_remaining`, and `stopped`. Slave registration persists the own-address register and event masks until unregister. The shared `i2cg_map` is static across instances.

Dependencies and integration: depends on platform resources, `regmap` syscon, MMIO accessors, Linux I2C master/slave APIs, firmware timing parsing, and OF compatible `hpe,gxp-i2c`.

Risks: engine identity is inferred from mapped address low bits, which is fragile if mapping assumptions change. The static global syscon map is initialized once without per-device lifetime management. Error interrupts clear all events and complete the active transfer, but timeout does not explicitly reset hardware. Slave and master events share one ISR and state object, so mixed traffic needs hardware validation.

Test signals: successful probe for all engine indices, global interrupt enable masking on probe/remove, multi-message repeated-start reads and writes, address NACK `-ENXIO`, data NACK `-EIO`, shared IRQ filtering, slave read/write/stop callbacks, and timeout behavior.
