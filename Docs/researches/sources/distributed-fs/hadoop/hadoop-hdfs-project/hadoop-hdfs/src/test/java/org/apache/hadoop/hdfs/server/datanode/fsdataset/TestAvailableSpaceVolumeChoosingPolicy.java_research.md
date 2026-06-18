# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/TestAvailableSpaceVolumeChoosingPolicy.java

Purpose: This unit test validates `AvailableSpaceVolumeChoosingPolicy` behavior for balanced fallback, preference toward high- or low-free-space volumes, insufficient selected-volume space, dynamic available-space changes, and randomized selection ratios.

Important APIs/types/functions: `AvailableSpaceVolumeChoosingPolicy`, `VolumeChoosingPolicy.chooseVolume`, `FsVolumeSpi.getAvailable`, configuration keys for balanced-space threshold and preference fraction, `ReflectionUtils`, `GenericTestUtils.assertValueNear`, and shared `TestRoundRobinVolumeChoosingPolicy` helpers.

Control flow: Tests configure policies with a one-megabyte threshold and varying preference fractions, build mocked volumes with specified available bytes, and assert exact selected-volume sequences. Randomized tests use a seeded `Random`, ten thousand iterations, and expected high/low-space selection ratios based on preference fraction.

State and persistence behavior: There is no disk state; mocked `getAvailable` values model changing capacity. The policy maintains round-robin cursors and random choices internally across calls.

Dependencies and integration points: It checks the policy used by DataNode block placement over FsDataset volumes and reuses round-robin tests for balanced cases and exception message coverage.

Risks and test signals: Signals are exact volume identity choices and randomized count tolerance. Risks include probabilistic flakiness, though seed and allowed error reduce it, and mock sequences that may diverge from real disk changes.
