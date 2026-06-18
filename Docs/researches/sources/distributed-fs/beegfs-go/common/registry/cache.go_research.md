# sources/distributed-fs/beegfs-go/common/registry/cache.go

Purpose: provides a thread-safe TTL cache for a remote component capability registry, including lazy initialization and refresh-on-error behavior.

Important types/APIs are `getClientFunc`, `CachedComponentRegistry`, options `WithRegistryTTL` and `WithSkipInit`, `NewCachedComponentRegistry`, `GetBuildInfo`, `RequireFeature`, `RequireFeatures`, `updateIfNeeded`, and `updateRegistry`.

Control flow: construction applies options, validates the client resolver, and either fetches capabilities immediately or starts with `ErrRegistryUninitialized`. Public reads call `updateIfNeeded`, then inspect cached registry and last error under an RW mutex. If a prior error exists, refresh is synchronous. If TTL has expired without an error, refresh happens asynchronously in a goroutine.

State includes the cached `ComponentRegistry`, component `startTime`, `lastUpdate`, `lastErr`, TTL, and mutex. Registry replacement occurs only when the component start timestamp changes, so same-process feature responses do not replace the cached registry.

Dependencies are `context`, `sync`, `time`, and protobuf `flex`. Integration points are long-lived CTL or service clients that need to gate behavior by remote capabilities without hitting gRPC on every check.

Risks: asynchronous refresh means callers may observe stale data for one call after TTL expiry. If capabilities change without a start timestamp change, the registry is not replaced. `lastUpdate` is set before the fetch, so repeated failures are throttled only after the first error path forces sync retries.

Test signals: cache tests cover constructor errors, TTL, async refresh, refresh after error, lazy initialization, and feature requirements.
