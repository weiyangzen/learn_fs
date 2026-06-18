# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/HasFileDescriptor.java

Purpose: `HasFileDescriptor` marks streams or wrappers that can expose an underlying Java `FileDescriptor`.

Important APIs: `getFileDescriptor`.

Control flow and state: interface-only contract; implementations decide whether the descriptor is live, duplicate, or tied to stream lifetime.

Dependencies and integration: used by local/native IO paths and consumers needing descriptor-level operations.

Risks: exposing descriptors can bypass stream abstractions and interacts with close semantics. Implementations must throw `IOException` when unavailable rather than returning invalid descriptors.

Test signals: descriptor availability before/after close, unsupported stream behavior, native/local stream integration, and caller handling of `IOException`.
