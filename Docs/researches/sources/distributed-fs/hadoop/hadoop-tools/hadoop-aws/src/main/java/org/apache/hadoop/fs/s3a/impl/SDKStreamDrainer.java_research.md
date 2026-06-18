# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/SDKStreamDrainer.java

## Purpose
`SDKStreamDrainer` encapsulates the decision to drain and close or abort an AWS SDK response stream when an S3A input stream is closed. It protects connection reuse while avoiding pathological reads of large remaining payloads when abort is requested or close fails.

## Important APIs and Types
It is generic over `TStream extends InputStream & Abortable` and implements `CallableRaisingIOE<Boolean>`. Constructor captures URI, stream, abort flag, remaining bytes, stream statistics, and reason. `apply()` records duration and returns whether abort occurred. `applyRaisingException()` is testing-only. Getters expose execution outcome, thrown exception, drained count, and abort state.

## Control Flow
`apply()` wraps `drainOrAbortHttpStream()` in stream-statistics duration tracking and stores any thrown exception instead of rethrowing. `drainOrAbortHttpStream()` enforces single execution with `AtomicBoolean`. If not forced to abort, it drains up to `remaining` bytes using `DRAIN_BUFFER_SIZE`, closes the stream, records non-abort close stats, and returns false. If draining/closing fails or abort was requested, it calls `sdkStream.abort()`, records abort close stats, and returns true.

## State and Persistence
Mutable per-call state includes `remaining`, `drained`, `executed`, `thrown`, and `aborted`. It does not persist data, but it releases or aborts HTTP connections and updates input stream statistics.

## Dependencies and Integration Points
It depends on AWS SDK `Abortable`, S3A input stream statistics, `InternalConstants.DRAIN_BUFFER_SIZE`, and IOStatistics duration helpers. It is used by S3A input stream close/unbuffer code paths.

## Risks and Edge Cases
The operation is one-shot; repeated invocation throws. If `InputStream.read()` returns zero repeatedly, the loop exits early and close may still cause SDK abort internally. Aborting after close failure preserves the last exception in `thrown` but `apply()` swallows it. The remaining byte count is an `int`, so callers must not pass values above integer range.

## Test Signals
Tests should cover full drain and close, forced abort, close failure escalation to abort, abort failure recording, duplicate invocation rejection, short reads, zero/negative remaining assumptions, duration/statistic updates, and `applyRaisingException()` propagation.
