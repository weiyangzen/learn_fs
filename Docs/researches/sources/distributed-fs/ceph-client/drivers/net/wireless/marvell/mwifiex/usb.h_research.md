# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/usb.h

## Purpose
`usb.h` defines the USB bus contract for mwifiex: supported vendor/product IDs, firmware file names, firmware-download protocol structures, endpoint/URB constants, USB card state, URB contexts, and TX aggregation bookkeeping used by `usb.c`.

## Important APIs, Types, and Functions
There are no functions exported here. Key constants include `USB8XXX_VID`, PID pairs for 8766/8797/8801/8997 firmware-download and firmware-ready modes, `USB8XXX_FW_DNLD`, `USB8XXX_FW_READY`, `MWIFIEX_TX_DATA_PORT`, `MWIFIEX_TX_DATA_URB`, `MWIFIEX_RX_DATA_URB`, `MWIFIEX_USB_TIMEOUT`, default firmware names, and firmware block protocol constants such as `FW_DNLD_TX_BUF_SIZE`, `FW_DNLD_RX_BUF_SIZE`, `FW_HAS_LAST_BLOCK`, and `FW_CMD_7`.

Core structures are `struct urb_context` for per-URB adapter/SKB/URB/endpoint state, `struct tx_aggr_tmr_cnxt` and `struct usb_tx_aggr` for timer-bound TX aggregation, `struct usb_tx_data_port` for each USB data OUT port, `struct usb_card_rec` for all USB device state, and packed `struct fw_header`, `struct fw_sync_header`, and `struct fw_data` for firmware download.

## Control Flow and Integration
`usb.c` allocates and fills these structures during probe and init. RX/TX callbacks recover `urb_context` from `urb->context`. Data endpoints use `usb_tx_data_port` to track URB slots, port block status, current ring index, and aggregation lists. Firmware download writes `struct fw_data` blocks and reads `struct fw_sync_header` responses according to constants in this header.

## State and Persistence Behavior
The header models persistent runtime state rather than implementing behavior. `usb_card_rec` persists for the lifetime of the USB interface and owns endpoint descriptors, completion, URB pending atomics, SKB/URB contexts, firmware boot state, multi-channel resync flag, and per-port aggregation state. The packed firmware structs encode host-device wire format and must remain layout-stable.

## Dependencies and Risks
The header depends on Linux USB and completion APIs plus mwifiex core types declared elsewhere. Risks are ABI/layout drift in packed firmware structs, mismatched PID-to-firmware naming, incorrect endpoint count constants causing ring overrun or underutilization, and aggregation timer/lock fields being used without proper initialization in `usb.c`.

## Test Signals
Compile-time signals include structure size/layout, firmware macro use, and successful `usb.c` build. Runtime signals include correct endpoint discovery, firmware file selection for each PID, URB ring allocation counts, aggregation timer initialization, and firmware block protocol interoperability.
