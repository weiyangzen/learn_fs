# subset-b-000505 Research

Grouped research for the requested BeeGFS Go watch, BeeSync work manager, and BeeGFS protobuf build artifacts. Each source section is bounded for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/internal/workmgr/work.go -->
# sources/distributed-fs/beegfs-go/rst/sync/internal/workmgr/work.go

## Purpose

This file implements the BeeSync worker-side execution path for BeeRemote work requests. It defines the durable journal entry shape used to persist requested work, the active work identity/context structures used by the manager, and the `worker` loop that pulls `workAssignment` objects from a queue, executes file-transfer or builder work against a remote storage target, reports results to BeeRemote, and cleans up journal/job-store state.

## Important APIs, Types, And Functions

`workEntry` persists a desired `workRequest`, actual `work` result, and `ExecuteAfter` reschedule time. The `workRequest` and `work` wrappers implement `GobEncode`/`GobDecode` by marshaling protobuf `flex.WorkRequest` and `flex.Work`, allowing Badger-backed `kvstore.MapStore` entries to store protobuf values through Go gob. `workIdentifier` keys active work by submission, job, and request IDs. `workAssignment` carries a cancellable context and identifier into a worker. `worker.run` drains the queue until its parent context is canceled. `worker.process` owns state validation, storage target lookup, readiness checks, journal commits, cleanup decisions, and dispatch to `processWork` or `processBuilder`. `sendWorkResult` retries BeeRemote updates until success, cancellation, or non-retryable failure.

## Control Flow

Processing starts by locking the work journal entry for the submission ID. Invalid or terminal starting states are converted to failed or resent to BeeRemote. Unknown remote storage targets fail immediately. Otherwise the selected `rst.Provider` is asked whether the work is ready; not-ready work is marked `RESCHEDULED`, assigned an `ExecuteAfter`, reported, and requeued through `rescheduleWork`. Ready work is marked `RUNNING` with an update-only journal commit. Non-builder work iterates unfinished parts and calls `ExecuteWorkRequestPart`, committing part progress after each transfer. Builder work streams generated `beeremote.JobRequest` values from `ExecuteJobBuilderRequest` and submits each to BeeRemote.

## State And Persistence

The work request is treated as desired state from BeeRemote, while the work result is actual local execution state. The journal is committed on every part completion so progress can survive crashes and be observed by readers. Completed and successfully reported work triggers cleanup of the journal entry and either the whole job-store entry or the single request ID within it. If cleanup of the job store fails, the journal entry is retained for retry. Canceled execution records local status but deliberately avoids result submission in some paths so the canceling owner can decide retry/report behavior.

## Dependencies And Integration Points

The worker depends on `common/kvstore` locking semantics, BeeSync metrics counters such as `beeSyncProcessed`, `beeSyncComplete`, and `beeSyncRescheduled`, `rst.ClientStore` providers, BeeRemote gRPC client methods `UpdateWorkRequest` and `SubmitJobRequest`, generated protobuf packages `flex` and `beeremote`, zap logging, and `unix.EAGAIN` for a BeeGFS client configuration hint. It is central to BeeSync restart/resume behavior because journal replay elsewhere can resubmit persisted work.

## Risks And Test Signals

The file is concurrency and persistence sensitive: errors in commit/delete ordering can duplicate BeeRemote reports or leak journal entries. `sendWorkResult` retries indefinitely with fixed one-second delay, which is robust for transient outages but can stall worker shutdown until context cancellation. Builder submission counts failed child jobs but still relies on BeeRemote-side status visibility. `processWork` currently treats all provider transfer errors as terminal, with TODOs noting retry classification gaps. No tests are in this file, so coverage likely comes from broader work manager or BeeSync integration tests that should assert cancellation, crash replay, reschedule, and cleanup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/internal/workmgr/work.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/Dockerfile -->
# sources/distributed-fs/beegfs-go/watch/Dockerfile

## Purpose

This Dockerfile packages the `beegfs-watch` binary into a minimal container image. It uses `gcr.io/distroless/static:latest`, copies the prebuilt binary to `/beegfs-watch`, and sets that binary as the entrypoint.

## Important APIs, Types, And Functions

There is no application code here. The operational contract is `COPY beegfs-watch /beegfs-watch` followed by `ENTRYPOINT ["/beegfs-watch"]`. A commented `USER 1000` documents a desired non-root posture that is not enabled because the event log Unix socket may be bind-mounted with permissions requiring root.

## Control Flow

Build-time flow is a single-stage image assembly; runtime flow is direct execution of `/beegfs-watch` with all configuration expected through flags, environment variables, or mounted config files handled by the Go binary.

## State And Persistence

The image contains only the binary. Runtime state, certificates, authentication files, config files, log files, and the BeeGFS event socket must be provided by the container environment through bind mounts, secrets, or stdout/stderr logging.

## Dependencies And Integration Points

It depends on an externally built static `beegfs-watch` binary in the Docker build context and on the distroless static base. It integrates with Kubernetes or container runtimes through mounts for `/etc/beegfs`, `/var/log/beegfs`, and the configured `sysFileEventLogTarget` equivalent.

## Risks And Test Signals

Using `latest` makes the base image mutable and can reduce reproducibility. Running as root broadens container privilege, although the comment explains why that may be needed. There are no local tests; validation should include image build, binary startup, config/cert mount access, and ability to open the Unix packet socket.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/cmd/beegfs-watch/main.go -->
# sources/distributed-fs/beegfs-go/watch/cmd/beegfs-watch/main.go

## Purpose

This is the BeeWatch daemon entry point. It wires configuration, logging, license verification, metadata event ingestion, subscriber management, dynamic config reloads, pprof, and graceful shutdown into a single process that relays BeeGFS metadata events to configured subscribers.

## Important APIs, Types, And Functions

`main` defines pflags for logging, management gRPC, subscriber handler behavior, hidden developer options, and version output. Build variables `binaryName`, `version`, `commit`, and `buildTime` are set through linker flags. It creates a `configmgr.Manager` over `config.AppConfig`, initializes a common logger, verifies the `io.beegfs.watch` license through `beegrpc.NewMgmtd`, constructs `metadata.New`, constructs `subscribermgr.New`, registers both logger and subscriber manager as config listeners, and starts `metaMgr.Manage`, `sm.Manage`, and `cfgMgr.Manage`.

## Control Flow

Startup order is deliberate: parse config, optionally dump config/version, initialize logging, optionally start pprof, read management TLS/auth files, verify license, initialize the metadata socket and event buffer, initialize subscriber manager, start subscriber handling, then start metadata ingestion last to avoid accepting events before subscribers are ready. Shutdown first cancels metadata ingestion, then waits until `EventBuffer.AllEventsAcknowledged()` or a second signal forces subscriber shutdown, then stops dynamic config and waits on the shared wait group.

## State And Persistence

