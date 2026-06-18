# sources/distributed-fs/eos/namespace/ns_quarkdb/CacheRefreshListener.hh

Purpose: declares the cache refresh listener used to subscribe to metadata invalidation messages from QuarkDB.

Important APIs/types/functions: `CacheRefreshListener(const QdbContactDetails&, MetadataProvider*)`, destructor, private `processIncomingFidInvalidation`, `processIncomingCidInvalidation`, and members for contact details, metadata provider, qclient subscriber, and fid/cid subscriptions.

Control flow: construction and destruction own subscriber/subscription lifetime; callbacks are private implementation details.

State and persistence: stores subscriber state and raw provider pointer only; no persistent data.

Dependencies and integration: integrates qclient pub/sub with the namespace `MetadataProvider`. Used by `NamespaceGroup`.

Risks: raw pointer lifetime and asynchronous callback shutdown ordering are the main hazards. Subscription channels must match the constants used by external invalidation tools.

Test signals: cache invalidation behavior should be covered by integration tests or inspector tooling that publishes invalidation events.
