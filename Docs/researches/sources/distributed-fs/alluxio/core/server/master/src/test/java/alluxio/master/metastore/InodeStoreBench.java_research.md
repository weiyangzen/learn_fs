# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/InodeStoreBench.java

Purpose: standalone microbenchmark for inode store write throughput and checkpoint/restore performance.

Important APIs/types/functions: uses `InodeStore`, `RocksInodeStore`, `HeapInodeStore`, `MutableInodeDirectory`, `CreateDirectoryContext`, `CheckpointInputStream`, and `PropertyKey.MASTER_METASTORE_DIR`. Helpers `runBenchmarks`, `writeBenchmark`, `checkpointBenchmark`, `doForMs`, and `writeInode` drive the workload.

Control flow: `main` enables console logging, benchmarks a Rocks inode store from the configured metastore directory, then benchmarks a heap inode store. Write benchmark warms up for two seconds, then runs five three-second rounds with four threads sharing a `CyclicBarrier`, counting directory inode writes. Checkpoint benchmark clears the store, writes one million inodes, writes a checkpoint to a temp file, restores it, and prints elapsed milliseconds.

State and persistence behavior: Rocks state is under the configured metastore directory; heap state is in-memory. Checkpoint state is written to a temp file and restored into the same static store.

Dependencies and integration points: not a JUnit test; intended for manual performance checks of metastore implementations and checkpoint serialization paths.

Risks: static `NEXT_INODE_ID` is not reset between benchmark phases, so IDs monotonically grow across stores. Restore into the same store after checkpoint write may not model a cold empty restore. No assertions or automated pass/fail thresholds exist.

Test signals: provides manual throughput/checkpoint timing signal only; not suitable as deterministic correctness coverage.
