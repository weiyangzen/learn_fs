# sources/distributed-fs/eos/namespace/ns_quarkdb/QdbContactDetails.hh

Purpose: packages qclient cluster membership and optional password/handshake settings for QuarkDB access.

Important APIs/types/functions: constructors, `empty`, `constructOptions`, and `constructSubscriptionOptions`. Options enable transparent redirects, two-minute retry timeout, optional HMAC handshake, and push subscriptions for pub/sub.

Control flow: option builders allocate an `HmacAuthHandshake` only when password is non-empty and otherwise return unauthenticated options.

State and persistence: stores `qclient::Members members` and `std::string password`; no persistence.

Dependencies and integration: used by namespace group, metadata flushers, qclient creation, and cache refresh listener.

Risks: password is stored as a plain string in memory. `empty` does not treat missing password as invalid. Retry timeout choices affect failure latency for startup and subscriptions.

Test signals: configuration/parser and integration tests validate member parsing and connection behavior.
