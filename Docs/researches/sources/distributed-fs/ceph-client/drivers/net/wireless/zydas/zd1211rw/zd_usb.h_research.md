# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_usb.h

## Purpose
Defines the ZD1211RW USB transport contract: endpoint numbers, vendor request formats, interrupt packet formats, RX/TX transport state, command batching state, timing thresholds, and exported USB APIs.

## Important APIs, Types, And Functions
Defines device types, endpoints, transfer limits, RF write bit limits, control request IDs, packed request structs (`usb_req_read_regs`, `usb_req_write_regs`, `usb_req_rfwrite`), interrupt structs (`usb_int_header`, `usb_int_regs`, `usb_int_retry_fail`), `read_regs_int`, `zd_ioreq16`, `zd_ioreq32`, `zd_usb_interrupt`, `zd_usb_rx`, `zd_usb_tx`, and `zd_usb`. Inline helpers map USB structures to `usb_device` and `ieee80211_hw`.

## Control Flow
No independent flow, but the declarations enforce that chip code uses 16-bit read/write batches, RF code uses `zd_usb_rfwrite()`, and MAC code uses RX/TX enable/disable and `zd_usb_tx()`. Interrupt replies complete register reads asynchronously.

## State And Persistence
`zd_usb_interrupt` persists interrupt URB state and pending register-read metadata. `zd_usb_rx` persists RX URBs, fragment buffer, idle work, and reset tasklet. `zd_usb_tx` persists enabled/stopped flags, submitted skb queue, URB anchor, submitted count, and watchdog work. `zd_usb` holds global async command batching state and transport flags.

## Dependencies And Integration Points
Includes Linux completion, netdevice, spinlock, skb, USB, and `zd_def.h`. Used by chip, MAC, RF, and USB implementation files.

## Risks
The fixed `req_buf[64]` is sized to current request maxima; changing maxima requires rechecking build assertions. Packed USB protocol structs must not change layout. Tasklet initialization in the C file relies on fields declared here. TX high/low watermarks directly affect mac80211 queue flow control.

## Test Signals
Compile with `BUILD_BUG_ON` request-size checks, run register batches at maximum counts, RF writes at bit-count limits, RX fragment handling, TX queue throttling, and interrupt enable/disable races.
