# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestConnectionTimeouts.java

## Purpose
`ITestConnectionTimeouts` verifies S3A timeout behavior for connection-pool acquisition and request operations. It deliberately constructs brittle filesystems with tiny timeouts, then confirms pool exhaustion and delayed SDK calls produce expected failures while uploads honor longer upload-specific timeouts.

## Important APIs, Types, and Functions
- Extends `AbstractS3ATestBase`.
- `createConfiguration()` removes timeout/purge bucket overrides, sets `PART_UPLOAD_TIMEOUT`, and enables `DIRECTORY_OPERATIONS_PURGE_UPLOADS` for cleanup.
- `timingOutConfiguration()` disables prefetching, forces classic input streams, sets `MAXIMUM_CONNECTIONS=1`, disables retries, enables create performance, and sets 10 ms acquisition/establish timeouts.
- `testGeneratePoolTimeouts()` opens many `openFile()` streams with a known `FileStatus` until a `ConnectTimeoutException` is raised.
- `testObjectUploadTimeouts()` uses `SdkFaultInjector` to delay PUT, GET, and optional part-upload requests to distinguish upload timeout from general request timeout.

## Control Flow
The pool test writes a file with the stable base FS, opens a separate one-connection FS, repeatedly builds whole-file open streams, reads one byte to force GET requests, and expects connection acquisition failure. All streams are cleaned up in `finally`.

The upload test configures long `PART_UPLOAD_TIMEOUT` and shorter request/acquisition timeouts, installs an SDK fault action that sleeps under the upload timeout, then verifies normal PUT succeeds and takes longer than the short timeout. It then switches injection to GET and expects read failure. If magic commit is enabled, it also validates part-upload timeout behavior on a magic path.

## State and Persistence Behavior
Tests create method-path objects in S3. Static state in `AWSClientConfig` and `SdkFaultInjector` is reset around test execution. Open streams and temporary FS instances are explicitly closed.

## Dependencies and Integration Points
The file integrates S3A configuration constants, classic input streams, `FutureDataInputStreamBuilder`, `AWSClientConfig`, `SdkFaultInjector`, magic committer paths, and Hadoop contract utilities.

## Risks and Edge Cases
Timing tests are sensitive to parallel test runs and stream implementation, hence prefetch is disabled. Low-level read timeout exceptions vary, so the read failure assertion accepts generic `Exception`. Magic multipart coverage is conditional on magic commit support.

## Test Signals
Passing confirms connection-pool timeout translation, upload-specific timeout propagation to PUT/part upload, and shorter timeout enforcement on reads.
