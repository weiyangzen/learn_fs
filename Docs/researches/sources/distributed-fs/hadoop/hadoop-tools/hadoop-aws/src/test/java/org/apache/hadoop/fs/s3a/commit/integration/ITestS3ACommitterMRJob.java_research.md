# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/integration/ITestS3ACommitterMRJob.java

## Purpose
YARN-backed MapReduce integration test that runs a real MR job against S3A using the directory, partitioned, and magic committers. It validates end-to-end committer binding, task output generation, success marker content, output visibility, and committer-specific cleanup.

## Important APIs, Types, and Functions
The class extends `AbstractYarnClusterITest` and is parameterized by `CommitterTestBinding` implementations: `DirectoryCommitterTestBinding`, `PartitionCommitterTestBinding`, and `MagicCommitterTestBinding`. It uses `LoggingTextOutputFormat`, `TextInputFormat`, `FileOutputFormat`, `Job`, `JobConf`, `SuccessData`, and MR/YARN cluster helpers. `MapClass` emits deterministic records per input file. Binding hooks include `validate()`, `test_100()`, `applyCustomConfigOptions()`, `validateResult()`, and `test_500()`.

## Control Flow and Behavior
`setup()` requires multipart uploads and binds the current cluster/filesystem to the selected committer binding. `test_000()` validates the binding, `test_100()` runs binding-specific preflight checks, `test_200_execute()` creates local text inputs, configures a no-reducer MR job, assigns a committer UUID, submits to the mini YARN cluster, waits for success, validates the `_SUCCESS` JSON, compares visible output files with expected `part-m-*` names, and checks that classic `_temporary` output is absent. `test_500()` delegates postflight checks. Magic validation logs and inspects any leftover magic directory rather than failing on it due to known speculative/partitioned task behavior.

## State, Persistence, and Dependencies
State spans local temp input files, YARN/MR job metadata, S3A output directories, success marker JSON, committer UUIDs, and optional local mock-results serialization. Directory binding validates private HDFS staging temp path construction under the current user. Dependencies include real S3A multipart capability, a mini YARN cluster, AWS region propagation to task environments, and Hadoop MR classpath/logging behavior.

## Integration Points, Risks, and Test Signals
This is one of the strongest end-to-end signals for S3A committer correctness in distributed execution. Risks include YARN process isolation, missing AWS region in child containers, filesystem cache leakage, log4j/classpath fragility, and S3 eventual/listing behavior. Passing tests show that each committer can run a real MR job, publish only final output, and write success metadata listing committed object keys.
