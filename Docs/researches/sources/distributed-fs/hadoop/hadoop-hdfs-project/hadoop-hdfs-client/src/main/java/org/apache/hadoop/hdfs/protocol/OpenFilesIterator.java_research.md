# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/OpenFilesIterator.java

## Purpose
`OpenFilesIterator` adapts batched open-file listing into a retryable remote iterator. The listing is explicitly not a consistent snapshot across batches.

## APIs and Control Flow
`OpenFilesType` defines filter modes `ALL_OPEN_FILES` and `BLOCKING_DECOMMISSION`, each with a short mode and reverse lookup. The iterator starts at `HdfsConstants.GRANDFATHER_INODE_ID`, stores filter type set and path, and calls `namenode.listOpenFiles(prevId, types, path)` inside a tracing scope. `elementToPrevKey()` returns the entry inode ID.

## State, Dependencies, and Integration
State is inherited cursor plus immutable filter references. It integrates with DFSAdmin, NameNode lease/open-file tracking, decommission workflows, and tracing.

## Risks and Test Signals
The path field is mutable only internally but not final. `OpenFilesType.valueOf(short)` returns null for unknown modes. Tests should cover filter mode conversion, default path `/`, cursor advancement, non-atomic listing changes across batches, tracing, and permissions for superuser-only listing.
