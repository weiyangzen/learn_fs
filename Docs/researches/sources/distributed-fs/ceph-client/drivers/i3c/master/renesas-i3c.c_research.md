# sources/distributed-fs/ceph-client/drivers/i3c/master/renesas-i3c.c

## Purpose

`renesas-i3c.c` implements a Renesas I3C controller master driver for RZ-family SoCs. It registers an I3C master, programs bus timing and device address table registers, supports DAA, selected CCCs, private I3C transfers, legacy I2C transfers, interrupt-driven FIFO/response handling, and noirq system suspend/resume.

## Important APIs, Types, and Functions

- Register macros cover protocol mode, bus control, master dynamic address, reset, timing, command/response queues, data FIFO, status/interrupt enables, and per-device `DATBAS` entries.
- `struct renesas_i3c` stores controller state: I3C core object, internal transfer state, address slots, cached I2C/I3C timing registers, clocks/resets, DAT backup, and xfer queue.
- `struct renesas_i3c_xfer` and `struct renesas_i3c_cmd` model one queued transfer and command payload/counters.
- `renesas_i3c_bus_init()` resets hardware, derives clock divisors and standard/extended bit-rate settings, initializes interrupts/FIFOs, assigns the master dynamic address, and registers master info.
- `renesas_i3c_daa()` preprograms DATBAS entries with candidate addresses, issues ENTDAA, and registers newly detected devices.
- `renesas_i3c_send_ccc_cmd()`, `renesas_i3c_i3c_xfers()`, and `renesas_i3c_i2c_xfers()` implement I3C core operations.
- ISR functions handle response, RX, TX, start, stop, transfer-end, and NACK events.

## Control Flow

Probe maps registers, enables clocks, deasserts optional resets, initializes the queue, resets hardware, requests named IRQs, initializes slot state, allocates DAT backup storage, and registers the I3C master. Bus init computes timing from the TCLK rate and requested bus rates, programs bitrate/timing registers, initializes status/interrupt control, assigns the master dynamic address, and sets master info.

I3C and CCC transfers create a one-command xfer, set `internal_state`, build a normal command queue descriptor, optionally prefill TX FIFO for writes larger than four bytes, enqueue the transfer, and wait up to one second. The response ISR decodes response status, reads remaining RX bytes, disables TX/RX interrupts, clears abort/error flags, completes the xfer, and advances the queue. Legacy I2C transfers switch protocol mode, use bus condition registers for START/repeated START/STOP, and let start/RX/TX/TEND/STOP ISRs drive byte-level progress.

## State and Persistence Behavior

Address slots are tracked in `free_pos` and `addrs[]`. Per-device master data stores the slot index. `DATBASn[]` backs up hardware DAT registers during noirq suspend; resume restores reference clock, master dynamic address, DATBAS entries, and common hardware init. `internal_state` guides ISR interpretation of the current transfer.

## Dependencies and Integration Points

The driver depends on platform resources, named IRQs, bulk clocks, optional resets, device tree matches, I3C core helpers, I2C timing parsing, and internal FIFO helpers from `../internals.h`.

## Risks and Edge Cases

IBI, Hot-Join, and target support are explicitly TODO. CCC support is restricted to one destination and an allowlist. `renesas_i3c_i3c_xfers()` allocates one command but loops over `i3c_nxfers`, reusing the same command structure sequentially, so multi-transfer behavior should be tested carefully. Several paths return 0 after transfer loops without propagating `xfer->ret`. I2C flow is byte-interrupt driven and sensitive to NACK/STOP ordering. PM resume restores DAT values but does not rerun full bus init timing calculation.

## Test Signals

Hardware tests should cover bus init at pure and mixed rates, DAA with zero and multiple devices, SETDASA and supported CCC read/write commands, private reads/writes including > FIFO-depth writes, legacy I2C read/write/repeated-start/NACK, named IRQ ordering, timeout dequeue, suspend/resume with attached devices, and unsupported CCC rejection.
