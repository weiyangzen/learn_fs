# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/unix/TestDomainSocket.java

Purpose: JUnit 5 integration coverage for Hadoop's native `DomainSocket` AF_UNIX wrapper. It validates socket lifecycle, path expansion, EOF, async close, socket attributes, client/server byte exchange, socketpair behavior, file descriptor passing, socket-path security, and shutdown semantics.

Important APIs/types/functions: `DomainSocket.bindAndListen`, `connect`, `socketpair`, `accept`, `close(true)`, `shutdown`, `getInputStream`, `getOutputStream`, `getChannel`, `sendFileDescriptors`, `recvFileInputStreams`, `validateSocketPathSecurity0`, `TemporarySocketDirectory`, `DomainChannel`, `SubjectInheritingThread`, and helper strategies `OutputStreamWriteStrategy`, `InputStreamReadStrategy`, `DirectByteBufferReadStrategy`, `ArrayBackedByteBufferReadStrategy`.

Control flow: setup creates a temporary socket directory and disables bind path validation; each test assumes native domain sockets loaded. The tests either bind/listen/connect, use socketpairs, or run two threads coordinating through `ArrayBlockingQueue`/`Future`. Descriptor passing creates real temporary files, sends their FDs with a byte payload, and validates received `FileInputStream`s. Path-security coverage mutates directory modes and checks expected exceptions.

State and persistence: uses temporary socket files, temporary data files, file descriptors, process umask/permission state, and global `DomainSocket` validation toggles. Resources are closed explicitly, though `PassedFile.finalize` is a fallback.

Dependencies/integration points: native Hadoop domain socket library, Unix filesystem permissions, `Shell.execCommand`, Hadoop `IOUtils`, Guava `Files`, JUnit assumptions/timeouts, and `SubjectInheritingThread`.

Risks: platform-sensitive and skipped when native loading fails; timing sleeps can be flaky; descriptor and socket leaks would affect later tests; permissions checks assume Unix semantics; direct and array-backed channel reads exercise buffer-position edge cases.

Test signals: success means AF_UNIX I/O, async close exceptions, receive timeout behavior, socketpair bidirectional messaging, FD passing, insecure path rejection, and half-shutdown EOF all work.
