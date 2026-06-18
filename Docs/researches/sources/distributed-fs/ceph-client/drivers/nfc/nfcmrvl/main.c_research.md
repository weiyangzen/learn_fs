# sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/main.c

Purpose: Provides the common Marvell NFC NCI driver core shared by USB, UART, I2C, and SPI transports.

Important APIs and functions: Exports `nfcmrvl_nci_register_dev()`, `nfcmrvl_nci_unregister_dev()`, `nfcmrvl_nci_recv_frame()`, `nfcmrvl_chip_reset()`, `nfcmrvl_chip_halt()`, and `nfcmrvl_parse_dt()`. Internal NCI ops are `nfcmrvl_nci_open()`, `nfcmrvl_nci_close()`, `nfcmrvl_nci_send()`, `nfcmrvl_nci_setup()`, and `nfcmrvl_nci_fw_download()`.

Control flow: Transport drivers call register with PHY id, driver data, low-level ops, device, and platform data. The core allocates an `nci_dev` with PHY-specific headroom/tailroom, initializes firmware download support, registers with the NCI core, and halts the chip. Open sets the running bit, clears prior PHY errors, and delegates to transport open. Send optionally wraps NCI packets in an HCI mux header, then delegates to transport send. Receive strips HCI mux packets, routes frames to firmware download while a download is active, or delivers to `nci_recv_frame()` only when running.

State and persistence: `struct nfcmrvl_private` owns flags, platform config, `nci_dev`, firmware download context, PHY identity, transport context, and ops. No persistent state beyond runtime device registration.

Dependencies and integration points: Integrates with Linux GPIO descriptors, DT parsing, NCI core, NFC firmware download API, and transport-specific `nfcmrvl_if_ops`.

Risks: HCI mux framing assumptions must match hardware; non-NFC mux packets are silently discarded. Register/unregister must abort firmware download before destroying workqueue state. Reset GPIO polarity is assumed by the binding. Test signals include open/close idempotence, muxed and unmuxed RX/TX, firmware-download routing, setup config command, reset/halt GPIO behavior, and all transport probe/remove paths.
