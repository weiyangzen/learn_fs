<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/VolumeScannerCBInjector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/VolumeScannerCBInjector.java

## Purpose

`VolumeScannerCBInjector` is a test-only callback injector for `VolumeScanner` and `BlockScanner` lifecycle points. Production methods are no-ops.

## Important APIs, Types, And Functions

- Static singleton access through `get()` and replacement through `set(VolumeScannerCBInjector)`.
- `preSavingBlockIteratorTask(VolumeScanner)` runs before scanner shutdown saves iterators.
- `shutdownCallBack(VolumeScanner)` runs during scanner shutdown request.
- `terminationCallBack(VolumeScanner)` runs after scanner work exits.

## Control Flow

`VolumeScanner` calls these hooks at deterministic lifecycle points. Tests replace the singleton with a subclass that blocks, records, or injects behavior; production uses the default no-op instance.

## State And Persistence

The only state is the static singleton reference. No filesystem or scanner state is persisted by this class.

## Dependencies And Integration Points

It is annotated private and visible for testing, and is directly integrated into `VolumeScanner.work()` and `VolumeScanner.shutdown()`.

## Risks And Edge Cases

Because the singleton is static, tests must reset it to avoid cross-test leakage. Callback implementations can block scanner shutdown or alter timing-sensitive tests if misused.

## Test Signals

Tests should verify callbacks fire in the expected order and reset the injector after use. Scanner tests can use the hooks to coordinate cursor-save and termination races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/VolumeScannerCBInjector.java -->