The daemon itself persists no event state on disk. Event state is in memory in the metadata manager's multi-cursor ring buffer, while subscriber-side acknowledgements can avoid duplicates after reconnects. It reads certificate and auth secret files at startup. Log persistence depends on `logger.Config` and can rotate file logs.

## Dependencies And Integration Points

The command integrates with BeeGFS management gRPC for license checks, BeeGFS metadata through the configured Unix socket, the common config manager for flag/env/TOML precedence, the common logger, `metadata.Manager`, and `subscribermgr.Manager`. The SIGHUP reload behavior is handled by `configmgr.Manage`, while SIGINT/SIGTERM drive shutdown.

## Risks And Test Signals

Startup can block or fail on management connection, TLS/auth file errors, license failure, or metadata socket setup. The shutdown loop can wait indefinitely after the second phase if subscriber disconnect cleanup hangs. Hidden `management.use-http-proxy` and developer pprof options affect network/security posture. There is no direct test file for `main`; behavior is signaled by component tests plus end-to-end daemon startup/shutdown and config reload tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/cmd/beegfs-watch/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/cmd/test-fileeventlogger/main.go -->
# sources/distributed-fs/beegfs-go/watch/cmd/test-fileeventlogger/main.go

## Purpose

This test utility connects to the BeeGFS file event Unix packet socket and writes synthetic v1-format metadata event packets. It is intended for manual or performance testing of BeeWatch metadata ingestion without a live metadata service.

## Important APIs, Types, And Functions

Command-line flags configure socket path, output log file, debug logging, event send frequency, path length, and number of random events. `getLogger` builds a zap logger. `generateEvent` assembles a binary event packet from little-endian fields and C-string-like path payloads. `joinSlices` concatenates packet fragments.

## Control Flow

After parsing flags and dialing `net.Dial("unixpacket", socketPath)`, the utility pre-generates either one fixed-size event or several random-sized events. With `frequency == 0`, it writes continuously as fast as possible. Otherwise it installs signal cancellation, starts a ticker, and writes one selected event per tick until interrupted.

## State And Persistence

State is limited to the open Unix packet connection, generated event byte slices, and optional log file. It does not persist sequence counters and uses hard-coded packet contents for dropped/missed sequence fields and event type.

## Dependencies And Integration Points

It depends on the raw v1 event layout expected by `metadata.deserializeEvent` and on BeeWatch listening at the configured Unix packet socket. It integrates with zap only for local logging.

## Risks And Test Signals

The generated packet layout is hand-built and easy to desynchronize from protocol changes. `pathLengths` can generate packets near the 64 KiB reader limit; extreme values should be tested against `metadata` buffer sizing. The random event loop chooses among precomputed events, not newly randomized payloads. The utility exits fatally on write errors, which is appropriate for manual testing but not a resilient load generator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/cmd/test-fileeventlogger/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/cmd/test-subscriber/main.go -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/cmd/test-subscriber/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/config/config.go -->
# sources/distributed-fs/beegfs-go/watch/internal/config/config.go

## Purpose

This file defines BeeWatch's top-level application configuration and the update/validation rules shared by the config manager, logger, metadata manager, and subscriber manager.

## Important APIs, Types, And Functions

`AppConfig` groups `logger.Config`, `MgmtdConfig`, `subscribermgr.HandlerConfig`, `[]metadata.Config`, `[]subscriber.Config`, and hidden developer settings. It implements `configmgr.Configurable`, `logger.Configurer`, and `subscribermgr.Configurer`. `GetLoggingConfig` and `GetSMConfig` expose component-specific views without import cycles. `NewEmptyInstance` supports unmarshalling. `UpdateAllowed` enforces dynamic reload constraints. `ValidateConfig` checks static metadata buffer and target requirements.

## Control Flow

Config updates are type-checked, then developer and metadata settings are rejected if changed after startup. Logging changes are permitted only for the `Level` field; all other log sink/rotation fields are fixed. Subscriber and handler changes are allowed and later interpreted by `subscribermgr.Manager`.

## State And Persistence

This file owns no runtime state but defines which config can change without process restart. That policy preserves metadata socket/buffer stability and avoids reinitializing developer-only server features or log sinks at runtime.

## Dependencies And Integration Points

It integrates with `common/configmgr`, `common/logger`, `common/types.MultiError`, `metadata.Config`, `subscriber.Config`, and `subscribermgr.HandlerConfig`. `main.go` must be manually kept in sync with `AppConfig` fields because flags are defined there.

## Risks And Test Signals

Reflection-based logging comparison can miss semantic equality issues if logger config adds non-comparable fields. The event-version field is validated indirectly by `metadata.New`, not here. Static validation currently requires exactly one metadata service and nonzero buffer fields. Tests cover metadata update rejection but not logging-level-only reload, subscriber validation, or malformed developer changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/config/config_test.go -->
# sources/distributed-fs/beegfs-go/watch/internal/config/config_test.go

## Purpose

This test file verifies the dynamic update policy for BeeWatch application configuration, specifically that metadata service configuration is immutable after startup.

## Important APIs, Types, And Functions

`TestUpdateAllowed` constructs an initial `AppConfig` with one `metadata.Config`, a variant with the event log path changed, and a variant with an additional metadata service. It asserts `UpdateAllowed` accepts the unchanged config and rejects both metadata changes.

## Control Flow

The test calls `currentConfig.UpdateAllowed(&currentConfig)`, `UpdateAllowed(&newConfig)`, and `UpdateAllowed(&newConfig2)`, using testify `assert.NoError` and `assert.Error` to express the allowed and rejected cases.

## State And Persistence

There is no persistence. Test state is in-memory config structs. The test models runtime reload semantics where metadata changes would require socket and buffer reconstruction.

## Dependencies And Integration Points

It imports `metadata.Config` and `stretchr/testify/assert`. Its signal is consumed by the config package and indirectly protects `main.go`/`configmgr` dynamic reload behavior.

## Risks And Test Signals

Coverage is narrow. It does not test rejection of developer changes, log sink changes, invalid config type, or allowance of subscriber and handler changes. It also does not test `ValidateConfig`. Still, it locks down the most critical invariant: metadata ingestion settings cannot be hot-swapped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/config/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/metadata/conn.go -->
# sources/distributed-fs/beegfs-go/watch/internal/metadata/conn.go

## Purpose

This file provides a small connection helper for the BeeGFS v2 file-event protocol. It serializes outbound control messages, reads inbound packets from a Unix packet connection, deserializes them, and coordinates reads with connection shutdown.

## Important APIs, Types, And Functions

`fileEventConnHandler` contains a `net.Conn`, mutex, reusable `Serializer`, reusable `Deserializer`, and logger. `send` serializes a `Serializable` with `Serializer.Assemble` and writes it to the connection. `recv` repeatedly reads into the deserializer buffer, respecting read deadlines and mutex locking, then calls `Disassemble` into the expected `Deserializable`.

