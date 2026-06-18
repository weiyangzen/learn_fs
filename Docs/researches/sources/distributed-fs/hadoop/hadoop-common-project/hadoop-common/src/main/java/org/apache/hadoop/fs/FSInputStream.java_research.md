## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSInputStream.java

Purpose: `FSInputStream` is the public evolving base class for Hadoop input streams that support seeking and positioned reads in addition to normal `InputStream` reads.

Important APIs and types: subclasses must implement `seek`, `getPos`, and `seekToNewSource`. The class implements default positioned `read(position, buffer, offset, length)`, `readFully` overloads, argument validation, and a `toString` that includes IO statistics when the subclass implements `IOStatisticsSource`.

Control flow, state, and persistence: positioned read validates arguments, synchronizes on the stream, saves the old position, seeks to the requested position, reads, downgrades EOFException to `-1`, and always seeks back to the old position. `readFully` loops until the requested length is filled or throws `EOFException`. The base class stores no mutable stream state itself.

Dependencies and integration: this is the superclass behind `FSDataInputStream` wrappers and filesystem-specific input streams. It uses `Seekable`, `PositionedReadable`, `FSExceptionMessages`, preconditions, logging, and IO statistics formatting.

Risks and test signals: default positioned reads are correct but potentially inefficient and synchronized. Implementations with expensive seek or non-idempotent read behavior may need overrides. Tests should cover negative positions, null buffers, insufficient destination space, zero-length reads, EOF downgrading, restoration of original position after failures, and `readFully` EOF behavior.
