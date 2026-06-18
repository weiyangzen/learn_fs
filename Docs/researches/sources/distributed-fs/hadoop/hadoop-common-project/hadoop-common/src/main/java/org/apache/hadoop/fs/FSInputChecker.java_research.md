## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSInputChecker.java

Purpose: `FSInputChecker` is an abstract `FSInputStream` that verifies checksums before returning data to users. Subclasses provide checksum-aware `readChunk` and chunk-boundary mapping through `getChunkPosition`.

Important APIs and types: constructors configure file identity, retry count, checksum verification, `Checksum`, chunk size, and checksum size. Key methods are `read`, `read(byte[], int, int)`, `readAndDiscard`, `seek`, `skip`, `available`, `getPos`, `set`, `readFully(InputStream, ...)`, and abstract `readChunk`/`getChunkPosition`. It uses `ChecksumException` and standard four-byte checksums.

Control flow, state, and persistence: local state tracks current chunk position, internal data buffer, checksum bytes, checksum int view, buffer position/count, verification flag, and retry count. Reads use buffered small reads or direct user-buffer chunk reads. `readChecksumChunk` invokes the subclass, verifies each chunk with `verifySums`, advances `chunkPos`, and on checksum error retries against a new source via `seekToNewSource`. `seek` can reposition within the current buffer, otherwise resets to a chunk boundary and discards bytes to the requested offset. No durable persistence exists.

Dependencies and integration: HDFS-like input streams subclass this to combine data and checksum streams. It depends on `FSInputStream`, `Checksum`, `ChecksumException`, logging, and `FSExceptionMessages`.

Risks and test signals: risks include checksum-size assumptions, retry off-by-one behavior, seeking past EOF semantics, synchronization bottlenecks, and reading/discarding corrupt intermediate bytes. Tests should cover aligned and unaligned reads, partial chunks, disabled checksums, checksum mismatch retry success/failure, negative seek, buffer-position seeking, skip beyond EOF, mark/reset behavior, and checksum byte order.
