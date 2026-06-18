# sources/distributed-fs/ceph-client/io_uring/eventfd.c

## Purpose
`eventfd.c` manages io_uring completion eventfd registration, signaling, and unregistering.

## Important APIs, Types, And Functions
- `struct io_ev_fd` stores the eventfd context, async-only mode, last CQ tail, refcount, pending signal bit, and RCU head.
- `io_eventfd_register()` installs an eventfd for a ring.
- `io_eventfd_unregister()` removes it.
- `io_eventfd_signal()` signals the eventfd when completions are posted and notification policy allows it.
- `__io_eventfd_signal()` either signals immediately or defers through RCU when signaling is not currently allowed.

## Control Flow
Registration requires `ctx->uring_lock`, rejects duplicate eventfd registration, copies the fd from userspace, gets an `eventfd_ctx`, snapshots current CQ tail under `completion_lock`, sets ring flags, and publishes via RCU. Signaling checks ring availability, disabled CQ flag, async-only policy, and refcount. For CQE events, it suppresses duplicate notifications when `cached_cq_tail` has not advanced.

## State And Persistence
Per-ring state is `ctx->io_ev_fd` and `IO_RING_F_HAS_EVFD`. `last_cq_tail` tracks notification coalescing. RCU/refcounted `io_ev_fd` persists until all signal paths drop references after unregister.

## Dependencies And Integration Points
The file depends on eventfd, eventpoll wake mask `EPOLL_URING_WAKE`, io-wq worker detection for async mode, RCU, completion lock, and ring CQ flags. It is called by completion posting paths.

## Risks And Edge Cases
RCU/refcount correctness is critical around unregister racing with signal. Deferred signaling uses an atomic pending bit to avoid queuing multiple RCU callbacks. Duplicate notification suppression depends on `cached_cq_tail` under `completion_lock`.

## Test Signals
Tests should cover register/unregister, duplicate register `-EBUSY`, disabled CQ eventfd flag, async-only behavior from worker vs submitter, CQ tail coalescing, and unregister while completions race.
