# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-stm32f4.c

Purpose: implements the STM32F4 I2C controller master adapter. It programs CR/CCR/TRISE timing, handles event and error IRQs, and supports standard and fast mode master transfers with repeated starts.

Important APIs/types/functions: `struct stm32f4_i2c_dev` stores adapter, device, MMIO, completion, clock, selected speed, parent clock rate, and active `stm32f4_i2c_msg`. `stm32f4_i2c_hw_config()` programs peripheral clock frequency, rise time, speed mode, and enables the peripheral. `stm32f4_i2c_xfer()` and `stm32f4_i2c_func()` provide the I2C algorithm. Event and error handlers are `stm32f4_i2c_isr_event()` and `stm32f4_i2c_isr_error()`.

Control flow: probe maps registers, obtains event/error IRQs, enables clock, resets the controller, derives speed from `clock-frequency`, requests IRQs, configures hardware, registers the adapter, then disables the clock until transfers. A transfer enables the clock and iterates messages through `stm32f4_i2c_xfer_msg()`. Each message sets address/count/buffer/result/stop, enables event/error interrupts, waits for bus-free on the first message, starts hardware, and waits on completion. Event IRQ handles start-bit, address sent, TXE/RXNE, and BTF with special read handling for 1-, 2-, 3-, and N-byte transfers. Error IRQ maps arbitration loss to `-EAGAIN` and ACK/bus errors to `-EIO`.

State and persistence: no runtime PM is used; the clock is manually enabled for probe initialization and each transfer. Active transfer state is held in `msg`. Hardware state persists while clocked, but transfers explicitly enable interrupts and set START/STOP/repeated START.

Dependencies and integration: depends on OF compatible `st,stm32f4-i2c`, MMIO resources, two IRQs, reset controller, clock framework, and the I2C core. Shared STM32 header is included for speed enum values, though this F4 implementation does not use the shared DMA helper.

Risks: parent clock must be in hardware-limited MHz ranges or probe/config fails. Read sequencing is sensitive to ACK/POS/STOP ordering; off-by-one changes can break 1/2/3 byte reads. Timeout path does not perform full controller reset, so later transfers depend on hardware/IRQ state being recoverable.

Test signals: clock-frequency selection, parent-rate boundary checks, 0/1/2/3/N-byte reads, multi-message repeated starts, NACK/arbitration/bus error IRQs, and reset/clock lifecycle during probe/remove.
