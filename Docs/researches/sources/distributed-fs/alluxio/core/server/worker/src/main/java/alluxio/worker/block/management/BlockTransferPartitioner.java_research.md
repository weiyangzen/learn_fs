# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/BlockTransferPartitioner.java

Purpose: Greedily partitions block transfers for concurrent execution, preferring groups that share exact source or destination locations.

Important APIs: `partitionTransfers`; private `findTransferBucketKey`; private `balancePartitions`; enum `TransferPartitionKey`.

Control flow: It picks source or destination as a bucket key based on how many transfers have exact locations and how distinct those locations are. If no exact locations exist, it returns one partition. If too many buckets exist, it greedily balances them by transfer count.

State and persistence: Stateless beyond local collections. No persistence.

Dependencies and integration: Used only by `BlockTransferExecutor`.

Risks and test signals: Balancing ignores block sizes and does not prevent all read/write conflicts. Tests should cover source-key, destination-key, no-key, tie by distinct count, partition-limit balancing, and stable handling of any-dir locations.
