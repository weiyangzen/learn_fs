# sources/distributed-fs/ceph-client/drivers/spi/spi-bcmbca-hsspi.c

## Purpose
Implements the Broadcom BCMBCA High Speed SPI controller driver for `brcm,bcmbca-hsspi-v1.1`. It is a newer HSSPI variant with a separate `spim-ctrl` chip-select override register, polling/interrupt completion modes, dual-bit support, and explicit SPI message-level chip-select handling.

## Important APIs, Types, And Functions
`struct bcmbca_hsspi` stores completion, bus/message mutexes, platform/clock resources, HSSPI and SPIM control MMIO bases, FIFO pointer, base speed, chip-select polarity cache, and wait mode. Sysfs exposes only `wait_mode`. Main helpers are `bcmbca_hsspi_set_cs()`, `bcmbca_hsspi_set_clk()`, `bcmbca_hsspi_wait_cmd()`, `bcmbca_hsspi_do_txrx()`, `bcmbca_hsspi_setup()`, `bcmbca_hsspi_transfer_one()`, and the IRQ handler.

## Control Flow
Probe maps named `hsspi` and `spim-ctrl` resources, enables `hsspi` or fallback `pll` clock, allocates the host, initializes locks/completion, configures SPI core callbacks, clears interrupts, caches default CS polarity, requests IRQ, enables runtime PM, creates the sysfs group, and registers the controller. Setup programs latch/launch edge behavior, CS polarity in the HSSPI global register, and override output polarity in `spim_ctrl`. Message transfer locks `msg_mutex`, runs each transfer through FIFO chunks, asserts CS as close as possible to command start, handles delays and `cs_change` between transfers, updates actual length, and deasserts CS unless the final transfer requests it remain active.

## State And Persistence
Persistent state includes MMIO bases, clocks, FIFO pointer, base speed, cached CS polarity, and sysfs-controlled `wait_mode`. Per-transfer state is local in `bcmbca_hsspi_do_txrx()`. `bus_mutex` protects shared global and SPIM control register changes; `msg_mutex` serializes transfer policy and wait-mode changes. Suspend disables clocks after SPI controller suspend; resume restores clocks and resumes the controller.

## Dependencies And Integration Points
The driver depends on Linux SPI, platform named resources, clocks, IRQs, sysfs, mutexes, completions, runtime PM, and OF. It advertises CPOL/CPHA/CS_HIGH plus RX/TX dual and 8-bit words. Unlike the older BCM63xx HSSPI driver, it does not expose xfer-mode sysfs or prepend logic; chip select is controlled through the external SPIM control override register.

## Risks And Edge Cases
CS 7 is special-cased to skip override, which is board-specific and can hide failures on other designs. `bcmbca_hsspi_do_txrx()` accepts a `msg` parameter but does not use it, so future changes should avoid assuming message context is active there. Interrupt-mode completion requires stale interrupt status to be cleared when switching modes. FIFO chunking must respect opcode space for TX/write operations. As with other HSSPI drivers, global clock polarity and CS polarity are shared hardware state protected by locks.

## Test Signals
Test polling and interrupt wait modes, all usable chip selects including CS7 behavior, CPOL/CPHA setup, CS_HIGH polarity, dual TX/RX transfers, FIFO boundary chunking, `cs_change` and `cs_off` sequencing, suspend/resume, and probe failure cleanup after sysfs registration. Timeout logs and missing deassertions on logic analyzer traces are key failure signals.
