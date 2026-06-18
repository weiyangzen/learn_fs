# sources/distributed-fs/ceph-client/drivers/spi/spi-kspi2.c

## Purpose

`spi-kspi2.c` is the KEBA SPI host controller type 2 driver for an FPGA IP core exposed as an auxiliary device. It implements byte-oriented polling transfers, a hardware semaphore for sharing the controller with non-Linux processors, automatic registration of board-provided SPI devices, and basic CPOL/CPHA plus clock divider support.

## Important APIs, Types, and Functions

`struct kspi2` stores the KEBA auxiliary device, MMIO base, SPI host, base clock frequency, control-register shadow, and created SPI child devices. Hardware sharing is implemented by `kspi2_inuse_lock()` and `kspi2_inuse_unlock()`, wired to `prepare_transfer_hardware` and `unprepare_transfer_hardware`. Transfer helpers are `kspi2_calc_minimal_divider()`, `kspi2_write_control_reg()`, `kspi2_txrx_byte()`, `kspi2_process_transfer()`, `kspi2_setup_transfer()`, and `kspi2_transfer_one()`. Child management uses `kspi2_register_devices()` and `kspi2_unregister_devices()`.

## Control Flow

Probe allocates a host, retrieves the containing `keba_spi_auxdev`, allocates child-device tracking, maps the auxiliary IO resource, reads the base clock selector, initializes control and CS registers, assigns controller callbacks, registers the controller, and creates each `spi_board_info` child device supplied by the auxiliary device. Before a transfer sequence, the SPI core calls prepare hardware, which polls the IN_USE bit until the hardware semaphore is acquired. Per message, CPOL/CPHA bits are updated through the shadowed control register. Per transfer, the driver validates byte-multiple word widths, selects a divider at or below requested speed, then writes and polls one byte at a time. Unprepare releases the hardware semaphore by writing IN_USE.

## State and Persistence Behavior

The driver keeps a shadow of the control register to avoid redundant writes, an array of child devices to unregister on removal, and base clock state read from hardware. The hardware semaphore state persists in the FPGA register and coordinates with external processors. No filesystem persistence exists; SPI commands may persistently modify attached devices.

## Dependencies and Integration Points

The driver depends on the KEBA auxiliary bus structures from `linux/misc/keba.h`, SPI core, MMIO polling helpers, and auxiliary-driver registration. It matches auxiliary device name `keba.spi`. Child SPI devices come from `keba_spi_auxdev->info`, not from DT child nodes.

## Risks and Edge Cases

Only 8-bit-multiple word widths are supported, but transfers are still processed byte-by-byte, so higher word widths do not change bus packing beyond validation. The hardware semaphore can block for up to 10 seconds and only warns on timeout. `num_chipselect` is 255 and CS register uses `0xff` as none, so chip-select numbering must avoid ambiguity with no-CS semantics. Throughput is limited by per-byte polling. Child device registration failure unwinds previously created devices.

## Test Signals

Test all base clock selector values and invalid selector, semaphore acquisition/release and timeout, CPOL/CPHA mode setup, speed clamping to min/max, byte and multi-byte transfers, RX-only/TX-only/full-duplex, unsupported mode bits, non-byte-multiple word width rejection, chip selects including high values near 255, automatic child creation and unwind, and removal unregistering all children.
