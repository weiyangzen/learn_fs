# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_req.h

## Purpose
Defines the DRBD request event vocabulary, request state-bit encoding, completion helper structure, and public request-state APIs used by the primary request path, receiver ack handling, transfer-log cleanup, and timers. The header documents the intended lifetime of `struct drbd_request`: creation on a primary, optional local and/or remote submission, transfer-log/list membership, conflict handling, local and peer completion, bitmap/activity-log cleanup, and final upper-bio completion/destruction.

## Important APIs, Types, And Functions
- `enum drbd_req_event` lists all state-machine inputs accepted by `__req_mod()`: creation/intention events, network queue/send/ack/failure events, conflict events, local completion/error events, disk abort/restart events, resend/frozen-I/O events, and no-op.
- `enum drbd_req_state_bits` defines bit positions for local state, network state, operation kind, activity-log membership, unplug hints, conflict postponement, completion suspension, and expected ack types.
- `RQ_LOCAL_*`, `RQ_NET_*`, `RQ_WRITE`, `RQ_UNMAP`, `RQ_ZEROES`, `RQ_IN_ACT_LOG`, `RQ_POSTPONED`, `RQ_COMPLETION_SUSP`, `RQ_EXP_RECEIVE_ACK`, `RQ_EXP_WRITE_ACK`, and `RQ_EXP_BARR_ACK` are the public bit masks manipulated by `drbd_req.c`, sender callbacks, receiver ack handlers, and cleanup paths.
- `MR_WRITE` and `MR_READ` are return flags used when transfer-log restart logic needs to count affected requests by operation type.
- `struct bio_and_error` is a stack carrier used by state transitions to return a bio plus final errno after dropping `req_lock`.
- `__req_mod()`, `_req_mod()`, and `req_mod()` are the state-transition entry points. The inline wrappers handle locking and delayed `complete_master_bio()`.
- Exported declarations connect request state to transfer-log epoch management (`start_new_tl_epoch()`, `tl_restart()`, `_tl_restart()`, `tl_abort_disk_io()`), destruction (`drbd_req_destroy()`), request timeout (`request_timer_fn()`), request retry (`drbd_restart_request()`), and remote-path eligibility (`drbd_should_do_remote()`).

## Control Flow
Callers that already hold `resource->req_lock` use `__req_mod()` directly when they also handle the returned `bio_and_error`, or `_req_mod()` when they want the wrapper to complete any returned bio after the state update. Callers outside the lock use `req_mod()`, which takes `req_lock` with IRQ save/restore, invokes `__req_mod()`, releases the lock, and then completes the master bio if requested.

The event and state-bit definitions encode the legal progression that `drbd_req.c` enforces. Local bits move from no local path to pending, completed ok/error, or aborted. Network bits move from no network path to pending, queued, sent, ok/failed, and done, with protocol-specific expectations for receive ack, write ack, and barrier ack. Operation bits distinguish reads from writes and special write operations so completion, bitmap, discard, and timeout behavior can branch without inspecting the original bio repeatedly.

## State And Persistence
The header itself stores no runtime state, but its bit layout is the persistence contract for in-memory request objects and transfer-log cleanup. `RQ_IN_ACT_LOG` means the activity log must be completed later; `RQ_NET_SIS` records that a peer set the range in-sync; `RQ_POSTPONED` suppresses final completion/destruction so retry logic can re-enter make-request; `RQ_COMPLETION_SUSP` prevents upper-bio completion while I/O is suspended; `RQ_EXP_BARR_ACK` accounts for an extra lifetime reference while a network write waits for its epoch barrier.

Because the comments define which bit combinations mean freeable, pending, failed, or acknowledged, changes to this header directly affect bitmap dirtying, upper-layer completion, transfer-log replay/cleanup, and whether local activity-log extents can be safely dropped after crashes.

## Dependencies And Integration Points
The header includes Linux module/slab/DRBD public headers and `drbd_int.h` for core structures. It is included by `drbd_req.c` for implementation, `drbd_receiver.c` for ack-to-event mapping, and `drbd_main.c` for transfer-log release/clear paths. The inline wrappers depend on `complete_master_bio()` being safe outside `req_lock` and on `__req_mod()` initializing `bio_and_error` before returning.

## Risks And Edge Cases
The state encoding is compact but non-obvious. Adding or reusing bits without auditing `RQ_LOCAL_MASK`, `RQ_NET_MASK`, destructor checks, and protocol-specific transitions can make requests complete early or never free. The wrapper comment that `__req_mod()` may free `req` is important: callers must not touch a request after invoking `_req_mod()`/`req_mod()` unless they hold another valid reference. Completion outside the spinlock is required because `bio_endio()` can re-enter block-layer paths and must not run under DRBD's request lock.

## Test Signals
Useful signals are compile-time coverage of every `enum drbd_req_event` switch case, lockdep-clean use of `req_mod()` from IRQ/BH/thread contexts, no use-after-free after `_req_mod()`, correct delayed bio completion outside `req_lock`, transfer-log cleanup handling `MR_WRITE`/`MR_READ`, and state-bit combinations observed in protocol A/B/C write completion, read retry, suspended I/O, barrier ack, and negative ack paths.
