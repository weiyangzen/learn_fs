# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/hif_usb.h

Purpose: Defines the ath9k_htc USB transport constants, firmware names/version bounds, endpoint IDs, URB pool sizing, stream tags, and USB HIF state structures used by `hif_usb.c` and HTC code.

Important APIs and types: Firmware macros define current module firmware paths and legacy filenames. Endpoint constants map WLAN TX/RX and register IN/OUT pipes. `struct tx_buf`, `rx_buf`, `cmd_buf`, `hif_usb_tx`, and `hif_device_usb` describe TX aggregation buffers, RX buffers, command contexts, transport queues/locks, USB anchors, firmware state, RX split-frame bookkeeping, and HTC linkage. Public prototypes are `ath9k_hif_usb_init()`, `ath9k_hif_usb_exit()`, and `ath9k_hif_usb_dealloc_urbs()`.

Control flow: The header has no executable flow, but its constants determine how `hif_usb.c` frames USB stream packets, sizes URB pools, requests firmware, and routes HTC control/data pipes.

State and persistence: Structures hold runtime-only USB device state. Firmware name and blob pointers are transient; the firmware image itself is requested from the system firmware store and downloaded to device RAM.

Dependencies and integration points: Depends on Linux USB, SKB, URB, anchor, completion, and list types through includers. It integrates with HTC target allocation and transport registration.

Risks: Pool-size constants directly bound memory use, queue pressure, and stream parsing assumptions. Endpoint IDs must match device descriptors checked at probe. Firmware version bounds control fallback behavior and supported device boot.

Test signals: Compile USB builds, validate endpoint matching, run with current and legacy firmware names, stress MAX_TX_URB_NUM/MAX_TX_BUF_NUM aggregation, and test RX transfers near `MAX_RX_BUF_SIZE` and `MAX_PKT_NUM_IN_TRANSFER`.
