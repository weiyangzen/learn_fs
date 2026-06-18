# sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xpc_uv.c

## Purpose
`xpc_uv.c` is the UV architecture backend for SGI/HPE Cross Partition Communication. It implements the `xpc_arch_operations` table for UV systems, using GRU message queues, UV BIOS watchlists, global physical addressing, heartbeat cachelines, and inter-partition activation/notification IRQs to support partition activation and channel payload delivery.

## Important APIs, Types, and Functions
The main exported entry points are `xpc_init_uv()` and `xpc_exit_uv()`, which install `xpc_arch_ops_uv` and create/destroy activation and notify GRU message queues. Queue construction is handled by `xpc_create_gru_mq_uv()`, `xpc_destroy_gru_mq_uv()`, `xpc_gru_mq_watchlist_alloc_uv()`, `xpc_get_gru_mq_irq_uv()`, and `xpc_send_gru_msg()`. Activation control uses `xpc_handle_activate_IRQ_uv()`, `xpc_handle_activate_mq_msg_uv()`, `xpc_send_activate_IRQ_uv()`, and local activation injection through `xpc_send_local_activate_IRQ_uv()`. Channel data flow uses `xpc_handle_notify_IRQ_uv()`, `xpc_handle_notify_mq_msg_uv()`, `xpc_send_payload_uv()`, `xpc_get_deliverable_payload_uv()`, and `xpc_received_payload_uv()`. UV-specific partition/channel state is stored in `struct xpc_partition_uv`, `struct xpc_channel_uv`, GRU descriptors, and FIFO lists.

## Control Flow
Initialization selects a NUMA node, creates two GRU message queues with IRQ handlers, publishes the local activation GRU descriptor and heartbeat GPA in the reserved page, and assigns the UV operation table. Remote activation messages update remote reserved-page data, heartbeat GPA, cached activation queue GPA, requested activation state, and channel-control flags before waking the heartbeat checker or channel manager. Channel open/close control is sent over the activation queue; payloads and ACKs are sent over the notify queue. Incoming notify messages either complete a sender slot when `size == 0` or copy a payload into a receive slot, enqueue it, and wake delivery kthreads or the channel manager.

## State and Persistence
All state is volatile kernel and UV partition state. Per-partition flags include cached remote activation queue descriptor validity and engaged/disengaged state. Heartbeat state is a cacheline-sized UV heartbeat value plus offline flag. Send slots, receive slots, cached notify descriptors, FIFO heads, and message queue pages live in kernel memory and are torn down on partition/channel or module exit. Remote accessibility is granted with `xp_expand_memprotect()` and revoked with `xp_restrict_memprotect()`.

## Dependencies and Integration Points
The file depends on UV hub and BIOS APIs, GRU kernel services, XPC common code, NUMA CPU/node selection, IRQ setup through UV MMR routing, remote memory copy helpers, and the global `xpc_partitions`/`xpc_rsvd_page` structures. It integrates with XPC channel management through `xpc_arch_ops`, with partition activation/deactivation through `XPC_DEACTIVATE_PARTITION()`, and with message delivery through XPC kthread wakeups.

## Risks and Edge Cases
`xpc_send_gru_msg()` retries indefinitely on queue-full or congestion conditions, which depends on eventual remote progress. Cached remote GRU descriptors can become stale and are invalidated only on activation updates or failed sends. Several paths use `BUG_ON()` for BIOS/watchlist/memory-protection failures, so unexpected platform errors are fatal. `xpc_init_mq_node()` passes the node id where a CPU argument is expected in the queue creation loop, making CPU/node assumptions worth reviewing. Locking spans mutexes, spinlocks, and channel locks; send failures can drop and reacquire channel locks around partition deactivation.

## Test Signals
Useful validation signals include successful UV-only initialization, creation of both GRU queues on the selected node, activation/deactivation handshakes across partitions, heartbeat change/offline detection, channel open/close flags, payload delivery and ACK slot recycling, stale descriptor recovery after remote restart, queue-full/congestion behavior under load, and clean `xpc_exit_uv()` teardown without memory-protection or IRQ leaks.
