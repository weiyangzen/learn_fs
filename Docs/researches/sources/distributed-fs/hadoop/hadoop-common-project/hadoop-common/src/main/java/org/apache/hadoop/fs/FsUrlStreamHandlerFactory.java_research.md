# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsUrlStreamHandlerFactory.java

Purpose: `FsUrlStreamHandlerFactory` exposes Hadoop filesystem schemes as Java URL protocols while deliberately avoiding standard JVM protocols.

Important APIs: `UNEXPORTED_PROTOCOLS`, constructors, and `createURLStreamHandler`.

Control flow and state: the constructor copies the configuration, forces FileSystem initialization by resolving `file`, creates one handler, and seeds `http`/`https` as unsupported. `createURLStreamHandler` caches whether each protocol has a `FileSystem` implementation in a `ConcurrentHashMap`; known protocols return the shared handler and unknown protocols return null to delegate to the JVM.

Dependencies and integration: integrates Java `URLStreamHandlerFactory`, `FileSystem.getFileSystemClass`, and `FsUrlStreamHandler`.

Risks: protocol support is cached, so runtime config changes after first lookup are not reflected. Returning a shared handler means one configuration is used for all supported protocols. Exporting `http`/`https` would break JVM behavior, so the denylist must remain.

Test signals: known Hadoop schemes return a handler, unknown schemes return null, http/https stay unexported, FileSystem initialization failure becomes runtime exception, and concurrent protocol lookups are stable.
