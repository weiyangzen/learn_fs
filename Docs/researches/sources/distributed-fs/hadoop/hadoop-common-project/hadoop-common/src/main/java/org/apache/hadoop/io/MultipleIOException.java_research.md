# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/MultipleIOException.java

Purpose: `MultipleIOException` packages several `IOException` instances into one `IOException` so callers can report all cleanup or multi-resource failures without losing every error after the first.

Important APIs and types: the private constructor stores a final `List<IOException>` and builds a summary message. `getExceptions()` exposes the underlying list. `createIOException(List<IOException>)` returns `null` for no failures, the single exception for one failure, or a `MultipleIOException` for multiple failures. Nested `Builder` lazily accumulates throwables, wrapping non-IO throwables in `IOException`, and exposes `build()` and `isEmpty()`.

Control flow: callers add failures as they occur, then call `build()` at the end of the aggregate operation. The factory preserves single-exception identity to avoid unnecessary wrapping and only allocates a multiple wrapper when needed.

State and persistence: state is in-memory exception list storage only. The list reference is not defensively copied, so later list mutation affects `getExceptions()` and potentially the exception's logical contents.

Dependencies and integration points: depends only on Java `IOException`, `ArrayList`, and `List`, plus Hadoop annotations. It is useful for close/delete/cleanup paths across Hadoop IO and filesystem code.

Risks and test signals: risks include returning `null` from `build()`/`createIOException`, which callers must handle, and exposing a mutable list. Tests should cover null/empty/single/multiple factory cases, non-IO throwable wrapping, message contents, and builder `isEmpty` transitions.
