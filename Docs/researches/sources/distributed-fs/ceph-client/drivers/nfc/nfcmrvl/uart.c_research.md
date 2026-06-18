# sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/uart.c

Purpose: Implements Marvell NFC over the kernel NCI UART framework, including DT/module-parameter configuration, firmware-download speed updates, and optional BREAK-based wake/sleep control.

Important APIs and functions: Transport callbacks are `nfcmrvl_uart_nci_send()` and `nfcmrvl_uart_nci_update_config()`. NCI UART callbacks are `nfcmrvl_nci_uart_open()`, `nfcmrvl_nci_uart_close()`, `nfcmrvl_nci_uart_recv()`, `nfcmrvl_nci_uart_tx_start()`, and `nfcmrvl_nci_uart_tx_done()`. Module params are `hci_muxed`, `flow_control`, and `break_control`.

Control flow: UART open searches a child DT node compatible with Marvell NFC UART, falls back to module parameters, registers the common NCI device, and binds `nu->drv_data`/`nu->ndev`. Sends delegate to the selected NCI UART low-level send operation. Firmware-download config changes call `nci_uart_set_config()` with the firmware-provided baud rate and flow-control setting. TX start clears BREAK to wake the controller; TX done asserts BREAK for deep-sleep wake support, except during firmware download.

State and persistence: Per-device state is common `nfcmrvl_private`; global module parameters provide fallback runtime configuration. BREAK state is physical line state, not durable persistence.

Dependencies and integration points: Depends on NCI UART registration, TTY `break_ctl`, DT child-node parsing, GPIO descriptor lookup for reset, and common Marvell core.

Risks: DT is discovered through the serial device parent, so platform layout matters. BREAK control assumes TTY ops support it. Firmware-download baud updates must occur at the correct boot stage. Test signals include DT and module-param configuration, HCI mux mode, firmware baud switch, BREAK wake/sleep, receive routing, and close during firmware download.
