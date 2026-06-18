# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/s3guard/TestS3GuardCLI.java

Purpose: small unit tests for the top-level `S3GuardTool.run` CLI dispatch and argument validation.

Important APIs/types/functions: `TestS3GuardCLI` extends JUnit `Assertions`; helper `run` uses `new Configuration(false)` and `S3GuardTool.run`; `runToFailure` intercepts `ExitUtil.ExitException`. Static imports cover `BucketInfo.NAME`, `INVALID_ARGUMENT`, `E_USAGE`, and other tool constants.

Control flow: tests call the CLI dispatcher with no bucket-info args, wrong filesystem scheme, no command, and unknown command, expecting the correct exit status for each case.

State and persistence: no filesystem state or persistent data is used.

Dependencies/integration: S3GuardTool command parser, Hadoop `ExitUtil`, LambdaTestUtils, and configuration defaults.

Risks: validates only dispatch/usage paths, not command execution; status-code changes in CLI policy will break exact assertions.

Test signals: intercepted exit exceptions with `INVALID_ARGUMENT` or `E_USAGE`.
