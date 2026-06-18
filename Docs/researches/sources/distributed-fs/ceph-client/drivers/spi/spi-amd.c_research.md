# sources/distributed-fs/ceph-client/drivers/spi/spi-amd.c

## Purpose

`spi-amd.c` implements the common AMD SPI master and SPI-MEM controller logic. It supports ACPI platform devices `AMDI0061`, `AMDI0062`, and `AMDI0063`, plus the PCI HID2 front-end through `amd_spi_probe_common()`.

The driver supports generic SPI messages through a FIFO/index command path and SPI-MEM operations for serial memories. HID2 adds DMA-style read/write support using a coherent 4 KiB-aligned buffer.

## Important APIs, types, and functions

- Register access helpers read/write 8/16/32/64-bit MMIO registers.
- `amd_spi_set_opcode()`, `amd_spi_set_rx_count()`, `amd_spi_set_tx_count()`, `amd_spi_busy_wait()`, and `amd_spi_execute_opcode()` abstract version-specific command execution.
- `amd_set_spi_freq()` chooses one of the hardware-supported speed encodings from `amd_spi_freq[]`.
- `amd_spi_fifo_xfer()` implements generic SPI message transfer through the FIFO, extracting the first TX byte as opcode.
- `amd_spi_supports_op()`, `amd_spi_adjust_op_size()`, and `amd_spi_exec_mem_op()` implement SPI-MEM validation and execution.
- `amd_spi_mem_data_in()`/`amd_spi_mem_data_out()` choose HID2 DMA paths for supported memory operations or fallback to index FIFO mode.
- `amd_spi_setup_hiddma()` allocates the coherent DMA buffer and programs HID2 interrupt/control registers.
- `amd_spi_probe_common()` fills the SPI controller fields and registers it; both the platform probe and PCI wrapper use it.

## Control flow

Platform probe maps MMIO from the platform resource, sets the version from ACPI match data, assigns bus 0, and calls common probe. The PCI wrapper maps HID2 registers separately and calls the same common path.

Generic SPI message flow selects the chip, walks `spi_message` transfers to collect opcode, TX data, RX length, and speed, writes FIFO/count registers, executes the opcode, waits for completion if RX is needed, reads FIFO data back, clears chip select on V2/HID2, and finalizes the message.

SPI-MEM flow checks opcode and size constraints, clamps operation size, sets per-op frequency, optionally toggles V2 4-byte address mode, then runs data-in or data-out. HID2 read/write commands use dedicated HID control registers and a coherent buffer; other paths use opcode/address/count/FIFO registers and busy polling.

## State and persistence behavior

`struct amd_spi` stores the MMIO base, current speed, hardware version, and HID2 DMA buffer address. Hardware state includes chip select, FIFO pointer, opcode/count registers, speed registers, V2 address mode, HID2 ring/output buffer registers, interrupt status, and control bits. Device-managed resources own controller registration and DMA allocation.

One subtle state issue: `amd_spi_probe_common()` registers the controller before calling `amd_spi_setup_hiddma()` for HID2. That means the controller can theoretically become visible before HID2 DMA setup succeeds.

## Dependencies and integration points

The driver depends on ACPI, platform devices, MMIO, DMA coherent allocation, SPI core, SPI-MEM, and the shared declarations in `spi-amd.h`. It exports `amd_spi_probe_common()` to the PCI wrapper.

## Risks and edge cases

- HID2 DMA helper functions poll interrupt status but ignore the return value from `readw_poll_timeout()`, so timeout failures may not propagate.
- The coherent DMA setup happens after `devm_spi_register_controller()`, which can leave a registered controller if HID2 setup fails.
- Generic FIFO transfer decrements `xfer->len` when consuming the opcode from the first TX transfer, mutating the transfer object.
- FIFO/index mode is capped at 64 data bytes, while the generic `max_transfer_size` reports 70 bytes including opcode/address overhead.
- HID2 read control computes `(op->data.nbytes / 4) - 1`; non-multiple-of-4 sizes need careful validation.
- Quad mode is limited to read operations by `supports_op()`, with write support limited to page-program opcodes.

## Test signals

Build with ACPI and PCI front-ends. Runtime tests should cover AMDI0061/0062/0063, generic SPI messages, SPI-MEM read/write/status operations, speed changes, V2 4-byte reads, HID2 4 KiB DMA reads and writes, non-4-byte-aligned lengths, chipselect handling for all four chipselects, and timeout injection for busy and HID2 interrupt polls.
