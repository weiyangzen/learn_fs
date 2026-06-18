# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/HdfsDataOutputStream.java

Purpose: `HdfsDataOutputStream` is the public evolving HDFS implementation of `FSDataOutputStream`. It exposes HDFS-specific write controls, especially current pipeline replication and sync flags, while supporting encrypted output streams.

Important APIs/types/functions: constructors accept `DFSOutputStream` or `CryptoOutputStream`, with optional start position. Crypto constructors verify the wrapped stream is a `DFSOutputStream`. `getCurrentBlockReplication()` returns the current valid replica count from the underlying DFS output stream. `hsync(EnumSet<SyncFlag>)` exposes detailed HDFS sync semantics. `SyncFlag` values are `UPDATE_LENGTH` and `END_BLOCK`.

Control flow: methods call `getWrappedStream()`, unwrap crypto if present, and delegate to `DFSOutputStream`. `hsync` flushes the crypto stream before unwrapping so encrypted buffered bytes reach the DFS stream before sync. `UPDATE_LENGTH` asks the NameNode to update block length; `END_BLOCK` syncs and rolls to a new block.

State and persistence behavior: this class stores no additional state. Persistent effects happen through the delegated `DFSOutputStream`: DataNode flushes, NameNode length updates, block finalization, and new block allocation.

Dependencies and integration points: integrates with `FSDataOutputStream`, `CryptoOutputStream`, `DFSOutputStream`, `FileSystem.Statistics`, and HDFS write/sync paths.

Risks: incorrect wrapping would cause `ClassCastException`, guarded by constructor checks for crypto but not for inherited `getWrappedStream()` state mutation. `hsync` with `END_BLOCK` changes block layout and should be tested with appends and encrypted streams. Tests should cover crypto flush-before-sync, current replication after pipeline failures, start-position constructors, and both sync flags.
