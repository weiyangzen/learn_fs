# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestCreateSessionTimeout.java

Purpose: S3 Express integration test proving the S3A CreateSession call honors the configured request timeout instead of a hardcoded longer timeout.

Important APIs/types/functions: `ITestCreateSessionTimeout` extends `AbstractS3ACostTest`; `createConfiguration()` requires an S3 Express bucket, disables FS caching, removes bucket overrides, enables HTTP signer customization, sets `SlowSigner`, `REQUEST_TIMEOUT=10ms`, and `RETRY_LIMIT=1`. `SlowSigner` extends `CustomHttpSigner` and sleeps in sync/async signing. `setup()` temporarily lowers `AWSClientConfig` minimum durations.

Control flow: the test invokes `fs.getFileStatus(path("testShortTimeout"))`, expects `AWSApiCallTimeoutException`, measures elapsed time with `DurationInfo`, verifies it is below a five-second threshold, confirms the signer sleep was interrupted, and scans the nested stack trace for `createSession`.

State and persistence: no test directory cleanup or mkdir work is needed; the test avoids persistent data and only creates a new filesystem session path probe. Static `AtomicLong` and `AtomicBoolean` coordinate sleep duration and interruption observation.

Dependencies/integration: AWS SDK HTTP signer SPI, S3A custom signer plumbing, S3 Express session creation, S3A timeout wrapping, and bucket capability assumptions.

Risks: only meaningful on S3 Express; timing assertions are environment-sensitive; static interruption state could be affected by repeated runs if not reset externally.

Test signals: expected timeout exception, bounded call duration, interrupted signing sleep, and evidence that the failing path went through CreateSession.
