# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2800usb.c

## Purpose
Implements the RT2800 USB driver. It provides USB-specific register access binding, firmware upload/autorun detection, USB DMA setup, embedded TXINFO/RXINFO descriptor handling, asynchronous TX status polling, EEPROM/efuse selection, queue sizing, mac80211 operation wiring, and a large USB device ID table.

## Important APIs, Types, And Functions
Key functions include `rt2800usb_start_queue()`, `rt2800usb_stop_queue()`, `rt2800usb_tx_sta_fifo_read_completed()`, `rt2800usb_async_read_tx_status()`, `rt2800usb_tx_dma_done()`, `rt2800usb_tx_sta_fifo_timeout()`, `rt2800usb_autorun_detect()`, `rt2800usb_write_firmware()`, `rt2800usb_init_registers()`, `rt2800usb_enable_radio()`, `rt2800usb_set_device_state()`, `rt2800usb_get_txwi()`, `rt2800usb_write_tx_desc()`, `rt2800usb_get_tx_data_len()`, `rt2800usb_work_txdone()`, `rt2800usb_fill_rxdone()`, `rt2800usb_read_eeprom()`, and `rt2800usb_probe_hw()`. Static operation tables bind USB to rt2x00 and RT2800 abstractions.

## Control Flow
USB probe calls `rt2x00usb_probe()` with `rt2800usb_ops`. Firmware loading first checks AutoRun mode through a special vendor request, optionally clears `REQUIRE_FIRMWARE`, otherwise writes one 4 KiB half of `rt2870.bin` to `FIRMWARE_IMAGE_BASE`, then requests firmware execution via USB device mode. Radio-on wakes the device, waits briefly, configures `USB_DMA_CFG` bulk RX/TX and aggregation limits, then calls shared RT2800 enable. TX prep places a TXINFO descriptor at skb data, uses TXWI after TXINFO for normal data and at skb start for beacons, pads USB bulk packets, and starts asynchronous TX status reads after DMA completion. RX parses RXINFO, validates packet length, reads trailing RXD, strips descriptors, sets crypto/L2PAD/MY_BSS flags, trims skb, and delegates RXWI parsing.

## State And Persistence
`TX_STATUS_READING` in `rt2x00dev->flags` serializes asynchronous TX_STA_FIFO reads. `txstatus_fifo`, `txstatus_timer`, and `txdone_work` hold pending tx status across URB completions. Firmware and EEPROM are cached in common rt2x00 fields. Queue limits are USB-specific: RX 128, TX AC queues 16, beacon 8. The module parameter `nohwcrypt` is global for all devices bound to the module.

## Dependencies And Integration Points
Depends on `rt2x00usb` vendor requests, async register reads, USB queue management, RT2800 shared firmware/check/config/key logic, mac80211 callback glue, and the Linux USB driver core. The device table integrates many vendor/product IDs and conditional Kconfig chipset families.

## Risks
TX status polling has race windows between pending checks and clearing `TX_STATUS_READING`; the code rechecks but regressions can stall completions. RX length validation protects against malformed USB data, but descriptor placement at packet tail is fragile. Firmware AutoRun changes capability flags at runtime. USB bulk aggregation limit calculation assumes queue sizes and frame constants. The huge ID table increases risk of binding unsupported revisions. Hub-initiated LPM is disabled, indicating link power management can break devices.

## Test Signals
Probe many USB IDs, firmware and AutoRun paths, TX under busy medium with delayed status, RX malformed length handling, suspend/resume/reset_resume, hardware crypto on/off, AP beaconing, scan, high-throughput bulk transfers, and disconnect while TX status reads/timers are active. Look for TX status FIFO overrun, URB status warnings, and bad frame size logs.
