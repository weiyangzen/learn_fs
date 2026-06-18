# sources/distributed-fs/eos/namespace/ns_quarkdb/CacheRefreshListener.cc

Purpose: implements QuarkDB pub/sub callbacks that invalidate MGM metadata caches when external tooling modifies file or container metadata.

Important APIs/types/functions: the constructor creates a `qclient::Subscriber`, subscribes to `constants::sCacheInvalidationFidChannel` and `constants::sCacheInvalidationCidChannel`, and attaches callbacks to `processIncomingFidInvalidation` and `processIncomingCidInvalidation`. Each callback parses the payload with `common::ParseUInt64` and calls `MetadataProvider::dropCachedFileID` or `dropCachedContainerID`.

Control flow: subscription setup happens at construction. Incoming messages are logged, parsed as unsigned ids, and ignored if parsing fails. Valid ids are wrapped in `FileIdentifier` or `ContainerIdentifier` before cache-drop dispatch.

State and persistence: holds subscriptions for listener lifetime; does not persist anything. The effect is cache invalidation in the in-process metadata provider.

Dependencies and integration: depends on `QdbContactDetails`, `qclient/pubsub`, `Constants.hh`, `MetadataProvider.hh`, `Identifiers.hh`, and `ParseUtils`. Created by `QuarkNamespaceGroup::startCacheRefreshListener`.

Risks: callback uses a raw `MetadataProvider*`, so provider lifetime must outlive the listener. Invalid messages are silently ignored after logging only the payload. Subscription callback threading depends on qclient and must not race provider destruction.

Test signals: expected to be integration-tested with cache invalidation flows; direct unit tests are not visible in this subset.
