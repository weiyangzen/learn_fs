# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestRollingUpgradeDowngrade.java

Purpose: verifies the obsolete rolling-upgrade downgrade path is rejected, both for active HA rolling-upgrade state and for a newer/future fsimage layout version.

Important APIs and types: `MiniQJMHACluster`, `MiniDFSCluster`, `DistributedFileSystem`, `RollingUpgradeAction.PREPARE`, `RollingUpgradeInfo`, `NNStorage`, `NameNodeLayoutVersion`, Mockito `spy` and `doReturn`, `SafeModeAction`, and `Assertions.assertThrows`.

Control flow: `testDowngrade` wraps the whole HA scenario in an expected `IllegalArgumentException`. It starts HA QJM, prepares rolling upgrade, creates namespace changes, queries for rollback image preparation, then attempts `restartNameNode(..., "-rollingUpgrade", "downgrade")`. `testRejectNewFsImage` saves namespace, spies `NNStorage` to report a future service layout version, writes storage metadata, and attempts downgrade restart, also expecting `IllegalArgumentException`.

State and persistence behavior: manipulates rolling-upgrade state, rollback images, fsimage storage metadata, service layout version, and NameNode restart options. The tests intentionally assert rejection rather than successful namespace mutation.

Dependencies and integration points: integrates rolling-upgrade startup option parsing, HA/QJM, storage layout version checks, safe-mode namespace saving, and Mockito storage spying.

Risks and edge cases: because `assertThrows` wraps broad setup and cleanup, an unexpected earlier `IllegalArgumentException` would also satisfy the test unless stack/context is inspected. The storage spy writes a future layout version to disk, so cleanup through cluster shutdown is important.

Test signals: `IllegalArgumentException` is thrown when downgrade is requested in both obsolete-downgrade scenarios.
