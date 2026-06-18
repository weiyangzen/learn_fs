# sources/cloud-native/containers-storage/pkg/ioutils/writers.go

Purpose: provides small writer adapters: no-op writer/closer/flusher, close callback wrapper, and byte-counting writer.

Important APIs, types, and functions: `NopWriter`, `NopWriteCloser`, `NopFlusher`, `NewWriteCloserWrapper`, `WriteCounter`, and `NewWriteCounter`.

Control flow: `NopWriter.Write` discards bytes and reports full length. `NopWriteCloser` delegates writes and makes `Close` a no-op. `NewWriteCloserWrapper` returns a writer with custom close callback. `WriteCounter.Write` delegates to its wrapped writer and accumulates the number of bytes successfully reported.

State and persistence: no persistence. `WriteCounter.Count` is mutable in-memory state and is not concurrency-protected.

Dependencies and integration points: depends on `io`. These helpers are used by higher-level stream plumbing, buffer pools, and code paths needing an `io.WriteCloser` around an existing writer.

Risks and edge cases: no-op writers can mask data loss if used accidentally. `WriteCounter` counts short writes exactly as reported but leaves error handling to callers. Close wrappers do not guard multiple close calls.

Test signals: `writers_test.go` verifies close callback, no-op close/write behavior, byte counting, and actual data forwarding.
