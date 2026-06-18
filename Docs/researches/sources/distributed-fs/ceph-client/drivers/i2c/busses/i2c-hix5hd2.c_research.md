# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-hix5hd2.c

Purpose: Hisilicon Hix5hd2 I2C bus driver. It implements interrupt-driven byte sequencing for a 7-bit-address MMIO controller, clock-rate setup, bus-idle checks, controller reset, and runtime PM autosuspend.

Important APIs/types/functions: `enum hix5hd2_i2c_state` models transfer state. `struct hix5hd2_i2c_priv` stores adapter, active message, completion, byte indexes, stop flag, MMIO, clock, spinlock, error, speed, and state. Key functions are `hix5hd2_i2c_init()`, `hix5hd2_i2c_drv_setrate()`, `hix5hd2_i2c_xfer_msg()`, `hix5hd2_i2c_message_start()`, `hix5hd2_i2c_irq()`, read/write handlers, `hix5hd2_i2c_xfer()`, and runtime suspend/resume.

Control flow: probe reads `clock-frequency` with a 100 kHz default and 400 kHz cap, maps MMIO, enables the clock, initializes registers and IRQ handling, enables runtime PM, and registers an adapter. Each message starts by clearing/enabling interrupts, writing the 8-bit address, and issuing START+WRITE. The ISR handles arbitration and NACK errors, advances read or write bytes on OVER interrupts, optionally emits STOP, disables interrupts, and completes the waiter. The outer transfer iterates messages and uses STOP on final or `I2C_M_STOP`.

State and persistence: active message pointer, `msg_idx`, `msg_len`, `stop`, `err`, and `state` persist during a transfer. Clock frequency, SCL high/low registers, and interrupt mask state persist while runtime active. Runtime suspend disables the clock; resume re-enables and reinitializes the controller.

Dependencies and integration: depends on OF compatible `hisilicon,hix5hd2-i2c`, platform MMIO/IRQ, clock framework, runtime PM, completions, spinlocks, and Linux I2C core.

Risks: only 7-bit addressing is supported. `pm_runtime_get_sync()` return is not checked in transfer. Timeouts reset the controller by clock-cycling it, which may affect a shared bus. Rate calculation is simple and assumes sane clock/frequency values. IRQ is requested with `IRQF_NO_SUSPEND`, so PM interactions need platform validation.

Test signals: transfers at default and configured frequencies, multi-message repeated-start behavior, NACK and arbitration error returns, timeout reset path, runtime autosuspend/resume reinitialization, and bus-idle wait after STOP.
