# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/DFSClientAdapter.java

`DFSClientAdapter` is a package-scoped testing adapter that exposes internal HDFS client state without reflection. It lets tests access or replace `DistributedFileSystem.dfs`, stop the lease renewer, call NameNode block-location helpers, inspect a `DFSClient`'s NameNode proxy, fetch previous-block state, and read a `DFSOutputStream` file ID.

All methods are static pass-throughs. `stopLeaseRenewer` is the only method with notable control flow: it calls `interruptAndJoin` and wraps `InterruptedException` as `IOException`. `setDFSClient` directly mutates the filesystem's client reference; the other methods expose package-private fields or internal methods.

The class persists nothing, but it can strongly affect live client state by replacing clients or stopping lease renewal. It depends on `DistributedFileSystem`, `DFSClient`, `DFSOutputStream`, `ClientProtocol`, `LocatedBlocks`, and `ExtendedBlock`.

The main risk is that tests can create impossible production states: broken lease ownership, mismatched clients, stopped lease renewal, or stale protocol proxies. Its test signal is indirect: it enables assertions and setup for lease recovery, block lookup, and stream identity scenarios that normal public APIs hide.
