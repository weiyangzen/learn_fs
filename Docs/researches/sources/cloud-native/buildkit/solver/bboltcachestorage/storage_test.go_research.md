## sources/cloud-native/buildkit/solver/bboltcachestorage/storage_test.go

Purpose: applies the solver shared cache storage conformance suite to the bbolt backend.

Important APIs/types/functions: `TestBoltCacheStorage` creates a temp database path, calls `NewStore`, registers cleanup to close it, and passes the store to `testutil.RunCacheStorageTests`.

Control flow: the test is mostly harness glue. All substantive scenarios come from the shared testutil suite.

State and persistence: test database lives under `t.TempDir` and is closed after the test.

Dependencies and integration points: verifies `bboltcachestorage.Store` satisfies `solver.CacheKeyStorage` behavior expected by the solver.

Risks and test signals: strength depends on `RunCacheStorageTests`; this file itself does not cover corruption, NoSync durability, or concurrent access. It is still the main regression signal for API conformance.
