<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/net/unix/DomainSocket.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/net/unix/DomainSocket.c

## Purpose
`DomainSocket.c` implements Hadoop's Unix-domain socket JNI operations, including server/client socket creation, path security validation, socket options, array/direct-buffer I/O, and file-descriptor passing with `SCM_RIGHTS`.

## Important APIs, Types, and Functions
JNI exports include `anchorNative()`, `validateSocketPathSecurity0()`, `bind0()`, `socketpair0()`, `accept0()`, `connect0()`, `setAttribute0()`, `getAttribute0()`, `close0()`, `closeFileDescriptor0()`, `shutdown0()`, `sendFileDescriptors0()`, `receiveFileDescriptors0()`, `readArray0()`, `available0()`, `writeArray0()`, and `readByteBufferDirect0()`. Key helpers include `errnoToSocketExceptionName()`, `newSocketException()`, `flexBufInit()`, `setup()`, `javaMillisToTimeVal()`, `write_fully()`, and `cmsghdr_with_fds`.

## Control Flow
`setup()` creates an AF_UNIX stream socket, copies and validates the path length, sets SIGPIPE suppression where available, and either connects or unlinks/binds/chmods/listens. Path security validation walks parent path components and rejects world-writable, unsafe group-writable, or unsafe owner-writable directories after optional skipped components. I/O methods copy Java arrays into stack-or-heap flexible buffers or use direct-buffer addresses, retry interrupted syscalls, translate EOF to Java `-1`, and map errno to socket exceptions. Descriptor passing builds a control message carrying up to 16 fds and sends at least one byte; receive creates Java `FileDescriptor` objects and closes received fds on error.

## State and Persistence
No global socket state is stored beyond file descriptor helper initialization. OS socket descriptors persist in Java as integers or `FileDescriptor` objects. Flexible buffers are per-call stack/heap allocations.

## Dependencies and Integration Points
It depends on Unix sockets, `poll`-style socket options, `ioctl(FIONREAD)`, Hadoop exception helpers, and `file_descriptor`. It backs Java `DomainSocket` used by HDFS short-circuit and local IPC paths.

## Risks and Edge Cases
`sendFileDescriptors0()` sets `jfdsLen = 0` before formatting the error for too many fds, hiding the original length. `receiveFileDescriptors0()` derives received fd count from `aux.hdr.cmsg_len` without validating control-message headers or truncation flags. Path security uses string tokenization and `stat`, so symlink races are possible. `setup()` closes fd only when `fd > 0`, leaking fd 0 on rare paths.

## Test Signals
Tests should cover bind/connect/accept/socketpair, path length and security rejection, buffer and timeout options, EOF behavior, SIGPIPE-safe writes, descriptor passing count limits and cleanup, direct-buffer reads, and concurrent close/shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/net/unix/DomainSocket.c -->
