# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/Abortable.java

## Purpose
`Abortable` is a public unstable filesystem interface for output streams that can abandon an active write so that closing the stream does not make partial data visible. It is especially relevant for object-store output streams and is passed through `FSDataOutputStream`.

## Important APIs and types
The interface declares `AbortableResult abort()`. Nested `AbortableResult` exposes `alreadyClosed()` and `anyCleanupException()`.

## Control flow
Implementations define abort semantics. The contract states that after abort, the active write must not become visible. If unsupported, `abort()` may throw `UnsupportedOperationException`. The result allows callers to distinguish first abort from an already closed/aborted stream and inspect cleanup exceptions that do not change abort semantics.

## State and persistence
The interface defines no state. Implementations typically manage upload/session state, temporary objects, multipart uploads, or local buffers. The persistence contract is negative: aborted data must not become visible.

## Dependencies and integration points
It depends only on `IOException` and Hadoop interface annotations. `FSDataOutputStream` can expose/pass through abort support from wrapped streams. Object store connectors implement this to cancel pending writes.

## Risks
The semantic requirement is strong: implementations must ensure close after abort cannot commit data, even under races or cleanup failures. The result's cleanup exception must not be confused with abort failure if data visibility was prevented. Callers need to handle unsupported streams.

## Test signals
Tests should cover abort before close, close after abort, repeated abort idempotence via `alreadyClosed()`, cleanup exception reporting, unsupported implementations, and object-store integration proving aborted data is not listed or readable.
