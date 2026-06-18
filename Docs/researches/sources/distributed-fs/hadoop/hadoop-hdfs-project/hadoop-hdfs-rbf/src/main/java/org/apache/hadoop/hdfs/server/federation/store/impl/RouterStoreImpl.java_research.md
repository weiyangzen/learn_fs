# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/impl/RouterStoreImpl.java

Purpose: Implements `RouterStore`, the state-store API for router registrations and router heartbeats.

Important APIs/types/functions: methods are `getRouterRegistration`, `getRouterRegistrations`, and `routerHeartbeat`.

Control flow: single-router lookup builds a partial `RouterState` with address equal to the requested router id, queries the driver, applies `overrideExpiredRecord` when found, and returns a response. Multi-router lookup reads cached records plus timestamp and returns both. Heartbeat writes the submitted `RouterState` with update allowed and duplicate errors disabled.

State/persistence behavior: router liveness and metadata persist as driver `RouterState` records. Listing uses the parent store cache, while heartbeats write directly to the state store.

Dependencies/integration: used by router heartbeat services and admin/status APIs; depends on `Query`, `QueryResult`, `RouterState`, and router protocol request/response factories.

Risks: single lookup queries the driver directly while list lookup uses cache, so freshness may differ; submitted heartbeat records are trusted; expired override mutates the response view.

Test signals: heartbeat insert/update, expired router override, cached timestamp propagation, direct query by address, and cache refresh behavior should be verified.
