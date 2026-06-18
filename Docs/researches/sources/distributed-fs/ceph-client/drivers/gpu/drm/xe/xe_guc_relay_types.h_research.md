# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_relay_types.h

## Purpose
Defines persistent state for VF-PF relay communication over GuC.

## Important APIs, Types, And Functions
`struct xe_guc_relay` contains a spinlock, worker, pending transaction list, incoming action list, transaction mempool, last relay ID, and diagnostic ratelimit state.

## Control Flow
The implementation initializes these fields only in SR-IOV mode. Send paths append to `pending_relays`; receive paths append to `incoming_actions`; the worker drains incoming actions; teardown exits the mempool.

## State And Persistence
All fields persist with the GuC object. `last_rid` is monotonically incremented for outgoing transactions, and the mempool bounds allocation in contexts where sleeping allocation is unsafe.

## Dependencies And Integration Points
Uses Linux mempool, ratelimit, spinlock, list, and workqueue types. The struct is embedded in `struct xe_guc`.

## Risks And Test Signals
The lists must be initialized before use and protected by `lock`. Mempool exhaustion affects relay availability under CTB-lock receive context. Relay KUnit and SR-IOV integration tests should verify pending and incoming list transitions.
