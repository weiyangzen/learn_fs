# sources/cloud-native/stargz-snapshotter/fs/reader/testutil.go

## Purpose
Provides the reusable test suite for reader behavior. It builds eStargz fixtures, injects metadata stores and caches, and validates lazy reads, preread behavior, verification, failure handling, and whole-file batch merge logic.

## Important APIs, Types, And Functions
`TestSuiteReader` runs `testFileReadAt`, `testCacheVerify`, `testFailReader`, `testPreReader`, and `testProcessBatchChunks`. `makeFile` builds sample eStargz data and returns a concrete `*file`. Helpers such as `exceptFile`, `failIDVerifier`, `breakReaderAt`, `calledReaderAt`, `mockCache`, and `mockFile` force cache-hit, cache-miss, verifier-failure, and partial-read scenarios.

## Control Flow
The suite iterates over offsets, sizes, file sizes, cache population patterns, and compression formats. It verifies expected bytes, then confirms chunks were cached or avoided. Verification tests deliberately race `Cache` with `VerifyTOC` or `SkipVerify` to ensure errors before TOC verification surface from `VerifyTOC`, while later errors surface from `Cache`. Preread tests assert reading one file can cache neighbor file chunks that share compressed ranges. Batch tests run workers over artificial chunk sets and validate `checkHoles`.

## State And Persistence
All fixtures are in memory. State includes per-test memory caches, mock read call lists, mutable verifier failure sets, and a global `MockReadAtOutput` that is restored with cleanup.

## Dependencies And Integration
Depends on `util/testutil` to build eStargz data, gzip/zstd/external TOC compression factories, `metadata.Store`, `cache.NewMemoryCache`, and digest verifiers. It is reusable by any metadata backend that satisfies the reader contract.

## Risks And Test Signals
Signals include byte-accurate reads across chunk boundaries, cache avoidance for prefilled chunks, propagation of bad source readers and digest failures, preread side effects, and detection of incomplete or overlapping batch reads. Risks are combinatorial test cost and reliance on assumptions about eStargz chunk placement for preread fixtures.
