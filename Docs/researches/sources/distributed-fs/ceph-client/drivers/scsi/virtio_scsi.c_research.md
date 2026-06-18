# sources/distributed-fs/ceph-client/drivers/scsi/virtio_scsi.c

## Purpose

`virtio_scsi.c` implements the Linux SCSI host adapter driver for virtio SCSI devices. It bridges SCSI midlayer commands, error handling, device scanning, hotplug/change events, blk-mq queue mapping, and virtio virtqueue transport. The device model uses one control virtqueue, one event virtqueue, and one or more request virtqueues.

## Important APIs, Types, And Functions

Primary state is `struct virtio_scsi`, which holds the virtio device, event buffers, queue counts/maps, stop-events flag, control/event queues, DMA-from-device event storage, and flexible request queue array. `struct virtio_scsi_vq` wraps a `struct virtqueue *` with a spinlock. `struct virtio_scsi_cmd` is per-command storage placed in `scsi_cmnd` private data for normal I/O or allocated from a mempool for TMFs.

Submission and completion helpers include `__virtscsi_add_cmd()`, `virtscsi_add_cmd()`, `virtscsi_kick_vq()`, `virtscsi_queuecommand()`, `virtscsi_complete_cmd()`, `virtscsi_vq_done()`, `virtscsi_req_done()`, and `virtscsi_mq_poll()`. Header builders are `virtio_scsi_init_hdr()` and, with protection information, `virtio_scsi_init_hdr_pi()`.

Error handling uses `virtscsi_tmf()`, `virtscsi_abort()`, `virtscsi_device_reset()`, and `virtscsi_eh_timed_out()`. Event handling uses `virtscsi_kick_event()`, `virtscsi_kick_event_all()`, `virtscsi_complete_event()`, `virtscsi_handle_event()`, `virtscsi_handle_transport_reset()`, `virtscsi_handle_param_change()`, and `virtscsi_rescan_hotunplug()`.

Lifecycle is implemented by `virtscsi_probe()`, `virtscsi_remove()`, `virtscsi_freeze()`, `virtscsi_restore()`, module init/exit, and the `virtio_driver` registration.

## Control Flow And State

Probe reads virtio config values, clamps queue count to possible CPUs/blk-mq queues, allocates a `Scsi_Host` with enough private space for request queues, initializes virtqueues, configures CDB/sense sizes, sets SCSI host limits, advertises protection information where supported, calls `scsi_add_host()`, marks the virtio device ready, posts event buffers, and scans the host.

Normal I/O starts in `virtscsi_queuecommand()`. The blk-mq unique tag selects a request virtqueue. The driver fills a virtio SCSI request header, copies the CDB, builds SG lists containing request header, optional data-out/protection buffers, response header, optional data-in/protection buffers, and adds them to the virtqueue under `vq_lock`. It kicks immediately only when `SCMD_LAST` is set; batched requests are kicked via `commit_rqs()`.

Completion callbacks drain virtqueue buffers while callbacks are disabled, translate virtio response codes into SCSI host/status bytes, set residuals and sense data, and call `scsi_done()`. Poll queues omit interrupts and are drained from `mq_poll`.

The event queue keeps eight reusable event buffers. Completion of an event buffer queues work unless removal has set `stop_events`. Work handles missed events by probing existing devices and rescanning the host, handles transport reset by adding/removing LUNs, handles parameter-change ASC/ASCQ by rescanning a device, then reposts the event buffer.

Task management functions allocate a command object from a mempool, send TMF requests on the control queue, wait synchronously, interpret TMF responses, poll request queues once to close interrupt races, and free the command object.

## Dependencies And Integration Points

The driver integrates with virtio core (`virtio_find_vqs()`, config access, feature negotiation, device ready/reset), SCSI core (`scsi_host_template`, queuecommand, EH handlers, scan/add/remove/rescan), blk-mq queue mapping and polling, block integrity/DIF/DIX support, DMA cache-clean inbuf posting for events, and system freezable workqueues. Module parameter `virtscsi_poll_queues` controls how many request queues are allocated for polling.

## Risks And Test Signals

Risks include races during event teardown, TMF completion before request interrupt processing, virtqueue full handling, and endian conversion of event/reason/status fields. The code explicitly polls request queues after TMFs and sets `stop_events` before canceling work to mitigate two major races. Another risk is stale hot-unplug state when missed events occur; the driver mitigates by issuing INQUIRY to known devices and rescanning.

Useful tests are virtio-scsi boot and hotplug/hotunplug, missed-event injection, queue-depth changes, request batching with `SCMD_LAST`, blk-mq poll queues, suspend/resume freeze/restore, abort and LUN reset error handling, T10 PI I/O, large SG lists up to `seg_max`, and transport failure response mapping.
