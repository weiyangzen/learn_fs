<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/ErrorHolder.h -->
# sources/compression/zstd/contrib/pzstd/ErrorHolder.h

## Purpose
`ErrorHolder` centralizes first-error capture for pzstd worker, reader, and writer code.

## Important APIs, Types, And Functions
The class exposes `setError`, `hasError`, `getError`, and `check(condition, message)`. A mutex protects the stored string so multiple worker threads can report failures safely.

## Control Flow
Callers use `check` after operations; on false it records the message and returns false. Later code polls `hasError` to stop queues/workers and `pzstdMain` prints the captured error for the current input.

## State And Persistence
State is an in-memory error string guarded by a mutex. Only the first or latest recorded error is retained for the process; nothing is persisted.

## Dependencies And Integration Points
It is embedded in `SharedState` and used by `Pzstd.cpp` compression/decompression flows and file-open logic.

## Risks
If multiple workers fail, message ordering is nondeterministic. Callers must consistently check `hasError` to avoid continuing after failure.

## Test Signals
Behavior is indirectly covered by pzstd round-trip and failure-path tests; direct tests would validate thread-safe set/check behavior.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/ErrorHolder.h -->
