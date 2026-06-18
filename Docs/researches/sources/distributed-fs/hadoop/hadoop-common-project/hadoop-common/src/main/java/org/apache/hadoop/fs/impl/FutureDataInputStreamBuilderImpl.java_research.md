# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FutureDataInputStreamBuilderImpl.java

## Purpose
Base builder for asynchronous FSDataInputStream open operations returning CompletableFuture<FSDataInputStream>.

## Important APIs, Types, and Functions
Constructors for FileContext+Path, FileSystem+Path, FileSystem+PathHandle; bufferSize(); builder(); getThisBuilder(); withFileStatus(); protected getFS/getBufferSize/getStatus.

## Control Flow
FileSystem constructors initialize buffer size from IO_FILE_BUFFER_SIZE_KEY. FileContext constructor has no FileSystem and uses default buffer size. withFileStatus stores optional status for implementations to skip metadata probes.

## State and Persistence Behavior
Stores FileSystem reference, buffer size, optional FileStatus, plus AbstractFSBuilderImpl option/path state. No persistence.

## Dependencies and Integration Points
Base for filesystem-specific openFile builders and FutureDataInputStreamBuilder API.

## Risks and Test Signals
Risks are null fileSystem for FileContext path if subclasses call getFS, stale FileStatus, and buffer size validation absent. Tests should cover constructor variants and fluent behavior.
