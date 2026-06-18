# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_ipc.c

## Purpose
This file implements Merrifield-style SST IPC posting, interrupt acknowledgement, synchronous wait-block matching, firmware-init processing, asynchronous firmware notifications, and command reply processing.

## Important APIs, types, and functions
Wait-block management is `sst_create_block()`, `sst_wake_up_block()`, and `sst_free_block()`. Host-to-DSP posting is `sst_post_message_mrfld()`, with deferred queue support through the context `ipc_dispatch_list`. Interrupt completion is handled by `intel_sst_clear_intr_mrfld()`. Firmware async processing is split across `process_fw_init()` and `process_fw_async_msg()`. Replies are decoded by `sst_process_reply_mrfld()`.

## Control flow
Synchronous callers create an `sst_block`, post an IPC, and sleep on the shared waitqueue. When a DSP reply arrives, `sst_process_reply_mrfld()` matches by IPC message ID and private driver ID, stores result/data in the block, and wakes the waiter. `sst_post_message_mrfld()` either busy-waits for a free IPCX register for synchronous sends or pulls the next queued dispatch-list message when the done interrupt/workqueue path indicates the DSP is ready. Large messages copy mailbox payload data before writing the IPC header.

Async firmware messages use driver ID zero. Period elapsed messages locate the stream by firmware pipe ID and call PCM and compressed callbacks unless the stream has been dropped back to init state. Drain messages call the compressed drain callback. Firmware init complete stores version/build information and releases the firmware-download waiter. Async error and underrun messages are logged.

## State and persistence behavior
Blocks live on `ctx->block_list` until matched, timed out, or freed. Posted messages are transient heap allocations. Firmware version persists in `ctx->fw_version`. The code mutates stream callbacks indirectly through async notifications but does not own stream allocation.

## Dependencies and integration points
It depends on shim/MMIO helpers from `sst_pvt.c`, IPC structures from `sst-mfld-dsp.h`, stream lookup from `sst_pvt.c`, and stream callbacks installed by `sst_drv_interface.c`. It is invoked from the top/bottom IRQ paths in `sst.c`.

## Risks and edge cases
Large mailbox payload size validation is done in the IRQ path, but this file trusts `msg_low` when duplicating reply payloads. `sst_post_message_mrfld()` frees messages even on posting failure. Block matching logs missing blocks only at debug level, which avoids log spam but can hide protocol mismatch. Period elapsed depends on unique pipe IDs in `streams[]`.

## Test signals
Test blocking IPC success, blocking IPC timeout, queued nonblocking IPC dispatch after done interrupt, large and short replies, firmware init complete, period elapsed callbacks, drain callbacks, buffer underrun logs, firmware async errors, and malformed/unmatched replies.
