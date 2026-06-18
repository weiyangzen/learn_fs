
# sources/distributed-fs/ceph-client/include/trace/events/spi.h

## Purpose
Defines core SPI tracepoints for controller idle/busy state, device setup, chip-select changes, message submit/start/done, and transfer start/stop including sampled TX/RX buffers.

## Important APIs, Types, and Functions
Event classes include `spi_controller`, `spi_message`, and `spi_transfer`. Events include `spi_controller_idle`, `spi_controller_busy`, `spi_setup`, `spi_set_cs`, `spi_message_submit`, `spi_message_start`, `spi_message_done`, `spi_transfer_start`, and `spi_transfer_stop`. Helper macros `spi_valid_txbuf()` and `spi_valid_rxbuf()` bound dynamic buffer copying by message optimization flags and transfer length.

## Control Flow
SPI core/controller code emits controller state transitions, setup and chip-select events around device configuration, message events through queue/execute/complete flow, and transfer events around individual transfers. Transfer events copy bounded TX/RX bytes for visibility.

## State and Persistence
No SPI state is persisted here. Trace records copy bus number, chip select, mode, max speed, message/transfer pointers, status, lengths, and optional data bytes. Pointer fields are correlation aids only.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h` and SPI core structures. Integrates with SPI controller drivers, SPI protocol drivers, spidev diagnostics, and logic-analyzer correlation.

## Risks
Copying transfer buffers can expose device data and add overhead. Optimized or controller-mutated messages may not have valid buffers for copying, hence the helper guards. Chip-select and mode fields must remain aligned with SPI core semantics.

## Test Signals
Signals include SPI message queue tests, setup/mode changes, chip-select toggling, full-duplex transfer tracing, optimized message paths, error status injection, and trace payload comparison to known transfers.
