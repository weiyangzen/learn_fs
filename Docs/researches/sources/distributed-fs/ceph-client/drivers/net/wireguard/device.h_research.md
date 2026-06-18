# sources/distributed-fs/ceph-client/drivers/net/wireguard/device.h

Purpose: Defines the central WireGuard device state and queue worker structures shared by device, packet, peer, socket, netlink, and timer code.

Important APIs and types: `struct multicore_worker` pairs a work item with a queue pointer for per-CPU crypto/handshake workers. `struct crypt_queue` wraps a `ptr_ring`, per-CPU workers, and last CPU cursor. `struct prev_queue` is the ordered per-peer queue used to preserve packet order after parallel crypto. `struct wg_device` aggregates netdev pointer, encrypt/decrypt/handshake queues, RCU sockets, creating netns, static identity, workqueues, cookie checker, lookup tables, allowedips trie, locks, peer/device lists, handshake queue length, peer count, update generation, fwmark, and incoming port. Exports `wg_device_init()` and `wg_device_uninit()`.

Control flow: The header has no executable flow, but it is the state contract used by `device.c` allocation/teardown, `send.c`/`receive.c` queueing, `netlink.c` control changes, `socket.c` RCU socket replacement, and `peer.c` peer insertion/removal.

State and persistence: Declares all volatile per-interface runtime state. `sock4`, `sock6`, and `creating_net` are RCU-protected; `device_update_lock` serializes control-plane mutations; `socket_update_lock` serializes socket replacement. No durable persistence exists.

Dependencies and integration points: Includes Noise, allowedips, peerlookup, cookie, netdevice, workqueue, mutex, ptr_ring, and socket types. It is high fanout and creates circular dependency pressure with `peer.h` and queueing headers.

Risks: Any field lifetime change affects multiple asynchronous paths. `prev_queue.empty` must match the first two members of `struct sk_buff`, enforced in queue code. Locking semantics are implicit in the struct and must remain consistent across callers.

Test signals: Build coverage across all WireGuard C files, RTNL link create/destroy, socket replacement, queue init/free, and peer removal while queues and work items are active.
