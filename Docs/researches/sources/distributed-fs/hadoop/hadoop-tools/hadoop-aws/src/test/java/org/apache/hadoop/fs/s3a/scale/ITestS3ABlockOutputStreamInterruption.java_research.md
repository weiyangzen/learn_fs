<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ABlockOutputStreamInterruption.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ABlockOutputStreamInterruption.java


## Purpose
JUnit 5 parameterized S3A scale test that validates close(), abort(), and retry behavior when block output stream uploads are interrupted across disk, array, and bytebuffer upload buffers.


## Important APIs, Types, and Functions
ITestS3ABlockOutputStreamInterruption, params(), createScaleConfiguration(), setup()/teardown(), interruptMultipartUpload(), createFile(), expectCloseInterrupted(), and the nested InterruptingProgressListener. It configures FAST_UPLOAD_BUFFER, MULTIPART_SIZE, FAST_UPLOAD_ACTIVE_BLOCKS, retry limits, directory-upload purge, and SdkFaultInjector auditing.


## Control Flow
Each test creates an S3A output stream with a progress listener, writes enough data to drive either multipart upload, magic commit upload, or simple PUT, then triggers thread interruption, abort(), or injected failures from progress callbacks. The assertions check listener event counts, InterruptedIOException propagation, multipart abort statistics, bytes transferred bounds, and idempotent second close/abort behavior.


## State and Persistence Behavior
Persistent state is S3 object and multipart-upload state: partial uploads must be aborted and completed objects must not appear after abort. Test instance state is limited to buffer type and active-block count, while SdkFaultInjector uses static evaluator/action counters reset before and after each test.


## Dependencies and Integration Points
Depends on S3AFileSystem create builders, FSDataOutputStream Abortable support, ProgressListenerEvent callbacks, magic commit path naming, IOStatistics counters, and AWS SDK execution interception through SdkFaultInjector.


## Risks and Test Signals
Racy by design because progress callbacks fire from upload/control paths; strict assertions around failed part counts are deliberately relaxed. Cleanup relies on fault injector reset and directory purge to avoid leaked multipart uploads. Failures signal regressions in interruption translation, multipart abort cleanup, or stream idempotency.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ABlockOutputStreamInterruption.java -->
