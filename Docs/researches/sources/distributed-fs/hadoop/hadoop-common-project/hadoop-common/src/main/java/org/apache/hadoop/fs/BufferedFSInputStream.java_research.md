## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BufferedFSInputStream.java

Purpose: wraps an `FSInputStream` in a `BufferedInputStream` while preserving Hadoop seek, positioned read, file descriptor, stream capability, vectored read, and IO statistics interfaces.

Important APIs and types: implements `Seekable`, `PositionedReadable`, `HasFileDescriptor`, `IOStatisticsSource`, and `StreamCapabilities`. Delegates positioned reads and vectored reads to the underlying `FSInputStream`/`PositionedReadable`.

Control flow: `getPos()` subtracts unread buffered bytes from the wrapped stream position. `seek()` rejects closed or negative positions, repositions within the current buffer when possible, otherwise invalidates the buffer and seeks the underlying stream. `skip()` is implemented as `seek(getPos()+n)`. Capability and stats methods probe/delegate to the inner stream.

State and persistence behavior: state is inherited buffering fields (`buf`, `pos`, `count`, `in`) plus underlying stream state. No persistence.

Dependencies and integration points: commonly used by filesystem open paths to add buffering while maintaining Hadoop stream contracts and vector I/O.

Risks: vectored read methods cast `in` to `PositionedReadable`, so construction with a non-positioned `FSInputStream` would fail at runtime for those methods. `skip(n)` returns `n` after seek and may report skipped bytes even if the underlying seek past EOF later behaves differently. Buffer-aware seek logic depends on accurate underlying `getPos()`.

Test signals: verify seek within buffer vs outside buffer, negative seek, closed stream errors, `getPos()` after buffered reads, positioned/vectored delegation, file descriptor passthrough, capabilities, and IO statistics retrieval.
