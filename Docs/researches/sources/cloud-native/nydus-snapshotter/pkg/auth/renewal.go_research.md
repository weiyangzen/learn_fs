# sources/cloud-native/nydus-snapshotter/pkg/auth/renewal.go

Purpose: implements the in-memory renewable credential cache and functions used by the snapshotter renewal loop.

Important APIs and functions: global `renewalStore`; `InitCredentialStore`; `GetStoredCredential`; `RenewCredential`; `EvictStaleCredentials`; internal `credentialEntry`; internal concurrency-safe `credentialStore` with `Add`, `Get`, `Remove`, and `Entries`.

Control flow: `InitCredentialStore` replaces the global store with a fresh map and interval. `GetStoredCredential` returns nil if disabled/missing. `RenewCredential` calls `fetchFromProviders` using `renewableProviders()` with a request valid until the next interval, increments success/failure metrics, and returns the refreshed keychain. `EvictStaleCredentials` snapshots entries and removes refs not in the supplied live set only if they are older than half the renewal interval.

State and persistence: credentials live only in process memory under an RW mutex. Each entry records ref, keychain pointer, and `renewedAt`. Metrics are updated on add/remove/renew.

Dependencies and integration points: called by auth lookup in `keychain.go` and by higher-level snapshot renewal code outside this subset. Uses `pkg/metrics/data` gauges/counters and containerd logging.

Risks: `RenewCredential` assumes `renewalStore` is non-nil; callers must initialize before use. `Get` returns the stored keychain pointer directly, so callers could mutate cached credentials. Global store replacement is not synchronized with concurrent users. Per-ref metrics labels can grow if many unique refs are cached, though removal deletes labels.

Test signals: `renewal_test.go` covers provider type assertions, store get/add/remove/upsert/entries/concurrency, renew success/failure, stale eviction with grace period, nil store behavior, and provider-chain cache interactions.