## Control Flow

`recv` locks the connection, sets a one-second read deadline, reads a packet, unlocks, and loops on deadline expiry with no bytes read. It treats `net.ErrClosed` as graceful disconnect, logs other read/deserialization errors, and returns a boolean success/failure to the v2 metadata connection state machine.

## State And Persistence

The handler is stateful only through reusable buffers and the underlying connection. It does not persist event sequence state; that is managed by `metadata.Manager`.

## Dependencies And Integration Points

It is used by `Manager.handleV2Connection` for handshake, range, stream-start, and event packets. It depends on the `serde.go` message interfaces and on Unix packet semantics where a read returns a whole packet.

## Risks And Test Signals

The recover block logs the raw connection buffer but does not return a structured panic error. The code assumes no meaningful partial read occurs on deadline expiry; if that invariant fails, an event is lost. `send` has no mutex, which is fine for current linear use but would matter if multiple goroutines wrote to the same handler. Direct tests are absent; coverage should be added around deadline, closed connection, malformed magic, and packet type mismatch behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/metadata/conn.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/metadata/deserialize.go -->
# sources/distributed-fs/beegfs-go/watch/internal/metadata/deserialize.go

## Purpose

This file decodes raw BeeGFS metadata event payloads into generated BeeWatch protobuf `Event` messages. It supports both legacy v1 packets and v2 packets introduced with BeeGFS 8.

## Important APIs, Types, And Functions

`deserializeEvent(buf, expectedSize)` is the main entry point. `parseV1Event` maps v1 dropped/missed sequence fields, event type, entry IDs, paths, and target fields. `parseV2Event` maps event flags, link count, v2 event type, identifiers, paths, message user ID, and timestamp. `parseCStrings` and `parseCString` decode length-prefixed null-terminated strings shared by both versions.

## Control Flow

The decoder reads the first uint16 as a major version. Version 1 additionally validates minor version zero and uses the embedded packet size to ensure enough bytes were read before parsing. Version 2 reads event flags, delegates to `parseV2Event`, and verifies the parsed byte count equals the size passed by the caller. Unsupported versions return errors.

## State And Persistence

All decoding is stateless. It returns a freshly allocated protobuf event while reading from a caller-owned reusable byte buffer. Sequence ID assignment for v1 and v2 stream packet sequence IDs happen outside this file.

## Dependencies And Integration Points

It depends on little-endian BeeGFS metadata protocol layout and generated `beewatch` protobuf types. `metadata.serde.SendMessage.Deserialize` reuses it for v2 streamed events, and `Manager.handleV1Connection` uses it directly for v1 socket packets.

## Risks And Test Signals

The low-level parsing performs unchecked slicing and relies on upstream packet size validation; malformed short buffers can panic rather than return an error. `parseCString` assumes the encoded length excludes the null terminator and that the terminator exists. Tests cover representative v1 and v2 packets and selected error cases for unsupported version and v2 size mismatch, but not truncated string fields or oversized lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/metadata/deserialize.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/metadata/deserialize_test.go -->
# sources/distributed-fs/beegfs-go/watch/internal/metadata/deserialize_test.go

## Purpose

This file validates raw metadata packet decoding for known v1 and v2 BeeGFS event examples and verifies selected malformed packet errors.

## Important APIs, Types, And Functions

`TestDeserialize` defines a table of byte slices and expected `pb.Event` values. Cases include v1 unlink, v1 rename, v1 setattr with missed events, v1 close-write with dropped events, v2 create, v2 open-read, and v2 last-writer-closed. A second table checks unsupported version and mismatched v2 parsed size.

## Control Flow

Each positive case calls `deserializeEvent(tc.input, uint32(len(tc.input)))` and asserts no error plus equality with the expected protobuf. Negative cases call the same function and assert an error.

## State And Persistence

The test is pure in-memory byte decoding. It encodes protocol fixtures directly in source, making the expected wire layout visible but verbose.

## Dependencies And Integration Points

It depends on generated `beewatch` protobuf enums and testify assertions. The fixtures protect the contract consumed by `metadata.Manager` and the test file event logger utility.

## Risks And Test Signals

The tests are strong regression signals for field offsets and enum mapping, especially the v2 timestamp/user fields. They do not cover packet truncation panic paths, invalid v1 minor version, target path edge cases beyond rename, or v2 stream wrapper parsing in `serde.go`. Because fixtures are hand-coded, changes to protobuf enum values or metadata packet layout require careful fixture updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/metadata/deserialize_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/metadata/manager.go -->
# sources/distributed-fs/beegfs-go/watch/internal/metadata/manager.go

## Purpose

This file implements BeeWatch metadata ingestion. It creates the Unix packet socket consumed by BeeGFS metadata services, negotiates v2 protocol state when needed, deserializes file events, assigns metadata identity fields, and pushes events into a shared multi-cursor ring buffer.

## Important APIs, Types, And Functions

`Manager` holds the `EventBuffer`, context, socket path/listener, last sequence ID, and selected event protocol version. `Config` defines event log target, buffer size, GC frequency, and event version. `newEventVersion` parses `major.minor` strings. `New` validates one metadata service, creates/removes socket paths, opens `net.Listen("unixpacket", ...)`, and returns a cleanup function. `Manage` accepts connections and dispatches `handleV1Connection` or `handleV2Connection`. `Sample` logs incoming event rate.

## Control Flow

`Manage` repeatedly starts an accept goroutine and waits for either shutdown or a connection. For each connection, it runs a reader goroutine and waits for app shutdown or connection failure. V2 handling sends a handshake, receives metadata ID/mirror ID, requests the message range, chooses a stream start sequence based on `lastSeqID` and available oldest event, sends `RequestMessageStreamStart`, and then receives `SendMessage` packets indefinitely. V1 handling simply reads packets and increments a local sequence counter.

## State And Persistence

Event state is in memory. `lastSeqID` prevents duplicate v2 pushes across reconnects and controls the v2 PMQ stream start point. The event buffer may drop old unacknowledged events on overflow and returns a dropped sequence ID for warning. The socket file is removed/recreated on startup and closed by the cleanup function.

## Dependencies And Integration Points

It integrates with `types.MultiCursorRingBuffer`, `serde.go`, `deserialize.go`, `fileEventConnHandler`, zap logging, and BeeGFS metadata service Unix packet protocol. `cmd/beegfs-watch/main.go` starts it only after subscribers are configured.

## Risks And Test Signals

`newEventVersion` uses `if major != 1 && major != 2 && minor != 0`, which accepts some unsupported major/minor combinations that may have been intended for rejection. `Manage` starts a new accept goroutine each loop and relies on socket close/context to retire blocked accepts. Event state is not durable, so process restart relies on metadata PMQ range plus subscriber acknowledgements. There are no direct manager tests; integration tests should cover v2 handshake, reconnect from `lastSeqID`, buffer overflow warnings, shutdown while blocked in read, and invalid event-version parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/metadata/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/metadata/serde.go -->
# sources/distributed-fs/beegfs-go/watch/internal/metadata/serde.go

