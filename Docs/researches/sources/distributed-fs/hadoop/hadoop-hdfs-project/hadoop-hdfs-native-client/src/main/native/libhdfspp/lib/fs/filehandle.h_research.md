<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/filehandle.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/filehandle.h

## Purpose
Declares `FileHandleImpl`, the concrete libhdfspp file handle for HDFS reads.

## Important APIs, Types, And Functions
The class implements `FileHandle` methods for asynchronous positioned read, synchronous positioned read, sequential read, seek, partial async pread with exclusion rules, cancellation, file event callback replacement, event handler access, read statistics, and protected factories for block readers and DataNode connections.

## Control Flow
Implementation in `filehandle.cc` uses located block metadata to select DataNodes and delegates protocol work to `BlockReaderImpl`.

## State And Persistence
Members capture cluster/path identity, shared async runtime, client name, immutable file/block metadata, bad-node tracker, current offset, cancellation state, live readers, event handlers, and atomic bytes-read count.

## Dependencies And Integration Points
Included by C bindings and filesystem code. It depends on reader group/block reader types, `IoService`, async stream/cancellation/events, bad DataNode tracking, generated protocol classes, and x-platform types.

## Risks
The documented threading model is restrictive; callers must avoid concurrent sequential `Read`, `Seek`, and callback replacement. Protected factories are test seams and must preserve reader registration/cancellation semantics when overridden.

## Test Signals
Tests should instantiate with mock file info and DataNode connections, override factories for deterministic block reads, and validate cancellation/statistics/seek behavior exposed through the public `FileHandle` API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/filehandle.h -->
