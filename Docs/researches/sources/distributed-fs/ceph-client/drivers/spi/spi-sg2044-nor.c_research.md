# sources/distributed-fs/ceph-client/drivers/spi/spi-sg2044-nor.c

## Purpose

`spi-sg2044-nor.c` is a Sophgo SG2044/SG2042 SPI NOR flash memory-controller driver using the `spi-mem` API. It implements command/register operations and memory reads/writes through a small FIFO, chunking reads at 64 KiB, and selecting SoC-specific FIFO interrupt behavior.

## Important APIs, Types, and Functions

`struct sg204x_spifmc_chip_info` records whether the optional `SPIFMC_OPT` register exists and which read FIFO trigger level to use. `struct sg2044_spifmc` stores the SPI controller, MMIO base, device, mutex, clock, and chip info. Helpers include interrupt and FIFO-pointer pollers, `sg2044_spifmc_init_reg()`, read/write/command paths, register-operation path, `sg2044_spifmc_exec_op()`, hardware init, and probe.

The spi-mem hook table exposes only `.exec_op`. Match data distinguishes `"sophgo,sg2044-spifmc-nor"` from `"sophgo,sg2042-spifmc-nor"`.

## Control Flow

Probe allocates a host, enables the AHB clock, maps registers, sets one chip select and 8-bit spi-mem capabilities, initializes a mutex, gets match data, performs controller init/reset, clears transfer CSR, and registers the controller. `exec_op()` serializes with the mutex and routes address-less operations to `sg2044_spifmc_trans_reg()` and addressed operations to read, write, or command helpers.

Read writes opcode, address bytes, dummy bytes, length, clears interrupts, starts the transfer, waits for read-FIFO interrupt, drains up to 8 bytes at a time after polling FIFO pointer size, waits for transfer done, and clears FIFO pointer. Large reads are split into `SPIFMC_MAX_READ_SIZE` chunks. Write similarly writes opcode/address/dummy, starts transfer, waits for FIFO empty, pushes data in up-to-8-byte batches, waits for done, and clears FIFO pointer. Register reads use dummy writes and optional FIFO-flush suppression.

## State and Persistence Behavior

The driver maintains only the mutex, clock, and controller register state. It does not persist data itself; flash contents and status/configuration registers are persistent in the attached NOR device. Hardware init disables direct memory mapping, resets controller state, sets a conservative clock divider, clears CE control, and seeds transfer CSR defaults.

## Dependencies and Integration Points

The file depends on platform/OF, clocks, MMIO polling, mutexes, and `spi-mem`. It is intended for SPI NOR clients and advertises dual/quad mode bits, though the transfer code currently programs mostly 1-bit bus-width constants and does not implement a supports-op filter.

## Risks and Edge Cases

`sg2044_spifmc_exec_op()` ignores return values from the routed operation helpers and always returns 0, so timeout or I/O errors can be hidden from spi-mem clients. `sg2044_spifmc_trans()` also discards helper return values. The driver advertises dual/quad mode bits but does not clearly program bus width from `op->cmd/addr/dummy/data.buswidth` in normal read/write paths. Address and dummy byte counts are combined into one hardware field, so unsupported combinations need validation. Poll loops use one-second timeouts and no IRQ handler. Register write status opcode `0x01` has special bidirectional configuration that should be checked against NOR behavior.

## Test Signals

Test JEDEC ID/status reads, write-enable/status writes, page program, erase, large reads spanning 64 KiB chunks, timeouts from FIFO and transfer-done waits, SG2042 vs SG2044 match data, dual/quad operations advertised by spi-nor, error propagation from helpers, and concurrent spi-mem access serialization.
