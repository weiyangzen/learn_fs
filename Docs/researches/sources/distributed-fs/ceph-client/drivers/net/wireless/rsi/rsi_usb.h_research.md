# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_usb.h

Purpose: Defines the RSI USB transport ABI, device IDs, endpoint constants, USB-private state, and small transport-specific inline helpers.

Important APIs and types: Constants define vendor/product IDs for 9113/9116, internal readiness/status/watchdog registers, vendor register read/write requests, TX headroom, bulk endpoint limits, WLAN/BT endpoint IDs, buffer sizes, and maximum RX packet size. `struct rx_usb_ctrl_block` tracks one RX URB, backing data, SKB, and endpoint. `struct rsi_91x_usbdev` stores the USB device/interface, endpoint selection, RX thread, RX URB control blocks, TX buffer, bulk endpoint descriptors, TX block size, write failure flag, and RX queue. USB-specific inline functions always report queue-not-full and infinite event timeout. `rsi_usb_rx_thread()` is the receive worker entry point.

Control flow and integration: The USB bus code uses the declared IDs and endpoint arrays during probe, URB setup, register access, and RX/TX scheduling. Unlike SDIO, `rsi_usb_check_queue_status()` does not gate TX on firmware queue status, so higher layers can enqueue without polling a buffer-status register.

State and persistence: Persistent bus state is held in URBs, endpoint maps, `rx_q`, `tx_buffer`, and write failure state. Firmware readiness and watchdog control are accessed through vendor register requests using the constants here.

Dependencies: Depends on Linux USB APIs, `rsi_main.h`, and `rsi_common.h`. Integration is with the RSI common TX/RX and thread abstractions.

Risks and test signals: Risks include endpoint discovery mismatches, URB lifetime and RX queue ordering, max packet size violations, vendor register access failure, and lack of queue-status backpressure compared with SDIO. Tests should cover probe for both product IDs, bulk endpoint parsing, RX URB refill, register read/write, watchdog disable request, TX headroom handling, disconnect while RX thread is active, and write-failure recovery.

Test signals: Source read size: 85 lines, 2487 bytes.
