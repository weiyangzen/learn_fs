# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-mailbox.c

## Purpose
This file implements host-to-firmware and firmware-to-host mailbox communication for cx18. It sends encoder/API commands, handles acknowledgments and timeouts, processes incoming DMA completion/debug commands, and dispatches completed buffers to V4L2, DVB, or ALSA consumers.

## Important APIs, Types, and Functions
Public APIs are `cx18_api()`, `cx18_vapi_result()`, `cx18_vapi()`, `cx18_api_func()`, `cx18_api_epu_cmd_irq()`, and `cx18_in_work_handler()`. `api_info[]` maps cx23418 command IDs to CPU/APU targets and timeout flags. Incoming work helpers include `epu_dma_done_irq()`, `epu_debug_irq()`, `epu_dma_done()`, `cx18_mdl_send_to_dvb()`, `cx18_mdl_send_to_vb2()`, and `cx18_mdl_send_to_alsa()`.

## Control Flow
Outgoing `cx18_api_call()` serializes access to the target mailbox, clears stuck busy state if needed, writes command/args/error/request/ack fields, sends an SW1 interrupt, waits on the matching ack wait queue, reads returned args/error, and applies extra delay for slow commands. Incoming IRQ handling snapshots the firmware mailbox, detects stale self-acked mailboxes, copies MDL ack data or debug strings, acknowledges non-stale mailboxes quickly, and queues work. Workqueue context resolves handles to streams, finds completed MDLs, moves data to DVB demux, vb2 buffers, ALSA callback, or stream `q_full`, reloads firmware queues, and wakes readers.

## State and Persistence
Mailbox request/ack sequence numbers live in SCB memory. Per-device wait queues, mailbox locks, incoming work orders, stream queues, and MDL state coordinate progress. Stale flags record mailbox lag conditions for deferred work.

## Dependencies and Integration Points
The file depends on SCB layout, interrupt helpers, MMIO/page helpers, queue/stream helpers, DVB demux, vb2, optional ALSA PCM callbacks, and cx2341x control translation. It is the bridge between V4L2 controls/streaming and firmware.

## Risks and Edge Cases
Mailbox timing is delicate. Incoming commands must be acknowledged quickly or firmware self-acks and stale data may be processed defensively. Work-order pool exhaustion drops incoming processing. DMA MDL IDs are validated for stale mailboxes, but lost MDLs can still require queue recovery. Outgoing waits are uninterruptible and return `-EINVAL` on ack timeout.

## Test Signals
Stress concurrent capture streams, DVB TS feeding, YUV vb2 capture, ALSA PCM capture, MPEG index rotation, firmware debug messages, API timeout injection, and module removal while DMA completions are pending.