## Purpose

This file defines the BeeGFS v2 file-event control protocol serialization/deserialization layer used between BeeWatch and the metadata service.

## Important APIs, Types, And Functions

`MsgID` enumerates packet types and has a `String` method. `Serializable` and `Deserializable` define message interfaces. `Serializer.Assemble` writes message ID, magic string `events\x00`, and message-specific payload. `Deserializer.Disassemble` validates packet type and magic, then calls message-specific `Deserialize`. Message structs include `HandshakeRequest`, `HandshakeResponse`, `RequestMessageNewest`, `SendMessageNewest`, `RequestMessageRange`, `SendMessageRange`, `RequestMessageStreamStart`, `SendMessage`, `CloseRequest`, and `SendClose`.

## Control Flow

Outbound messages are serialized through little-endian binary writes into a reusable buffer. Inbound messages are first copied from a raw connection buffer into a parsing buffer, then decoded by expected type. `SendMessage.Deserialize` reads the stream sequence ID and event size, decodes the remaining bytes with `deserializeEvent`, assigns `Event.SeqId`, and leaves metadata ID/mirror assignment to the manager.

## State And Persistence

The serializer/deserializer hold reusable memory but no durable state. Deserialization panics are treated as fatal: the deferred recover in `Disassemble` prints diagnostic hex and exits the process.

## Dependencies And Integration Points

It depends on the same raw protocol as BeeGFS metadata and on generated `beewatch` protobuf event types. `conn.go` uses it for all v2 connection packets, while `manager.go` defines protocol sequencing.

## Risks And Test Signals

The fatal `os.Exit(1)` on deserialize panic can terminate BeeWatch on malformed input; returning an error would be safer for a network-facing parser. Many `binary.Write`/`binary.Read` calls ignore errors in message-specific methods. Magic/type validation is a useful guard, but tests for it are not present. The generated `SendMessage` event-size field is uint16, so event payloads above that limit are unsupported by protocol design.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/metadata/serde.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/subscriber/config.go -->
# sources/distributed-fs/beegfs-go/watch/internal/subscriber/config.go

## Purpose

This file defines subscriber configuration and factory logic. It converts user-provided subscriber config into concrete `Subscriber` instances used by subscriber handlers.

## Important APIs, Types, And Functions

`Config` contains common subscriber fields `Type`, `ID`, `Name`, and embedded `GrpcConfig` squashed for Viper/mapstructure. `GrpcConfig` contains address, TLS certificate, TLS verification/disable flags, proxy flag, and disconnect timeout. `NewSubscribersFromConfig` creates all subscribers and fails on the first invalid config. `newSubscriberFromConfig` initializes common disconnected state and selects the implementation by `Type`.

## Control Flow

The current factory supports only `Type: "grpc"`. It wraps a `GRPCSubscriber` returned by `newGRPCSubscriber` inside a generic `Subscriber`. Unknown types return an error and prevent manager updates from applying.

## State And Persistence

The produced `Subscriber` holds static config, thread-safe state initialized to `DISCONNECTED`, and an implementation interface. No state is persisted here.

## Dependencies And Integration Points

It integrates with `subscribermgr.Manager.UpdateConfiguration`, which calls `NewSubscribersFromConfig` before adding/removing handlers. Mapstructure tags define the external TOML/env config contract.

## Risks And Test Signals

Subscriber IDs are not checked for duplicates here; duplicate IDs could confuse handler maps and ring-buffer cursors. Required fields such as gRPC address are not statically validated in this file. Tests confirm gRPC construction and default disconnect timeout, but more coverage is needed for unknown types, duplicate IDs, and missing addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/subscriber/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/subscriber/config_test.go -->
# sources/distributed-fs/beegfs-go/watch/internal/subscriber/config_test.go

## Purpose

This file tests subscriber factory behavior for configured gRPC subscribers and the comparable-test helpers used to compare structs with non-comparable fields.

## Important APIs, Types, And Functions

`testConfig` defines two gRPC subscribers. `TestNewSubscribersFromConfig` calls `NewSubscribersFromConfig`, builds expected `Subscriber` and `GRPCSubscriber` objects, then compares common fields through `newComparableSubscriber`.

## Control Flow

The test validates slice length, common subscriber config/state, and implementation-specific gRPC config. It also switches over the concrete `Interface` type to make adding new subscriber types a deliberate test update.

## State And Persistence

All state is in memory. It specifically verifies initial state is `DISCONNECTED` and that `DisconnectTimeout` defaults to 30 when unset.

## Dependencies And Integration Points

It depends on testify assertions and `subscriber` package test helper `ComparableGRPCSubscriber`. It protects the configuration contract used by `subscribermgr.Manager.UpdateConfiguration`.

## Risks And Test Signals

The test is good at catching factory output drift, but it does not test error paths for unknown subscriber type, malformed config, or duplicate subscriber ID. It also does not verify TLS/proxy behavior because connection establishment is covered by runtime integration rather than unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/subscriber/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/subscriber/grpc.go -->
# sources/distributed-fs/beegfs-go/watch/internal/subscriber/grpc.go

## Purpose

This file implements the gRPC subscriber client used by BeeWatch handlers to connect to external subscriber services, send event streams, receive acknowledgement responses, and disconnect cleanly.

## Important APIs, Types, And Functions

`GRPCSubscriber` embeds `GrpcConfig` and holds `grpc.ClientConn`, generated `pb.SubscriberClient`, bidirectional stream, response channel, and mutex-protected receive-loop state. `newGRPCSubscriber` applies the default disconnect timeout. `Connect` reads optional TLS CA cert, creates a client connection through `beegrpc.NewClientConn`, and opens `ReceiveEvents`. `Send` sends one protobuf event. `Receive` starts at most one goroutine receiving `pb.Response` messages. `Disconnect` closes the send side, drains responses until stream close or timeout, and closes the gRPC connection.

## Control Flow

Handlers call `Connect`, then `Receive`, then repeatedly call `Send`. `Receive` returns an existing channel if already active, preventing duplicate stream receivers. On stream receive error or EOF, the receive goroutine exits and closes the channel. `Disconnect` is defensive against partially initialized connections by nil-checking stream and connection fields.

## State And Persistence

Connection state is in memory only. Persistent delivery progress is externalized through subscriber acknowledgements, not stored by this client. `recvStreamActive` controls goroutine lifecycle across reconnects.

## Dependencies And Integration Points

It depends on common `beegrpc` helpers for TLS/proxy options, generated `beewatch` subscriber client, grpc-go, and `common/types.MultiError`. It is the concrete implementation behind `subscriber.Interface` used by `subscribermgr.Handler`.

## Risks And Test Signals

