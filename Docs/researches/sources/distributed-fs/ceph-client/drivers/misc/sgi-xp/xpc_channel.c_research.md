# sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xpc_channel.c

Purpose: implements XPC channel connection/disconnection protocol and send/receive entry points. It manages per-channel state, message queue references, user callouts, and kthread activation for message delivery.

Important APIs/functions: external functions include `xpc_process_sent_chctl_flags()`, `xpc_partition_going_down()`, `xpc_initiate_connect()`, `xpc_connected_callout()`, `xpc_initiate_disconnect()`, `xpc_disconnect_channel()`, `xpc_disconnect_callout()`, `xpc_allocate_msg_wait()`, `xpc_initiate_send()`, `xpc_initiate_send_notify()`, `xpc_deliver_payload()`, and `xpc_initiate_received()`. Core internal state-machine helpers are `xpc_process_connect()`, `xpc_process_disconnect()`, `xpc_process_openclose_chctl_flags()`, and `xpc_connect_channel()`.

Control flow: channel connection requires local and remote open requests, message structure setup, open replies, open complete messages, and final connected flags. Disconnect sends close request, waits for local kthreads/references and remote close protocol or partition disengagement, notifies blocked senders, tears down message structures, clears registration-derived fields, and completes unregister waiters. Send APIs reference the partition, delegate payload placement to `xpc_arch_ops.send_payload()`, and dereference. Receive delivery obtains an architecture-provided payload, takes a message-queue reference, calls the registered channel callback, and requires user acknowledgment through `xpc_initiate_received()`.

State and persistence: channel fields track flags, reason/line, queue sizes, callback/key, kthread counts, message allocation waiters, notify counts, and delayed chctl flags. State is per active remote partition and not persistent across teardown.

Dependencies and integration: depends on XP registrations, XPC partition references, architecture operations for all transport-specific queue/chctl work, and kthread management in `xpc_main.c`.

Risks: open/close races are complex, especially delayed flags while `XPC_C_WDISCONNECT` is set. Callouts may run with locks held in some notify paths and must obey non-blocking requirements where documented. Failure to pair payload delivery with `xpc_received()` holds message-queue references and can block teardown. Message-size mismatches disconnect the channel.

Test signals: exercise simultaneous open/close, registration/unregistration while partitions are active, queue exhaustion with wait/nowait, notify callbacks on disconnect, missing receive acknowledgments, partition going down, and architecture send/setup failure returns.
