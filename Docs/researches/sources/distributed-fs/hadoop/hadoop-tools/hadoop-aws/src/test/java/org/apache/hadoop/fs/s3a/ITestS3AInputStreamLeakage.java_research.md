# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AInputStreamLeakage.java

Purpose: Verifies S3A input stream leak detection through finalization/GC logging and `STREAM_LEAKS` statistics.

Important APIs/types/functions: `FSDataInputStream`, `ObjectInputStream`, `S3AInputStream`, `StreamStatisticNames.STREAM_LEAKS`, `GenericTestUtils.LogCapturer`, `WeakReference`, `System.gc()`, `System.runFinalization()`, and `IOStatistics`.

Control flow: setup assumes the filesystem advertises `STREAM_LEAKS`. The test creates a file, opens a stream without try-with-resources, reads one byte, captures a weak reference to the wrapped stream, records leak counter, captures root logs, nulls the strong reference, forces GC/finalization, waits briefly, then asserts log output includes the leak message, path, thread, and test stack. It also asserts the leak counter increased, exactly by one for the classic stream.

State and persistence: creates one S3 object; intentionally relies on GC/finalizer behavior and root logger capture. Cleanup closes the stream only if it was not nulled.

Dependencies and integration points: S3A stream finalizer/leak-detection implementation, IOStatistics counters, logging content, and JVM GC/finalization behavior.

Risks: GC/finalizer timing is inherently flaky; log-message text is brittle; prefetch streams may increment leak counters more than once due to nested streams.

Test signals: catches removal or weakening of leak logging/statistics for unclosed input streams.
