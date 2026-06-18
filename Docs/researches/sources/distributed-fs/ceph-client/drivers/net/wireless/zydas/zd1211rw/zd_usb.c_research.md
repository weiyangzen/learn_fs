# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_usb.c

## Purpose
Implements the USB bus driver and transport for ZD1211RW. It matches USB IDs, ejects virtual installer devices, uploads firmware, initializes hardware, manages interrupt/RX/TX URBs, implements register and RF vendor commands, detects TX/RX stalls, handles USB reset/resume, and registers/unregisters mac80211 hardware.

## Important APIs, Types, And Functions
Exports `zd_usb_init()`, `zd_usb_clear()`, `zd_usb_init_hw()`, `zd_usb_read_fw()`, `zd_usb_enable_int()`, `zd_usb_disable_int()`, `zd_usb_enable_rx()`, `zd_usb_disable_rx()`, `zd_usb_enable_tx()`, `zd_usb_disable_tx()`, `zd_usb_tx()`, `zd_tx_watchdog_enable()`, `zd_tx_watchdog_disable()`, `zd_usb_reset_rx_idle_timer()`, `zd_usb_scnprint_id()`, `zd_usb_ioread16v()`, `zd_usb_iowrite16v_async_start/end()`, `zd_usb_iowrite16v_async()`, `zd_usb_iowrite16v()`, and `zd_usb_rfwrite()`. Driver callbacks include `probe`, `disconnect`, `pre_reset`, `post_reset`, module init/exit, and URB completions `int_urb_complete`, `rx_urb_complete`, and `tx_urb_complete`.

## Control Flow
Probe resets the USB device, allocates `ieee80211_hw`, sets ZD1211B flag from ID table, reads the permanent MAC over the pre-firmware interface, and registers mac80211. First `zd_op_start()` calls `zd_usb_init_hw()`, which uploads boot/helper firmware, resets USB configuration, and invokes MAC/chip init. Interrupt URB completion handles register-read replies, hardware interrupt status, and retry-fail TX status, then resubmits. RX enables five bulk URBs, handles split/merged USB frames, passes complete packets to `zd_mac_rx()`, and resets RX if idle for 30 seconds. TX creates one bulk URB per skb, anchors it, tracks queue pressure, reports completion to MAC, and uses a watchdog to queue device reset after a 5-second stuck skb. Register reads send a request on EP_REGS_OUT and wait for a matching interrupt reply with retry handling; writes batch asynchronous URBs through an anchor.

## State And Persistence
`struct zd_usb` owns the USB interface reference, command anchors, async write state, request buffer, interrupt URB/buffer/completion, RX URB array and fragment buffer, TX submitted skb queue/anchor/count, and flags `is_zd1211b`, `initialized`, `was_running`, and `in_async`. Firmware remains in device memory until reset. `pre_reset` records whether the device was running, stops transport, and holds `chip->mutex`; `post_reset` unlocks and resumes if needed.

## Dependencies And Integration Points
Depends on Linux USB core, firmware loader, workqueues/tasklets, mac80211, skb queues, and local MAC/chip definitions. Integrates firmware files `zd1211/zd1211_{ur,ub,uphr}` and `zd1211/zd1211b_{ur,ub,uphr}`, mac80211 registration, and USB device reset callbacks.

## Risks
URB lifetime, anchors, coherent buffers, and skb ownership are delicate. Register reads depend on interrupt endpoint availability and can be overridden by retry-fail or CR_INTERRUPT events; stale replies are filtered by address matching. `zd_usb_iowrite16v_async_end()` timeout semantics depend on anchor state and `cmd_error`. RX fragment detection uses packet-size modulus heuristics. Reset paths lock `chip->mutex` across USB reset callbacks, so lock ordering must stay consistent. Firmware version mismatch handling is intentionally less invasive than the vendor driver.

## Test Signals
Probe all listed ZD1211/ZD1211B IDs, installer eject IDs, full/high-speed devices, missing firmware, firmware version mismatch, repeated register read/write batches, RF writes with min/max bit counts, RX merged and split frames, TX queue stop/wake thresholds, TX watchdog reset, RX idle reset, disconnect during traffic, and USB pre/post reset resume.
