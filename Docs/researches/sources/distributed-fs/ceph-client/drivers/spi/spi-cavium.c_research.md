# sources/distributed-fs/ceph-client/drivers/spi/spi-cavium.c

## Purpose

`spi-cavium.c` is the shared transfer engine for Cavium OCTEON/ThunderX MPI SPI controllers. It implements polling, register programming, chip-select retention, byte chunking, and message finalization for the platform and PCI front-ends.

## Important APIs, Types, and Functions

`octeon_spi_transfer_one_message()` is the exported controller callback used by both front-ends. It iterates message transfers and calls `octeon_spi_do_transfer()`. `octeon_spi_do_transfer()` configures `cvmx_mpi_cfg`, writes up to nine bytes at a time to DAT registers, starts transfers through `cvmx_mpi_tx`, polls readiness via `octeon_spi_wait_ready()`, copies received bytes, and executes transfer delays. `octeon_spi_wait_ready()` loops on the MPI busy bit.

## Control Flow

For each `spi_transfer`, the core computes CPHA/CPOL-derived idle and late-CS settings, a clock divisor from `sys_freq` and requested speed, CS polarity, LSB-first, 3-wire mode, and per-CS enable bits. It writes the config register only when it changes. The data path splits transfers into `OCTEON_SPI_MAX_BYTES` chunks of nine bytes. Full chunks force `leavecs = 1`; the final chunk sets `leavecs` according to whether this is the last transfer and `cs_change`. RX data is read back after each hardware transaction. The message callback accumulates actual length, stops on errors, sets message status, and finalizes the message.

## State and Persistence Behavior

The shared state in `struct octeon_spi` caches `last_cfg` to avoid redundant config writes and `cs_enax` to keep CS enable bits accumulated for chip selects below four. Per-transfer pointers and lengths are local. No persistent host storage is written; hardware registers retain the latest config until overwritten or cleared by front-end remove.

## Dependencies and Integration Points

The file depends on the SPI core, delay helpers, 64-bit MMIO accessors, and `spi-cavium.h` register/bitfield definitions. It is not a module by itself; front-ends compile and call it.

## Risks and Edge Cases

`octeon_spi_wait_ready()` has no timeout, so broken hardware can spin indefinitely. The clock divisor calculation does not clamp or reject zero `speed_hz`, and `clkdiv` can become zero or out of hardware range depending on inputs. Transfers larger than nine bytes are handled, but all operations are CPU-polling and synchronous. RX-only transfers use `txnum = 0` but `totnum` nonzero; hardware behavior must match that assumption. The cached `cs_enax` only sets bits and never clears per-device CS enable bits until front-end remove.

## Test Signals

Functional tests should cover TX-only, RX-only, full-duplex, transfers crossing nine-byte boundaries, `cs_change` across multi-transfer messages, all advertised mode bits, LSB-first, 3-wire, chip selects 0-3, and transfer delays. Fault tests should include bad speed values and simulated stuck busy bit to motivate timeout handling.
