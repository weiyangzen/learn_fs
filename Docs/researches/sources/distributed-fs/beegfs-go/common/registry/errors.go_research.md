# sources/distributed-fs/beegfs-go/common/registry/errors.go

Purpose: defines registry package sentinel errors for feature and capability lookup failures.

Important exported errors are `ErrUnsupportedFeature`, `ErrRegistryClientUnavailable`, `ErrRegistryUninitialized`, and `ErrCapabilitiesNotSupported`.

Control flow is indirect: other registry files wrap or compare these sentinels with `errors.Is`. `capability.go` returns unsupported-feature errors when required feature trees are absent and maps unimplemented gRPC capabilities to `ErrCapabilitiesNotSupported`. `cache.go` uses unavailable and uninitialized sentinels for client resolver and lazy-init states.

State and persistence: none; these are package-level immutable `error` values from `errors.New`.

Dependencies are only the standard `errors` package. Integration points are callers that branch on unsupported remote features versus inability to fetch the registry at all.

Risks: callers need to preserve wrapping with `%w` or `errors.Join` for `errors.Is` to work. The sentinels intentionally distinguish unsupported features from unsupported capability RPC, which should not be collapsed in UI or retry logic.

Test signals: cache and capability tests assert these sentinels with `assert.ErrorIs`.
