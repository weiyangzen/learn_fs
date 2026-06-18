<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mt7621.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-mt7621.c

## Purpose

`spi-mt7621.c` is a compact SPI controller driver for the Ralink/MediaTek MT7621 SoC. The hardware is treated as a half-duplex, flash-oriented controller with a small command/data window and native chip select polarity register. The driver deliberately disables claimed full-duplex behavior because the silicon shifts unintended opcode data in that mode.

## Important APIs, Types, and Functions

`struct mt7621_spi` stores the controller pointer, MMIO base, system clock frequency, last programmed speed, and `pending_write` byte count. Register helpers `mt7621_spi_read()` and `mt7621_spi_write()` wrap MMIO accesses. `mt7621_spi_set_native_cs()` selects the hardware slave, forces more-buffer mode, disables full-duplex, and controls active chip-select polarity.

The message and transfer path is implemented by `mt7621_spi_prepare_message()`, `mt7621_spi_prepare()`, `mt7621_spi_wait_till_ready()`, `mt7621_spi_write_half_duplex()`, `mt7621_spi_read_half_duplex()`, `mt7621_spi_flush()`, and `mt7621_spi_transfer_one()`. `mt7621_spi_setup()` clamps and validates requested device speed. Probe maps registers, gets the system clock, allocates/registers the controller, issues `device_reset()`, and advertises two native chip selects.

## Control Flow

Before a message, the driver waits for the transfer register to become idle, scans all transfers to find the lowest requested speed, and programs the controller clock divider. The divider must fit the hardware's 12-bit-ish range, with rates below 2 clamped to 2. The mode programming honors LSB-first but clears CPHA/CPOL because only mode 0 is considered reliable on this controller.

Write transfers accumulate bytes into the opcode/data registers using the hardware's unusual opcode byte ordering. Once the buffer reaches 36 bytes or the transfer ends, `mt7621_spi_flush()` triggers a half-duplex operation with no RX bytes. Read transfers combine any pending write prefix with the read transaction, program `MOREBUF` with TX and RX bit counts, start the transaction, wait for completion, and copy up to 32 RX bytes per iteration from the DATA registers.

`transfer_one` rejects simultaneous TX and RX buffers with `-EIO`, otherwise dispatches to the read or write half-duplex helper and returns synchronously.

## State and Persistence Behavior

The only persistent driver state is per-controller runtime state in `struct mt7621_spi`. `pending_write` is a transient batching mechanism that lets a write prefix be combined with a subsequent read, which matches flash command/address/read patterns. `speed` records the last requested speed but is not used as a skip cache in the current path.

There is no host-side persistence; persistent side effects are operations performed by attached SPI devices.

## Dependencies and Integration Points

The driver depends on the platform bus, device tree compatible `ralink,mt7621-spi`, clock framework, reset framework, MMIO helpers, and the SPI core. It exposes `SPI_CONTROLLER_HALF_DUPLEX`, `SPI_LSB_FIRST`, 8-bit words, GPIO descriptor support, and two native chip selects.

## Risks and Edge Cases

The driver intentionally forces mode 0 despite advertising only `SPI_LSB_FIRST` mode bits; devices requiring other modes are not supported. `mt7621_spi_wait_till_ready()` uses a fixed 2000 microsecond polling loop, so unusually slow hardware or long operations may timeout. The pending-write batching and opcode swizzling are fragile because the first four bytes are written with different byte order than later data registers. Full-duplex requests fail by design.

`mt7621_spi_prepare_message()` uses each transfer's `speed_hz` directly; if a transfer has zero speed, it can become the selected minimum and later cause invalid divider behavior unless upper layers normalize it.

## Test Signals

Tests should cover mode-0 flash transactions, command/address write followed by read, TX-only transfers over 36 bytes, reads over 32 bytes, native CS0/CS1 polarity behavior, GPIO chip select fallback, divider bounds for max and minimum speeds, reset failure, busy timeout, and explicit rejection of full-duplex transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mt7621.c -->
