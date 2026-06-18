# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/AbstractBlockStoreEventListener.java

Purpose: `AbstractBlockStoreEventListener` is a convenience base class for block-store event listeners that only care about a subset of events.

Important APIs are no-op implementations of every `BlockStoreEventListener` callback: access, abort, commit to local/master, move by client/worker, remove by client/worker/general, block lost, and storage lost by tier/path or location. Control flow is intentionally empty; subclasses override only relevant methods.

State and persistence are absent. Dependencies are the block store listener interface and block location types. Integration points include `BlockHeartbeatReporter`, which extends this class and overrides movement/removal/loss callbacks. Risks are low, but missed overrides silently drop events, so listener implementations must be reviewed against required reporting semantics. No direct tests in this subset cover the base class.
