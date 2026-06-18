# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/unix/DomainSocket.java

Purpose: Java wrapper around native UNIX domain socket operations, including bind/listen, accept, connect, socketpair, socket attributes, shutdown/close, stream I/O, readable channel I/O, and file descriptor passing.

Important APIs/types/functions: static native loader and `getLoadingFailureReason`, `disableBindPathValidation`, `getEffectivePath`, `bindAndListen`, `socketpair`, `connect`, `accept`, `setAttribute`, `getAttribute`, `close(boolean)`, `shutdown`, `sendFileDescriptors`, `recvFileInputStreams`, nested `DomainInputStream`, `DomainOutputStream`, and `DomainChannel`.

Control flow: static initialization verifies non-Windows native support. Public operations acquire `CloseableReferenceCount` references before using `fd` and unreference in finally blocks. `close(false)` marks closed, calls shutdown to interrupt blocking operations, waits for references to drain, then closes the fd. `close(true)` skips the drain wait after shutdown. Descriptor receive wraps native descriptors in `FileInputStream`s and cleans partial resources on failure.

State and persistence: per-socket immutable `fd` and `path`, refcount/closed state, and stream/channel wrapper instances. No persistence beyond OS socket files created by native bind.

Dependencies and integration: depends on libhadoop native methods, `NativeCodeLoader`, `CloseableReferenceCount`, and `DomainSocketWatcher`. Used by HDFS short-circuit local reads and peer transport.

Risks: native availability and path-security validation are deployment-sensitive. Reference count bugs can leak or prematurely close descriptors. `DomainChannel` only supports direct or array-backed buffers. `close(true)` can be necessary for server accept but changes lifecycle guarantees.

Test signals: `TestDomainSocket` covers socketpair, bind/connect, streams, attributes, descriptor passing, path validation, and close behavior, usually gated by native availability.
