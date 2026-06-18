# sources/distributed-fs/ceph-client/net/ceph/osd_client.c

## Purpose
`osd_client.c` is the kernel libceph OSD request engine. It builds MOSDOp requests, maps object locators through the current OSD map, owns per-OSD messenger sessions, submits and retries requests, processes OSD replies, handles OSD map changes, manages watch/notify linger requests, tracks OSD backoff ranges, and provides sparse-read receive support to the messenger. It is the integration point between CephFS/RBD/RADOS callers and the lower messenger/auth/monitor/map machinery.

## Important APIs, types, and functions
- Public request construction and lifecycle APIs include `ceph_osdc_alloc_request()`, `ceph_osdc_new_request()`, `ceph_osdc_alloc_messages()`, `ceph_osdc_start_request()`, `ceph_osdc_wait_request()`, `ceph_osdc_cancel_request()`, `ceph_osdc_sync()`, `ceph_osdc_get_request()`, and `ceph_osdc_put_request()`.
- Operation setup helpers populate `struct ceph_osd_req_op`: `osd_req_op_init()`, `osd_req_op_extent_init()`, `osd_req_op_extent_update()`, `osd_req_op_extent_dup_last()`, `osd_req_op_cls_init()`, `osd_req_op_xattr_init()`, `osd_req_op_alloc_hint_init()`, `osd_req_op_copy_from_init()`, and the `*_osd_data_*()` helpers for pages, bios, bvecs, pagelists, and iterators.
- `struct ceph_osd_client` holds the current `ceph_osdmap`, OSD session tree, linger request trees, map-check trees, request counters, mempools, message pools, and workqueues. Its synchronization root is `osdc->lock`, a read/write semaphore.
- `struct ceph_osd` models one OSD session: messenger connection, request/linger rbtrees, backoff trees, LRU state, auth handshake state, keepalive list node, and sparse-read receive state.
- `struct ceph_osd_request_target` records base and target object identifiers, current raw PG and actual shard PG, up/acting sets, selected OSD, pool flags, pause state, epoch, and resend markers.
- Linger/watch public APIs include `ceph_osdc_watch()`, `ceph_osdc_unwatch()`, `ceph_osdc_notify()`, `ceph_osdc_notify_ack()`, `ceph_osdc_list_watchers()`, and `ceph_osdc_flush_notifies()`.
- OSD map and cluster-state entry points include `ceph_osdc_handle_map()`, `ceph_osdc_maybe_request_map()`, `ceph_osdc_update_epoch_barrier()`, `ceph_osdc_abort_requests()`, `ceph_osdc_clear_abort_err()`, and `ceph_osdc_reopen_osds()`.
- Messenger integration is through `osd_con_ops`, with callbacks for allocation, dispatch, fault handling, sparse reads, auth handshake, reencoding, signing, and signature verification.

## Control flow
Request setup starts with allocation from the request slab/mempool or a flexible allocation for larger operation arrays. Callers initialize operation descriptors and attach data buffers, then allocate request and reply `ceph_msg` objects. `ceph_osdc_new_request()` also maps file layout offsets into object names and object extents using Ceph layout math, fills `r_base_oid` and `r_base_oloc`, and records snap/write metadata.

Submission flows through `ceph_osdc_start_request()` -> `submit_request()` -> `__submit_request()`. `__submit_request()` calls `calc_target()` against the current OSD map, creates or looks up the target `struct ceph_osd`, assigns a monotonically increasing TID atomically with request linking, and either sends, pauses, map-checks, or completes with an error. Writes are paused on full or `PAUSEWR` maps unless force flags allow them; reads are paused on `PAUSERD`; requests can also be held behind an epoch barrier.

`send_request()` refuses to send if the request falls inside an installed OSD backoff range. Otherwise it revokes any old queued message, sets retry/redirect flags, encodes MOSDOp front data in `encode_request_partial()`, records send timing, assigns the TID to the message header, and queues the message on the OSD connection. `encode_request_finish()` runs later from the messenger to append peer features for modern OSDs or reencode the front into a pre-luminous v4 layout when needed.

Reply handling uses `get_reply()` during receive allocation to find the registered request by TID and either reuse or resize the preallocated reply message. `handle_reply()` decodes `MOSDOpReply`, rejects mismatched retry attempts, handles redirect and read-replica `-EAGAIN` by resubmitting, validates operation counts and data length, records per-op return values and out lengths, finishes the request, and invokes completion inline. Decode or consistency failure completes with `-EIO`.

