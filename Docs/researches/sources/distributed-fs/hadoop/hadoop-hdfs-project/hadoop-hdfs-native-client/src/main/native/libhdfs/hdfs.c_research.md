# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/hdfs.c

## Purpose
`hdfs.c` is the primary C implementation of libhdfs. It adapts the public `hdfs/hdfs.h` API to Hadoop Java `FileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FutureDataInputStreamBuilder`, zero-copy reads, file metadata, and exception/errno behavior through JNI.

## Important types and state
`hdfsFS` values are Java `FileSystem` global references cast to C handles. `struct hdfsFile_internal` wraps a Java stream global reference, an `hdfsStreamType` (`input` or `output`), and capability flags. Direct read and direct pread support are represented by `HDFS_FILE_SUPPORTS_DIRECT_READ` and `HDFS_FILE_SUPPORTS_DIRECT_PREAD`, discovered through `FSDataInputStream#hasCapability`.

Builder state is held in `struct hdfsBuilder` and linked `hdfsBuilderConfOpt` nodes until `hdfsBuilderConnect` consumes and frees the builder. Stream builder state is held in `struct hdfsStreamBuilder`. Async open uses `hdfsOpenFileBuilder` and `hdfsOpenFileFuture`, each owning Java global references. Zero-copy state is held in `hadoopRzOptions` and `hadoopRzBuffer`; options cache an EnumSet and optional ByteBufferPool, while buffers own or point to Java ByteBuffer memory until released.

## Connection and configuration control flow
`hdfsNewBuilder` creates a builder; setters record NameNode, port, user, Kerberos ticket cache, force-new flag, and configuration key/value pairs. `hdfsBuilderConnect` creates a Java `Configuration`, applies options, chooses local/default/URI connection mode, handles Kerberos cache path and user string, calls either `FileSystem#get`, `newInstance`, `getLocal`, or `newInstanceLocal`, promotes the result to a global reference, frees local references and the builder, and returns the `hdfsFS` handle. `calcEffectiveURI` prepends `hdfs://` and appends the explicit port when appropriate, rejecting duplicate URI ports.

`hdfsConfGetStr`, `hdfsConfGetInt`, and `hdfsConfStrFree` expose configuration reads through a temporary Java `Configuration`.

## File open, async open, and lifecycle
`hdfsOpenFile` wraps the stream-builder API. `hdfsOpenFileImpl` validates access mode, constructs a `Path`, fetches configuration defaults, dispatches to `FileSystem#open`, `#append`, or `#create`, stores the stream as a global reference, tags it as input or output, and sets direct-read capability flags for input streams. `hdfsCloseFile` calls the appropriate Java `close`, deletes the global ref, and frees the C wrapper. `hdfsDisconnect` closes the Java `FileSystem` and deletes the global ref.

Async open wraps Java `FutureDataInputStreamBuilder`: allocation calls `FileSystem#openFile`, `hdfsOpenFileBuilderMust` and `Opt` update builder options, build returns a Java `Future`, get methods call `Future#get` with or without `TimeUnit`, cancel maps Java boolean false to `-1`, and free methods delete global references.

## I/O control flow
`hdfsRead` and `hdfsPread` validate stream type and length. If capability flags are set, they use `NewDirectByteBuffer` and Java ByteBuffer read methods to avoid heap array copies. Otherwise they allocate Java byte arrays, call the Java read overloads, copy the returned region to the caller buffer, return zero at EOF, and return `-1` with `EINTR` for zero-byte reads. `hdfsPreadFully` has direct and byte-array variants around `readFully`.

`hdfsWrite` validates output stream type, copies C bytes into a Java byte array, calls `FSDataOutputStream#write`, and returns the full requested length because the Java stream does not report partial writes. `hdfsSeek`, `hdfsTell`, `hdfsFlush`, `hdfsHFlush`, `hdfsHSync`, `hdfsAvailable`, and `hdfsUnbufferFile` delegate to the corresponding Java stream methods.

## Metadata and filesystem operations
Path operations construct Java `Path` objects and delegate to Java `FileSystem`: `hdfsExists`, `hdfsCopy`, `hdfsMove`, `hdfsDelete`, `hdfsRename` with `Options.Rename.NONE`, working directory get/set, directory create, replication, chown, chmod, and utime. Capacity and used space come from `FsStatus`. Default block size has both filesystem and path-aware variants.

`hdfsGetHosts` calls `getFileStatus` and `getFileBlockLocations`, then builds a NULL-terminated `char***` host matrix freed by `hdfsFreeHosts`. `hdfsGetPathInfo` and `hdfsListDirectory` convert Java `FileStatus` values to `hdfsFileInfo`. To preserve binary compatibility, extended encrypted-file state is stored in padded space after the owner string and read by `hdfsFileIsEncrypted`.

## Zero-copy behavior
`hadoopRzOptionsAlloc`, `hadoopRzOptionsSetSkipChecksum`, `hadoopRzOptionsSetByteBufferPool`, and `hadoopRzOptionsFree` manage zero-copy options and cached `ReadOption` EnumSet state. `hadoopReadZero` calls `FSDataInputStream#read(ByteBufferPool, int, EnumSet)`, translates `UnsupportedOperationException` to `EPROTONOSUPPORT`, stores returned ByteBuffer as a global ref, and extracts either a direct pointer or a copied heap-backed buffer. `hadoopRzBufferFree` calls `releaseBuffer`, deletes the global ByteBuffer ref, frees copied memory if needed, and clears the buffer.

## Dependencies and integration points
This file depends heavily on `jni_helper` for JVM attachment, method invocation, class/object construction, C/Java string conversion, enum lookup, and TLS exception strings; `exception` for mapping Java failures to errno; `jclasses` for cached Java classes; and Hadoop Java classes from `org.apache.hadoop.fs`, `org.apache.hadoop.hdfs`, `java.net.URI`, `java.util.EnumSet`, `java.nio.ByteBuffer`, and `java.util.concurrent`.

## Risks
JNI reference ownership is the main risk: every successful handle stores a global ref and must delete it exactly once. Several APIs return heap memory (`hdfsFileInfo`, host matrices, config strings, read-stat structs, hedged metrics) with paired free functions. Error mapping depends on Java exception class names; new Java exception classes can become `EINTERNAL`. Direct ByteBuffer paths require stream capability detection and JVM support. The extended encrypted flag stored behind `mOwner` is ABI-preserving but fragile if callers mutate owner strings or assume allocation size. Some functions set `errno` to positive Java-mapped errors while a few internal paths use negative local values in diagnostics, so callers should rely on public return contracts.

## Test signals
`test_libhdfs_ops.c` covers basic I/O, direct/fallback read and pread, async open, metadata, permissions, append, local FS, and user connections. `test_libhdfs_threaded.c` covers concurrency, exception TLS, statistics, hedged metrics, permissions, and large listings. `test_libhdfs_zerocopy.c` covers zero-copy options and buffer semantics. `test_libhdfs_mini_stress.c` stresses concurrent shared-FS reads and injected libhdfspp errors. `vecsum.c` provides performance and zero-copy benchmark coverage.
