# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-master.c

## Purpose
DesignWare I2C master-mode implementation. It calculates master timings, drives FIFO-based transfers, handles master interrupts or polling, supports protocol mangling and SMBus block reads, performs recovery, and exposes master configuration/probe helpers.

## Important APIs, Types, And Functions
Exports `i2c_dw_xfer()`, `i2c_dw_configure_master()`, `i2c_dw_isr_master()`, and `i2c_dw_probe_master()`. Core internals are `i2c_dw_set_timings_master()`, `i2c_dw_xfer_init()`, `i2c_dw_xfer_msg()`, `i2c_dw_read()`, `i2c_dw_read_clear_intrbits()`, `i2c_dw_process_transfer()`, `__i2c_dw_xfer_one_part()`, `i2c_dw_xfer_common()`, and `i2c_dw_init_recovery_info()`. AMD Navi GPU has `amd_i2c_dw_xfer_quirk()`.

## Control Flow
Probe initializes completion, computes SCL high/low counts for standard/fast/fast-plus/high-speed modes, preserves BIOS bus-clear support, and attaches optional GPIO recovery. A normal transfer resumes PM, acquires any hardware lock, splits messages at `I2C_M_STOP`, validates same-address and restart limitations, initializes registers and target address, fills TX FIFO with write data or read commands, then waits for completion. IRQ or polling clears precise interrupt bits, drains RX FIFO, refills TX FIFO, handles aborts and spurious stops, and completes on STOP/abort with no outstanding reads.

## State And Persistence
Transfer state is stored in `dw_i2c_dev`: message indexes, TX/RX buffers, outstanding read commands, `cmd_err`, `msg_err`, `abort_source`, and `status`. Hardware is disabled after each transfer and may return to slave mode if a slave is registered.

## Dependencies And Integration Points
Relies on common DesignWare register/PM/lock helpers, regmap, GPIO descriptors, pinctrl, reset control, runtime PM, and Linux I2C recovery. It feeds the common adapter algorithm via `i2c_dw_xfer()`.

## Risks
FIFO and interrupt latency can terminate transfers early when TX FIFO empties. Restart support differs when `emptyfifo_hold_master` is false. SMBus block-read length correction is subtle. AMD Navi polling quirk has separate behavior and lacks protocol mangling. Abort-source mapping must preserve `TX_ABRT_SOURCE` before clearing.

## Test Signals
Test write, read, combined read/write, SMBus block read, `I2C_M_STOP` splitting, invalid address changes, no-restart hardware, TX abort/noack/arbitration loss, polling mode, GPIO recovery, AMD Navi quirk, and suspend/resume around active adapters.
