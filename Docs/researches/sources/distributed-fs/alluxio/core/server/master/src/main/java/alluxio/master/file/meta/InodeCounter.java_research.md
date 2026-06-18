# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeCounter.java

Purpose: `LongAdder`-based inode counter that supports master checkpointing.

Important APIs and types: extends `LongAdder` and implements `Checkpointed`. `getCheckpointName` returns `CheckpointName.INODE_COUNTER`; `writeToCheckpoint` writes the current sum as a long; `restoreFromCheckpoint` resets then adds the checkpointed long.

Control flow: checkpointing serializes a single count. Restore rebuilds the counter from the checkpoint stream.

State and persistence behavior: in-memory adder with checkpoint persistence. The counter is not journaled per increment here; checkpointing captures aggregate state.

Dependencies and integration points: depends on Alluxio checkpoint stream APIs and `LongAdder`. Used by file master metadata components tracking inode counts.

Risks: `LongAdder.sum()` is weakly consistent under concurrent updates, so checkpoint callers should coordinate if exact counts are required. Restore assumes the input is a long checkpoint.

Test signals: tests should cover increment/checkpoint/restore, reset behavior, empty/default count, and checkpoint name.
