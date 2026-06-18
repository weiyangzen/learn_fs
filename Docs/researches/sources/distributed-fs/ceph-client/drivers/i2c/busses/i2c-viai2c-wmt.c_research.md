# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-viai2c-wmt.c

## Purpose

`i2c-viai2c-wmt.c` is the WonderMedia/WMT platform adapter built on the VIAI2C common byte-mode core. It handles WMT-specific clocking, timing registers, IRQ decoding, and OF registration.

## Important APIs, Types, and Functions

`wmt_i2c_func()` advertises I2C, SMBus emulation, and `I2C_FUNC_NOSTART`. `wmt_i2c_reset_hardware()` enables and programs the clock, clears interrupts, enables the controller, and selects standard/fast timing. `wmt_i2c_isr()` clears status, maps address NAK and SCL timeout to errors, delegates data progression to `viai2c_irq_xfer()`, and completes the transfer.

## Control Flow

Probe calls `viai2c_init()` with WMT platform ID, gets IRQ, requests it, gets the OF clock, reads `clock-frequency`, sets fast TCR if 400 kHz, initializes adapter metadata, resets hardware, and registers the adapter. Remove disables interrupts, disables the clock, and deletes the adapter.

## State and Persistence Behavior

The WMT file sets persistent clock rate and timing registers at probe. Runtime transfer state is the shared `struct viai2c`. No PM callbacks are present; clock lifetime is probe-to-remove.

## Dependencies and Integration Points

It binds to `wm,wm8505-i2c`, depends on OF clock APIs, platform IRQs, MMIO, and the common VIAI2C exports. It integrates with I2C core through a normal `i2c_algorithm`.

## Risks

The clock is obtained with `of_clk_get()` and manually disabled only on remove or adapter-add failure, so probe failure after clock acquisition needs careful balance. Timing supports only standard and 400 kHz fast mode. ISR returns `IRQ_HANDLED` even if status is zero.

## Test Signals

Check OF probe, 100 kHz and 400 kHz timing, IRQ NAK and SCL timeout errors, `I2C_M_NOSTART` transfers, zero-length quick writes, adapter-add failure cleanup, and remove-time interrupt/clock disable.
