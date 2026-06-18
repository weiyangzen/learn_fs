# sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/spi.c

Purpose: Implements the Marvell NCI-over-SPI transport using the kernel NCI SPI helper and an interrupt-driven slave handshake.

Important APIs and functions: `struct nfcmrvl_spi_drv_data` stores SPI device, `nci_spi`, completion, flags, and common private pointer. Key functions are `nfcmrvl_spi_int_irq_thread_fn()`, `nfcmrvl_spi_nci_send()`, `nfcmrvl_spi_nci_update_config()`, `nfcmrvl_spi_parse_dt()`, `nfcmrvl_spi_probe()`, and `nfcmrvl_spi_remove()`.

Control flow: Probe parses platform data or DT IRQ, requests a falling-edge threaded IRQ, registers the common Marvell NCI device as SPI, enables firmware download, allocates the `nci_spi` helper, and initializes handshake completion. Send sets `SPI_WAIT_HANDSHAKE`, appends a dummy byte required by the controller DMA behavior, and calls `nci_spi_send()` with the completion. The IRQ either completes the send handshake or reads an SPI packet and forwards it to the common receiver.

State and persistence: Runtime state includes `SPI_WAIT_HANDSHAKE`, `handshake_completion`, transport speed in `nci_spi->xfer_speed_hz`, and common private flags. No durable persistence exists.

Dependencies and integration points: Depends on Linux SPI, OF IRQ parsing, `net/nfc/nci_spi.h` helpers via included NCI headers, common Marvell core, and firmware config values from `nfcmrvl_fw_spi_config`.

Risks: IRQ semantics are overloaded between handshake completion and RX notification. The dummy byte affects frame tailroom and must match controller expectations. `nci_spi` allocation result is not checked before later use. Test signals include handshake IRQ ordering, RX IRQ path, firmware speed update, DT IRQ parsing, dummy-byte framing, and probe/remove fault injection.
