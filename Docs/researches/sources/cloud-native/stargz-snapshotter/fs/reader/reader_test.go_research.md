# sources/cloud-native/stargz-snapshotter/fs/reader/reader_test.go

## Purpose
Adapts the generic reader test suite to the in-memory metadata backend. It is intentionally small because the real behavioral matrix lives in `testutil.go`.

## Important APIs, Types, And Functions
`TestReader` constructs a `TestRunner` that adapts `testing.T` to the local suite interface, then invokes `TestSuiteReader(testRunner, memorymetadata.NewReader)`.

## Control Flow
Each subtest name and body is delegated to `testing.T.Run`. The suite receives `memorymetadata.NewReader` as the `metadata.Store` factory, so all file-read, cache, verification, preread, and batch-processing cases run against the in-memory metadata implementation.

## State And Persistence
No production state is persisted. Test state is scoped to the `testing.T` lifecycle and in-memory caches created by the suite.

## Dependencies And Integration
Depends on `metadata/memory` and the same package's `TestSuiteReader`. This file is the integration point ensuring the generic reader contract remains true for the default in-memory metadata reader.

## Risks And Test Signals
The main risk is that the suite adapter hides failures if it mishandles `TestingT`; it checks the concrete type before invoking `Run`. Passing this test signals that `reader.go` works with the memory metadata reader across the comprehensive shared suite.
