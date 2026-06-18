# sources/distributed-fs/juicefs/pkg/vfs/context_cancellation_test.go

Purpose: protects cancellation behavior for readers and internal control commands.

Important APIs and types: `blockingChunkReader`, `blockingChunkStore`, `createCancellationTestReader`, `decodeControlOutput`, `runInternalControlWithCancel`, `buildTestTreeForControlCancel`, and four tests for reader close/invalidate and control Info/Summary cancellation.

Control flow and state: the blocking reader exposes channels to detect read start, cancellation, and release. Tests verify `FileReader.Close` and `DataReader.Invalidate` do not immediately cancel an in-flight BUSY read; the read completes after release. Control tests build a small tree, run `handleInternalMsg` with a context canceled immediately, decode progress/data frames, and require failed/EINTR-style responses for InfoV2 and OpSummary.

Persistence and integration: uses memory metadata, UUID-backed format names, mock chunk store, VFS creation helpers, and internal control binary framing.

Risks and test signals: the tests document a deliberate behavior: close/invalidate mark state but do not cancel BUSY reads immediately. They are timing-sensitive but give strong regression signals for cancellation semantics and internal response framing.
