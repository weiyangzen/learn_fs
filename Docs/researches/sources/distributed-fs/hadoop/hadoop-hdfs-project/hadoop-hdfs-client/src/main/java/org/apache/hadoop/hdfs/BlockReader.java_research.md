# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/BlockReader.java

Purpose: private interface for reading a single HDFS block from a single DataNode.

Important APIs and functions: extends `ByteBufferReadable` and `Closeable`; defines byte-array `read`, `skip`, `available`, `close`, `readFully`, `readAll`, `isShortCircuit`, `getClientMmap`, `getDataChecksum`, and `getNetworkDistance`.

Control flow contract: implementations must return `-1` at EOF even for zero-byte reads. Comments acknowledge a checksum caveat: implementations may modify the user buffer before detecting checksum failure because data is read before checksum verification.

State and persistence: interface only. Implementations own sockets, local file descriptors, checksum state, mmap handles, and DataNode distance metadata.

Dependencies and integration: used by `DFSInputStream` read paths, short-circuit local reads, mmap support, read options, and checksum validation.

Risks and test signals: the buffer-before-checksum behavior is a correctness contract clients need to understand. Implementations must keep `readFully`/`readAll` semantics distinct to avoid EOF and partial-read bugs.
