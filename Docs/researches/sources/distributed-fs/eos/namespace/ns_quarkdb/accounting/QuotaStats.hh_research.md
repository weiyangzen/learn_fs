## sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/QuotaStats.hh

Purpose: Declares the QuarkDB quota accounting implementation. It documents the per-container hash layout for user and group quota counters and exposes the quota-node and manager classes.

Important APIs and types: `QuarkQuotaNode` extends `IQuotaNode` and provides file add/remove, node meld, backend refresh, full core replacement, and partial core update. It stores UID/GID hash keys plus non-owning backend/flusher pointers inherited from `QuarkQuotaStats`. `QuarkQuotaStats` extends `IQuotaStats`, creates and caches `IQuotaNode`s, removes quota nodes, returns all quota IDs, and contains static helpers for key construction and parsing.

State and persistence: the interface maps one quota node to one container ID. Backend state is split into `quota:<id>:uid` and `quota:<id>:gid` style hashes using suffix constants. In-memory cache ownership is in `pNodeMap`; backend write durability is delegated to `MetadataFlusher`.

Dependencies and integration: integrates with EOS quota interfaces, container IDs, QuarkDB `QClient`, and `MetadataFlusher`. `QuarkQuotaStats` is a friend of `QuarkQuotaNode` for dependency access, while `QuarkQuotaNode` relies on inherited `IQuotaNode::pCore`.

Risks and test signals: since methods return raw `IQuotaNode*` owned by `pNodeMap`, consumers must not retain pointers past `removeNode()` or destruction. Tests should lock down documented key names, duplicate-node errors, null return for missing nodes, and that `configure()` intentionally has no runtime configuration.
