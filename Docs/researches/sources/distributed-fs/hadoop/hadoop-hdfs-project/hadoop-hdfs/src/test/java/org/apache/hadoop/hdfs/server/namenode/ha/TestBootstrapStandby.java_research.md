# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestBootstrapStandby.java

## Purpose

`TestBootstrapStandby` validates `BootstrapStandby` against a three-NameNode HA topology with file-based shared edits, covering successful bootstraps, later checkpoints, rolling upgrade rollback images, missing shared edits, preformatted dirs, non-active source nodes, and bootstrap-specific transfer throttling.

## Important APIs, Types, and Functions

The fixture builds a custom `MiniDFSNNTopology`, keeps NN0 active, shuts down other NameNodes, and uses `BootstrapStandby.run`, `FSImageTestUtil`, `NameNodeAdapter`, `CheckpointSignature`, `NNStorage`, `NameNodeLayoutVersion`, `RollingUpgradeAction`, `DistributedFileSystem`, `LogCapturer`, Mockito spies, and `SubjectInheritingThread`.

## Control Flow

Tests delete standby name dirs, confirm startup fails before bootstrap, run bootstrap with `-nonInteractive` or `-force`, verify copied checkpoint txids, and restart standbys. Later-checkpoint tests roll logs and save namespace before bootstrapping. Rolling-upgrade tests spoof future layout versions, ensure invalid-version handling before upgrade, prepare rolling upgrade, copy both normal and rollback images, restart with rolling-upgrade args, and then verify failure modes. Missing-log tests delete a shared finalized edits segment and expect `ERR_CODE_LOGS_UNAVAILABLE`. Rate throttling compares global image-transfer rate with bootstrap-specific rate.

## State and Persistence Behavior

The tests mutate local NameNode storage dirs, shared edits directories, fsimage checkpoints, rollback images, `seen_txid`, rolling-upgrade state, and transfer-rate config. They directly delete directories and edit-log segments to create failure scenarios.

## Dependencies and Integration Points

It integrates HA bootstrap, HTTP image transfer, shared edits validation, checkpoint signatures, rolling upgrade, fsimage rollback handling, configuration of transfer throttles, and MiniDFSCluster restart semantics.

## Risks and Edge Cases

Bootstrapping from stale or incomplete shared edits can create unusable standbys. Rolling upgrades require version compatibility and rollback image transfer. Existing directories must be rejected unless forced. Throttling behavior must use the bootstrap-specific key to avoid global transfer settings breaking bootstrap.

## Test Signals

Signals include return code `0` for valid bootstrap, `ERR_CODE_INVALID_VERSION`, `ERR_CODE_LOGS_UNAVAILABLE`, and `ERR_CODE_ALREADY_FORMATTED` for specific failures, matching NN files after bootstrap, unchanged shared `seen_txid`, rollback checkpoints present during rolling upgrade, and expected timeout only when the bootstrap-specific rate is too low.
