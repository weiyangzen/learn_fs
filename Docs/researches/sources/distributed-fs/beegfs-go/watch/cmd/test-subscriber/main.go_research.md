# sources/distributed-fs/beegfs-go/watch/cmd/test-subscriber/main.go

## Purpose

This is a documented demonstration subscriber that implements the BeeWatch gRPC `Subscriber` service. It shows how an external service can receive file system events, persist the latest sequence ID, acknowledge progress back to BeeWatch, and shut down without requiring BeeWatch to drop buffered events.

## Important APIs, Types, And Functions

`EventSubscriberServer` embeds `bw.UnimplementedSubscriberServer` and implements `ReceiveEvents`. `NewEventSubscriberServer` constructs it. `MockDB` simulates persistence of `lastSeqID` and `lastDroppedSeq`. `MockDB.Run` loads and writes a simple `seq,dropped` file. `MockDB.Add`, `GetSeqID`, and `Sample` provide event ingestion, acknowledgement reads, and rate logging. `getLogger` creates zap loggers. The `main` function configures flags, TLS, gRPC server setup, registration, pprof, signal handling, and shutdown.

## Control Flow

The server listens on `grpc-address`, optionally with TLS. For each BeeWatch stream, `ReceiveEvents` starts a periodic acknowledgement goroutine when `ack-frequency` is nonzero, then repeatedly receives events and sends them to `MockDB`. The mock DB goroutine serially processes events, detects duplicates or gaps relative to the last sequence ID, and writes final sequence state on shutdown. Main uses `grpc.Server.Stop()` rather than `GracefulStop()` to force active stream cancellation during shutdown.

## State And Persistence

The mock database persists two comma-separated sequence values in `mock-db-filename`, allowing restarts to acknowledge the last received event and reduce duplicate delivery. The code intentionally avoids locking around sequence reads in `GetSeqID`, accepting slightly stale acknowledgements for simplicity.

## Dependencies And Integration Points

It depends on generated `github.com/thinkparq/protobuf/go/beewatch` gRPC definitions, grpc-go, optional TLS credentials, zap logging, and the BeeWatch subscriber handler's bidirectional stream semantics. It is both a runnable test fixture and integration documentation for third-party subscribers.

## Risks And Test Signals

The mock DB channel is unbuffered and `Add` is not thread-safe by design, so multiple concurrent streams could serialize or block unexpectedly. The sample logs sequence gaps but does not repair them. File permissions use `0755` for the state file, which is broader than needed. Useful validation includes running BeeWatch against this subscriber, reconnecting with a saved sequence file, and varying acknowledgement frequency to observe duplicate/drop behavior.
