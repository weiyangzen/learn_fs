# sources/distributed-fs/beegfs-go/common/registry/cache_test.go

Purpose: tests `CachedComponentRegistry` behavior against a configurable mock `RegistryGetter`.

Important helpers are `mockResponse`, `mockRegistryClient`, `newCapabilities`, and `registryClientFunc`. The mock returns queued responses and counts calls under a mutex.

Control flow: tests verify missing clients and unimplemented capability RPCs surface the expected sentinels; TTL values are applied; reads inside TTL do not refresh; reads after TTL eventually trigger asynchronous refresh; failed refresh stores `lastErr`; a subsequent call refreshes synchronously and clears the error; lazy `WithSkipInit` registries fetch on first `RequireFeature(s)`.

State behavior under test includes `ttl`, `lastErr`, cached build info, call counts, and nested feature trees. The tests use `assert.Eventually` for asynchronous refresh.

Dependencies are `testing`, `time`, `sync`, `grpc/status`, `grpc/codes`, `timestamppb`, and `testify/assert`.

Integration points are the gRPC capabilities endpoint and the feature validation layer in `capability.go`.

Risks: async timing tests can be sensitive to slow environments. Tests inspect private mutex-protected state, which makes internal changes visible. They do not test concurrent callers racing through `updateRegistry`, nil response shape errors, or unchanged start timestamp with changed features.

Test signals: strong coverage of cache refresh and lazy/error behavior.
