# sources/distributed-fs/ceph-client/drivers/spi/spi-cadence-xspi.c

## Purpose

`spi-cadence-xspi.c` is the Cadence XSPI flash controller driver. It primarily implements `spi-mem` STIG command execution with SDMA data movement, plus Marvell CN10 hardware-overlay support for PHY setup, clock programming, 64-bit SDMA FIFO access, and a special generic `transfer_one_message` path.

## Important APIs, Types, and Functions

`struct cdns_xspi_dev` stores the platform device, SPI controller, IO/AUX/SDMA/XFER windows, IRQ, completions, current chip select, SDMA buffers, hardware bank count, Marvell-overlay state, and handler callbacks. `struct cdns_xspi_driver_data` supplies overlay selection and PHY register defaults.

Important functions include `cdns_xspi_controller_init()`, `cdns_xspi_send_stig_command()`, `cdns_xspi_mem_op_execute()`, `marvell_xspi_mem_op_execute()`, `cdns_xspi_supports_op()`, `cdns_xspi_adjust_mem_op_size()`, `cdns_xspi_irq_handler()`, `cdns_xspi_probe()`, and PM callbacks. Marvell-specific helpers include `cdns_mrvl_xspi_setup_clock()`, `cdns_xspi_configure_phy()`, `marvell_xspi_sdma_handle()`, `cdns_xspi_transfer_one_message_b0()`, and generic command packing/readback helpers.

## Control Flow

Probe allocates a host, selects driver data from OF match, assigns standard or Marvell mem ops and handler callbacks, validates child chip-select `reg` values, maps IO/SDMA/AUX and optional XFER resources, requests a shared IRQ, configures Marvell clock/PHY if needed, validates controller magic/features, sets `num_chipselect` from hardware bank count, and registers the controller.

For a `spi-mem` operation, the driver updates `cur_cs`, waits for the controller to become idle, switches to STIG mode, enables interrupts, emits a profile-1 instruction command, optionally emits a data sequence command, waits for SDMA trigger and STIG done completions, drains/fills SDMA through the selected handler, disables interrupts, and checks command status bits for DQS/CRC/bus/sequence errors. The Marvell mem path first reprograms the overlay clock based on the SPI device speed.

The Marvell B0 message path enables an XFER state machine, chunks transfers into up to 32 qwords, uses generic STIG commands for small transfers or a generic command plus SDMA data sequence for larger transfers, reads returned qwords through overlay registers with bit reversal, honors delays, and releases the state machine unless `cs_change` keeps CS active.

## State and Persistence Behavior

The driver maintains volatile controller state only: current CS, SDMA buffer pointers for the active command, completion state, SDMA error flag, Marvell PHY/clock state, and ongoing generic-transfer qword index. Persistent side effects are limited to SPI flash operations and controller/PHY register programming. Suspend stops the SPI controller through `spi_controller_suspend()`. Resume reconfigures Marvell clock/PHY, disables controller interrupts, and resumes the core.

## Dependencies and Integration Points

The file integrates with platform resources named `io`, `sdma`, `aux`, and optionally `xfer`, OF child nodes, Linux `spi-mem`, IRQ completions, MMIO accessors, bitfield helpers, PM sleep callbacks, and the SPI controller framework. Supported compatibles are `cdns,xspi-nor` and `marvell,cn10-xspi-nor`.

## Risks and Edge Cases

The completion objects are not reinitialized before each command, so stale completions would be a concern if a previous command completed before the next wait; IRQ ordering should be reviewed carefully. `cdns_xspi_supports_op()` mutates `spi->mode` while answering support queries under ACPI builds, which can make support probing stateful. `cdns_xspi_adjust_mem_op_size()` clamps all data directions to SDMA size, including no-data operations. The Marvell generic message path decrements `t->len` in-place, which is unusual for SPI transfer descriptors. Busy-wait timeouts are short and may be sensitive to slow firmware/hardware. PHY lock polling appears to read the interrupt status register for `CDNS_XSPI_DLL_LOCK`, so register selection should be checked against the hardware manual.

## Test Signals

Validation should cover standard and Marvell probe, bad magic number, child CS out of range, missing resource fallback by index, IRQ request failure, STIG no-data commands, read/write SDMA commands at SDMA-size boundary, injected SDMA errors, command status failure bits, Marvell clock divisor changes, suspend/resume reinitialization, and B0 generic-message transfers below 10 bytes, above 10 bytes, exact qword multiples, partial qwords, and `cs_change` sequences.
