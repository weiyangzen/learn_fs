# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestBufferData.java

## Purpose
`TestBufferData` validates lifecycle, state transitions, action futures, read-only protection, and checksum integrity for prefetch buffer blocks.

## Important APIs, Types, And Functions
It constructs `BufferData(blockNumber, ByteBuffer)` and tests `getState()`, `setPrefetch()`, `setCaching()`, `getActionFuture()`, `updateState()`, `setReady()`, `getChecksum()`, `getBuffer()`, `setDone()`, `throwIfStateIncorrect()`, and static `getChecksum()`. The nested `StateChanger` functional interface drives invalid transition checks.

## Control Flow
Argument tests reject negative block numbers, null buffers/futures/states, and state mismatches. Valid state tests move from `BLANK` to `PREFETCHING`, `CACHING`, and `READY`, checking future replacement. Invalid tests attempt `setPrefetch()` or `setCaching()` from all disallowed states. `testSetReady()` records checksum, makes the buffer read-only, rejects repeated ready, mutates the backing array, and expects `setDone()` to detect checksum drift. `testChecksum()` verifies checksum ignores unused buffer capacity beyond limit.

## State And Persistence
State is in-memory buffer data, state enum, future reference, and checksum. No persistence.

## Dependencies And Integration Points
It depends on `CompletableFuture`, `ByteBuffer`, `ReadOnlyBufferException`, `ExceptionAsserts`, and the prefetch state machine.

## Risks
The backing array can still be mutated after a read-only view is exposed; checksum verification catches this late corruption. Incorrect state transitions can race prefetch/caching logic.

## Test Signals
Signals are exact state values, future identity changes, read-only buffer exceptions, checksum nonzero/stability, and expected illegal-state messages.
