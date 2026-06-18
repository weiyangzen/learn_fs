# sources/cloud-native/buildkit/solver/testutil/memorycachestorage_test.go

## Purpose
This file binds the generic cache storage conformance suite to the in-memory storage implementation. It is intentionally tiny: all behavioral coverage lives in `cachestorage_testsuite.go`.

## Important APIs
`TestMemoryCacheStorage` calls `RunCacheStorageTests(t, solver.NewInMemoryCacheStorage)`.

## Control Flow
The single test delegates to the reusable suite, which creates fresh storage instances per subtest and validates result, link, release, backlink, and reverse lookup behavior.

## State and Persistence
The implementation under test is in-memory, so there is no durable persistence. The test ensures the memory-backed storage maintains consistent graph state during the process lifetime.

## Dependencies and Integration Points
It depends on package `solver/testutil` and `solver.NewInMemoryCacheStorage`. It provides direct regression coverage for the default memory storage used by many solver tests.

## Risks
Because this file only delegates, failures point to either the implementation or the shared suite. It does not add in-memory-specific edge cases beyond the common storage contract.

## Test Signals
High signal as a smoke and conformance test for the in-memory backend; detailed assertions are inherited from the suite.
