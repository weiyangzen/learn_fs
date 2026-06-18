# sources/cloud-native/nydus-snapshotter/pkg/auth/renewal_test.go

Purpose: verifies renewable provider contracts, credential store semantics, renewal behavior, stale eviction, and interaction between provider lookup and the renewal store.

Important APIs and functions: test doubles `mockProvider`, `mockNonRenewableProvider`, and `trackingProvider`; tests for `RenewableProvider` type assertions, `credentialStore` methods, `RenewCredential`, `EvictStaleCredentials`, `GetStoredCredential`, and `getRegistryKeyChainFromProviders`.

Control flow: tests swap globals (`renewableProviders`, `renewalStore`) and restore them with defers. Store tests add/remove/inspect entries. Renewal tests substitute a tracking provider and check call counts and nil/non-nil results. Eviction tests use tiny intervals or normal intervals to test grace behavior. Provider-chain tests verify cached hit, renewable storage, non-renewable no-storage, and nil-store behavior.

State and persistence: in-memory only. The concurrency test runs add/get/entries/remove from 100 goroutines against one store to exercise locking.

Dependencies and integration points: imports real providers for type assertions, so changes to provider renewal membership should update this test.

Risks and gaps: tests do not assert Prometheus metric values or `RenewCredential` with nil `renewalStore`. The tracking provider's `nilNext` path is defined but not heavily used. Global mutation means tests must remain careful about parallelization.

Test signals: strong coverage of store locking and expected renewable-vs-nonrenewable caching behavior.
