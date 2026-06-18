# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-ev-handle.c

## Purpose
Implements brick-side reverse event dispatch to libgfchangelog consumers. It manages reverse RPC clients, event selection reference counts, rotating buffer consumption, sequence numbering, and batched event sends.

## APIs, Types, and Functions
Dispatch helpers include `changelog_dispatch_vec()`, `changelog_event_dispatch_rpc()`, `changelog_ev_dispatch()`, `_dispatcher()`, and `sequencer()`. Connection lifecycle is handled by `changelog_rpc_notify()`, `changelog_ev_connector()`, `changelog_ev_queue_connection()`, `changelog_ev_cleanup_connections()`, `get_client()`, and `put_client()`. It defines `changelog_ev_program` for `CHANGELOG_REV_PROC_EVENT`.

## Control Flow, State, and Persistence
Probe handling in `changelog-rpc.c` enqueues `changelog_rpc_clnt_t` objects in `pending`. The connector thread creates RPC clients to the consumer’s reverse socket, and connect notifications move them to `active` while selecting their event filter. Dispatcher threads poll the rotating buffer once per second, claim consumable buffers, stamp sequence ranges, and send up to `NR_IOVEC` payload vectors per reverse RPC. Disconnect/destroy events disable clients, deselect filters, drop refs, and may trigger cleanup when xlator shutdown is pending.

## Dependencies and Integration
Depends on `rot-buffs`, shared RPC helpers, XDR event request types, event selection helpers in `changelog-helpers.c`, and RPC client lifecycle from libglusterfs. It is initialized by `changelog_init_rpc_threads()` in `changelog-rpc.c` and consumes events written by `changelog_dispatch_event()`.

## Risks and Test Signals
Risks include polling latency, coarse active-list locking while iterating clients, missing retransmit logic despite sequence acknowledgments, refcount/list races on disconnect, and buffer starvation under high event rates. Test signals include multi-client filtering, disconnect during dispatch, sequence continuity across split batches, NR_IOVEC boundary cases, and rotating-buffer empty/consumable/starvation return paths.
