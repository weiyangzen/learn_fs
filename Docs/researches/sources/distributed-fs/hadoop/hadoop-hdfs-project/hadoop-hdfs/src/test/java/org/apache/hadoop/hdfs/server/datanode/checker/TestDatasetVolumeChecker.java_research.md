# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/checker/TestDatasetVolumeChecker.java

Purpose: This parameterized unit test verifies `DatasetVolumeChecker` classification for every `VolumeCheckResult` plus thrown exceptions, both for single-volume async callbacks and full-dataset synchronous checks.

Important APIs/types/functions: `DatasetVolumeChecker`, `DatasetVolumeChecker.Callback`, `AsyncChecker`, `Checkable`, `FsVolumeSpi.check`, `FsDatasetSpi.FsVolumeReferences`, `FakeTimer`, `Futures.immediateFuture`, `VolumeCheckResult`, and disk-check configuration keys.

Control flow: `data()` supplies `HEALTHY`, `DEGRADED`, `FAILED`, and `null` as exception case. `testCheckOneVolume` builds one mocked volume, installs a `DummyChecker` that immediately invokes `check`, schedules `checkVolume`, waits for the callback, and verifies healthy versus failed sets. `testCheckAllVolumes` builds a mocked dataset with two volumes and asserts failed-volume set size. Bad config tests instantiate the checker with invalid timeout, min-gap, and tolerated-failures values.

State and persistence behavior: No disk state is persisted. State under test is checker counters, callback arguments, mocked volume references, and validation of configuration-derived thresholds.

Dependencies and integration points: It validates the bridge between `DatasetVolumeChecker` and pluggable `AsyncChecker`, plus FsDataset volume-reference acquisition.

Risks and test signals: Signals are callback counts, Mockito `check` invocations, failed-set sizes, and exact exception messages. Risk is mostly mock fidelity and parameterized repetition of config tests.
