# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/terasort/ITestTerasortOnS3A.java

## Purpose
Scale test running the full Teragen, Terasort, and Teravalidate pipeline on S3A with S3A committers. It compares directory staging with magic committer modes, including magic in-memory commit tracking.

## Important APIs, Types, and Functions
The class extends `AbstractYarnClusterITest`, is tagged `@ScaleTest`, and is parameterized over `DirectoryStagingCommitter.NAME`, `MagicS3GuardCommitter.NAME` with tracking disabled, and magic with tracking enabled. It uses Hadoop examples `TeraGen`, `TeraSort`, `TeraValidate`, `ToolRunner`, `DurationInfo`, success marker validation, and committer configuration patching.

## Control Flow and Behavior
`setup()` requires scale tests and multipart uploads, then creates unique S3A paths for the parameter. `applyCustomConfigOptions()` sets small partition/sample parameters and magic tracking mode. Ordered tests delete previous data, run teragen, require its success before terasort, require terasort success before teravalidate, validate `_SUCCESS` at each stage, record durations in a static map, write a CSV report, reset duration state, and finally delete the test directory.

## State, Persistence, and Dependencies
State spans S3A input/output/validate directories, MR/YARN job state, success marker JSON files, static duration tracking, and a local CSV report under the test report directory. Dependencies include scale-test enablement, mini YARN cluster, S3A multipart support, Hadoop terasort tools, and S3A committer config injection.

## Integration Points, Risks, and Test Signals
This is an expensive but realistic signal for production-style MR workloads on S3A. It validates that committers handle chained MR jobs, success-file loading between stages, and final cleanup. Risks include long runtime, scale-test gating, static state across parameterized runs, and YARN/S3 operational flakiness.
