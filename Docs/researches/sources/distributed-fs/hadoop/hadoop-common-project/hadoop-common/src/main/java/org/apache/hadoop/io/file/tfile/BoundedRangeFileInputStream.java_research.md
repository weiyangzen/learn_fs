# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/BoundedRangeFileInputStream.java

Purpose: exposes a fixed byte range of a shared `FSDataInputStream` as an independent `InputStream`.

Important APIs/types/functions: constructor with stream/offset/length; `available()`, `read()` overloads, `skip()`, `mark()`, `reset()`, `markSupported()`, and `close()`.

Control flow: reads synchronize on the underlying FS stream, seek to this wrapper's logical position, read at most the remaining range, then advance the wrapper position. EOF clamps `end` to current position. `skip` only advances local position. `mark/reset` store and restore local position.

State and persistence: local `pos`, `end`, and `mark`; no durable state. Close nulls the underlying stream reference and invalidates range state.

Dependencies and integration: used by `BCFile.Reader.RBlockState` to constrain decompression to a block's compressed region.

Risks: after close, calling methods that dereference `in` can throw `NullPointerException`; close does not close the shared underlying stream. `available()` depends on underlying stream availability and clamps to range. Tests should cover independent wrappers over one FS stream, range EOF, mark/reset, invalid offsets, skip beyond end, and close behavior.
