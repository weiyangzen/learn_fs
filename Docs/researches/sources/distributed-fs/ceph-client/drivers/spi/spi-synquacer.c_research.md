# sources/distributed-fs/ceph-client/drivers/spi/spi-synquacer.c

## Purpose
`spi-synquacer.c` is the Socionext Synquacer high-speed SPI controller driver. It registers a platform SPI host for OF or ACPI systems, supports up to four chip selects, 8/16/24/32-bit words, single/dual/quad transfers, configurable clock source, and interrupt-driven FIFO transfer handling.

## Important APIs, Types, And Functions
`struct synquacer_spi` stores device state, transfer completion, cached configuration (`cs`, `bpw`, `mode`, `speed`, bus width, transfer mode), clock source, MMIO base, FIFO word counters, active buffer pointers, and IRQ names. `synquacer_spi_probe()` and `synquacer_spi_remove()` own platform lifecycle. `synquacer_spi_transfer_one()`, `synquacer_spi_set_cs()`, `synquacer_spi_config()`, and `synquacer_spi_enable()` are the central controller operations. FIFO movement happens through `read_fifo()` and `write_fifo()`, while `sq_spi_rx_handler()` and `sq_spi_tx_handler()` handle RX and TX IRQs.

## Control Flow
Probe allocates a host, maps registers, determines clock source from OF `clock-names` or ACPI `socionext,ihclk-rate`, enables the clock, computes min/max speed, reads ACES/RTM properties, requests separate RX and TX IRQs, configures SPI mode and word-size masks, enables the hardware, enables runtime PM, and registers the controller. A transfer begins by clearing stop, flushing FIFOs, optionally promoting aligned 8-bit transfers to 32-bit FIFO access for efficiency, calling `synquacer_spi_config()`, setting active buffers and word counts, seeding TX FIFO when transmitting, programming RX threshold when receiving, clearing interrupts, starting DMSTART, enabling TX or RX interrupts, and waiting for completion.

TX IRQs continue filling FIFO until `tx_words` reaches zero, then disable TX interrupts and complete. RX IRQs drain FIFO when threshold or slave-release status is seen and complete when all RX words are consumed. RX transfers stop the controller afterward and drain leftover FIFO contents into a local scratch buffer.

## State And Persistence
Configuration is cached in `struct synquacer_spi` and reused when speed, width, bpw, mode, CS, and transfer direction are unchanged. Suspend disables the clock after `spi_controller_suspend()` when runtime PM has not already suspended. Resume invalidates the cached speed, enables the clock, re-enables hardware, and resumes the controller. No persistent state exists beyond hardware registers and cached runtime state.

## Dependencies And Integration Points
The file depends on SPI core APIs, platform resources, OF and ACPI matching, clk, runtime PM, MMIO, interrupts, and device properties. OF compatible is `socionext,synquacer-spi`; ACPI ID is `SCX0004`. It integrates optional hardware behaviors through `socionext,set-aces` and `socionext,use-rtm`.

## Risks
Full-duplex dual/quad is explicitly rejected; only 1-bit bus full duplex is allowed. Clock divider limits reject very low requested rates. The driver mutates `xfer->bits_per_word` temporarily to use 32-bit FIFO access and restores it; regressions here would affect SPI core expectations. RX cleanup drains a fixed-depth scratch buffer after stopping, so unexpected residual data larger than FIFO depth would be lost but is intended only as cleanup. Runtime PM ops are represented by system sleep PM only, so clock state assumptions depend on probe/runtime interactions.

## Test Signals
Test 8/16/24/32-bit word transfers, aligned 8-bit transfers divisible by four, RX-only and TX-only paths, unsupported full-duplex dual/quad rejection, low-speed divider rejection, ACES/RTM property behavior, OF and ACPI probing, and suspend/resume reconfiguration. IRQ completion and timeout diagnostics are primary failure signals.
