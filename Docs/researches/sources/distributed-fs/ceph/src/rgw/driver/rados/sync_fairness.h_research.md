# sources/distributed-fs/ceph/src/rgw/driver/rados/sync_fairness.h

## Purpose
Declares the sync fairness abstraction used by RGW sync code and the RADOS-backed factory.

## Important APIs, types, and functions
- `BidManager` defines `start()`, `is_highest_bidder(index)`, and `notify_cr()`.
- `create_rados_bid_manager()` constructs a RADOS watch/notify implementation for a given control object and shard count.

## Control flow
Consumers create a bid manager, call `start()` to establish watch state, periodically run the coroutine returned by `notify_cr()`, and gate shard work with `is_highest_bidder()`.

## State and persistence behavior
The interface hides all state. Implementations may keep bid maps in memory and use a RADOS object for peer notification.

## Dependencies and integration points
Forward declares `RadosStore`, `rgw_raw_obj`, and `RGWCoroutine`. It is integrated by RGW multisite sync scheduling code that needs distributed shard ownership fairness.

## Risks and edge cases
The interface does not specify exception behavior for invalid shard indexes or ownership when no notify exchange has completed. Callers need to handle `start()` failures and coroutine ownership of the raw pointer returned by `notify_cr()`.

## Test signals
Mock implementations can test sync scheduler behavior; RADOS implementation tests should validate factory construction and lifecycle through the declared interface.
