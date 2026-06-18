# sources/cloud-native/stargz-snapshotter/metadata/memory/reader_test.go

## Purpose
Adapts the shared metadata reader test suite to the in-memory metadata implementation.

## Important APIs, Types, And Functions
`TestReader` constructs a `testutil.TestRunner` and calls `testutil.TestReader(testRunner, readerFactory)`. `readerFactory` wraps `NewReader` and type-asserts to `*reader` so the suite can access `NumOfNodes`.

## Control Flow
The runner maps suite subtests onto `testing.T.Run`. Each fixture in the shared suite is built as eStargz and opened with `memory.NewReader`, then validated.

## State And Persistence
No persistent state. Test state consists of in-memory eStargz section readers and metadata maps.

## Dependencies And Integration
Depends on `metadata/testutil`, the common `metadata.Option` type, and the local memory reader. It verifies that the default metadata backend satisfies both production and test-only interfaces.

## Risks And Test Signals
Passing this test signals correct metadata traversal, attributes, file reads, preread callbacks, telemetry calls, and clone ID stability for memory metadata. It does not cover persistent database-backed metadata behavior.
