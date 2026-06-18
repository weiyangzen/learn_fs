# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestMultiThreadedHflush.java

## Purpose
This file stress-tests concurrent `hflush` and write behavior on a single `FSDataOutputStream`, including races between repeated flushes and stream close. It also contains a CLI benchmark wrapper for manual throughput/latency measurements.

## Important APIs, Types, And Functions
`WriterThread` extends `SubjectInheritingThread` and repeatedly writes a shared random buffer then calls `hflush`. `testMultipleHflushersRepl1` and `testMultipleHflushersRepl3` call `doTestMultipleHflushers`. `testHflushWhileClosing` creates flusher threads that loop until `ClosedChannelException`. `doMultithreadedWrites` coordinates workers with `CountDownLatch` and captures failures in `AtomicReference`. `CLIBenchmark` exposes the workload through `ToolRunner`.

## Control Flow
The main workload opens a file, performs several empty and non-empty flushes, starts writer threads simultaneously, waits for completion, propagates any thread exception, and closes the stream. The close-race test starts ten flusher threads, writes bytes in the main thread, closes the stream while flushers are active, joins all flushers, and fails on any unexpected exception.

## State And Persistence
State is mostly client-side stream state: current packet buffer, DFSOutputStream close state, DataStreamer interactions, and concurrent error visibility through `AtomicReference`. The test does not restart the cluster or validate persisted bytes directly; successful close and absence of unexpected exceptions are the main durability-adjacent signals.

## Dependencies And Integration Points
It uses `MiniDFSCluster`, `FileSystem`, `FSDataOutputStream.hflush`, `SubjectInheritingThread`, `StopWatch`, `SampleQuantiles`, and Hadoop `Tool`/`Configured` for the benchmark path.

## Risks
The test intentionally maximizes races on one stream, so timing and thread scheduling can affect reproducibility. Shared `SampleQuantiles` is updated by multiple writer threads, relying on the metrics implementation. The close-race expects `ClosedChannelException`; changes in stream-close exception wrapping may break it even if behavior is acceptable.

## Test Signals
Passing signals are no deferred exceptions from writer threads, expected `ClosedChannelException` termination for flushers during close, successful stream close after concurrent writes, and printed latency quantiles for manual benchmark visibility.
