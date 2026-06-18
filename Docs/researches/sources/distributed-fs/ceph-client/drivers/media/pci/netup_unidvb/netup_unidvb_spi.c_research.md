# sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/netup_unidvb_spi.c

Purpose: Implements an internal SPI controller for NetUP Universal Dual DVB-CI cards, primarily to expose the onboard FPGA flash as an MTD SPI NOR device for firmware maintenance.

Important APIs, types, and functions: `struct netup_spi_regs` describes a 1024-byte data window plus control/status and clock-divider registers. `struct netup_spi` stores the SPI controller, register base, spinlock, waitqueue, and transfer state. `netup_spi_init()` allocates/registers the SPI host, enables SPI interrupts, and creates an `m25p128` child device with a read-only 16 MiB partition. `netup_spi_transfer()` implements `transfer_one_message` by fragmenting transfers into <=1024-byte hardware operations. `netup_spi_interrupt()` acknowledges completion and wakes the transfer waitqueue. `netup_spi_release()` unregisters and masks IRQs.

Control flow: Initialization attaches a devm SPI host to the PCI device, sets mode capabilities, assigns one chip select, maps the controller at BAR0 offset `0x4000`, programs clock divider `2`, enables `NETUP_UNIDVB_IRQ_SPI`, registers the controller, then instantiates the flash device. Each SPI transfer resets chip select, iterates message transfers and fragments, copies TX data or zero fill into MMIO, starts hardware with interrupt mask/start/optional last-CS bits, waits up to six seconds, copies RX data if requested, updates `actual_length`, and finalizes the message.

State and persistence: Software state is minimal: START vs DONE for the active fragment and the host pointer stored in `ndev->spi`. Flash contents are persistent hardware state, but the driver marks the partition read-only via `MTD_CAP_ROM`. Controller configuration is rebuilt at init.

Dependencies and integration points: Probe calls `netup_spi_init()` when the module parameter asks for SPI or when old firmware is detected. Interrupts are dispatched by `netup_unidvb_core.c`. Integrates with SPI controller APIs, SPI flash board-info plumbing, MTD partition metadata, and the local NetUP register/IRQ definitions.

Risks: `netup_spi_transfer()` sets `spi->state` without taking the spinlock used by the interrupt handler, relying on simple ordering around MMIO start and waitqueue wakeups. Timeout returns `-EIO` but does not explicitly reset the controller before later messages. `spi_new_device()` uses legacy board-info with modalias `m25p128`, which may depend on SPI NOR compatibility naming. The flash partition name is a static buffer rewritten per card and shared across instances.

Test signals: Validate fragmented transfers around 1024-byte boundaries, RX-only zero-fill behavior, timeout handling, IRQ-not-mine path, last-CS handling across multi-transfer messages, controller unregister while idle, multiple cards if supported, and MTD child creation with the expected partition name and read-only flags.
