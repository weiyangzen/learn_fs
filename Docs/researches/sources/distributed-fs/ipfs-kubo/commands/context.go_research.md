# Research: sources/distributed-fs/ipfs-kubo/commands/context.go

Purpose: Defines command execution context for Kubo commands, including lazy node/API construction, request logging, gateway-specific API behavior, and cleanup.

Important APIs/types/functions: `Context` holds config root, request log, plugin loader, gateway mode, cached CoreAPI/node, and `ConstructNode`. `GetConfig`, `GetNode`, `ClearCachedNode`, `GetAPI`, `Context`, `LogRequest`, and `Close` are the key methods.

Control flow, state, and persistence: `GetNode` lazily calls `ConstructNode` once and caches the result. `ClearCachedNode` discards the cache to avoid daemon startup using an earlier offline node. `GetAPI` lazily builds a CoreAPI and disables block fetching when used by a gateway with `Gateway.NoFetch`. `LogRequest` adds an active `ReqLogEntry` and returns a closure that marks it finished. `Close` closes the cached node. Persistent repository state is accessed through `node.Repo.Config()` but not modified here.

Dependencies and integration points: Bridges `go-ipfs-cmds`, Kubo core/coreapi/config, plugin loader, and command request logging. Gateway and daemon startup paths depend on its node caching semantics.

Risks and test signals: The cached `api` is not cleared when `ClearCachedNode` is called, so callers must ensure stale API state cannot survive node replacement. No locking protects lazy fields, so concurrent command setup could race if shared unexpectedly. Tests are indirect through command integration.
