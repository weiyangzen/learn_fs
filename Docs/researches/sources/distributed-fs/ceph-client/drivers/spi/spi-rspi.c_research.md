# sources/distributed-fs/ceph-client/drivers/spi/spi-rspi.c

## Purpose

`spi-rspi.c` is the Renesas RSPI/QSPI controller driver for legacy SH RSPI, RZ RSPI, and R-Car Gen2 QSPI variants. It handles register-layout differences through `struct spi_ops`, supports PIO and optional DMA, can use multiplexed or split RX/TX IRQs, and exposes dual/quad transfer modes for QSPI.

## Important APIs, Types, and Functions

`struct rspi_data` stores MMIO base, current speed, controller and platform device, waitqueue, lock for `RSPI_SSLP`, clock, cached command/status/pin-control fields, IRQ numbers, variant ops, DMA completion flag, and byte-access mode. `struct spi_ops` supplies variant-specific configuration and transfer methods plus clock divisors, flags, FIFO size, and native-SS count.

Configuration helpers include `rspi_set_rate()`, `rspi_set_config_register()`, `rspi_rz_set_config_register()`, `qspi_set_config_register()`, and `qspi_setup_sequencer()`. Transfer helpers include interrupt waits, byte PIO, `rspi_dma_transfer()`, RSPI/RZ/QSPI transfer functions, and QSPI trigger programming. Lifecycle code includes DT parsing, reset control deassert/assert action, IRQ setup, DMA channel setup, probe/remove, and PM suspend/resume.

## Control Flow

Probe selects variant ops from OF or platform id, parses chip-select count and optional reset, maps registers, gets the clock, enables runtime PM, initializes waitqueue/lock, sets SPI controller mode bits and speed bounds, requests either a mux IRQ or separate RX/TX IRQs, optionally requests DMA channels, and registers the controller.

For each message, `rspi_prepare_message()` selects the minimum transfer speed, builds `spcmd` from SPI mode/CS/bit order, configures polarity through `RSPI_SSLP`, programs variant configuration registers, optionally programs the QSPI sequencer for multiple single/dual/quad modes, and enables the SPI function. Transfer uses DMA when available and length exceeds variant FIFO size; `-EAGAIN` falls back to PIO. PIO waits for TX empty and RX full via IRQ-backed waitqueues. QSPI reads and writes program FIFO trigger thresholds and sequence modes. Unprepare disables the SPI function and resets the sequencer.

## State and Persistence Behavior

State is runtime-only: current speed, `spcmd`, `spsr`, `sppcr`, IRQ wait state, DMA completion flag, byte-access selection, and SSL polarity. No persistent storage is used. Reset controls are deasserted during probe and asserted automatically by devm action on teardown when present.

## Dependencies and Integration Points

The file depends on platform/OF, clocks, reset controls, PM runtime, DMAengine, SH DMA compatibility filters, waitqueues, spinlocks, interrupts, and SPI core message hooks. It supports `renesas,rspi`, `renesas,rspi-rz`, and `renesas,qspi` compatibles and legacy `"rspi"` platform IDs.

## Risks and Edge Cases

DMA temporarily disables the normal RX/TX IRQ lines because hardware needs SPxIE bits set for DMA; IRQ balance must be restored on every failure path. `rspi_wait_for_interrupt()` uses cached `rspi->spsr` updated by IRQ handlers, so lost interrupts cause HZ timeouts. `qspi_setup_sequencer()` supports only four distinct mode runs per message. Clock calculations round divisors and then overwrite `speed_hz` with the effective value; boundary speeds need validation. PIO transfer ignores the return from the final `rspi_wait_for_tx_empty()` in `rspi_common_transfer()`.

## Test Signals

Run RSPI SH, RSPI RZ, and QSPI variants with PIO and DMA, mux and split IRQs, active-high CS through native and GPIO CS, loopback, dual/quad QSPI read/write sequences, more-than-four QSPI mode changes, DMA fallback, timeout injection on TX/RX waits, reset-control probe failures, and suspend/resume.