`Connect` uses `context.TODO()` for the stream, relying on `Disconnect` rather than context cancellation. Send failures cause handler reconnect without retrying the individual event send. `Receive` drops receive errors instead of surfacing them except via closed channel. `Disconnect` can block up to `DisconnectTimeout` draining responses. Unit tests only cover construction defaults; integration tests should cover TLS misconfiguration hints, reconnect loops, response draining, and idempotent disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/subscriber/grpc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/subscriber/subscriber.go -->
# sources/distributed-fs/beegfs-go/watch/internal/subscriber/subscriber.go

## Purpose

This file defines the common subscriber abstraction and thread-safe lifecycle state used by subscriber handlers independent of transport type.

## Important APIs, Types, And Functions

`Interface` requires `Connect`, `Send`, `Receive`, and `Disconnect`. The unexported `state` enum has `DISCONNECTED`, `CONNECTING`, `CONNECTED`, and `DISCONNECTING`. `State` wraps the current state with an RW mutex and provides `GetState`/`SetState`. `Subscriber` embeds `Config`, `State`, and the transport `Interface`. `ComparableSubscriber` is a test-only comparable view.

## Control Flow

The interface is intentionally lifecycle-oriented: handlers own state transitions, while concrete subscribers only perform connection operations. This separation lets `subscribermgr.Handler.Handle` implement common reconnection and send/receive logic.

## State And Persistence

State is process-local and thread-safe. No subscriber state is persisted in BeeWatch; durable acknowledgement state is expected to live in the subscriber service itself.

## Dependencies And Integration Points

It depends on generated `beewatch` protobuf event and response types. `subscriber/config.go` constructs subscribers, `grpc.go` implements the current interface, and `subscribermgr/handler.go` drives state transitions.

## Risks And Test Signals

The contract says `Disconnect` must be idempotent and `Connect` is not expected to be idempotent; concrete implementations must honor that or handlers can leak resources. The exported state constants are unexported type values, limiting misuse but still package-visible. Tests indirectly validate initial state through config tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/subscriber/subscriber.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/subscriber/subscriber_test.go -->
# sources/distributed-fs/beegfs-go/watch/internal/subscriber/subscriber_test.go

## Purpose

This file contains test-only reflection helpers for comparing subscriber structs that include non-comparable fields, especially interface-backed concrete subscriber values.

## Important APIs, Types, And Functions

`ComparableSubscriberT` constrains allowed comparable output types to `ComparableSubscriber` and `ComparableGRPCSubscriber`. `newComparableSubscriber` reflects over a source subscriber implementation, copies fields with matching names and types into a comparable struct, and returns the typed comparable pointer.

## Control Flow

The helper iterates source fields, checks whether the destination comparable type has a field with the same name, verifies the type matches, and copies the value. On mismatch or cast failure it prints a diagnostic and returns nil.

## State And Persistence

No persistent state exists. This helper is test support for struct comparison only.

## Dependencies And Integration Points

It is used by `config_test.go` to compare configured `Subscriber` and `GRPCSubscriber` values. It depends on reflection and the subscriber interface shape.

## Risks And Test Signals

Because diagnostics use `fmt.Printf` rather than `testing.T`, failures surface through nil/equality assertions in callers. New subscriber types require updating the type constraint and adding comparable structs. This helper can mask omitted fields if the comparable type is not kept up to date, so comments correctly require maintenance alongside subscriber struct changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/subscriber/subscriber_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/subscribermgr/handler.go -->
# sources/distributed-fs/beegfs-go/watch/internal/subscribermgr/handler.go

## Purpose

This file implements the lifecycle manager for one subscriber. It connects with retry/backoff, starts bidirectional event and acknowledgement loops, advances the subscriber's ring-buffer cursor, handles reconnects, and disconnects on shutdown or stream errors.

## Important APIs, Types, And Functions

`Handler` wraps context/cancel, logger, `MultiCursorRingBuffer`, `HandlerConfig`, a `subscriber.Subscriber`, a mutex, and `lastSeqID`. `newHandler` adds a cursor for the subscriber ID and initializes state. `Handle` is the state machine. `connectLoop` applies exponential backoff with jitter. `receiveLoop` reads subscriber acknowledgements and calls `AckEvent`. `sendLoop` polls the event buffer and calls `Send`. `doDisconnect` and `Stop` handle cleanup and cancellation.

## Control Flow

`Handle` locks the handler for its lifetime, connects when disconnected, starts receive and send loops when connected, and disconnects when either loop exits or the handler context is canceled. On connect, it waits briefly for an initial acknowledgement so it can avoid resending events the subscriber already persisted. It then resets the send cursor to the ack cursor and streams events on a poll interval until no more events are available or send fails.

## State And Persistence

`lastSeqID` avoids duplicate sends after restart/reconnect even when the ring buffer is not yet repopulated enough for `AckEvent` to move the cursor. Durable progress is still subscriber-owned. The handler owns one cursor in the shared buffer for the subscriber ID; removal is done by the manager when a subscriber is deleted.

## Dependencies And Integration Points

It depends on `subscriber.Interface`, `types.MultiCursorRingBuffer`, generated `beewatch.Response` via the subscriber interface, and zap. It integrates tightly with `metadata.Manager` by consuming from the same event buffer that metadata pushes into.

## Risks And Test Signals

Polling adds delivery latency and CPU tradeoffs controlled by `PollFrequency`. The backoff clamp can produce values near `MaxReconnectBackOff - rand`, so zero or small config values should be validated elsewhere. Ack errors are logged once and tolerated during startup, which is pragmatic but can hide persistent subscriber bugs at debug level. Tests cover construction only; higher-value tests should simulate subscriber sends/acks, reconnects, duplicate suppression, and shutdown with unacknowledged events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/subscribermgr/handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/subscribermgr/handler_test.go -->
# sources/distributed-fs/beegfs-go/watch/internal/subscribermgr/handler_test.go

## Purpose

This file tests basic handler initialization and subscriber add/remove diffing logic for the subscriber manager.

## Important APIs, Types, And Functions

`TestNewHandler` constructs a logger, handler config, empty subscriber, and ring buffer, then asserts key handler fields are initialized. `TestEvaluateChangedSubscribers` builds current handler IDs 1 and 2 and new subscriber IDs 1 and 3, then asserts ID 3 is added, ID 2 removed, and ID 1 verified.

## Control Flow

The tests call package-private functions `newHandler` and `evaluateAddedAndRemovedSubscribers`, using testify assertions to validate returned state and maps.

## State And Persistence

No persistence exists. `TestNewHandler` also implicitly verifies `newHandler` adds a cursor by creating a usable buffer, although it does not assert cursor map contents directly.

## Dependencies And Integration Points

It depends on `subscriber.Subscriber`, `types.NewMultiCursorRingBuffer`, zap development logger, and testify. It protects manager update behavior used during dynamic config reload.

## Risks And Test Signals

