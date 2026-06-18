# sources/cloud-native/moby/daemon/logger/ring.go

Purpose: lossy asynchronous ring-buffer wrapper for log drivers.

Important APIs/types/functions: `NewRingLogger`, `ringLogger`, `ringWithReader`, `Log`, `Close`, `BufSize`, `run`, `messageRing`, `Enqueue`, `Dequeue`, `Close`, and `Drain`.

Control flow/state/persistence: `NewRingLogger` starts a background goroutine forwarding queued messages to the underlying logger. `messageRing.Enqueue` drops a new message when adding it would exceed byte capacity and the queue is non-empty; an oversized first message is still accepted. `Close` stops new logs, closes the ring, waits for the worker, drains remaining messages synchronously, logs failures rate-limited, and closes the underlying logger.

Dependencies/integration: wraps any `Logger`; preserves `LogReader` support through `ringWithReader`. Uses core message ownership and error logging.

Risks: dropped messages are silent by design. Close error handling assumes after first failure the underlying driver is unhealthy and returns remaining messages to pool. Atomic close flag plus buffer close must remain consistent.

Test signals: `ring_test.go` covers queue capacity, close, read passthrough, and error behavior.
