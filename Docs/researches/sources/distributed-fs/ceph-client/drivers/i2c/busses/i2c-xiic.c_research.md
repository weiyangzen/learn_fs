# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-xiic.c

## Purpose

`i2c-xiic.c` is the Xilinx XIIC/AXI IIC controller driver. It supports interrupt-driven and atomic transfers, dynamic and standard controller modes, endian-aware MMIO, runtime PM, programmable timing registers, SMBus block reads, and platform-data-created child devices.

## Important APIs, Types, and Functions

`struct xiic_i2c` stores MMIO base, adapter, completion, transfer message pointers, locks, RX/TX positions, endianness, clock, state, mode flags, quirks, SMBus block-read state, clock rates, and atomic-transfer state. Key functions include `xiic_setclk()`, `xiic_reinit()`, `xiic_read_rx()`, `xiic_fill_tx_fifo()`, `xiic_process()`, `xiic_start_recv()`, `xiic_start_send()`, `xiic_start_xfer()`, `xiic_xfer()`, and `xiic_xfer_atomic()`.

## Control Flow

Probe maps MMIO, gets IRQ and clock, enables runtime PM, reads optional `clock-frequency`, requests a threaded IRQ, detects endianness by probing FIFO reset/status, reinitializes hardware, registers a numbered adapter, and optionally instantiates platform-data clients. Transfers resume runtime PM, choose dynamic mode unless broken-read, read length >255, or SMBus block read requires standard mode, reinitialize the controller, start the first message, and wait for completion. The threaded ISR handles arbitration/TX errors, RX full, TX empty/half, bus-not-busy, starts next messages, and completes the waiter.

## State and Persistence Behavior

Transfer state is held in `tx_msg`, `rx_msg`, `nmsgs`, `tx_pos`, `rx_pos`, `state`, `dynamic`, `prev_msg_tx`, and `smbus_block_read`. Normal transfers use a mutex and completion; atomic transfers use a spinlock and polling. Runtime suspend disables the clock, and runtime resume enables it. Hardware is reset/reinitialized for each transfer and on certain errors.

## Dependencies and Integration Points

The driver binds OF compatibles `xlnx,xps-iic-2.00.a` and `xlnx,axi-iic-2.1`, uses platform resources, clocks, runtime PM, threaded IRQs, I2C core, and optional `i2c-xiic` platform data. The older compatible marks dynamic reads broken.

## Risks

Mode selection is complex and central to correctness. Standard-mode repeated starts can corrupt transactions if TX FIFO is not empty, so several paths wait explicitly. SMBus block receive length has special minimum-length handling and error signaling through mutated message lengths. Atomic transfer uses direct runtime suspend/resume helpers and polls bus-busy, so it must not sleep. Endianness detection depends on FIFO-empty status after a reset write.

## Test Signals

Cover little/big endian systems, standard/dynamic mode selection, read lengths 1/2/16/255/256, SMBus block read including invalid lengths, combined write-read transfers, zero-length writes, arbitration loss, TX error, timeout, atomic transfers, runtime PM autosuspend/resume, single-master busy-bus behavior, and platform-data child creation.
