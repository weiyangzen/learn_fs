# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/checker/TestDatasetVolumeCheckerFailures.java

Purpose: This companion test covers `DatasetVolumeChecker` failure cases not covered by the parameterized suite: hung checks, closed volumes, and minimum synchronous-check gap enforcement.

Important APIs/types/functions: `DatasetVolumeChecker.checkAllVolumes`, `FakeTimer`, `DFS_DATANODE_DISK_CHECK_TIMEOUT_KEY`, `DFS_DATANODE_DISK_CHECK_MIN_GAP_KEY`, `ClosedChannelException`, `FsVolumeSpi.obtainReference`, and checker counters `getNumSyncDatasetChecks`/`getNumSkippedChecks`.

Control flow: Setup configures a one-second minimum disk-check gap. `testTimeout` creates a volume whose `check` sleeps forever and expects it to be reported failed with a one-second timeout. `testCheckingClosedVolume` makes `obtainReference` throw `ClosedChannelException`, expecting no failed volume and no check invocation. The min-gap test checks once, immediately checks again and expects skip, then advances `FakeTimer` and expects another real check.

State and persistence behavior: All volumes are mocks. The persistent checker state is its last-check timestamp and counters.

Dependencies and integration points: It exercises volume reference acquisition, async timeout handling, and rate limiting of full-dataset disk checks.

Risks and test signals: Signals are failed-set sizes, check invocation count, and counter values. Risk comes from sleeping forever in a worker and relying on timeout cancellation/shutdown behavior.
