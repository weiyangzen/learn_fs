# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00usb.c

## Purpose
`rt2x00usb.c` is the generic USB transport implementation for rt2x00 USB devices. It provides vendor control requests for register access, cached buffered register transfers, asynchronous register reads, bulk URB queue submission, RX/TX completion work, USB queue flushing and watchdog recovery, endpoint discovery, URB allocation, probe/disconnect, and PM forwarding.

## Important APIs, Types, And Functions
Exported APIs include `rt2x00usb_vendor_request()`, `rt2x00usb_vendor_req_buff_lock()`, `rt2x00usb_vendor_request_buff()`, `rt2x00usb_regbusy_read()`, `rt2x00usb_register_read_async()`, `rt2x00usb_kick_queue()`, `rt2x00usb_flush_queue()`, `rt2x00usb_watchdog()`, `rt2x00usb_disable_radio()`, `rt2x00usb_clear_entry()`, `rt2x00usb_initialize()`, `rt2x00usb_uninitialize()`, `rt2x00usb_probe()`, `rt2x00usb_disconnect()`, and PM suspend/resume when enabled. Private callbacks handle TX URB completion, RX URB completion, TX status work, RX done work, endpoint assignment, URB allocation, and register shadow allocation.

## Control Flow
Control transfers route through `rt2x00usb_vendor_request()`, which retries until timeout, treats repeated protocol/timeouts or device removal as disappearance, and clears `DEVICE_STATE_PRESENT` on fatal USB errors. Buffered register requests serialize with `csr_mutex` and chunk transfers through a kmalloc-backed `CSR_CACHE_SIZE` buffer. Async register reads allocate a control URB and callback context, anchor the URB, and optionally resubmit based on the callback return value.

TX queue kicking walks entries from `Q_INDEX_DONE` to `Q_INDEX`, clears `ENTRY_DATA_PENDING`, pads the skb to the driver-reported USB length, fills a bulk OUT URB, and submits it. TX URB completion marks IO failure on status, calls DMA done, lets chip code observe TX DMA done, and queues txdone work when no hardware TX status FIFO is required or status is available. RX kicking walks free entries, marks device ownership, calls DMA start, fills a bulk IN URB, and submits it. RX completion validates length/status, calls DMA done, and queues RX work, which passes completed entries to `rt2x00lib_rxdone()`.

Initialization finds bulk IN/OUT endpoints, assigns missing TX queues to the last discovered TX endpoint, allocates one URB per entry and optional beacon guardian URBs, and leaves queue entry setup to shared queue code. Uninitialization kills anchored async URBs, cancels timer/work, and frees all per-entry URBs. Probe resets the USB device, allocates mac80211 hardware, sets `RT2X00_CHIP_INTF_USB`, initializes work items and a USB anchor, allocates CSR/eeprom/RF storage, and calls `rt2x00lib_probe_dev()`.

## State And Persistence
USB transport state includes `rt2x00dev->csr.cache`, `eeprom`, `rf`, `anchor`, `num_proto_errs`, rxdone/txdone work items, txstatus timer, per-queue endpoint/maxpacket fields, and per-entry URBs in `struct queue_entry_priv_usb` or beacon guardian private data. State is in kernel memory and USB device state only; it is released on disconnect or uninitialize.

## Dependencies And Integration Points
The file depends on Linux USB core APIs, rt2x00 shared queue structures, rt2x00lib DMA/TX/RX completion, chip-specific `get_tx_data_len`, optional `tx_dma_done`, workqueues, hrtimers, and mac80211 hardware allocation. USB chip drivers include `rt2x00usb.h` and call `rt2x00usb_probe()` from their interface driver.

## Risks
USB buffer rules are strict: direct vendor-request buffers must be kmalloc-backed, so buffered access must be used for stack or arbitrary buffers. Fatal USB error detection clears device presence, which affects all later callbacks. URB completion and queue state must agree on ownership bits or completions can be ignored. `rt2x00usb_work_txdone()` reports unknown status unless chip-specific TX status is available. Flush loops depend on completion work draining queues within ten 50 ms sleeps. Async register reads free only the context, relying on URB lifetime rules after `usb_free_urb()` and anchoring.

## Test Signals
Signals include successful control register read/write and EEPROM reads, endpoint discovery on devices with shared or per-queue endpoints, TX bulk submission and completion under queue pressure, RX URB recycling, repeated USB protocol error handling, watchdog reset of timed-out TX DMA, flush with URB kill on drop, disconnect while URBs are in flight, suspend/resume forwarding, and no leaks from anchored async reads.