OSD map handling begins in `osd_dispatch()` for `CEPH_MSG_OSD_MAP`. `ceph_osdc_handle_map()` validates FSID, applies sequential incremental maps when possible, otherwise takes the newest full map, scans all requests and linger requests for target changes, closes sessions whose OSD went down or address changed, kicks resends, updates monitor subscriptions, aborts write requests when `ABORT_ON_FULL` applies, and wakes authentication waiters. Pool deletion uncertainty is resolved with async monitor version checks (`send_map_check()` and `send_linger_map_check()`).

Linger/watch flow allocates a `ceph_osd_linger_request`, registers it in client and OSD rbtrees, sends a watch/notify registration request, waits for commit, and then maintains state across map changes and connection faults. Watch notifications are decoded in `handle_watch_notify()` and queued to `notify_wq`; disconnect/error callbacks are normalized and also queued. Periodic timeout work sends watch pings to validate committed watches.

Backoff control decodes `MOSDBackoff` messages into hobject ranges per spg. Block messages install ranges and ACK the OSD; unblock messages remove ranges and attempt to resend matching requests that are no longer plugged. Connection faults clear all backoffs for that OSD and resubmit pending work.

Sparse reads are stateful across the messenger data cursor. `osd_sparse_read()` alternates through header, extent-count, extent-array, data-length, and data states; it zero-fills holes in the caller buffer, exposes extent data receive lengths to the messenger, and stores decoded sparse extent arrays back onto the matching OSD op.

## State and persistence behavior
State is in memory only. Persistent cluster truth comes from monitor-delivered OSD maps and OSD replies, but this file itself maintains no on-disk state. Major mutable structures are rbtrees keyed by TID, OSD id, linger id, spgid, hobject range, and backoff id. Request references are managed with `kref`; OSD sessions with `refcount_t`; linger requests with `kref`. Request data ownership varies by data type and `own_pages`/`pages_from_pool` flags, so release paths must mirror initialization.

The client schedules two delayed works: request/keepalive timeout scanning and idle OSD-session cleanup. `ceph_osdc_stop()` destroys workqueues, cancels delayed works, closes sessions, validates empty trees and counters, then destroys map, pools, and mempools.

## Dependencies and integration points
This file depends directly on `osdmap.c` APIs for pool lookup, object-to-PG mapping, acting/up set calculation, primary shard selection, and OSD map decoding. It uses `striper.c` through layout calculations for file-backed object requests. It uses `pagelist.c` and `pagevec.c` for encoded payloads and reply buffers, `snapshot.c` for snap context references, and `string_table.c` through pool namespace references in `ceph_object_locator`. It integrates with monitor client map subscriptions and version checks, messenger connection operations, auth client authorizers/signatures, debugfs state dumps, and higher CephFS/RBD callers through exported libceph APIs.

## Risks and edge cases
- Lock ordering is subtle: `osdc->lock`, per-OSD `mutex`, request-tree spinlock paths for sparse reads, and linger mutexes interact with callbacks and workqueues.
- Resend decisions depend on exact PG split, up/acting change, force-resend epoch, pool full, pause, and replica-read state; a missed condition can produce stale reads or writes sent to the wrong primary.
- Data ownership is mixed across pages, pagelists, bios, bvecs, and iov_iters. Incorrect `own_pages` or mempool flags can leak pages or double-free.
- Wire compatibility is broad: MOSDOp v8/v4 reencoding, reply v4+ decode, watch notify versions, object locator redirects, and messenger v2 addressing all need regression coverage.
- Sparse-read cursor state is per OSD connection and tied to matching request/op indexes; receive aborts and connection faults must reset it to avoid corrupting later replies.
- Backoff ranges are sorted by hobject identity and scoped to spgid; PG split or malformed ranges can plug or unblock too much work.
- Full/nearfull handling and `ABORT_ON_FULL` affect user-visible errors and cap-release epoch barriers.

## Test signals
Useful tests include OSD read/write request submission with map changes, pool deletion while requests are pending, full cluster/pool behavior with and without `ABORT_ON_FULL`, replica-read fallback on `-EAGAIN`, redirect replies, OSD connection fault/resend behavior, watch registration/reconnect/ping/notify/disconnect flows, list-watchers decode, class method calls, copy-from payload construction, sparse-read replies with holes and multiple ops, big-endian sparse extent conversion, and backoff block/unblock messages. Kernel sanitizers and lockdep are particularly valuable for this file because many correctness failures are lifetime or locking bugs.
