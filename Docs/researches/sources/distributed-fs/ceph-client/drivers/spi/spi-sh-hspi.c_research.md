# sources/distributed-fs/ceph-client/drivers/spi/spi-sh-hspi.c

## Purpose

`spi-sh-hspi.c` is a simple SuperH HSPI SPI host driver. It uses programmed I/O only, manually controls hardware chip select, computes the closest clock divisor for each transfer, and completes whole SPI messages synchronously through `transfer_one_message`.

## Important APIs, Types, and Functions

`struct hspi_priv` stores MMIO base, controller, device, and clock. Register helpers are `hspi_write()`, `hspi_read()`, and `hspi_bit_set()`. `hspi_status_check_timeout()` polls status bits with a fixed retry loop. `hspi_hw_setup()` programs clock divisor and CPOL/CPHA. `hspi_transfer_one_message()` performs byte-by-byte transfers with CS handling. Probe/remove handle resource mapping, clock acquisition, runtime PM enable, controller registration, and cleanup.

## Control Flow

Probe obtains the memory resource, allocates a SPI host, gets the clock, maps registers, enables runtime PM, sets mode and 8-bit word capabilities, installs `transfer_one_message`, and registers. For each message, the transfer loop sets up hardware and asserts CS when starting a CS segment, writes one byte to SPTBR after waiting for TX space, waits for RX ready, reads SPRBR into the RX buffer when present, applies transfer delay, and deasserts CS when `cs_change` or message end requires it.

## State and Persistence Behavior

State is minimal and runtime-only: MMIO register contents, clock, and CS level. There is no persistent state and no DMA/IRQ state. Attached SPI devices own any persistent side effects.

## Dependencies and Integration Points

The driver uses platform resources, clocks, runtime PM, MMIO, and the SPI core. It supports only 8-bit words and CPOL/CPHA mode bits. OF matching recognizes `renesas,hspi`.

## Risks and Edge Cases

`msg->actual_length` is incremented by `t->len` even if an inner byte loop breaks early after a timeout, so partial failures may overreport transferred bytes. Clock selection brute-forces 64 divisor settings but does not reject large frequency error. `spi_transfer_delay_exec()` runs after the byte loop even if a timeout occurred in that transfer. There is no DMA or interrupt support, so long messages burn CPU and depend on fixed polling delays.

## Test Signals

Test all four modes, CS hold and `cs_change`, TX-only/RX-only/full-duplex messages, timeout paths for TX and RX status bits, requested speeds across divisor boundaries, probe/remove clock cleanup, runtime PM, and actual_length on injected mid-transfer failure.
