# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/BlockReaderUtil.java

## Purpose
`BlockReaderUtil` centralizes simple helper behavior shared by local, remote, and external `BlockReader` implementations.

## Important APIs, types, and functions
`readAll(BlockReader, byte[], int, int)` repeatedly calls `BlockReader.read` until it has filled the requested length, sees EOF, or gets a non-positive read result. It returns EOF or the number of bytes actually read. `readFully(BlockReader, byte[], int, int)` loops until the requested length is read and throws `IOException` on premature EOF.

## Control flow
Both helpers use the `BlockReader` byte-array read path. `readAll` preserves partial-read semantics by returning already-read bytes if EOF follows a partial read. `readFully` treats any negative return before satisfying `len` as a hard error.

## State and persistence behavior
The class is stateless and package-private. It does not persist data or modify reader state beyond consuming bytes through the provided reader.

## Dependencies and integration points
It depends only on the `BlockReader` interface and `IOException`. It is called by `BlockReaderLocalLegacy`, `BlockReaderRemote`, and `ExternalBlockReader` to keep `readAll`/`readFully` semantics consistent.

## Risks and test signals
The main test signals are EOF behavior with zero bytes read versus after a partial read, propagation of reader exceptions, and ensuring no infinite loop if an implementation returns `0` while progress is expected. Callers rely on underlying readers to follow Hadoop read semantics.
