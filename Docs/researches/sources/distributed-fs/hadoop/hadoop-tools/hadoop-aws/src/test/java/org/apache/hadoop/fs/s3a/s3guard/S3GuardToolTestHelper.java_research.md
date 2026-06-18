# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/s3guard/S3GuardToolTestHelper.java

Purpose: utility class for S3Guard CLI tests, centralizing command invocation, output capture, varargs conversion, and expected exit-code handling.

Important APIs/types/functions: static `exec(S3GuardTool,Object...)`, `expectExecResult`, low-level `exec(expectedResult,errorText,cmd,buf,args)`, `varargsToString`, `runS3GuardCommand`, and `runS3GuardCommandToFailure`.

Control flow: object arguments are converted to strings, commands are run with a `PrintStream` backed by `ByteArrayOutputStream`, and output is returned or logged on failure. Exceptions implementing `ExitCodeProvider` are treated as success when their code matches the expected result; otherwise they are rethrown. Return-code mismatches become JUnit `assertEquals` failures including command output.

State and persistence: captures command stdout in memory only; no persistent state.

Dependencies/integration: `S3GuardTool.run`, Hadoop `ExitCodeProvider`, `ExitUtil.ExitException`, LambdaTestUtils, and SLF4J logging.

Risks: if a command opens a cached filesystem, `S3GuardTool.run` may close it afterward as warned; helper assumes output fits memory; expected-result handling differs for returned codes versus thrown exit-code providers.

Test signals: helper itself has no tests here, but callers rely on captured output, exact exit-code matching, and logged buffers for diagnostics.
