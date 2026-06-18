# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/ProgressableProgressListener.java

Purpose: AWS SDK transfer listener that bridges S3 transfer progress into Hadoop `Progressable` callbacks and S3A write statistics.

Important APIs/types: implements `TransferListener`. Constructor captures `S3AStore`, object key, optional `Progressable`, and initializes `lastBytesTransferred`. Overrides `transferInitiated`, `transferComplete`, and `bytesTransferred`; adds `uploadCompleted(ObjectTransfer)` for final delta reconciliation.

Control flow: transfer initiation and completion each increment write operations. Every bytes-transferred event invokes optional progress callback, computes delta from cumulative transferred bytes, updates put-progress statistics, and stores the new cumulative value. `uploadCompleted` checks final transfer snapshot for bytes not reported through listener events and records a positive delta.

State and persistence behavior: mutable in-memory `lastBytesTransferred`; persistent effects are metrics/statistics updates in `S3AStore`, not file data changes.

Dependencies and integration points: integrates AWS SDK v2 transfer manager progress events with Hadoop MapReduce progress reporting and S3A instrumentation.

Risks: assumes progress snapshots are monotonically increasing; negative deltas would decrement statistics if callbacks arrive out of order. Race handling is explicitly delegated to `uploadCompleted`.

Test signals: tests should cover progress callback invocation, delta calculation across multiple events, operation counters, final positive delta handling, and no failure when progress callback is null.
