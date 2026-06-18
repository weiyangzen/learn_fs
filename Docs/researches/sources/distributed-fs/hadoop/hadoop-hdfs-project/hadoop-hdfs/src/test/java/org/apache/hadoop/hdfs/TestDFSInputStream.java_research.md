# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSInputStream.java

Purpose: This class tests DFSInputStream read-side behavior: skip semantics, short-circuit local reads, selecting a new source DataNode, open-info length accounting, NULL checksum behavior across DataNode restart, cached replica preference, and invalid block-token retry during block-reader creation.

Important APIs/types/functions: `DFSInputStream`, `DistributedFileSystem`, `DFSClient`, `DomainSocket`, `TemporarySocketDirectory`, `DfsClientConf`, `LocatedBlock`, `DatanodeInfoWithStorage`, `DFSClientFaultInjector`, and `InvalidBlockTokenException`.

Control flow: `testSkipInner` creates a deterministic 4 MiB file and repeatedly skips random distances, validating the next byte. Remote and local-block-reader tests delegate to it, with local reads enabling short-circuit sockets and temporarily disabling TCP reads for testing. Other tests open a file and check `seekToNewSource`, configure last-block-length retries to zero, restart a DataNode while writing with NULL checksum, mock located-block cached/non-cached locations, and inject one invalid token exception before a successful read.

State and persistence behavior: Tests write actual HDFS files, flush under-construction data, restart a DataNode, inspect live DataNode descriptors, and temporarily mutate `DFSInputStream.tcpReadsDisabledForTesting` and `DFSClientFaultInjector`. The invalid-token test keeps an under-construction block open while reading from offset 1024.

Dependencies and integration points: It integrates short-circuit domain sockets, DataNode block loading after restart, NameNode block-location metadata, DFS client read-priority configuration, and token-refresh retry logic in block-reader construction.

Risks and test signals: Signals include byte-accurate reads after skip, different current datanode after source switch, expected file length/last-block state, live DataNode count after restart, selected DataNode identity, and successful read after injected token failure. Risks include domain-socket platform assumptions, sleeps for block loading, and global fault-injector cleanup.
