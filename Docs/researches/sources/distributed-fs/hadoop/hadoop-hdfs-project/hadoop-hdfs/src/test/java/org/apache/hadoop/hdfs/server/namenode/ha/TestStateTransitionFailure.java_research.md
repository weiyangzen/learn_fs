# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestStateTransitionFailure.java

Purpose: verifies that a NameNode shuts down when transition to active fails partway through service startup.

Important APIs and types: `MiniDFSCluster`, `MiniDFSNNTopology.simpleHATopology`, `CommonConfigurationKeys.FS_TRASH_INTERVAL_KEY`, `ExitUtil.ExitException`, and `GenericTestUtils.assertExceptionContains`.

Control flow: the test configures an illegal negative trash interval, starts a two-NN HA cluster with zero DNs and `checkExitOnShutdown(false)`, waits for startup, and attempts `cluster.transitionToActive(0)`. A successful transition fails the test. The expected path catches `ExitException` and asserts it contains the trash emptier startup error.

State and persistence behavior: no namespace persistence is central here. The relevant state is HA service transition state and daemon process shutdown behavior when active services cannot be fully initialized.

Dependencies and integration points: integrates HA state transition code with trash emptier initialization and Hadoop's exit trapping utility used in tests.

Risks and test signals: risk is a partially active NameNode remaining alive after initialization failure, which could serve inconsistent or incomplete active services. The explicit `ExitException` content check is the signal that failure is both detected and routed through shutdown.
