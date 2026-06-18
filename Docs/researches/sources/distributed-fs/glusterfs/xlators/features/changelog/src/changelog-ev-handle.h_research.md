# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-ev-handle.h

## Purpose
Defines brick-side reverse RPC client and connection-list structures for changelog event delivery.

## APIs, Types, and Functions
`changelog_rpc_clnt_t` stores owning xlator, lock, atomic refcount, disconnect flag, filter mask, reverse socket path, owning `changelog_clnt_t`, RPC client pointer, list node, and cleanup callback. Inline helpers manage refs and disconnected state. `changelog_clnt_t` owns pending, active, and wait queues, their locks/conditions, the rotating buffer, and sequence counter. The header declares connector, dispatcher, queue, cleanup, and cleanup-notification functions.

## Control Flow, State, and Persistence
Pending clients are inserted under `pending_lock`, moved to active after connect under active locking, and destroyed after disconnect plus final ref release. Sequence state is held in memory and is reset when RPC threads initialize. No persistent state is represented here.

## Dependencies and Integration
Uses Gluster lists, locks, atomics, `rpc-clnt.h`, and `rot-buffs.h`. Included by `changelog-helpers.h`, `changelog-rpc.c`, and `changelog-ev-handle.c`.

## Risks and Test Signals
Risks include refcount underflow, `list_del()` on already removed nodes, lock-order mistakes between pending/active/wait locks, and stale socket/filter ownership. Test signals are thread-sanitized connect/disconnect tests, final unref cleanup, and queue transitions under simultaneous dispatch.
