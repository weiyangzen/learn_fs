# sources/distributed-fs/ceph-client/drivers/spi/spi-microchip-core-qspi.c

## Purpose

`spi-microchip-core-qspi.c` drives the Microchip coreQSPI controller. It supports regular SPI transfers plus optimized `spi-mem` operations for SPI flash, including single/dual/quad modes, software chip-select control, command/data frame programming, and interrupt completion.

## Important APIs, Types, And Functions

`struct mchp_coreqspi` stores MMIO, clock, completion, operation mutex, current TX/RX buffers and lengths, and IRQ. Important helpers are `mchp_coreqspi_set_mode()`, `mchp_coreqspi_set_cs()`, `mchp_coreqspi_setup_clock()`, `mchp_coreqspi_config_op()`, FIFO routines for read/write/write-read, `mchp_coreqspi_isr()`, and `mchp_coreqspi_wait_for_ready()`. `spi-mem` integration is `mchp_coreqspi_exec_op()`, `mchp_coreqspi_supports_op()`, and `mchp_coreqspi_adjust_op_size()`.

## Control Flow, State, And Persistence

Probe maps registers, enables the clock, initializes completion/mutex, requests a shared IRQ, configures chip-select count, advertises SPI memory caps, enables master/controller mode, puts CS into software direct mode, and registers the controller. Memory ops lock the device, wait ready, configure per-op clock and line mode, program frame counts and dummy cycles, assert CS, push opcode/address/data or prepare RX, enable interrupts, wait for completion, then deassert CS and disable interrupts. Regular SPI messages use prepare/unprepare to lock, configure frames over all transfers, apply dual/quad mode, and add a required 750 us unprepare delay.

State is volatile register configuration plus serialized in-flight buffer pointers. No persistent storage exists.

## Dependencies And Integration Points

The driver depends on platform/OF, clocks, interrupts, MMIO polling, SPI core, and `spi-mem`. It matches `microchip,coreqspi-rtl-v2` and advertises per-operation frequency support.

## Risks And Test Signals

Risks include busy-wait FIFO loops, unaligned word accesses, complex frame accounting, unsupported quad-write extended-read-only cases, and mutex/IRQ completion paths that can leave CS asserted on error. Test with spi-nor command negotiation, dual/quad reads, rejected quad program ops, regular `spi_sync()` transfers, transfers above 256 bytes through adjusted op size, timeout/IRQ loss, and CS polarity/GPIO CS combinations.
