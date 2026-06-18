# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/s3guard/AbstractS3GuardToolTestBase.java

Purpose: shared integration-test base for S3Guard tool CLI tests, including common command execution helpers and baseline bucket/tool behavior checks.

Important APIs/types/functions: extends `AbstractS3ATestBase`; tracks `toolsToClose`; exposes `toClose`, `expectResult`, `expectSuccess`, `run`, `runToFailure`, and `assertExitCode`. Tests exercise `S3GuardTool.BucketInfo`, `S3GuardTool.Uploads`, unsupported command list, marker policy options, missing bucket, missing arguments, and magic commit capability flag.

Control flow: setup delegates to superclass; teardown closes registered tools after superclass teardown. Tests instantiate command classes with current configuration, execute through helper methods, and assert command output or `ExitUtil.ExitException` status.

State and persistence: uses live S3A filesystem URI and command instances; no durable data beyond possible tool probes. A nonexistent bucket URI constant is used for failure tests.

Dependencies/integration: S3GuardTool command classes, marker tool option names, launcher exit codes, S3A unknown-store exception behavior, and `S3GuardToolTestHelper`.

Risks: S3Guard is deprecated/unsupported in newer flows, so tests encode compatibility behavior rather than active metadata-store behavior; missing bucket behavior depends on store probing.

Test signals: command exit codes, output containing S3A client info, unknown marker policy rejection, unsupported command rejection, and expected exceptions for missing buckets/args.
