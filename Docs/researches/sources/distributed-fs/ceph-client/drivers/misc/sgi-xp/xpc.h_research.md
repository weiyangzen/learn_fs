# sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xpc.h

Purpose: defines XPC's internal partition, channel, reserved-page, heartbeat, message, state-machine, and architecture-operation contracts. It is the shared private header for `xpc_main.c`, `xpc_channel.c`, `xpc_partition.c`, and UV-specific XPC code.

Important APIs/types: key structures include `xpc_rsvd_page`, `xpc_heartbeat_uv`, `xpc_gru_mq_uv`, activation message variants, `xpc_openclose_args`, UV FIFO/message-slot types, `xpc_channel_uv`, `xpc_channel`, `xpc_partition_uv`, `xpc_partition`, and `xpc_arch_operations`. It defines channel flags, chctl flags, partition activation/setup states, default heartbeat/disengage tunables, and refcount helpers.

Control flow: the header encodes the major state machines: reserved page setup advertises heartbeat and activation queue addresses; partition activation transitions from inactive to activation requested, activating, active, and deactivating; channels move through open request/reply/complete and close request/reply flags; kthreads deliver payloads and manage disconnect callouts. `xpc_arch_operations` abstracts UV/SN transport details such as heartbeat, chctl sends, message queues, and engagement.

State and persistence: XPC state is volatile in `xpc_partitions[]`, per-channel message queues, cached remote descriptors, heartbeat values, chctl bitfields, timers, wait queues, atomics, and references. The reserved page is a shared firmware/platform memory area whose timestamp advertises initialization.

Dependencies and integration: includes `xp.h` for public return codes and registration/callback contracts. UV architecture code fills `xpc_arch_ops`. XP base installs XPC entry points after XPC init.

Risks: many flags can coexist transiently; invalid combinations are guarded mostly by `DBUG_ON()`. Refcount helpers are central to avoiding use-after-free of partition infrastructure and message queues. Message sizes must stay within one or two GRU cachelines. Reserved page version major mismatch rejects peers.

Test signals: state-machine coverage for activation, reactivation, heartbeat loss, open/close races, disconnect wait, message delivery/ack, notifier completion, and architecture-operation failure paths.
