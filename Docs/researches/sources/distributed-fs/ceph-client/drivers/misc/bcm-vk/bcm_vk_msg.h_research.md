# sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk_msg.h

## Purpose
`bcm_vk_msg.h` defines the host/card message-queue ABI and in-kernel bookkeeping structures used by the Broadcom VK misc-device transport.

## Important APIs, Types, and Functions
Key wire-facing structures are `struct bcm_vk_msgq`, the BAR1 queue descriptor, and `struct vk_msg_blk`, the fixed 16-byte message unit. Driver-side structures include `struct bcm_vk_sync_qinfo`, `struct bcm_vk_ctx`, `struct bcm_vk_wkent`, `struct bcm_vk_qs_cnts`, and `struct bcm_vk_msg_chan`. Constants define queue counts, block size, transport ID fields, function IDs (`VK_FID_TRANS_BUF`, `VK_FID_SHUTDOWN`, `VK_FID_INIT`), command masks, context limits, PID hash size, BAR segment sizing, and shutdown types.

## Control Flow
The header supports the lifecycle implemented in `bcm_vk_msg.c`: synchronize queue descriptors into `bcm_vk_sync_qinfo`, allocate a context for each open file, wrap a user request in `bcm_vk_wkent`, track it on a channel pending list, attach DMA SGL state when needed, and complete it when a matching response arrives.

## State and Persistence
The structures are runtime-only and persist only for the lifetime of a VK device or file descriptor. `bcm_vk_ctx` tracks per-open counters and wait queues; `bcm_vk_wkent` owns the copied outbound message, optional inbound response, DMA descriptors, and original user message ID; channel state owns queue locks and per-priority pending lists.

## Dependencies and Integration Points
The header includes the VK UAPI header and `bcm_vk_sg.h`. It is consumed by the VK core, message transport, and SGL code. `struct vk_msg_blk` is an ABI boundary with firmware and user space, so its size and field interpretation are integration-critical.

## Risks and Edge Cases
The flexible-array `bcm_vk_wkent` is sized dynamically by callers and depends on correct `to_v_blks` accounting, especially when in-band SGL blocks are appended. Queue count constants distinguish maximum allocated arrays from firmware-advertised usable queues. Transport IDs combine queue and message ID in one field, so helper use must be consistent.

## Test Signals
Compile-time checks should preserve `sizeof(struct vk_msg_blk) == 16` and array bounds. Runtime tests should confirm queue selection fallback, internal/user message ID remapping, context accounting, and shutdown message encoding.
