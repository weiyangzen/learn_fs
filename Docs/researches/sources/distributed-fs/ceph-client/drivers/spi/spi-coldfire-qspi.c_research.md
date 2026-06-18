# sources/distributed-fs/ceph-client/drivers/spi/spi-coldfire-qspi.c

## Purpose

`spi-coldfire-qspi.c` is the Freescale/Motorola ColdFire queued SPI controller driver. It uses the QSPI command/data RAM, an interrupt-backed waitqueue, platform-supplied chip-select callbacks, and optional runtime/system PM clock gating to perform 8-bit and 16-bit transfers.

## Important APIs, Types, and Functions

`struct mcfqspi` stores MMIO base, IRQ, clock, platform CS callbacks, and waitqueue. Register helpers wrap QMR/QDLYR/QWR/QIR/QAR/QDR accesses. Transfer engines `mcfqspi_transfer_msg8()` and `mcfqspi_transfer_msg16()` fill command and TX buffers, run queued transfers in 16-entry then 8-entry ping-pong chunks, wait for SPE to clear, and drain RX. `mcfqspi_transfer_one()` programs mode/baud and dispatches the right engine. `mcfqspi_set_cs()`, `mcfqspi_setup()`, `mcfqspi_probe()`, `mcfqspi_remove()`, and PM callbacks provide SPI integration.

## Control Flow

Probe requires platform data and `cs_control`, allocates a host, maps registers, requests IRQ, enables `qspi_clk`, initializes chip-select callbacks, creates the waitqueue, sets mode and bits-per-word capabilities, enables runtime PM, and registers the controller. A transfer programs QMR for master, bits per word, CPOL/CPHA, and baud divisor. It enables SPIF interrupt, runs the 8- or 16-bit queued transfer routine, then disables interrupts. The IRQ clears SPIF and wakes the waitqueue used by the transfer routines.

## State and Persistence Behavior

Persistent state is limited to controller registers, the platform CS backend, and clock/runtime PM state. Per-transfer data remains on the stack inside transfer routines and blocks until completion. Remove unregisters, disables runtime PM, programs QMR to master with baud 0, and tears down chip-select callbacks.

## Dependencies and Integration Points

The driver depends on ColdFire architecture headers, platform data (`struct mcfqspi_platform_data` and CS control callbacks), MMIO, IRQs, clocks, runtime PM, and the SPI core. It does not use OF parsing in this file.

## Risks and Edge Cases

The waitqueue waits have no explicit timeout, so lost interrupts or stuck SPE can hang the transfer. In the no-TX-buffer path of `mcfqspi_transfer_msg8()`, the initial fill loop iterates over `count` instead of `n`, which may overrun the 16-entry RAM window for large RX-only transfers; the 16-bit path uses `n`. Baud calculation uses the `MCF_BUSCLK / 2` macro rather than the enabled clock rate. The driver assumes platform CS callbacks are valid and synchronous.

## Test Signals

Tests should cover missing platform data, missing CS callbacks, IRQ and clock failures, 8-bit and 16-bit TX/RX/RX-only transfers, lengths 1, 8, 16, 17, and large multi-chunk transfers, CS polarity callbacks, runtime/system suspend/resume, stuck SPE/interrupt loss, and the RX-only command RAM fill boundary.
