# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/UploadContentProviders.java

## Purpose
`UploadContentProviders` supplies retry-safe AWS SDK `ContentStreamProvider` implementations for S3A uploads from files, byte buffers, and byte arrays. It avoids SDK defaults to control stream recreation, offsets, and resource cleanup.

## Important APIs and Types
Static factories create `BaseContentProvider` instances for file slices, byte buffers, and byte arrays, optionally guarded by an `isOpen` predicate. `BaseContentProvider<T>` tracks size, stream creation count, current stream, start time, and close behavior. Private subclasses implement file-with-offset, byte-buffer, and byte-array stream creation.

## Control Flow
`BaseContentProvider.newStream()` closes any current stream, checks the optional open predicate, increments creation count, logs on first recreation, and delegates to subclass `createNewStream()`. File providers open a `FileInputStream`, seek to offset, and wrap it in `BufferedInputStream`. Byte-buffer providers reset buffer limit/position and wrap it in `ByteBufferInputStream`. Byte-array providers create `ByteArrayInputStream` with offset and size.

## State and Persistence
Providers maintain current stream references and creation counts. They do not copy byte buffer or byte array contents, so external data remains shared. They read local files or in-memory buffers during upload retries; no object-store persistence happens in this class.

## Dependencies and Integration Points
It depends on AWS SDK `ContentStreamProvider`, Hadoop `ByteBufferInputStream`, `IOUtils.cleanupWithLogger`, and functional IO helpers. It is used by S3A upload code to provide replayable request bodies.

## Risks and Edge Cases
Byte buffers and arrays are not copied; mutation during upload corrupts data. `ByteBufferContentProvider.createNewStream()` mutates the source buffer position/limit, which callers must not reuse concurrently. `isOpen` predicate failures prevent retry after stream close. File provider IO failures are wrapped as `UncheckedIOException`. Size is long in base but byte-buffer/array streams require integer size.

## Test Signals
Tests should cover stream recreation counts, closing previous streams, file offset reads, byte buffer position/limit reset, byte-array offset bounds, negative offset/size rejection, open-predicate failure, mutation caveats, and retry behavior.