The tests do not exercise `Handle`, `connectLoop`, send/receive loops, or disconnect paths. They are useful smoke tests for construction and diffing but leave the subscriber delivery state machine largely untested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/subscribermgr/handler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/subscribermgr/manager.go -->
# sources/distributed-fs/beegfs-go/watch/internal/subscribermgr/manager.go

## Purpose

This file manages the set of active subscriber handlers and applies dynamic subscriber configuration changes. It adds, removes, restarts, and shuts down handlers while preserving event-buffer cursors when appropriate.

## Important APIs, Types, And Functions

`Manager` stores logger, handler slice, shared metadata event buffer, and wait group. `New` constructs it and tags the logger. `Configurer` defines the app-config view needed for subscriber updates. `UpdateConfiguration` validates new subscribers, evaluates additions/removals/verifications, stops old handlers, removes cursors for deleted subscribers, swaps handlers for changed config, and starts new handler goroutines. `evaluateAddedAndRemovedSubscribers` computes ID maps. `Manage` waits for global shutdown and stops all handlers.

## Control Flow

On every config update, new subscriber configs are fully parsed first. Removed handlers are stopped and locked before cursor removal. Existing handlers with changed subscriber config or handler config are stopped, locked, replaced, and restarted. New subscribers get new handlers and goroutines. Shutdown simply calls `Stop` on all handlers and leaves wait-group completion to each handler.

## State And Persistence

Manager state is the in-memory handler slice. Cursor lifetime is tied to subscriber presence: updated subscribers keep cursors to avoid dropping events during config changes, while removed subscribers have cursors removed. There is no persisted subscriber list beyond the external config source.

## Dependencies And Integration Points

It implements `configmgr.Listener`, receives `config.AppConfig` through the `Configurer` interface, uses `subscriber.NewSubscribersFromConfig`, and coordinates with `types.MultiCursorRingBuffer` plus the shared application wait group from `main.go`.

## Risks And Test Signals

The handler mutex is intentionally locked during replacement/removal and not unlocked because the old handler is discarded; this is unusual but documented. Duplicate subscriber IDs in the new config are not explicitly rejected and map-based diffing would collapse them. `Manage` does not wait itself after stopping handlers; the shared wait group handles that. Unit tests cover diffing, but update/restart/cursor behavior needs integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/subscribermgr/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/types/eventqueue.go -->
# sources/distributed-fs/beegfs-go/watch/internal/types/eventqueue.go

## Purpose

This file defines an older mutex-protected FIFO queue for BeeWatch events. A TODO states it is not currently used and was retained from early performance comparisons against ring-buffer designs.

## Important APIs, Types, And Functions

`EventQueue` holds a slice of `*pb.Event` and a mutex. `NewEventQueue` initializes the slice. `Push` appends an event. `Pop` returns and removes the first event or nil. `RemoveUntil` drops all events with `SeqId <= id`.

## Control Flow

All operations lock the queue mutex around slice mutation. `Pop` and `RemoveUntil` repeatedly reslice from the front, producing straightforward FIFO behavior.

## State And Persistence

State is in-memory only. No persistence or subscriber cursor support exists, which is why this structure is not the active BeeWatch event buffer.

## Dependencies And Integration Points

It depends only on generated `beewatch.Event` types. It has no current production integration points according to the file comment.

## Risks And Test Signals

`NewEventQueue(length)` creates a slice with length `length`, not capacity `length`, so a new queue initially contains `length` nil entries. If reused, that would cause early `Pop` calls to return nil before pushed events. Front-reslicing can retain underlying references and has O(n) memory movement implications over time. The file has no tests and should either be removed or fixed before use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/types/eventqueue.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/types/eventringbuffer.go -->
# sources/distributed-fs/beegfs-go/watch/internal/types/eventringbuffer.go

## Purpose

This file implements a simple single-cursor ring buffer for BeeWatch events. It stores pointers to protobuf events, overwrites the oldest event when full, and supports pop/peek/remove operations.

## Important APIs, Types, And Functions

`EventRingBuffer` has `buffer`, `start`, `end`, and an RW mutex. `NewEventRingBuffer` creates a size+1 buffer to distinguish full from empty. `Push` inserts and advances `end`, moving `start` on overwrite. `Pop` removes and nils the oldest event. `RemoveUntil` drops events through a sequence ID. `Peek` returns the oldest event without moving. `IsEmpty` reports `start == end`.

## Control Flow

Every mutating method locks the buffer. Push writes at `end`, advances modulo length, and if it collides with `start`, advances `start`. Pop and remove clear slots to allow garbage collection.

## State And Persistence

State is in-memory only. This buffer has one logical reader and no acknowledgement tracking, so production multi-subscriber delivery uses `MultiCursorRingBuffer` instead.

## Dependencies And Integration Points

It depends on generated `beewatch.Event` types. Tests cover it directly, but active metadata/subscriber code uses the multi-cursor buffer.

## Risks And Test Signals

`Peek` calls `IsEmpty` while holding `RLock`; Go `sync.RWMutex` permits multiple read locks by the same goroutine, so this is fine but redundant. The overwrite policy silently discards old events. Tests validate capacity, overflow ordering, pop, peek, and remove-until behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/types/eventringbuffer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/types/eventringbuffer_test.go -->
# sources/distributed-fs/beegfs-go/watch/internal/types/eventringbuffer_test.go

## Purpose

This file tests the simple `EventRingBuffer` implementation for initialization, overflow ordering, pop/peek semantics, and sequence-based removal.

## Important APIs, Types, And Functions

`TestNewEventBuffer` checks that internal capacity is requested size plus one. `TestEventBufferPushPop` pushes many events through a small buffer and verifies only the most recent capacity-sized window remains. `TestRemoveUntil` pushes events, removes through sequence ID 5, and confirms the remaining count.

## Control Flow

Tests create generated `pb.Event` values with sequential `SeqId`, push them into the buffer, then pop/peek and assert expected sequence IDs and empty states.

## State And Persistence

All state is in-memory. Tests intentionally cause overflow to validate destructive retention behavior.

## Dependencies And Integration Points

It depends on testify and generated `beewatch.Event`. The tested buffer is not the active multi-subscriber buffer, but it documents the simpler ring-buffer semantics used as a baseline.

## Risks And Test Signals

`TestRemoveUntil` comment says five items remain after removing through 5 from events 0..10, and the loop indeed expects five pops for IDs 6..10. Missing cases include wraparound removal, remove on empty buffer, and concurrent access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/types/eventringbuffer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/types/multicursorringbuffer.go -->
# sources/distributed-fs/beegfs-go/watch/internal/types/multicursorringbuffer.go

## Purpose

This file implements BeeWatch's primary event buffer: a single-writer, multi-reader ring buffer with per-subscriber send and acknowledgement cursors. It is optimized to let metadata ingestion push events with minimal locking while multiple subscribers independently read and ack progress.

