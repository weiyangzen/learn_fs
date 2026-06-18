# sources/cloud-native/buildkit/solver/testutil/cachestorage_testsuite.go

## Purpose
This file defines a reusable conformance suite for implementations of `solver.CacheKeyStorage`. It verifies result storage, cache links, release cascading, backlinks, and reverse lookup by result ID.

## Important APIs
`RunCacheStorageTests` accepts a factory for a fresh `CacheKeyStorage` and runs six test functions. `runStorageTest` wraps each case in a named subtest. The individual tests are `testResults`, `testLinks`, `testResultReleaseSingleLevel`, `testBacklinks`, `testResultReleaseMultiLevel`, and `testWalkIDsByResult`. Helpers `getFunctionName` and `rootKey` provide readable subtest names and expected backlink digests.

## Control Flow
Each test gets a new storage instance. Result tests add results with timestamps, walk by key, and load by key/result ID. Link tests add multiple targets under the same link and walk them. Release tests remove result IDs and check whether cache IDs and graph links are retained or pruned. Backlink tests verify reverse edges from child cache IDs to parent links. Reverse lookup tests walk all cache IDs associated with a result ID.

## State and Persistence
The suite exercises storage semantics but owns no persistent state itself. It assumes each storage factory returns isolated state. Several tests run in parallel, so implementations must tolerate independent concurrent test processes over separate instances.

## Dependencies and Integration Points
It imports `solver`, OCI digest, `pkg/errors`, and `testify/require`. It is used by storage implementation tests, including the in-memory cache storage test in this subset.

## Risks Covered
The suite catches orphaned links after release, accidental parent deletion while children still reference it, missing backlink root-key normalization, incorrect not-found errors, and missing reverse result indexes. It does not test durable on-disk crash recovery.

## Test Signals
Strong contract-level signal for cache storage implementations. The Windows timestamp guard avoids false failures from coarse clock resolution.
