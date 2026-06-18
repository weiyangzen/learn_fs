<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReplicaInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReplicaInfo.java

## Purpose

`ReplicaInfo` is the abstract base for DataNode replica metadata. It extends HDFS `Block`, implements `Replica`, and adds storage location, file/stream, mutation, scanner, recovery, and intrusive hash-set link operations.

## Important APIs, Types, And Functions

- Volume access: `getVolume()`, package-private `setVolume()`, `getStorageUuid()`, `isOnTransientStorage()`, and `getFileIoProvider()`.
- Storage stream and URI operations for block data and metadata: `getBlockURI`, input/output streams, existence, length, delete, rename, copy, and metadata counterparts.
- Recovery and lifecycle hooks: `getOriginalReplica`, `getRecoveryID`, `setRecoveryID`, `bumpReplicaGS`, `breakHardLinksIfNeeded`, `createInfo`, `truncateBlock`, and `updateWithReplica`.
- Scanner integration: `compareWith(FsVolumeSpi.ScanInfo)`.
- Implements `LightWeightResizableGSet.LinkedElement` via `getNext`/`setNext`.

## Control Flow

Subclasses provide all storage-specific behavior. Common code delegates file I/O provider selection to the attached volume, falling back to a default no-hook provider when tests or checksum utilities operate without a volume. `toString()` calls the key abstract methods to render a detailed diagnostic summary.

## State And Persistence

The base stores block id/length/generation stamp through `Block`, an `FsVolumeSpi` reference, and a next pointer for hash-set membership. Persistent bytes and metadata live in subclass-specific local files or provided remote regions.

## Dependencies And Integration Points

It is the core type stored in DataNode volume maps and used by scanners, recovery, balancer pinning, block senders, dataset checks, and provided storage. It bridges protocol `ReplicaRecoveryInfo` with local storage implementations.

## Risks And Edge Cases

Some methods assume non-null volume; `getStorageUuid()` and `isOnTransientStorage()` will fail if called on volume-less test/checksum instances. `toString()` can invoke subclass methods that throw for incomplete or unsupported states. Subclasses must keep block fields and physical files consistent.

## Test Signals

Tests should cover subclass contracts, null-volume fallback for file I/O provider, hash-set link behavior, diagnostic rendering, generation-stamp bump and file rename coupling, scanner comparisons, and recovery-info creation for supported states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReplicaInfo.java -->