## Important APIs, Types, And Functions

`MultiCursorRingBuffer` stores event slots, `start`, `end`, cursor map, cursor-map lock, GC counter/frequency. `SubscriberCursor` stores `sendCursor`, `ackCursor`, mutex, and `ackError`. Public methods include `NewMultiCursorRingBuffer`, `AddCursor`, `RemoveCursor`, `AllEventsAcknowledged`, `Push`, `GetEvent`, `ResetSendCursor`, and `AckEvent`. Internal helpers `collectGarbage`, `getOldestAckCursor`, and `searchIndexOfSeqID` manage space reclamation and acknowledgement lookup.

## Control Flow

`Push` writes at `end`, advances it, and periodically or urgently calls `collectGarbage`. GC finds the oldest acknowledgement cursor and frees events before it; if the buffer is out of space and subscribers have not acknowledged the oldest event, it advances affected cursors and reports the dropped sequence ID. `GetEvent` reads the next event for one subscriber and advances its send cursor if non-nil. `AckEvent` validates the acknowledged sequence against sent events, handles exact next acknowledgements, calculated offsets, skipped/dropped sequence IDs, and a ring-aware binary search fallback.

## State And Persistence

All state is in memory. Cursor state determines what each subscriber can receive and when events can be garbage-collected. `ackError` excludes a subscriber from shutdown blocking when its ack cursor is invalid, usually during startup before the buffer has been repopulated.

## Dependencies And Integration Points

It depends on generated `beewatch.Event`. `metadata.Manager` is the single writer through `Push`; subscriber handlers call `AddCursor`, `GetEvent`, `AckEvent`, `ResetSendCursor`, `RemoveCursor`, and `AllEventsAcknowledged`.

## Risks And Test Signals

This is the most concurrency-sensitive BeeWatch type. It intentionally avoids buffer-wide locks on reads/pushes, so correctness depends on a single writer and cursor locking discipline. `collectGarbage` has a likely bug when dropping the oldest unacknowledged event: it clears the old start, advances `start`, then returns `b.buffer[b.start].SeqId`, which is the new oldest event, not the dropped event. Nil holes are noted as a TODO risk in `AckEvent`. Tests cover many wraparound, GC, ack, and binary-search cases but do not cover race detector concurrency or dropped sequence ID return accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/types/multicursorringbuffer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/types/multicursorringbuffer_test.go -->
# sources/distributed-fs/beegfs-go/watch/internal/types/multicursorringbuffer_test.go

## Purpose

This file tests `MultiCursorRingBuffer` behavior across acknowledgement completion, overflow, garbage collection, cursor reset, acknowledgement edge cases, and ring-aware sequence search.

## Important APIs, Types, And Functions

`MCRBTestCase` packages named buffer fixtures. Tests include `TestAllEventsAcknowledged`, `TestPush`, `TestCollectGarbage`, `TestGetOldestAckCursor`, `TestMCRBGetEventAndResetSendCursor`, `TestAckEvent`, and `TestSearchIndexOfSeqID`.

## Control Flow

The tests use hand-built ring states for internal helpers and constructed buffers for public flows. They push sequential or intentionally skipped sequence IDs, add cursors, get events, acknowledge events, reset send cursors, and assert internal buffer/cursor positions.

## State And Persistence

The tests validate in-memory cursor and slot state directly, including nil-cleared slots after GC. This direct internal inspection gives strong regression detection for ring index math.

## Dependencies And Integration Points

It depends on generated `beewatch.Event` and testify. The tested behavior is directly consumed by metadata ingestion and subscriber handlers.

## Risks And Test Signals

Coverage is broad for deterministic index math and skipped sequence IDs, including wraparound binary search. Missing signals include concurrent race tests, `RemoveCursor`/`AddCursor` idempotence assertions, `ackError` shutdown behavior, and the exact dropped sequence ID returned by `Push`/`collectGarbage`. Adding those would catch subtle delivery-loss reporting bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/types/multicursorringbuffer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/types/types.go -->
# sources/distributed-fs/beegfs-go/watch/internal/types/types.go

## Purpose

This file is the package documentation stub for `watch/internal/types`, which contains internal BeeWatch data structures.

## Important APIs, Types, And Functions

It declares `package types` with a package comment. No runtime APIs, types, constants, or functions are defined here.

## Control Flow

There is no control flow. Package behavior is implemented in sibling files such as `eventringbuffer.go`, `multicursorringbuffer.go`, and `eventqueue.go`.

## State And Persistence

No state or persistence exists in this file.

## Dependencies And Integration Points

The file integrates with Go documentation tooling by documenting the package. It has no imports.

## Risks And Test Signals

There are no direct risks beyond documentation drift. The package's behavioral risks are in the ring buffer implementations and tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/watch/internal/types/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-protobuf/.github/workflows/checks.yml -->
# sources/distributed-fs/beegfs-protobuf/.github/workflows/checks.yml

## Purpose

This GitHub Actions workflow verifies that generated protobuf outputs are current on pull requests. It regenerates Go, C++, and Rust artifacts and fails if the repository diff changes.

## Important APIs, Types, And Functions

The workflow is named `checks`, runs on `pull_request`, and defines one `checks` job in the `rust` container. It sets `CARGO_NET_GIT_FETCH_WITH_CLI=true`, checks out code, caches tool directories keyed by the Makefile hash, installs `golang` and codegen tools on cache miss, adds `$HOME/.local/bin` to the GitHub path, and runs `git config --global --add safe.directory` plus `make clean && make test-protos`.

## Control Flow

The job installs dependencies only when the cache misses. `make test-protos` regenerates all protobuf outputs and uses `git status` to detect uncommitted generated-code changes.

## State And Persistence

Persistent state is the Actions cache for local bin/include, Cargo, Go, and `/usr/local/go`. Build outputs are regenerated in the checked-out workspace and should end clean.

## Dependencies And Integration Points

It depends on `actions/checkout@v4`, `actions/cache@v4`, apt `golang`, the repository Makefile, protoc/protoc-gen-go/protoc-gen-go-grpc/protoc-rs, and GitHub runner/container semantics.

## Risks And Test Signals

The cache key only hashes the Makefile, so dependency/tool changes outside it may not invalidate. The job uses a mutable `rust` container tag. The safe.directory path is hard-coded to `/__w/protobuf/protobuf`, which assumes repository naming. The main signal is strong: generated files must be reproducible and committed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-protobuf/.github/workflows/checks.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-protobuf/.github/workflows/contributors.yml -->
# sources/distributed-fs/beegfs-protobuf/.github/workflows/contributors.yml

## Purpose

This workflow enforces ThinkParQ contributor policy on pull requests by checking CLA-approved PR authors and approved commit author/committer identities.

## Important APIs, Types, And Functions

