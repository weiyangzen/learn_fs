# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/CountingProgressListener.java

Purpose: progress listener for S3A scale tests that counts upload lifecycle events, transferred bytes, and failures while logging bandwidth.

Important APIs/types/functions: implements Hadoop `Progressable` and S3A `ProgressListener`; stores an `EnumMap<ProgressListenerEvent, AtomicLong>`, total bytes, and a `NanoTimer`. Public methods include `progressChanged`, `get`, `getBytesTransferred`, `getUploadEvents`, `getStartedEvents`, `getFailures`, `verifyNoFailures`, and `assertEventCount`.

Control flow: `progress()` is a no-op for generic Hadoop progress. `progressChanged()` increments the event counter, logs started events, accumulates bytes on completed PUT/part events and computes effective bandwidth, logs failures, and ignores other events.

State and persistence: thread-safe atomic counters and byte totals live in memory for one test listener instance; no external persistence.

Dependencies/integration: S3A progress event enum, Hadoop contract `NanoTimer`, AssertJ assertions, and scale-test `_1MB` constant.

Risks: logger category points at `AbstractSTestS3AHugeFiles`; bandwidth division assumes nonzero elapsed seconds; only selected failure events contribute to `getFailures`.

Test signals: scale tests use no-failure assertions, upload-event counts, byte totals, and optional exact event count assertions.
