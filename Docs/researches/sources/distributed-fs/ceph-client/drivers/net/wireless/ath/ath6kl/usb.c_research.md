<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/usb.c

## Purpose
`usb.c` is the USB HIF backend for ath6kl. It maps USB endpoints to ath6kl logical pipes, manages URB context pools, submits RX/TX bulk transfers, implements BMI and diagnostic vendor control messages, registers the USB driver, and connects USB devices to the common core using HTC pipe mode.

## Important APIs, Types, And Functions
`struct ath6kl_usb_pipe` stores per-pipe URB pool, anchors, endpoint descriptor, pipe handle, thresholds, completion work, and completion skb queue. `struct ath6kl_usb` stores the USB device/interface, all pipes, diagnostic buffers, core pointer, lock, and workqueue. `struct ath6kl_urb_context` binds URB completion to pipe, skb, and core.

Resource functions include `ath6kl_usb_alloc_urb_from_pipe()`, `ath6kl_usb_free_urb_to_pipe()`, `ath6kl_usb_alloc_pipe_resources()`, `ath6kl_usb_setup_pipe_resources()`, and cleanup helpers. Data path functions include `ath6kl_usb_post_recv_transfers()`, `ath6kl_usb_recv_complete()`, `ath6kl_usb_usb_transmit_complete()`, `ath6kl_usb_io_comp_work()`, `ath6kl_usb_send()`, `hif_start()`, `hif_stop()`, and `hif_detach_htc()`.

HIF ops are in `ath6kl_usb_ops`, including pipe send/map/free-queue queries, BMI read/write, diagnostic read/write, power, stop, suspend/resume stubs, and no-op scatter cleanup.

## Control Flow
Probe creates USB resources, enumerates endpoint descriptors into logical pipes, allocates the common core, sets HIF type/ops, mailbox block size and BMI max size, then initializes core in HTC pipe mode. `hif_start()` posts RX transfers and sets TX thresholds. RX completion queues received skbs to pipe work and reposts URBs when enough free contexts accumulate. TX completion returns the URB context to the pool and queues skb completion work. The work item calls `ath6kl_core_rx_complete()` or `ath6kl_core_tx_complete()` depending on pipe direction.

Service mapping sends WMI control on TX control and data down RX data, maps BE/BK to low-priority TX, maps VI/VO to low- or medium-priority TX based on firmware capability, and uses RX data for receive. BMI and diagnostic operations use vendor control requests rather than mailbox CMD53.

Disconnect stops TX/RX, waits briefly for target reboot, cleans up core, kills anchored URBs, flushes work, frees pipe resources, buffers, workqueue, and USB object.

## State And Persistence
State is volatile: endpoint/pipe mappings, URB context counts, submitted anchors, completion queues, diagnostic buffers, and workqueue. Module firmware declarations are metadata. USB autosuspend support is declared but cfg80211 suspend/resume hooks are stubs.

## Dependencies And Integration Points
It depends on Linux USB APIs, ath6kl core and pipe-mode HTC, WMI service IDs, firmware capability bits, and core RX/TX completion handlers. Unlike SDIO, it does not support scatter and does not use mailbox BMI credits.

## Risks
URB pool exhaustion returns `-ENOMEM` and can occur if multiple endpoints map to one pipe, as noted by TODO. Completion work uses skbs as completion tokens, so ownership must remain exact across submit failures, disconnect, and flush. `ath6kl_usb_diag_read32()` sends the size of the write diagnostic command for read requests, which appears intentional for fixed command buffer size but should be verified against firmware. USB suspend only flushes I/O and PM resume reposts RX data/data2 without full cfg80211 resume support.

## Test Signals
Signals include USB probe endpoint logs, pipe resource counts/leak warnings, RX/TX completion logs, URB submit failures, vendor control request failures, core init result, disconnect cleanup without URB leaks, pipe free queue counts under load, and resume repost behavior. Tests should cover high-rate TX/RX, disconnect during active URBs, BMI/diag request failures, endpoint descriptor variants, and firmware capability changes in pipe mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/usb.c -->