The `verify` job runs on PR opened/synchronize events. It checks out full history, reads `vars.APPROVED_CONTRIBUTORS` as a space-separated user list, checks the PR creator login, then reads `vars.APPROVED_COMMITTERS` as JSON mapping names to emails. For each commit unique to the PR base branch, it extracts author and committer names/emails with `git show`, masks emails in logs, and validates names and emails with `jq`.

## Control Flow

The workflow exits early if there are no PR-specific commits. Otherwise it accumulates `EXIT_CODE=1` for every failed identity check and exits once all commits are processed, allowing all violations to be reported in one run.

## State And Persistence

There is no persistent repository state. Policy state lives in GitHub Actions variables. Full git history is fetched to compute `origin/$BASE_REF..HEAD`.

## Dependencies And Integration Points

It depends on `actions/checkout@v3`, GitHub PR event fields, repository/org Actions variables, git, jq, and GitHub workflow command annotations for errors/notices/masking.

## Risks And Test Signals

If `APPROVED_COMMITTERS` is invalid JSON or jq is unavailable, the workflow will fail during validation. Name-based lookup means approved contributors must use exact configured `user.name`. The workflow masks actual emails before logs but still prints names. This is policy validation, not code validation, and its signal is commit hygiene rather than build correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-protobuf/.github/workflows/contributors.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-protobuf/Cargo.toml -->
# sources/distributed-fs/beegfs-protobuf/Cargo.toml

## Purpose

This manifest defines the Rust crate metadata for generated BeeGFS protobuf definitions.

## Important APIs, Types, And Functions

The package is named `protobuf`, version `0.0.0`, edition 2021, with ThinkParQ authorship, repository homepage, README, and `publish = false`. Dependencies are `tonic`, `prost`, `tonic-prost`, and `prost-types` at version `0.14`. The library root is `rust/lib.rs`.

## Control Flow

Cargo uses this manifest to compile the generated Rust modules under `rust/`. There is no build script here; generation is handled by the Makefile through `protoc-rs`.

## State And Persistence

The manifest does not persist runtime state. `Cargo.lock` is removed by `make clean`, suggesting this repository treats generated libraries and tool checks as source artifacts rather than a published locked application.

## Dependencies And Integration Points

Version comments require dependency versions to match the `protoc-rs` generator version used in the Makefile. The generated Rust files import prost/tonic types according to this manifest.

## Risks And Test Signals

Because the crate is unpublished and named generically `protobuf`, consumers likely use path/git dependencies rather than crates.io. Dependency version drift relative to `protoc-rs` can break generated code compilation. CI `make test-protos` catches generation drift, but a Rust compile/test job would be needed to catch all Cargo compatibility issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-protobuf/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-protobuf/Makefile -->
# sources/distributed-fs/beegfs-protobuf/Makefile

## Purpose

This Makefile is the canonical protobuf generation and verification driver for Go, C++, and Rust BeeGFS protobuf artifacts.

## Important APIs, Types, And Functions

Targets include `all`, `protos`, `test`, `test-protos`, `clean`, `check-tools`, and `install-tools`. Variables define source and output directories plus pinned tool versions: protoc 29.2, protoc-gen-go 1.36.2, protoc-gen-go-grpc 1.5.1, and protoc-rs 0.6.0. `protos` runs `protoc` for Go/gRPC and C++ outputs and `protoc-rs` for Rust outputs. `test-protos` regenerates and fails if `git status` sees changes under generated output directories.

## Control Flow

`protos` depends on `check-tools`, ensuring exact codegen versions before generation. `install-tools` downloads protoc, installs Go plugins with `go install`, and installs ThinkParQ's `protoc-rs` with Cargo from a git tag. `clean` removes generated outputs, target, and Cargo.lock.

## State And Persistence

Generated code is written into `go`, `cpp`, and `rust` directories and expected to be committed. Tool installation writes under `$HOME/.local`. `clean` is destructive to generated directories but intended before regeneration.

## Dependencies And Integration Points

It integrates with GitHub Actions checks, Go module paths under `github.com/thinkparq/protobuf/go`, C++ protobuf runtime, Rust prost/tonic code, curl, unzip, cargo, go, and protoc.

## Risks And Test Signals

Exact version checks improve reproducibility but can make local builds brittle if users have different tools. `install-tools` assumes Linux and maps `aarch64` to `aarch_64`. `test-protos` is a strong drift detector but mutates the worktree, as documented. Generated-code consumers rely on this Makefile as the source of truth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-protobuf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-protobuf/cpp/beegfs.pb.cc -->
# sources/distributed-fs/beegfs-protobuf/cpp/beegfs.pb.cc

## Purpose

This is generated C++ protobuf implementation code for `beegfs.proto`. It provides runtime descriptors, enum validation, default instances, parsing tables, serialization, byte sizing, merge/copy/swap, clearing, construction, and destruction for BeeGFS common protobuf messages.

## Important APIs, Types, And Functions

The generated namespace is `beegfs`. Message implementations covered here are `LegacyId` and `EntityIdSet`. Enum descriptor and validity functions are emitted for `EntityType`, `NodeType`, `ReachabilityState`, `ConsistencyState`, `CapacityPool`, `NicType`, `QuotaIdType`, and `QuotaType`. `LegacyId` stores `num_id` and `node_type`. `EntityIdSet` stores optional `uid`, optional UTF-8 `alias`, and optional nested `LegacyId`. The file defines `descriptor_table_beegfs_2eproto`, parse tables, default instances, class data, `_InternalSerialize`, `ByteSizeLong`, `MergeImpl`, `CopyFrom`, `InternalSwap`, `Clear`, `GetMetadata`, and static descriptor registration.

## Control Flow

At load time, static initialization registers the descriptor table through protobuf internals. Runtime parsing uses table-driven protobuf `TcParser` entries. Serialization writes only set/non-default fields and unknown fields. Merge/copy functions preserve unknown field sets and optional-field has bits. Destructors release unknown fields, arena strings, and nested `LegacyId` allocations when not arena-owned.

## State And Persistence

The file maintains process-global descriptor/default-instance state and per-message cached sizes/has bits. It does not persist data itself; persistence is protobuf wire-format serialization handled by generated methods.

## Dependencies And Integration Points

It depends on `beegfs.pb.h` and protobuf C++ runtime headers from version 5.29.2. It is generated by the repository Makefile from `proto/beegfs.proto` and should not be hand-edited. Downstream C++ code includes the header and links this implementation for BeeGFS common identifiers and enum types.

## Risks And Test Signals

The header warns "DO NOT EDIT" and "NO CHECKED-IN PROTOBUF GENCODE"; manual edits would be overwritten. Runtime compatibility depends on matching generated code with the protobuf runtime version. Optional field presence bits are semantically important for `EntityIdSet`, distinguishing unset from zero/empty values. CI `make test-protos` verifies this generated file is current; compile/link tests in downstream C++ consumers are needed to catch ABI or runtime mismatch issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-protobuf/cpp/beegfs.pb.cc -->
