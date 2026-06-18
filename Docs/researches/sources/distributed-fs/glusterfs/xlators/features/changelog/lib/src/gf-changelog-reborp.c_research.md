# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-reborp.c

## Purpose
Implements the library-side reverse RPC server, named “reborp” as the reverse of probe. It accepts event batches pushed back by the brick-side changelog xlator and invokes registered consumer callbacks.

## APIs, Types, and Functions
`gf_changelog_reborp_init_rpc_listner()` creates a temporary Unix socket listener. `gf_changelog_reborp_rpcsvc_notify()` handles accept/disconnect, unlinks the temporary socket after accept, and calls connected/disconnected callbacks. `gf_changelog_event_handler()` decodes `changelog_event_req`, deep-copies payload iovecs into `struct gf_event`, queues them, and replies with `changelog_event_rsp`. Callback flow is handled by `gf_changelog_callback_invoker()`, `gf_changelog_invoke_callback()`, `queue_ordered_event()`, `queue_unordered_event()`, `pick_event_ordered()`, and `pick_event_unordered()`. `gf_changelog_connection_janitor()` drains cleanup entries.

## Control Flow, State, and Persistence
After the normal probe client asks the brick to connect back, this listener receives reverse RPC event calls. Event payloads are copied out of request memory, optionally sorted by sequence number, then consumed by a per-connection callback-invoker thread. Ordered mode initializes `next_seq` from the first event and only wakes the invoker when the expected sequence is present; unordered mode dispatches FIFO. No persistent files are written here, but journal-mode callbacks enqueue paths that are later persisted by the journal handler.

## Dependencies and Integration
Depends on `changelog-rpc-common` for server creation and reply serialization, XDR types from `changelog-xdr`, libgfchangelog helper types such as `gf_changelog_t`, and changelog event filters. It is started from `gf_changelog_setup_rpc()` before the probe request and shares RPC program numbers with the xlator reverse-dispatch path in `changelog-ev-handle.c`.

## Risks and Test Signals
Risks include unbounded event queue growth, ordered mode blocking forever on a missing sequence, callback execution from a single invoker thread, cleanup TODOs, and all server-side filtering currently being repeated library-side. Test signals include accept/disconnect callbacks, XDR decode failure replies, ordered out-of-order delivery, payload deep-copy correctness across multiple iovecs, and cleanup path behavior when callbacks or RPC clients disconnect.
