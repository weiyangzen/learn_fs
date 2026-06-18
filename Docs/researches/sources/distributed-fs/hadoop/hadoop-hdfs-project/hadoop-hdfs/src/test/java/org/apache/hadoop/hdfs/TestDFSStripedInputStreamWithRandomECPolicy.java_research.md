<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedInputStreamWithRandomECPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedInputStreamWithRandomECPolicy.java

## Purpose
This subclass reruns the `TestDFSStripedInputStream` suite with a random non-default erasure coding policy, broadening read coverage beyond the default policy geometry.

## Important APIs, Types, and Functions
- Extends `TestDFSStripedInputStream`.
- Constructor selects `StripedFileTestUtil.getRandomNonDefaultECPolicy()` and logs it.
- Overrides `getEcPolicy` to return the selected policy so inherited setup uses different data/parity/cell-size parameters.

## Control Flow
There are no local test methods. JUnit inherits the parent class tests, and the overridden policy changes all parent setup calculations and expected-byte paths. The parent has a guard in `testBlockReader` to skip range expectations when the active policy is not the default `RS-6-3-1024k`.

## State and Persistence Behavior
State is a single instance-level `ErasureCodingPolicy` chosen at construction and then used for all inherited tests in that instance. All cluster, file, and buffer state is managed by the parent class.

## Dependencies and Integration Points
This integrates the parent striped input-stream suite with the broader EC policy catalog exposed by `StripedFileTestUtil`, validating that parent logic is policy-parametric.

## Risks
Random policy selection can make failures less reproducible unless logs are retained. Some inherited assertions may be implicitly tuned to default geometry; the parent skip in `testBlockReader` handles one known default-specific case.

## Test Signals
The signal is inherited read-suite success under a non-default EC policy, demonstrating that `DFSStripedInputStream` behavior is not coupled to one policy shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedInputStreamWithRandomECPolicy.java -->
