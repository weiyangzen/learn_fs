# sources/distributed-fs/ceph-client/drivers/usb/storage/uas.c

## Purpose

`uas.c` implements the USB Attached SCSI driver. It binds UAS-capable USB mass-storage interfaces, allocates streams when available, exposes a SCSI host with tagged queueing, submits command/status/data URBs, handles UAS IUs, and coordinates reset, suspend, shutdown, and disconnect.

## Important APIs, Types, and Functions

`struct uas_dev_info` stores the USB interface/device, URB anchors, quirk flags, queue depth, endpoint pipes, stream mode, reset/shutdown state, pending command table, spinlock, and work items. `struct uas_cmd_info` is per-SCSI-command private state with UAS tag, state bits, and URB pointers. Key paths include `uas_queuecommand_lck()`, `uas_submit_urbs()`, `uas_stat_cmplt()`, `uas_data_cmplt()`, `uas_eh_abort_handler()`, `uas_eh_host_reset_handler()`, `uas_configure_endpoints()`, `uas_probe()`, `uas_pre_reset()`, `uas_post_reset()`, `uas_suspend()`, `uas_disconnect()`, and `uas_shutdown()`.

## Control Flow

Probe first reuses `uas_use_uas_driver()` to validate the interface, switches to the UAS alternate setting, allocates a SCSI host, initializes anchors/work, discovers UAS endpoints, allocates USB streams for SuperSpeed devices, registers the host, and schedules asynchronous scanning. SCSI queueing finds a free one-based UAS tag, initializes state bits for status, command, and optional data URBs, pre-submits data URBs when streams are unavailable, and either submits everything immediately or queues work for retry on allocation/submission pressure.

Status URB completions decode IU tags and IDs. STATUS IUs copy sense data and complete commands; READ_READY and WRITE_READY trigger data URB submission; RESPONSE IUs evaluate task-management responses; errors cancel outstanding data URBs. Data URB completions clear inflight bits, set residuals or host errors, and call `uas_try_complete()`. Completion only calls `scsi_done()` after command, data-in, data-out, and abort state are all clear. Reset paths block requests, wait for pending commands, free and reallocate streams, kill anchored URBs on host reset, zap command table entries, and report bus resets.

## State and Persistence Behavior

State is entirely in memory and USB device configuration: command slots in `cmnd[]`, URB anchors, per-command state flags, stream allocation, endpoint pipes, SCSI queue depth, and quirk flags. The driver changes USB alternate settings, allocates/frees streams, and on restart shutdown deliberately switches back to altsetting 0 and resets the device so firmware/BIOS code sees usb-storage mode. There is no filesystem persistence.

## Dependencies and Integration Points

The driver depends on USB core, UAS descriptors and IUs, SuperSpeed streams, scatter-gather support, SCSI host/template APIs, SCSI error handling, workqueues with `WQ_MEM_RECLAIM`, and shared usb-storage quirk definitions. It integrates with `unusual_uas.h`, `uas-detect.h`, `scsiglue.h`, and SCSI block-device configuration flags such as broken FUA, max sectors, no REPORT LUNS, and capacity heuristics.

## Risks and Edge Cases

The command state machine is concurrency-sensitive: status, command, data, abort, reset, and workqueue paths all coordinate under `devinfo->lock`. `uas_eh_abort_handler()` intentionally returns `FAILED` because it does not send a UAS abort task management command; it only drops local references and kills data URBs. SuperSpeed streams reserve two tags, so queue-depth math must avoid off-by-one firmware bugs. Suspend/pre-reset wait loops can time out if a device stops sending status IUs. The shutdown mode switch/reset is scoped to system restart because some firmware hangs with devices left in UAS mode.

## Test Signals

Validate UAS and fallback binding, endpoint pipe mapping, USB2 non-stream mode, SuperSpeed stream allocation/freeing, tagged queue depth, READ_READY/WRITE_READY sequencing, bidirectional command handling, sense copying, RESPONSE IU error mapping, data URB errors/residuals, allocation retry work, SCSI aborts, host reset, pre/post reset, suspend timeout, disconnect with pending commands, and restart shutdown reverting to altsetting 0.
