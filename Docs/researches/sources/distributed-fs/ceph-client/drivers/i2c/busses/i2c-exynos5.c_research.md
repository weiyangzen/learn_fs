# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-exynos5.c

## Purpose
Samsung Exynos5/Exynos7/ExynosAutoV9/Exynos8895 high-speed I2C master adapter. It supports auto-mode FIFO transfers, variant timing formulas, bus recovery, atomic transfers by polling IRQ status, and noirq system PM.

## Important APIs, Types, And Functions
`struct exynos5_i2c` stores adapter, active message, completion, message pointer, IRQ, MMIO registers, clocks, device, state, spinlock, transfer-done latch, atomic flag, operating clock, and variant data. `struct exynos_hsi2c_variant` captures FIFO depth and hardware type. Core functions are `exynos5_i2c_set_timing()`, `exynos5_hsi2c_clock_setup()`, `exynos5_i2c_init()`, `exynos5_i2c_reset()`, `exynos5_i2c_irq()`, `exynos5_i2c_message_start()`, `exynos5_i2c_xfer_msg()`, `exynos5_i2c_xfer()`, and `exynos5_i2c_xfer_atomic()`.

## Control Flow
Probe reads `clock-frequency`, gets `hsi2c` and optional `hsi2c_pclk`, enables clocks, maps MMIO, clears stale interrupts, initializes lock/completion, requests IRQ, loads variant data, programs timings, resets/init hardware, registers the adapter, then disables clocks. Transfers enable clocks, process messages one by one, program address/FIFO/interrupt/auto-conf, wait for completion or poll IRQs in atomic mode, wait for bus idle on final stop, reset on errors, and disable clocks. IRQ handles variant-specific transfer status, drains RX FIFO or fills TX FIFO, disables interrupts, clears pending IRQs, and completes.

## State And Persistence
Transfer state is `msg`, `msg_ptr`, `state`, `trans_done`, and `atomic`. `trans_done` is latched because the hardware bit clears on read. Timings and controller mode are restored on reset/resume.

## Dependencies And Integration Points
Depends on OF compatible table for Samsung variants, clocks, MMIO, IRQs, spinlocks, I2C core, and noirq PM callbacks. Functionality excludes SMBus quick.

## Risks
Timing math differs by hardware variant and can fail on unsupported clock combinations. FIFO trigger levels depend on message length and FIFO depth. Bus recovery manually toggles auto/manual mode and emits read clocks/STOP for stuck SDA on newer variants. Atomic mode disables the IRQ and calls the IRQ handler manually, so locking and status polling must remain IRQ-safe.

## Test Signals
Test each OF variant, 100 kHz/400 kHz/1 MHz timing, read/write FIFO boundary lengths, transfer-done/error status mapping, timeout reset, bus recovery from stuck master state, atomic transfers, clock enable/disable balance, and noirq suspend/resume.
