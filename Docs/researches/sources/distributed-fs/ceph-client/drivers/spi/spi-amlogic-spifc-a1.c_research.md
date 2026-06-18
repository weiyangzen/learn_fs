# sources/distributed-fs/ceph-client/drivers/spi/spi-amlogic-spifc-a1.c

## Purpose

`spi-amlogic-spifc-a1.c` is a SPI-MEM-only driver for the Amlogic A1 SPI flash controller. It programs a user-command engine and a 512-byte data buffer to execute memory operations with single, dual, or quad bus widths.

## Important APIs, types, and functions

- `struct amlogic_spifc_a1` stores the SPI controller, clock, device, MMIO base, and cached current speed.
- `amlogic_spifc_a1_request()` starts a user request and polls for finish, plus data-updated for reads.
- `amlogic_spifc_a1_fill_buffer()` and `amlogic_spifc_a1_drain_buffer()` write/read the controller data buffer with 32-bit repeated IO and pad handling.
- `amlogic_spifc_a1_set_cmd()`, `set_addr()`, and `set_dummy()` program operation phases.
- `amlogic_spifc_a1_read()` and `write()` configure DIN/DOUT and trigger a request.
- `amlogic_spifc_a1_exec_op()` translates a `spi_mem_op` into command/address/dummy/data phases.
- `amlogic_spifc_a1_adjust_op_size()` clamps data transfers to `SPIFC_A1_BUFFER_SIZE`.
- PM callbacks disable/enable the clock and reinitialize hardware.

## Control flow

Probe maps MMIO, enables the controller clock, initializes hardware timing and AHB settings, enables runtime PM, configures the SPI controller for SPI-MEM with per-op frequency, and registers it.

For each SPI-MEM operation, the driver sets the requested clock rate, clears user registers, writes command/address/dummy configuration, resets the data-buffer pointer for data operations, then either reads, writes, or issues a no-data request. Reads wait for both finish and data-updated bits before draining the buffer.

## State and persistence behavior

The cached `curr_speed_hz` avoids redundant `clk_set_rate()` calls. Hardware state includes user control registers, data-buffer pointer, AHB enable state, timing register, and the clock rate. Runtime suspend disables the clock; resume calls `hw_init()` to restore baseline hardware state.

## Dependencies and integration points

The driver depends on OF platform probing (`amlogic,a1-spifc`), an unnamed clock, MMIO resources, runtime PM, and the SPI-MEM framework. It supports one chip select and 8-bit words with dual/quad TX/RX mode bits.

## Risks and edge cases

- The driver does not define a `supports_op()` callback; it relies on SPI-MEM defaults plus hardware errors and size adjustment.
- Dummy cycles are computed as `dummy.nbytes << 3` and do not divide by dummy bus width.
- `ilog2(buswidth)` assumes bus widths are powers of two; invalid widths should be filtered by the SPI-MEM framework.
- Buffer size is limited to 512 bytes, so large memory operations are split by the core.
- Runtime PM must keep the clock enabled during transfers through `auto_runtime_pm`.

## Test signals

Build with `CONFIG_SPI_AMLOGIC_SPIFC_A1`. Runtime tests should cover read ID/status, small and 512-byte reads/writes, split larger SPI-MEM operations, dual/quad modes, dummy cycles, per-op clock changes, runtime suspend/resume, and system sleep resume preserving hardware initialization.
