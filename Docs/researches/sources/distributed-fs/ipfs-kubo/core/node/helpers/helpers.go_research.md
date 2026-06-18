# sources/distributed-fs/ipfs-kubo/core/node/helpers/helpers.go

Purpose: defines lifecycle-aware context utilities for node services. Important APIs are `type MetricsCtx context.Context` and `LifecycleCtx`.

Control flow: `LifecycleCtx` derives a cancelable context from the metrics/root context and appends an fx `OnStop` hook that cancels it. Long-running services use this context to stop when the node lifecycle stops.

State and persistence: only in-memory context cancellation state is held. No external persistence.

Dependencies and integration: depends on Go `context` and fx. It is used across blockstore cache setup, host/routing construction, discovery, pubsub, provider resource-manager logging, and other background services.

Risks: comments acknowledge this is a workaround for services using contexts imperfectly. If callers ignore the returned context, shutdown still depends on explicit close hooks. No direct tests here; shutdown behavior is covered indirectly by service tests and `core/shutdown`.
