# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestWriteToReplica.java

## Purpose

`TestWriteToReplica` validates `FsDatasetImpl` and `FsDatasetSpi` behavior when writing to, appending to, recovering, and recreating replicas in different states. It also verifies replica-map persistence across quick DataNode restart in a federated cluster and RBW recovery behavior for inconsistent on-disk length metadata.

## Important APIs and types

- Replica states are represented by test indexes for `FINALIZED`, `TEMPORARY`, `RBW`, `RWR`, `RUR`, and `NON_EXISTENT`.
- `FsDatasetTestUtils` creates finalized, temporary, RBW, waiting-to-be-recovered, and under-recovery replicas.
- APIs under test include `append`, `recoverAppend`, `recoverClose`, `recoverRbw`, `createRbw`, `createTemporary`, and `getReplicaInfo`.
- Exceptions distinguish invalid states: `ReplicaNotFoundException`, `ReplicaAlreadyExistsException`, and `DiskOutOfSpaceException`.
- `ReplicaMap.addAll`, `replicas`, `get`, and `remove` are used to compare pre- and post-restart maps.

## Control flow

Each primary test starts a MiniDFSCluster, builds six blocks, creates replicas in all relevant states, and calls a helper. Append tests first force disk-out-of-space by manipulating volume accounting, then verify successful append only for finalized replicas and recovery append for finalized and RBW replicas. Temporary, RWR, RUR, and non-existent cases must throw state-appropriate exceptions.

Close recovery allows finalized and RBW replicas but rejects temporary, RWR, RUR, and non-existent replicas. RBW tests reject recovery of non-RBW states, reject `createRbw` when any existing state already owns the block, recover existing RBW successfully, and allow `createRbw` for a non-existent block. Temporary creation rejects existing states, allows a non-existent block, rejects duplicate creation with the same generation stamp, and allows recreation when the generation stamp is newer.

The restart test creates a federated two-name-node cluster, collects block pool IDs and volumes, creates multiple replica states per pool and volume, snapshots `volumeMap`, restarts the DataNode, and verifies finalized replicas remain finalized while RBW/RWR/RUR convert to RWR and temporary replicas are not persisted. The inconsistent RBW test lowers in-memory bytes-on-disk and verifies recovery can reconcile it when data exists, then truncates the file and expects recovery failure.

## State and persistence behavior

The tests create actual replica files in randomized MiniDFSCluster directories. Restart behavior persists finalized and recovery-relevant replicas while intentionally dropping temporary pipeline replicas. Generation stamps are mutated in test block objects after successful transitions. The inconsistent RBW test edits the block file length through `RandomAccessFile`.

## Dependencies and integration points

This file integrates low-level DataNode dataset state machines, replica file layout, block pools, federation, generation stamps, disk-space checks, DataNode restart recovery, and on-disk metadata reconciliation.

## Risks and edge cases

- The tests depend on exact exception message prefixes, which can make harmless wording changes noisy.
- The setup creates one representative block per state, not all combinations of length and generation-stamp mismatch.
- Direct volume accounting manipulation for disk-out-of-space is implementation-specific.
- Restart assertions encode current conversion semantics for RBW/RWR/RUR to RWR.

## Test signals

Strong signals are the state matrix for append/close/RBW/tmp creation, disk-out-of-space validation, duplicate and newer-generation temporary behavior, federation-aware replica-map persistence, intentional non-persistence of temporary replicas, and RBW recovery distinction between inconsistent metadata and truly truncated data.
