# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/HdfsPartialListing.java

## Purpose
`HdfsPartialListing` represents one parent-indexed result from the batched multi-directory listing API. It can hold either a successful list of `HdfsFileStatus` objects or a `RemoteException`.

## APIs and Behavior
Two public constructors create success or failure entries. The private constructor enforces exactly one of `partialListing` or `exception` using XOR. Accessors expose `parentIdx`, `partialListing`, and `exception`; `toString()` includes all fields.

## State, Dependencies, and Integration
It depends on Hadoop `Preconditions`, Commons `ToStringBuilder`, and IPC `RemoteException`. It integrates with batched directory listing responses that need to correlate each partial result to the input parent path.

## Risks and Test Signals
The successful listing list is not defensively copied. Tests should cover constructor XOR validation, exception propagation per parent, parent index ordering, and toString output for mixed success/failure batches.
