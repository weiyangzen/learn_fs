# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-iop3xx.c

Purpose: provides the platform I2C adapter driver for Intel XScale IOP3xx and IXP46x controllers. It is an interrupt-driven byte-oriented master driver using the register definitions in `i2c-iop3xx.h`.

Important APIs, types, and functions: `struct i2c_algo_iop3xx_data` stores MMIO address, wait queue, spinlock-protected interrupt status, enabled status bits, adapter id, and optional GPIO descriptors used to clear GPOD before enabling. `iop3xx_i2c_xfer()` is the algorithm transfer hook. Helper layers split into reset/enable/cleanup, wait helpers, address emission, byte read/write, message handling, IRQ handling, and platform probe/remove.

Control flow: probe allocates adapter and private state, obtains optional SCL/SDA GPIOs, requests and maps the memory region, requests the IRQ, initializes wait queues and locks, resets/enables hardware, and registers a numbered adapter. A transfer waits idle, resets/enables the unit, then handles each message by sending the target address followed by byte-wise read or write. Each byte operation starts a hardware transfer and waits for TX-empty or RX-full status captured by the IRQ handler. Cleanup clears master start/byte/stop/SCL enable bits.

State and persistence: transient state is mostly interrupt status in `SR_received`, protected by `lock` and consumed by waiters. The driver resets and re-enables the controller at the start of each transfer, so hardware transaction state is intentionally short-lived. The global `i2c_id` assigns an internal id but adapter numbering uses platform id.

Dependencies and integration points: integrates with platform devices, OF compatibles `intel,iop3xx-i2c` and `intel,ixp4xx-i2c`, legacy `I2C_CLASS_HWMON`, raw MMIO access, optional GPIO descriptors, Linux IRQ and wait queue APIs, and the I2C core.

Risks: the driver refuses address `MYSAR` because writing to the local target address can latch up IOP331 hardware. `iop3xx_i2c_wait_idle()` uses the same interrupt status mechanism as transfer waits, so stale status handling matters. The IRQ handler always returns handled after masking status, which may obscure unexpected shared IRQ behavior. Probe uses manual allocation, mapping, request_irq, and release paths rather than devm for most resources.

Test signals: validate probe/remove resource unwinding, IRQ-driven TX/RX completion, timeout when no interrupt arrives, bus error and arbitration loss status mapping, local target address refusal, combined read/write messages with repeated starts, optional GPIO clearing before enable, and compatibility on both IOP3xx and IXP46x variants.
