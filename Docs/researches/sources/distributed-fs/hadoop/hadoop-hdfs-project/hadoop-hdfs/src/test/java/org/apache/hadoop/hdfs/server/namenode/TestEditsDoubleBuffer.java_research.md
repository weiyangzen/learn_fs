# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditsDoubleBuffer.java

## Purpose
`TestEditsDoubleBuffer` verifies the in-memory double-buffer used by edit-log output streams before flushing bytes to persistent storage. It checks buffer accounting, flush-state transitions, close behavior with unflushed data, and human-readable edit dumps on close failure.

## Important APIs, Types, And Functions
The file exercises `EditsDoubleBuffer`, `DataOutputBuffer`, `writeRaw`, `setReadyToFlush`, `flushTo`, `close`, and `countBufferedBytes`. For operation serialization it uses `FSEditLogOp.SetReplicationOp`, `DeleteOp`, `AllocateBlockIdOp`, `OpInstanceCache`, and a layout version from `NameNodeLayoutVersion.Feature.ROLLING_UPGRADE`.

## Control Flow
`testDoubleBuffer` writes raw bytes to the current buffer, swaps buffers, flushes to an output buffer, and repeats to confirm byte counts and `isFlushed` status. `shouldFailToCloseWhenUnflushed` writes one byte and expects close to throw an IOException mentioning unflushed data. `testDumpEdits` writes three typed edit operations, captures `EditsDoubleBuffer.LOG`, attempts to close without flushing, and verifies the logged output contains each operation's string form.

## State And Persistence Behavior
The buffer maintains a current write buffer and a ready-to-flush buffer. This test asserts that writing into the current buffer alone does not mark the buffer unflushed until `setReadyToFlush` swaps it, and that `flushTo` drains the ready buffer and resets byte counts. The dump test ensures unflushed edit operations are observable in logs for diagnostics before data is discarded by a failed close.

## Dependencies And Integration Points
`EditsDoubleBuffer` is a lower-level dependency of edit-log file streams. Its correctness affects batching, flushing, and diagnostics in `FSEditLog`. The test integrates with `GenericTestUtils.LogCapturer` rather than full filesystem storage.

## Risks And Test Signals
Risks include byte-accounting drift, incorrectly allowing close with unflushed edits, losing diagnostics for pending operations, and mistaken flush-state transitions. Test signals are exact buffer lengths, `isFlushed` booleans, expected close exception text, and logged serialized edit operations.
