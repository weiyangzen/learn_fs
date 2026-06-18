# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CloseableReferenceCount.java

Purpose: `CloseableReferenceCount` tracks references to a closeable resource and prevents new references after closure.

Important APIs and types: methods are `reference`, `unreference`, `unreferenceCheckClosed`, `isOpen`, `setClosed`, and `getReferenceCount`. State is encoded in an `AtomicInteger` with bit 30 as closed and low bits as count.

Control flow: `reference` increments first, then rolls back and throws `ClosedChannelException` if closed. `unreference` decrements and returns true only when status equals closed-with-zero-references. `setClosed` CASes in the closed bit and returns the current count, or throws if already closed.

State and persistence behavior: all state is in one atomic integer. No persistence.

Dependencies and integration points: used by closeable channel/socket-like resources needing concurrent acquisition and asynchronous close detection.

Risks: reference count overflow is not guarded except by the closed bit layout. `unreferenceCheckClosed` can throw `AsynchronousCloseException` after decrementing. Calling unreference at zero triggers a precondition failure after underflow sentinel.

Test signals: cover open reference/unreference, close with outstanding refs, no-new-ref after close, closed-and-zero return value, double close, underflow failure, and concurrent race between reference and close.
