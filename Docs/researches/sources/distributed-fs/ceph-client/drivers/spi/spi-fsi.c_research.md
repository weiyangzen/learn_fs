# sources/distributed-fs/ceph-client/drivers/spi/spi-fsi.c

## Purpose
Exposes SPI controllers attached behind an IBM FSI2SPI bridge. The driver discovers child SPI controllers under an FSI engine, checks that the upstream FSI mux is configured for SPI, and implements half-duplex SPI message execution through 64-bit bridge register accesses and a hardware sequencer.

## Important APIs, Types, And Functions
`struct fsi2spi` stores the shared FSI engine and mutex. `struct fsi_spi` stores each SPI controller device, bridge pointer, and base offset. Register access flows through `fsi_spi_read_reg()` and `fsi_spi_write_reg()`, with `fsi_spi_check_status()` validating the FSI2SPI interface. SPI-side helpers include `fsi_spi_reset()`, `fsi_spi_status()`, sequence builders, `fsi_spi_transfer_init()`, `fsi_spi_transfer_data()`, and `fsi_spi_transfer_one_message()`. Probe is `fsi_spi_probe()`.

## Control Flow
Probe first validates the mux via `FSI_MBOX_ROOT_CTRL_8`, allocates one bridge state, then creates one SPI controller for each available child node with a `reg` base. Message execution validates the mux again, then for each transfer requires a TX phase first, builds a sequence selecting slave `cs + 1`, emits shift-out chunks of up to eight bytes, optionally folds the next RX or TX transfer into the same sequence, deselects the slave, writes the sequence register, and moves data through `DATA_TX` or `DATA_RX`. TX waits for TDR not full; RX waits for RDR full.

## State And Persistence
The bridge mutex serializes all register accesses across child controllers. Controller state is the per-child base plus runtime status/reset state in hardware. The driver clears errors by resetting clock/status registers. No persistent storage is used.

## Dependencies And Integration Points
Depends on the FSI subsystem, big-endian FSI register access, OF child nodes, and the SPI core. It registers as an FSI driver for engine ID `0x23` and creates standard SPI controllers with `SPI_CONTROLLER_HALF_DUPLEX`.

## Risks
Transfer shapes are tightly constrained: TX must precede RX, RX is at most 8 bytes, TX chunks are limited, and only simple adjacent transfer folding is supported. Poll loops use 1 second timeouts. Mux misconfiguration returns `-ENOLINK`/`-ENODEV`, and bridge errors trigger reset.

## Test Signals
Mux-disabled probe, multiple child controllers, TX-only commands, TX+RX command/read pairs, timeout paths, bridge status error reset, max transfer size enforcement, and concurrent controller access through the bridge mutex are the main signals.
