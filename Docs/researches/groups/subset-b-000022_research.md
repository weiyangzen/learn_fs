# subset-b-000022 research

This grouped report covers the exact subset-b-000022 source manifest. Each section preserves the original source path and is bounded by the requested reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/session.go -->
## sources/cloud-native/buildkit/session/session.go

Purpose: implements the client-side BuildKit session object: a long-lived h2c gRPC server exposed over a caller-provided `Dialer`. It lets frontends attach services such as SSH, upload, secrets, and auth to one bidirectional control connection.

Important APIs/types/functions: `Dialer` is the transport hook; `Attachable` registers a service on a `grpc.Server`; `Session` owns id, shared key, cancellation, server, net connection, and close state. `NewSession` creates the server with BuildKit grpc error interceptors, health service, and optional OpenTelemetry stats handler inherited from the input context. `Allow` registers attachables. `Run` builds session metadata containing id, shared key, and every exposed method URL, dials h2c, then serves gRPC on the returned connection. `Close` closes the connection, stops the server, waits for `Run`, and marks the session closed. `MethodURL` formats `/service/method`.

Control flow: `Run` serializes startup with `mu`, refuses work after `Close`, sets a cancel cause and `done` channel, advertises registered services in metadata, dials, releases the lock, then calls `serve`. `Close` holds the same lock while closing conn/server and waiting for `done`, so concurrent close/run paths are serialized.

State and persistence: all state is in memory. The durable-ish identity is the generated session id and caller supplied shared key, only propagated as connection metadata.

Dependencies and integration points: uses `identity`, `grpcerrors`, tracing/otelgrpc, gRPC health, and the unshown `serve` helper in this package. Consumers use `session.Caller` on the daemon side to call registered services.

Risks and test signals: `context()`/`closed()` depend on `s.ctx`, but this file never assigns it; callers should not rely on those helpers unless set elsewhere. Close waits under the mutex, so a broken serve path could stall close. Test coverage is indirect through session helpers and feature-specific providers.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/session.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/copy.go -->
## sources/cloud-native/buildkit/session/sshforward/copy.go

Purpose: bridges an `io.ReadWriteCloser` such as an SSH agent socket and a bidirectional gRPC stream carrying `BytesMessage` chunks.

Important APIs/types/functions: `Stream` is the minimal gRPC-like interface with `SendMsg` and `RecvMsg`. `Copy(ctx, conn, stream, closeStream)` pumps bytes in both directions and closes resources on EOF, stream errors, connection errors, or context cancellation.

Control flow: an `errgroup` starts two goroutines. The receive-to-conn goroutine repeatedly receives a `BytesMessage`, writes its data to `conn`, and reuses the message buffer. If the stream returns EOF, it half-closes the write side when `conn` supports `CloseWrite`; otherwise it closes the connection. The conn-to-stream goroutine reads up to 32 KiB from `conn`, sends each chunk, and calls `closeStream` on connection EOF so gRPC clients can see CloseSend. Both goroutines check context cancellation after blocking I/O and return `context.Cause(ctx)` when canceled.

State and persistence: no persistent state; only transient buffers and a connection lifecycle. `defer conn.Close()` plus explicit closes make shutdown aggressive.

Dependencies and integration points: used by the SSH socket mount listener and provider server. It depends on `errgroup` and `pkg/errors` for concurrent error propagation and wrapping.

Risks and test signals: close races are expected and largely benign, but the first non-nil errgroup error wins. The code assumes byte framing is not semantically meaningful beyond ordering. `raw_provider_test.go` exercises bidirectional message flow, larger payloads, and stream adapters.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/copy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/ssh.go -->
## sources/cloud-native/buildkit/session/sshforward/ssh.go

Purpose: exposes a local Unix socket inside a build that forwards each accepted connection to an SSH agent service registered on a BuildKit session.

Important APIs/types/functions: `DefaultID` is `"default"` and `KeySSHID` is the gRPC metadata key selecting an agent. `SocketOpt` carries ID, UID, GID, and mode for the mounted socket. `MountSSHSocket` creates a temporary directory, listens on `ssh_auth_sock`, applies ownership and permissions, starts an accept loop, and returns path plus cleanup closure. `CheckSSHID` asks the session provider whether an ID is configured.

Control flow: `server.run` uses an errgroup with one goroutine waiting for context cancellation and another accepting listener connections. For each accepted connection it creates an SSH client on `session.Caller.Conn()`, wraps the caller context, adds metadata for the selected id, opens `ForwardAgent`, and runs `Copy` in its own goroutine.

State and persistence: state is a temporary filesystem socket and listener. The cleanup closure closes the listener and removes the socket path; the parent temp directory is removed only on setup error, not in the closer, which may leave an empty temp directory.

Dependencies and integration points: integrates with session `Caller`, generated SSH gRPC stubs, and metadata. This is consumed by executor mount plumbing for `RUN --mount=type=ssh`.

Risks and test signals: accept loop returns errors such as listener close; the caller ignores `s.run` errors because it runs in a goroutine. Per-connection `Copy` errors are also intentionally detached. Socket ownership/mode failures abort setup. Provider tests validate the backing gRPC service path.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/ssh.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/ssh.pb.go -->
## sources/cloud-native/buildkit/session/sshforward/ssh.pb.go

Purpose: generated protobuf message bindings for `ssh.proto`.

Important APIs/types/functions: defines `BytesMessage` with `Data []byte`, `CheckAgentRequest` with `ID string`, and empty `CheckAgentResponse`. Each type has generated `Reset`, `String`, `ProtoMessage`, `ProtoReflect`, deprecated `Descriptor`, and getter methods. The file descriptor encodes the `moby.sshforward.v1.SSH` service with unary `CheckAgent` and bidirectional streaming `ForwardAgent`.

Control flow: there is no handwritten control flow. Generated methods delegate to `protoimpl` for reflection, descriptor compression, message info storage, and init-time type construction.

State and persistence: message state is per-instance protobuf runtime state, unknown fields, and size cache. No persistence is performed here.

Dependencies and integration points: generated from `github.com/moby/buildkit/session/sshforward/ssh.proto`; used by `ssh.go`, `raw_provider.go`, vtproto fast paths, and generated gRPC stubs.

Risks and test signals: do not manually edit. Schema changes must be made in `ssh.proto` and regenerated with matching protoc/protoc-gen-go versions. Compatibility risk is field-number stability: `data = 1` and `ID = 1` must remain compatible with clients. Functional behavior is tested through provider and SSH forwarding tests rather than generated methods directly.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/ssh.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/ssh.proto -->
## sources/cloud-native/buildkit/session/sshforward/ssh.proto

Purpose: declares the wire contract for BuildKit SSH agent forwarding over a session.

Important APIs/types/functions: package `moby.sshforward.v1`, Go package `github.com/moby/buildkit/session/sshforward`. Service `SSH` has `CheckAgent(CheckAgentRequest) returns (CheckAgentResponse)` and `ForwardAgent(stream BytesMessage) returns (stream BytesMessage)`. `BytesMessage` carries raw bytes in field 1. `CheckAgentRequest` carries an agent ID in field 1. `CheckAgentResponse` is empty and acts as existence/permission acknowledgement.

Control flow: the proto itself has no execution, but it drives two runtime flows: checking if an SSH id is available before mounting, and tunneling arbitrary SSH-agent protocol bytes through a bidirectional stream.

State and persistence: no stored state. The stream is session-scoped and transient.

Dependencies and integration points: compiled into `ssh.pb.go`, `ssh_grpc.pb.go`, and `ssh_vtproto.pb.go`; used by `sshforward.MountSSHSocket`, `sshforward.CheckSSHID`, and `sshprovider.socketProvider`.

Risks and test signals: schema is intentionally small. Backward compatibility depends on not renumbering existing fields or changing stream direction. Tests around `raw_provider` validate the stream can tunnel framed JSON payloads, standing in for SSH-agent byte streams.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/ssh.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/ssh_grpc.pb.go -->
## sources/cloud-native/buildkit/session/sshforward/ssh_grpc.pb.go

Purpose: generated gRPC client and server bindings for the SSH session service.

Important APIs/types/functions: `SSHClient` exposes `CheckAgent` and `ForwardAgent`. `NewSSHClient` wraps a `grpc.ClientConnInterface`. `SSHServer` requires both service methods and should embed `UnimplementedSSHServer` for forward compatibility. `RegisterSSHServer` registers the service. `_SSH_CheckAgent_Handler` and `_SSH_ForwardAgent_Handler` adapt incoming gRPC calls to the server implementation. `SSH_ServiceDesc` names the service and declares unary and stream descriptors.

Control flow: client methods invoke `cc.Invoke` or create a new stream using static method names. Server handlers decode requests or wrap stream objects, then call the implementation.

State and persistence: no persistent state; generated stubs only hold a client connection pointer.

Dependencies and integration points: consumed by `sshforward.CheckSSHID`, `sshforward.server.run`, and `sshprovider.socketProvider.Register`. Depends on gRPC-Go generics for `grpc.BidiStreamingClient[BytesMessage, BytesMessage]` and server aliases.

Risks and test signals: generated code requires gRPC-Go v1.64.0 or newer. Manual edits would be overwritten. Compatibility risk is service/method name stability because session metadata advertises method URLs. Provider tests exercise both unary and streaming generated methods through an in-memory listener.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/ssh_grpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/ssh_vtproto.pb.go -->
## sources/cloud-native/buildkit/session/sshforward/ssh_vtproto.pb.go

Purpose: generated vtprotobuf helpers for faster clone, equality, marshal, size, and unmarshal operations on SSH protobuf messages.

Important APIs/types/functions: provides `CloneVT`, `CloneMessageVT`, `EqualVT`, `EqualMessageVT`, `MarshalVT`, `MarshalToVT`, `MarshalToSizedBufferVT`, `SizeVT`, and `UnmarshalVT` for `BytesMessage`, `CheckAgentRequest`, and `CheckAgentResponse`. The unmarshal paths parse protobuf wire types, skip unknown fields, and return explicit errors for illegal tags or malformed varints.

Control flow: generated marshal methods write fields in reverse into sized buffers; unmarshal loops over field numbers and wire types, appending byte fields and strings where present. Empty response methods are mostly no-ops plus unknown-field skipping.

State and persistence: only per-message byte slices and strings are manipulated. Unknown fields are skipped rather than retained by these helpers.

Dependencies and integration points: used by protobuf/gRPC runtime or optimized call sites when vtproto methods are detected. It complements, not replaces, `ssh.pb.go`.

Risks and test signals: generated code must match `ssh.proto` field numbers exactly. The biggest operational risk is stale generation after schema edits. Functional stream coverage in `raw_provider_test.go` indirectly verifies message transmission, while vtproto-specific wire edge cases are not tested in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/ssh_vtproto.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/sshprovider/agentprovider.go -->
## sources/cloud-native/buildkit/session/sshforward/sshprovider/agentprovider.go

Purpose: builds a session attachable that exposes one or more SSH agents or private-key files to the BuildKit daemon, with optional raw socket passthrough.

Important APIs/types/functions: `AgentConfig` carries ID, paths, and `Raw`. `AgentConfig.toDialer` normalizes paths, applies SSH_AUTH_SOCK/default fallback, and enforces raw mode constraints. `NewSSHAgentProvider` validates unique IDs and returns a `socketProvider`. `toDialer` converts one socket, one Windows pipe, or multiple private key files into a `dialerFn`. `source.agentDialer` serves an `agent.Agent` over `net.Pipe`; `readOnlyAgent` blocks mutating operations against a forwarded real agent.

Control flow: configs are normalized to IDs, then each path is classified as Windows pipe, Unix socket, or private key file. Sockets are either returned raw or wrapped in a read-only SSH agent server. Key files are limited to 100 KiB reads, parsed with `ssh.ParseRawPrivateKey`, and added to an in-memory keyring. Mixing sockets and keys is rejected.

State and persistence: maintains only in-memory keyrings and socket dialer paths. It reads key files but does not persist them. Real agents are protected by a read-only wrapper for add/remove/lock/extension operations.

Dependencies and integration points: integrates with `sshforward` service, Go crypto SSH agent package, OS socket probing, and Windows pipe helpers. Build CLI parsing feeds these configs.

Risks and test signals: passphrase-protected private keys are not supported. `Uploader.Add`-style locking is not used here, but config creation is single-threaded. Raw mode deliberately exposes the socket protocol. Tests cover missing default agents, raw-mode path count, non-socket raw rejection, and Unix socket acceptance.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/sshprovider/agentprovider.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/sshprovider/agentprovider_test.go -->
## sources/cloud-native/buildkit/session/sshforward/sshprovider/agentprovider_test.go

Purpose: validates SSH agent provider config handling, especially raw mode.

Important APIs/types/functions: `TestToAgentSource` calls `build.ParseSSH` and `sshprovider.NewSSHAgentProvider` with different CLI-like strings. It creates a temp regular file and a real Unix socket to test path classification.

Control flow: the test first accepts either successful default provider creation or the expected missing SSH_AUTH_SOCK error. It then verifies `raw=true` without exactly one path fails during parsing/provider setup, raw mode with a normal file fails as not a socket, and raw mode with a Unix socket succeeds for both `default=raw=true,<sock>` and `default=<sock>,raw=true` syntaxes.

State and persistence: temp directory, file, and listener are test-scoped. The listener is closed by defer.

Dependencies and integration points: crosses CLI parsing in `cmd/buildctl/build` with provider construction in `sshprovider`.

Risks and test signals: this is Unix-socket oriented; Windows named pipe behavior is covered by platform-specific helper logic but not by this test. It is a strong signal that raw mode constraints are enforced before exposing a provider.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/sshprovider/agentprovider_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/sshprovider/agentprovider_unix.go -->
## sources/cloud-native/buildkit/session/sshforward/sshprovider/agentprovider_unix.go

Purpose: supplies non-Windows platform behavior for SSH agent fallback and pipe parsing.

Important APIs/types/functions: `getFallbackAgentPath` returns an error instructing users to set `SSH_AUTH_SOCK`. `getWindowsPipeDialer` always returns nil.

Control flow: there is no branching beyond direct returns. When `AgentConfig.toDialer` sees no path and `SSH_AUTH_SOCK` is empty, this fallback turns that into a user-facing configuration error.

State and persistence: none.

Dependencies and integration points: selected by `//go:build !windows`; complements `agentprovider_windows.go`. Used by `AgentConfig.toDialer`.

Risks and test signals: the fallback does not search common Unix agent paths, so UX depends on environment configuration. `agentprovider_test.go` accepts the exact "invalid empty ssh agent socket" path wrapping triggered by this helper.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/sshprovider/agentprovider_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/sshprovider/agentprovider_windows.go -->
## sources/cloud-native/buildkit/session/sshforward/sshprovider/agentprovider_windows.go

Purpose: implements Windows-specific SSH agent discovery and named-pipe dialing.

Important APIs/types/functions: `getFallbackAgentPath` checks `\\.\pipe\openssh-ssh-agent` using `windows.FindFirstFile` and returns it if available. `isWindowsPipePath` detects named pipe paths with slash/backslash tolerant regex. `getWindowsPipeDialer` returns a `socketDialer` using `windowsPipeDialer` when a path is a pipe. `windowsPipeDialer` calls `winio.DialPipe`.

Control flow: fallback avoids `os.Stat` because Windows named pipes do not behave like normal filesystem entries. Config path classification in `agentprovider.go` calls `getWindowsPipeDialer` before `os.Stat`, so pipe paths can bypass Unix socket/file logic.

State and persistence: no durable state. The only resource is the find handle, which is closed.

Dependencies and integration points: depends on Microsoft go-winio and x/sys/windows; selected only on Windows builds. It lets BuildKit support OpenSSH agent forwarding on Windows clients.

Risks and test signals: regex pipe detection must handle path variants; false negatives would fall through to `os.Stat`. The fallback only supports the standard OpenSSH pipe. No Windows-specific test is in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/sshprovider/agentprovider_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/sshprovider/pipe_test.go -->
## sources/cloud-native/buildkit/session/sshforward/sshprovider/pipe_test.go

Purpose: provides an in-memory `net.Listener` built on `net.Pipe` for SSH provider tests.

Important APIs/types/functions: `pipeListener` implements `net.Listener`. `Accept` initializes channels lazily, waits for dialed connections, tracks accepted conns, and returns `net.ErrClosed` after close. `Dialer(ctx)` creates a pipe pair and sends one side to `Accept`, honoring context cancellation. `Addr` returns a simple `pipeAddr`. `Close` closes the accept channel and all tracked conns.

Control flow: `Dialer` and `Accept` rendezvous over `chConn`. Close sets `closed`, closes the channel, and closes accepted connections. `Accept` also handles nil receives from a closed channel.

State and persistence: only test-scoped in-memory state: mutex, closed flag, accepted conns, channel, and unused `closedCh` field. `closedCh` is initialized and selected in `Accept` but never closed, so channel closure via `chConn` is what actually unblocks accepts.

Dependencies and integration points: used by `raw_provider_test.go` to run both the gRPC server transport and echo backend without OS sockets.

Risks and test signals: the unused `closedCh` looks stale but does not break current tests because `chConn` is closed. Since it is test-only, production risk is none.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/sshprovider/pipe_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/sshprovider/raw_provider.go -->
## sources/cloud-native/buildkit/session/sshforward/sshprovider/raw_provider.go

Purpose: implements the server side of the SSH forwarding gRPC service by mapping SSH IDs to dialers.

Important APIs/types/functions: `dialerFn` dials an agent connection. `socketProvider` holds `map[string]dialerFn`. `CheckAgent` verifies an ID exists and returns an empty response. `ForwardAgent` reads `buildkit.ssh.id` from incoming metadata, dials the selected agent, and bridges it to the gRPC stream with `sshforward.Copy`. `Register` registers the generated SSH server.

Control flow: both RPCs default empty IDs to `sshforward.DefaultID`. `ForwardAgent` validates metadata, fails fast on unknown ID, dials, defers close, then blocks until `Copy` completes.

State and persistence: provider state is the in-memory ID-to-dialer map. It does not mutate during requests.

Dependencies and integration points: registered via session `Attachable`; called by `sshforward.MountSSHSocket` client code. Relies on gRPC metadata for per-stream ID selection.

Risks and test signals: unknown IDs return a plain wrapped error, so callers rely on message text. Raw dialers may expose writable agent capabilities unless `agentprovider.go` wrapped them. `raw_provider_test.go` exercises unknown ID, check success, and bidirectional streaming.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/sshprovider/raw_provider.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/sshprovider/raw_provider_test.go -->
## sources/cloud-native/buildkit/session/sshforward/sshprovider/raw_provider_test.go

Purpose: tests the raw SSH provider transport as a generic bidirectional byte tunnel.

Important APIs/types/functions: `echoServer` accepts net connections and responds to JSON `echoRequest` messages with `echoResponse` counts. `dialerFnToGRPCDialer` adapts a provider dialer into `grpc.WithContextDialer`. `TestRawProvider` wires a `socketProvider`, gRPC server/client, and echo backend over `pipeListener`. `streamWriter` and `streamReader` adapt gRPC `BytesMessage` streams to `io.Writer`/`io.Reader`.

Control flow: the test starts echo and provider services, checks unknown and known agent IDs, opens `ForwardAgent` with metadata ID `test`, sends two small JSON messages and one 10,000 byte payload, then verifies echoed data and incrementing counts.

State and persistence: all test state is in memory. Stream reader buffers partial `BytesMessage` payloads to satisfy arbitrary `Read` sizes.

Dependencies and integration points: covers generated gRPC stubs, `socketProvider`, `sshforward.Copy`, and `pipeListener` together.

Risks and test signals: this is a strong signal for byte-stream correctness, metadata selection, and larger-than-single-small-message handling. It does not test cancellation, EOF half-close, or real SSH-agent semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/sshforward/sshprovider/raw_provider_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/testutil/testutil.go -->
## sources/cloud-native/buildkit/session/testutil/testutil.go

Purpose: provides an in-memory session dialer for tests without opening network sockets.

Important APIs/types/functions: `Handler` handles an incoming connection and metadata. `Dialer` mirrors the session dialer signature. `TestStream(handler)` returns a dialer backed by `sockPair`. `sockPair` builds two cross-connected `io.Pipe` based `net.Conn` implementations. `sock` implements `net.Conn` methods with no-op deadlines and dummy addresses.

Control flow: each call to the returned dialer launches the handler in a goroutine with `context.WithoutCancel(ctx)` and one side of the pipe, logs handler errors, closes that side, and returns the other side to the session under test.

State and persistence: transient pipe pairs only.

Dependencies and integration points: used by session tests that need to connect `Session.Run` to a fake manager/handler. Uses `bklog` for handler error logging.

Risks and test signals: deadlines are no-ops, so tests using timeout behavior may not model real net.Conn semantics. `context.WithoutCancel` intentionally keeps handler work alive past dialer context cancellation, which is useful for sessions but can hide cancellation bugs.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/testutil/testutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/upload/upload.go -->
## sources/cloud-native/buildkit/session/upload/upload.go

Purpose: client-side helper for pulling upload content from a session provider and writing it to an `io.Writer`.

Important APIs/types/functions: `New(ctx, c, url)` builds outgoing metadata from URL path and host, opens an `Upload.Pull` bidirectional stream on the session caller connection, and returns `*Upload`. `Upload.WriteTo(w)` receives `BytesMessage` chunks until EOF and writes them to `w`, returning the byte count.

Control flow: `New` derives the session context through `c.Context`, attaches metadata keys `urlpath` and `urlhost`, creates a client from `c.Conn`, and calls `Pull`. `WriteTo` loops on `RecvMsg`; EOF is successful completion, other errors are wrapped, and writer errors return with the bytes written so far.

State and persistence: `Upload` stores only the active gRPC stream. No content is buffered beyond one message.

Dependencies and integration points: pairs with `uploadprovider.Uploader` and generated upload stubs. Used when BuildKit needs client-provided HTTP-like response bodies through the session.

Risks and test signals: short writes are counted but not retried; it trusts `io.Writer` contract that non-nil error accompanies incomplete writes. The `keyHost` metadata is set but provider code in this subset only consumes path. No direct test appears in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/upload/upload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/upload/upload.pb.go -->
## sources/cloud-native/buildkit/session/upload/upload.pb.go

Purpose: generated protobuf message bindings for `upload.proto`.

Important APIs/types/functions: defines `BytesMessage` with `Data []byte` and standard generated protobuf methods/getters. The file descriptor encodes the `moby.upload.v1.Upload` service and its bidirectional streaming `Pull` method.

Control flow: generated `Reset`, `String`, reflection, descriptor, getter, and init functions delegate to protobuf runtime. There is no handwritten logic.

State and persistence: per-message protobuf runtime state, unknown fields, and size cache only.

Dependencies and integration points: consumed by `upload.go`, `uploadprovider/provider.go`, `upload_grpc.pb.go`, and vtproto helpers. Generated from `github.com/moby/buildkit/session/upload/upload.proto`.

Risks and test signals: field number `data = 1` must remain stable for wire compatibility. Generated file should not be edited manually. Behavioral coverage comes from upload provider/client paths outside this generated file.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/upload/upload.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/upload/upload.proto -->
## sources/cloud-native/buildkit/session/upload/upload.proto

Purpose: declares the BuildKit session upload streaming contract.

Important APIs/types/functions: package `moby.upload.v1`, Go package `github.com/moby/buildkit/session/upload`. Service `Upload` has a bidirectional streaming `Pull(stream BytesMessage) returns (stream BytesMessage)`. `BytesMessage` contains raw `bytes data = 1`.

Control flow: runtime users currently use the server-to-client direction to send chunks from an `io.ReadCloser` and the client receives until EOF. The bidirectional signature leaves room for request messages, but provider code in this subset ignores inbound messages and only sends data.

State and persistence: none in schema.

Dependencies and integration points: generates `upload.pb.go`, `upload_grpc.pb.go`, and `upload_vtproto.pb.go`; used by session upload helper and provider.

Risks and test signals: changing stream direction or field number would break existing clients. Since the schema is minimal, most risk sits in provider lifecycle and chunking rather than protobuf design.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/upload/upload.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/upload/upload_grpc.pb.go -->
## sources/cloud-native/buildkit/session/upload/upload_grpc.pb.go

Purpose: generated gRPC client/server bindings for the upload service.

Important APIs/types/functions: `UploadClient` exposes `Pull`; `NewUploadClient` wraps a `grpc.ClientConnInterface`; `UploadServer` requires `Pull`; `UnimplementedUploadServer` provides forward-compatible default behavior; `RegisterUploadServer` registers the service; `_Upload_Pull_Handler` adapts server streams; `Upload_ServiceDesc` declares the stream.

Control flow: client `Pull` creates a new stream with the static method name and returns a typed bidirectional stream. Server handler wraps the raw `grpc.ServerStream` and calls `srv.(UploadServer).Pull`.

State and persistence: no persistent state.

Dependencies and integration points: used by `upload.New` and `uploadprovider.Uploader.Register`. Depends on gRPC-Go v1.64.0 or newer.

Risks and test signals: generated code must stay in sync with `upload.proto`. The bidirectional type accepts client sends even if current provider ignores them; future protocol additions should preserve compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/upload/upload_grpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/upload/upload_vtproto.pb.go -->
## sources/cloud-native/buildkit/session/upload/upload_vtproto.pb.go

Purpose: generated vtprotobuf fast-path helpers for upload `BytesMessage`.

Important APIs/types/functions: implements clone, equality, marshal, sized-buffer marshal, size, and unmarshal methods for `BytesMessage`. Unmarshal parses wire type 2 for the `data` field and skips unknown fields.

Control flow: marshal allocates based on `SizeVT`, writes bytes field if present, and returns the produced slice. Unmarshal loops over protobuf wire data, appends decoded bytes to `Data`, and returns descriptive errors for invalid wire format.

State and persistence: operates only on message fields in memory.

Dependencies and integration points: complements standard protobuf generated code and may be used by optimized serializers in the session upload path.

Risks and test signals: stale generated code after proto changes is the main risk. Because upload messages are raw byte chunks, malformed length handling is important; generated unmarshal includes bounds checks. No vtproto-specific tests are in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/upload/upload_vtproto.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/upload/uploadprovider/provider.go -->
## sources/cloud-native/buildkit/session/upload/uploadprovider/provider.go

Purpose: session attachable that lets the daemon pull one-shot `io.ReadCloser` payloads registered by the client.

Important APIs/types/functions: `New` creates an `Uploader` with an id-to-reader map. `Uploader.Add(r)` generates an identity id, stores the reader, and returns an `http://buildkit-session/<id>` URL. `Register` registers the upload gRPC service. `Pull(stream)` resolves the id from incoming `urlpath` metadata, removes the reader from the map, streams it with `io.Copy`, and closes it. `writer.Write` sends data as upload `BytesMessage` chunks capped at 3 MiB.

Control flow: `Pull` reads metadata, uses `path.Base` to get id, locks the map, returns an error for missing ids, deletes the id before streaming to enforce one-shot semantics, then copies and closes.

State and persistence: in-memory map of pending readers. Intended state is transient and consumed exactly once.

Dependencies and integration points: pairs with `upload.New`. Uses BuildKit identity generation and gRPC metadata.

Risks and test signals: `Add` writes to the map without taking `mu`, while `Pull` reads/deletes with `mu`; concurrent `Add`/`Pull` would race. Since ids are removed before successful copy, failed streams cannot be retried. No direct test is in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/upload/uploadprovider/provider.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/containerd/content.go -->
## sources/cloud-native/buildkit/snapshot/containerd/content.go

Purpose: wraps a containerd content store so all operations run under a fixed namespace, while forbidding direct deletes and optionally falling back to another namespace for reads.

Important APIs/types/functions: `NewContentStore` creates `Store{ns, content.Store}`. `Namespace` and `WithNamespace` expose namespace controls. Store methods `Info`, `Update`, `Walk`, `Status`, `ListStatuses`, `Abort`, `ReaderAt`, and `Writer` inject `namespaces.WithNamespace`. `Delete` returns an error to forbid content deletion. `nsWriter.Commit` also injects namespace. `WithFallbackNS` returns `nsFallbackStore`, whose `Info`, `Walk`, and `ReaderAt` can fall back to a secondary namespace.

Control flow: normal methods wrap context then delegate. Fallback store first queries main; on containerd not-found it queries fallback. `Walk` records digests seen in main, then walks fallback and suppresses duplicates.

State and persistence: no state beyond namespace strings and underlying content store. Persistence is delegated to containerd. Delete is intentionally blocked.

Dependencies and integration points: used when BuildKit shares containerd content across namespaces. Integrates with containerd content API and errdefs.

Risks and test signals: fallback is read-only for missing content; writes always go to main. `Delete` prohibition protects BuildKit from deleting shared content but may surprise generic content-store callers. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/containerd/content.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/containerd/snapshotter.go -->
## sources/cloud-native/buildkit/snapshot/containerd/snapshotter.go

Purpose: adapts containerd snapshotters into BuildKit snapshotters while forcing all operations into a configured namespace and forbidding direct remove through the namespace wrapper.

Important APIs/types/functions: `NewSnapshotter` returns BuildKit `snapshot.Snapshotter` by wrapping `nsSnapshotter` with `snapshot.FromContainerdSnapshotter`. `NSSnapshotter` exposes the namespace wrapper as a containerd `snapshots.Snapshotter`. `nsSnapshotter` embeds `snapshots.Snapshotter` and overrides methods to inject namespace into context. `Remove` returns an error.

Control flow: each method creates a namespaced context then delegates to the embedded snapshotter. `Prepare` and `View` return containerd mounts directly. `Remove` is blocked to prevent unsafe deletion through this adapter.

State and persistence: wrapper only stores namespace and underlying snapshotter. Snapshot metadata/layers persist in containerd.

Dependencies and integration points: integrates containerd snapshotters with BuildKit's snapshot abstraction and optional identity mapping.

Risks and test signals: callers needing removal must use the intended GC/lifecycle path, not this wrapper. Namespace injection is easy to miss if methods are added to the interface later. Tests are indirect through snapshotter/merge behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/containerd/snapshotter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/diffapply_linux.go -->
## sources/cloud-native/buildkit/snapshot/diffapply_linux.go

Purpose: Linux implementation of merge snapshot diff application. It computes filesystem changes between lower/upper snapshots and applies them into a destination snapshot with metadata preservation, overlay whiteout handling, hardlink optimization, and corrected usage accounting.

Important APIs/types/functions: `mergeSnapshotter.diffApply` drives the process. `applierFor` resolves the destination root from bind/overlay/local mounts. `applier.Apply` sequences delete, hardlink, and copy paths. `applyCopy` preserves type, ownership, mode, xattrs, opaque dirs, and timestamps. `Usage` walks the apply root and avoids double-counting hardlinks, including cross-snapshot hardlinks. `differFor` mounts lower/upper views and selects overlay optimized changes or `fs.Changes`. `safeJoin` prevents unsafe path traversal. `needsUserXAttr` detects rootless overlay xattr mode via a temporary snapshot.

Control flow: for each `Diff`, committed snapshots are mounted as views and active snapshots via `Mounts`. A `differ` emits parent modifications and changes; the `applier` deletes/whiteouts old paths, links where possible, copies otherwise, defers directory mtimes, flushes mtimes after all changes, then reports usage.

State and persistence: writes directly into the destination snapshot upperdir/root. It records in-memory visited parents, inode maps, deferred mtimes, and cross-snapshot linked inodes. Persistent effects are filesystem contents and merge usage labels applied by `merge.go`.

Dependencies and integration points: tightly coupled to `mergeSnapshotter.Merge`, containerd continuity fs diffing, BuildKit overlay utilities, rootless mount options, leases, and Linux xattrs.

Risks and test signals: path safety, whiteout conversion, xattr failures, rootless overlay behavior, hardlink EXDEV/EMLINK fallback, and release ordering are critical. `snapshotter_test.go` covers merge ordering, metadata/mtime, hardlinks, capabilities, and usage across overlayfs/native variants.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/diffapply_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/diffapply_unsupported.go -->
## sources/cloud-native/buildkit/snapshot/diffapply_unsupported.go

Purpose: non-Linux fallback for merge diff application.

Important APIs/types/functions: `mergeSnapshotter.diffApply` returns an error saying diffApply is not supported on the current GOOS. `needsUserXAttr` similarly returns unsupported.

Control flow: direct error return only.

State and persistence: none.

Dependencies and integration points: selected by `//go:build !linux`; lets the package compile on unsupported platforms while preventing runtime merge behavior from silently doing the wrong thing.

Risks and test signals: callers of `Merge` on non-Linux will fail when diff application is needed. Platform-specific local mounters still exist, but merge application is Linux-only. Tests for merge are Linux build-tagged.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/diffapply_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/imagerefchecker/checker.go -->
## sources/cloud-native/buildkit/snapshot/imagerefchecker/checker.go

Purpose: provides a cache external-reference checker that reports whether a sequence of layer digests is referenced by any image in a containerd image store.

Important APIs/types/functions: `Opt` carries image and content stores. `New` returns a factory for `cache.ExternalRefChecker`. `Checker.Exists(key, blobs)` initializes once, caches answers by caller key, and checks if `layerKey(blobs)` was registered. `init` lists images and dispatches handlers over their targets. `layersHandler` reads manifests/indexes and passes manifest layers to `registerLayers`.

Control flow: first `Exists` call loads all image layer stacks. Manifest descriptors register their layer digest sequence; index descriptors return child manifests for traversal; blob read errors are ignored for missing content paths.

State and persistence: in-memory `images` set and result cache. No writes.

Dependencies and integration points: integrates containerd `images.Dispatch`, content reads, OCI descriptors, and BuildKit cache external reference checks used to avoid garbage collecting image-backed snapshots.

Risks and test signals: `layerKey` concatenates digest strings without delimiters, which is probably safe with digest syntax but not formally length-delimited. `init` silently returns on list/dispatch errors, yielding false negatives. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/imagerefchecker/checker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/localmounter.go -->
## sources/cloud-native/buildkit/snapshot/localmounter.go

Purpose: defines a small cross-platform helper abstraction for mounting BuildKit mountables or raw mount lists onto local paths.

Important APIs/types/functions: `Mounter` has `Mount` and `Unmount`. `LocalMounter(mountable, opts...)` and `LocalMounterWithMounts(mounts, opts...)` create `localMounter`. `ForceRemount` sets `forceRemount`, preventing writable bind/nullfs short-circuit behavior on platforms that support it.

Control flow: this file only constructs state. Platform files implement `Mount`/`Unmount`.

State and persistence: `localMounter` stores mounts, mountable, target path, release function, and force flag under a mutex. It persists nothing beyond temporary mount directories created by platform implementations.

Dependencies and integration points: used by snapshot differ, tests, and code needing a local filesystem view of `Mountable`.

Risks and test signals: correct release behavior depends on platform files setting `target` and `release` consistently. `ForceRemount` is important when callers need an actual mount path even for writable binds.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/localmounter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/localmounter_darwin.go -->
## sources/cloud-native/buildkit/snapshot/localmounter_darwin.go

Purpose: Darwin implementation of local mount/unmount.

Important APIs/types/functions: `(*localMounter).Mount` lazily obtains mounts from the mountable, short-circuits writable single `bind` mounts by returning the source, otherwise creates a temp dir and calls `mount.All`. `Unmount` recursively unmounts with `unix.MNT_FORCE`, removes the temp dir, and calls the mountable release.

Control flow: mutex protects idempotent mount/unmount. Existing target is reused. Writable bind shortcut avoids requiring mount privileges for simple local directories.

State and persistence: temporary directory path in `target`, release callback from mountable, and mounted filesystem state. Cleanup removes the target directory.

Dependencies and integration points: used whenever BuildKit needs to inspect a snapshot on Darwin.

Risks and test signals: `forceRemount` is not honored in the Darwin shortcut, unlike FreeBSD/Linux; callers expecting forced remount on writable binds may get source path. Errors during mount remove the temp directory. No Darwin tests in subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/localmounter_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/localmounter_freebsd.go -->
## sources/cloud-native/buildkit/snapshot/localmounter_freebsd.go

Purpose: FreeBSD implementation of local mount/unmount.

Important APIs/types/functions: `Mount` lazily gets mounts, short-circuits writable single `nullfs` mounts unless `forceRemount` is set, otherwise mounts all into a temp dir. `Unmount` calls `mount.Unmount`, removes target, and invokes release.

Control flow: guarded by mutex and idempotent on repeated `Mount`. FreeBSD differs from Linux/Darwin by using `nullfs` as the bind-like shortcut type.

State and persistence: temporary mount target and release callback. No durable state beyond mounted filesystem while active.

Dependencies and integration points: selected on FreeBSD builds for snapshot local access.

Risks and test signals: only single writable nullfs gets shortcut; other bind-like forms require mount support. Release errors are returned after unmount cleanup. No FreeBSD-specific tests in subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/localmounter_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/localmounter_linux.go -->
## sources/cloud-native/buildkit/snapshot/localmounter_linux.go

Purpose: Linux implementation of local mount/unmount with rootless mount option adjustment and file-bind support.

Important APIs/types/functions: `Mount` lazily obtains mounts, applies `rootlessmountopts.FixUp` in user namespaces, returns writable bind/rbind source unless forced, detects single bind source files, creates temp dirs/files, and calls `mount.All`. `Unmount` uses `syscall.MNT_DETACH`, removes target, and calls release.

Control flow: mutex protects state. For a single bind/rbind, non-read-only mounts avoid remounting unless `forceRemount`; read-only/file binds are mounted into a temp target. File bind creates an empty placeholder file under the temp dir before mounting.

State and persistence: temp mount target, possibly a placeholder file, mountable release callback. State is cleaned on unmount.

Dependencies and integration points: used heavily by diff apply, snapshot tests, and BuildKit filesystem access. Integrates rootless user namespace handling.

Risks and test signals: if placeholder file creation fails, the code calls `os.RemoveAll(dest)` after `dest` has been changed to `<tmp>/file`, leaving the temp directory behind. Rootless option rewriting mutates `lm.mounts`. Linux snapshot tests exercise this path indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/localmounter_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/localmounter_windows.go -->
## sources/cloud-native/buildkit/snapshot/localmounter_windows.go

Purpose: Windows implementation of local mounting for single containerd mount entries and bind emulation.

Important APIs/types/functions: `Mount` enforces exactly one mount, returns writable bind/rbind sources directly, emulates read-only binds via `bindfilter.ApplyFileBinding`, and otherwise calls `mountWithRetries`. `mountWithRetries` retries transient "file being used by another process" errors with backoff. `Unmount` removes bindfilter bindings or calls `mount.Unmount`, then removes target and release.

Control flow: mutex protects idempotence. Non-bind mounts get up to two retries for known Windows race symptoms. Unmount treats invalid parameter/not found from bindfilter as already unmounted.

State and persistence: temp directory target plus Windows bindfilter/mount state.

Dependencies and integration points: depends on go-winio bindfilter, containerd mount, and Windows error constants. Used for Windows snapshot local access.

Risks and test signals: only one mount is supported; multi-layer Windows snapshots must encode parent layers in mount options. Returning writable bind source before setting `target` means the temp directory created just before may be leaked. No Windows-specific test in subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/localmounter_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/merge.go -->
## sources/cloud-native/buildkit/snapshot/merge.go

Purpose: wraps a snapshotter with a `Merge` operation that materializes a committed snapshot from a list of diffs, using Linux diff application and storing corrected usage for hardlink-based merges.

Important APIs/types/functions: `Diff` names lower and upper snapshot keys. `MergeSnapshotter` extends `Snapshotter` with `Merge`. `NewMergeSnapshotter` configures hardlink merge, overlay base skipping, and rootless userxattr behavior. `Merge` chooses a base key, creates a temporary lease, prepares a destination snapshot, applies diffs, and commits with usage labels. `Usage` returns stored merge usage when labels exist. `withMergeUsage` and `mergeUsageOf` encode/decode size and inode labels.

Control flow: overlay-based snapshotters can skip an initial chain of diffs that already matches parent relationships and use the last upper as the merge parent. A temporary lease protects views and prepared snapshots during merge. `diffApply` returns usage, then `Commit` persists it as labels.

State and persistence: persistent state is the committed snapshot plus labels `buildkit.mergeUsageSize` and `buildkit.mergeUsageInodes`. Runtime flags choose hardlink and xattr behavior.

Dependencies and integration points: depends on leases, user namespace detection, `needsUserXAttr`, and the underlying snapshotter. Tests exercise native/overlay behavior.

Risks and test signals: userxattr detection failures disable optimizations. Commit failure after prepare may leave cleanup to snapshotter/lease GC. Usage label parse errors make `Usage` fail. `snapshotter_test.go` covers merge content, hardlinks, file capabilities, and usage.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/merge.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/snapshotter.go -->
## sources/cloud-native/buildkit/snapshot/snapshotter.go

Purpose: defines BuildKit's snapshotter abstraction and adapters to and from containerd snapshotters.

Important APIs/types/functions: `Mountable` aliases executor mountable refs. `Snapshotter` interface adds name, BuildKit `Mountable` returns, close, and identity mapping to containerd snapshot operations. `FromContainerdSnapshotter` wraps a containerd snapshotter. `fromContainerd.Mounts/View` return `staticMountable`; `Commit` preserves inherited labels from active snapshots. `NewContainerdSnapshotter` adapts back to containerd API and tracks mount release callbacks. `getRedirectDirOption` and `setRedirectDir` disable overlay `redirect_dir` when needed.

Control flow: adapter methods delegate containerd operations and translate mount lists to mountables or vice versa. `containerdSnapshotter.returnMounts` records releases and applies redirect_dir options. `release` calls all stored release functions.

State and persistence: adapter state includes snapshotter name, idmap, release callbacks, and cached redirect_dir detection. Persistent snapshot state remains in underlying snapshotter.

Dependencies and integration points: central bridge between BuildKit executor/cache and containerd snapshotters. Redirect_dir handling protects diff correctness on Linux overlay.

Risks and test signals: `containerdSnapshotter` accumulates release callbacks until global release, so callers must call the returned release function. Redirect_dir detection is Linux-specific but guarded by stat/userns checks. Tests in snapshotter merge use this adapter.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/snapshotter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/snapshotter_test.go -->
## sources/cloud-native/buildkit/snapshot/snapshotter_test.go

Purpose: Linux integration tests for merge snapshot behavior across overlayfs, native, and native without cross-snapshot hardlinks.

Important APIs/types/functions: `newSnapshotter` builds a containerd metadata DB, content store, lease manager, and merge snapshotter in a test namespace. Helpers `activeKey`, `committedKey`, `mergeKey`, `withMount`, `requireContents`, `statPath`, and capability helpers create and inspect snapshots. `TestMerge`, `TestHardlinks`, `TestMergeFileCapabilities`, and `TestUsage` cover the main behavior.

Control flow: tests create multiple committed snapshots with additions, removals, hardlinks, symlinks, renames, metadata changes, and file capabilities; merge different diff sequences; mount results; and compare full directory contents plus mtimes, link counts, capabilities, ownership, and usage.

State and persistence: all state is under `t.TempDir`, bbolt metadata DB, containerd snapshotter directories, and temporary leases. Cleanup closes DB/snapshotters.

Dependencies and integration points: exercises `merge.go`, `diffapply_linux.go`, local mounters, containerd metadata, native/overlay snapshotters, continuity fstest, and libcap.

Risks and test signals: root is required for overlayfs and capability tests. These tests are strong regression signals for merge correctness, but platform-gated to Linux and may skip parts in unprivileged environments.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/snapshotter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/staticmountable.go -->
## sources/cloud-native/buildkit/snapshot/staticmountable.go

Purpose: implements a simple immutable `Mountable` backed by a static mount slice and optional identity mapping.

Important APIs/types/functions: `staticMountable.Mount` returns a copy of mounts, applies redirect_dir option if needed, increments an atomic count, and returns a release function that decrements the count. `IdentityMapping` returns the stored idmap.

Control flow: mount calls do not perform OS mounts; they hand out mount metadata and release bookkeeping. If release count goes below zero and `BUILDKIT_DEBUG_PANIC_ON_ERROR=1`, the release function panics.

State and persistence: in-memory atomic count tracks outstanding mount references. No persistence.

Dependencies and integration points: used by `FromContainerdSnapshotter.Mounts` and `View`. Redirect_dir option shares logic with snapshotter adapter.

Risks and test signals: double release normally only decrements below zero silently unless debug panic is enabled. Returning a shallow copy of mount structs protects slice structure but options slices are still shared by value unless replaced by redirect_dir logic.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/snapshot/staticmountable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/bboltcachestorage/storage.go -->
## sources/cloud-native/buildkit/solver/bboltcachestorage/storage.go

Purpose: persistent bbolt-backed implementation of solver `CacheKeyStorage`, storing cache result records and dependency links between cache keys.

Important APIs/types/functions: `NewStore` opens bbolt with `NoSync` and creates buckets `_result`, `_links`, `_byresult`, `_backlinks`. `Exists`, `Walk`, `WalkResults`, `Load`, `AddResult`, `Release`, `WalkIDsByResult`, `AddLink`, `WalkLinks`, `HasLink`, and `WalkBacklinks` implement cache metadata operations. `releaseHelper` and `emptyBranchWithParents` recursively delete unreferenced branches. `isEmptyBucket` checks bucket emptiness.

Control flow: results are stored under cache key id and reverse indexed by result id. Links are stored as `json(CacheInfoLink) + "@" + target`, with backlinks for reverse traversal. `Release` walks all cache ids for a result, deletes result entries and reverse indexes, then prunes empty link/result buckets and parent backlinks. Walk methods collect data inside read transactions then call callbacks outside the transaction.

State and persistence: bbolt database persists cache graph metadata, not actual result blobs. `NoSync` improves speed at durability risk. Link digests are normalized in walk methods by hashing digest plus output.

Dependencies and integration points: used by `cacheManager` as durable cache metadata. Actual result storage is a separate `CacheResultStorage`.

Risks and test signals: link key encoding uses `@` separator around JSON; digest strings in JSON should not break split but malformed keys error. Recursive pruning is subtle. `storage_test.go` runs shared cache storage tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/bboltcachestorage/storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/bboltcachestorage/storage_test.go -->
## sources/cloud-native/buildkit/solver/bboltcachestorage/storage_test.go

Purpose: applies the solver shared cache storage conformance suite to the bbolt backend.

Important APIs/types/functions: `TestBoltCacheStorage` creates a temp database path, calls `NewStore`, registers cleanup to close it, and passes the store to `testutil.RunCacheStorageTests`.

Control flow: the test is mostly harness glue. All substantive scenarios come from the shared testutil suite.

State and persistence: test database lives under `t.TempDir` and is closed after the test.

Dependencies and integration points: verifies `bboltcachestorage.Store` satisfies `solver.CacheKeyStorage` behavior expected by the solver.

Risks and test signals: strength depends on `RunCacheStorageTests`; this file itself does not cover corruption, NoSync durability, or concurrent access. It is still the main regression signal for API conformance.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/bboltcachestorage/storage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/cache_test.go -->
## sources/cloud-native/buildkit/solver/cache_test.go

Purpose: unit tests for in-memory cache manager/storage behavior and cache-key graph semantics.

Important APIs/types/functions: helper constructors `depKeys`, `testCacheKey`, `testCacheKeyWithDeps`, `expKey`, `dgst`, and `testResult`. Tests include `TestInMemoryCache`, `TestInMemoryCacheSelector`, `TestInMemoryCacheSelectorNested`, `TestInMemoryCacheReleaseParent`, `TestInMemoryCacheRestoreOfflineDeletion`, and `TestCarryOverFromSublink`.

Control flow: tests save root and dependent cache keys, query by digest/input/output/selectors, load records, release backing results, and verify graph pruning or retained links. Selector tests prove that dependency selectors constrain matches and that alternate sublinks can carry cache matches forward.

State and persistence: uses in-memory cache key and result storage. Release tests mutate storage to simulate deleted results and offline restore.

Dependencies and integration points: exercises `cacheManager`, `CacheKey`, in-memory storage implementations, and dummy results.

Risks and test signals: strong coverage for query/link intersection semantics, selector matching, result release cleanup, and restoration after result storage changes. It does not test bbolt directly except through the separate conformance test.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/cachekey.go -->
## sources/cloud-native/buildkit/solver/cachekey.go

Purpose: defines solver cache keys and dependency key wrappers.

Important APIs/types/functions: `NewCacheKey(dgst, vtx, output)` creates a root cache key id from `rootKey`. `CacheKeyWithSelector` pairs an exportable cache key with an optional selector digest and has trace fields. `CacheKey` stores id, dependency key matrix, operation digest, vertex digest, output index, cache-manager-specific ids, and index ids. `TraceFields`, `Deps`, `Digest`, `Output`, and `clone` expose safe views.

Control flow: methods lock around mutable fields. `Deps` returns cloned outer/inner slices so callers cannot mutate stored deps. `clone` copies manager id mapping but intentionally does not copy deps in this file unless the caller sets them.

State and persistence: cache keys are in-memory graph nodes. Manager-specific ids connect them to persistent `CacheKeyStorage`.

Dependencies and integration points: heavily used by `cacheManager`, scheduler `edge`, exporters, and tests. Uses digest identities for cache matching.

Risks and test signals: `TraceFields` dependency reporting overwrites `"id"`/`"selector"` in a map inside the loop, so each dependency group only retains the last dependency in trace output; functional behavior is unaffected but debug detail is reduced. Tests cover key matching through manager behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/cachekey.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/cachemanager.go -->
## sources/cloud-native/buildkit/solver/cachemanager.go

Purpose: implements the main solver cache manager that maps cache keys to persisted metadata and actual result storage.

Important APIs/types/functions: `NewInMemoryCacheManager`, `NewCacheManager`, `ReleaseUnreferenced`, `Query`, `Records`, `Load`, `LoadWithParents`, `Save`, `ensurePersistentKey`, `getIDFromDeps`, and `rootKey`. `LoadedResult` carries a loaded result with its cache result and key.

Control flow: creation runs `ReleaseUnreferenced` to prune metadata for missing result blobs. `Query` intersects dependency links by input/output/digest/selector and repairs missing links across dependency alternatives. Root queries check root key existence. `Save` persists the actual result, stores result metadata, and recursively persists dependency links. `LoadWithParents` optionally asks result storage for parent results and filters them through cache key ancestry.

State and persistence: mutex protects manager operations. Metadata persists through `CacheKeyStorage`; result payloads persist through `CacheResultStorage`. Cache key ids may be deterministic root ids or generated ids based on dependency graph intersection.

Dependencies and integration points: called by scheduler edges for cache probing, loading, and saving. Emits trace logs with cache operation fields.

Risks and test signals: `filterResults` appears to check `m[id]` while iterating cache results and may be sensitive to whether result-storage parent maps are keyed by cache-key id or result id. `ReleaseUnreferenced` ignores `Release` errors. Cache tests cover common graph/link behavior and deletion recovery.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/cachemanager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/cacheopts.go -->
## sources/cloud-native/buildkit/solver/cacheopts.go

Purpose: carries cache-related runtime options through contexts and lets operations retrieve options from a state's ancestors.

Important APIs/types/functions: `CacheOpts` is `map[any]any`. `CacheOptGetterOf` fetches a getter from context. `WithCacheOptGetter` installs one. `withAncestorCacheOpts` creates a getter that walks a solver state and optionally ancestors to find requested keys from `op.cacheRes.Opts`. `walkAncestors` traverses active solver parents without revisiting digests. `ProgressControllerFromContext` retrieves a progress controller keyed by `progressKey`.

Control flow: getter builds a requested key set, walks current state first, skips errored vertexes, copies matching option values, and stops after current state unless `includeAncestors` is true. Ancestor traversal uses a stack and solver active map under read lock.

State and persistence: context values and in-memory solver state only.

Dependencies and integration points: used by solver operations that need cache result context options, especially progress propagation during cache load/export paths.

Risks and test signals: missing parents log warnings and skip that branch. Context key types are private, preventing external collisions. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/cacheopts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/cachestorage.go -->
## sources/cloud-native/buildkit/solver/cachestorage.go

Purpose: declares the interfaces and small data records separating solver cache metadata from actual result storage.

Important APIs/types/functions: `ErrNotFound` is the storage not-found sentinel. `CacheKeyStorage` defines key existence, walking, result metadata, release, forward links, and backlinks. `CacheResult` stores result id and creation time. `CacheInfoLink` describes a dependency link by input index, output index, operation digest, and selector. `CacheResultStorage` saves/loads concrete `Result`s, loads remote descriptors, and checks existence.

Control flow: none; pure contracts.

State and persistence: implementations persist metadata and result payloads separately. `CacheInfoLink` JSON tags define on-disk encoding in bbolt storage.

Dependencies and integration points: implemented by bbolt/in-memory stores and consumed by `cacheManager`. `LoadRemotes` integrates session groups and compression config for remote cache/export operations.

Risks and test signals: interface changes have broad impact. The `CacheInfoLink` JSON representation is part of persistent bbolt key encoding. Shared storage tests validate implementations.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/cachestorage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/combinedcache.go -->
## sources/cloud-native/buildkit/solver/combinedcache.go

Purpose: combines multiple cache managers, typically remote/imported caches plus a main writable cache, behind one `CacheManager` interface.

Important APIs/types/functions: `NewCombinedCacheManager`, `combinedCacheManager.ID`, `ReleaseUnreferenced`, `Query`, `Load`, `Save`, and `Records`. `ID` hashes the comma-joined child manager IDs. `Load` can promote loaded results from a non-main cache into the main cache.

Control flow: `ReleaseUnreferenced`, `Query`, and `Records` run child managers in parallel with `errgroup`. Query/record maps deduplicate by cache key or result id, preferring main manager entries. `Load` calls `LoadWithParents` on the record's owning manager, saves loaded parent/result chain into main when needed, releases all non-returned results, and returns the first loaded result.

State and persistence: no independent storage; delegates to child managers. It may persist promoted results into `main`.

Dependencies and integration points: used by solver when combining local cache with imported cache sources.

Risks and test signals: parallel goroutines use `context.TODO` for query records rather than caller cancellation in some paths. If `main` is nil, `Save` is a no-op returning nil key. No direct tests in this subset; cache tests cover underlying manager semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/combinedcache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/debug.go -->
## sources/cloud-native/buildkit/solver/debug.go

Purpose: optional scheduler debugging instrumentation for solver edge state transitions.

Important APIs/types/functions: package globals `debugScheduler` and `debugSchedulerSteps` read `BUILDKIT_SCHEDULER_DEBUG` and `BUILDKIT_SCHEDULER_DEBUG_STEPS`. `debugSchedulerCheckEdge` selects edges to log. The remaining `debugScheduler*` helpers log merge decisions, pre/post unpark state, pipe creation, incoming finish/update, cache upgrades, dependency requests, and inconsistent graph state.

Control flow: most helpers are no-ops unless `e.debug` is true or a serious error occurs. `debugSchedulerPreUnparkSlow` emits detailed fields for edge, deps, incoming requests, update pipes, states, cache keys, and slow/preprocess availability.

State and persistence: debug configuration is process environment state read at init/lazily. Output goes to BuildKit logging, not persistent solver state.

Dependencies and integration points: used throughout `edge.go` and edge merging logic elsewhere. Uses `go-csvvalue` for comma-separated debug step parsing and `bklog`.

Risks and test signals: `debugSchedulerCheckEdge` appears to compute `name` from `steps[0]` inside the loop and then checks `strings.Contains(name, v)`, which may not match the intended current vertex name; debug filtering could be inaccurate. No tests in subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/edge.go -->
## sources/cloud-native/buildkit/solver/edge.go

Purpose: core scheduler state machine for one solver edge, coordinating dependency requests, cache-map loading, cache probing/loading, operation execution, result release, and incoming pipe responses.

Important APIs/types/functions: `edgeStatusType` states initial/cache-fast/cache-slow/complete. `edge`, `dep`, `edgeState`, and `edgeRequest` hold mutable scheduling state. Key methods include `unpark`, `processUpdates`, `recalcCurrentState`, `processCacheMapReq`, `processDepReq`, `processDepSlowCacheReq`, `respondToIncoming`, `createInputRequests`, `desiredStateDep`, `execIfPossible`, `loadCache`, and `execOp`.

Control flow: `unpark` processes completed async updates, responds to incoming requests when possible, starts cache-map loading, starts cache load or execution if desired complete and data is ready, or requests dependency states. Dependencies advance through fast cache keys, slow result-based cache, and complete results. Cache records short-circuit execution; failed cache loads remove loaded records and retry other paths. Executions save cache keys/results and return `CachedResult`.

State and persistence: in-memory edge state tracks cache maps, keys, records, dependency pipe receivers, loaded records, errors, result, owner/release counts, and debug flag. Persistence happens only through `op.Cache().Save` and cache manager calls.

Dependencies and integration points: integrates `activeOp`, `CacheManager`, `pipe` scheduler primitives, `CacheMap` dependency selectors/slow funcs, and result/exporter types.

Risks and test signals: this is concurrency-sensitive. Risks include stale state causing open incoming pipes, subtle cache phase decisions, result release races, and fallback forced solves. Debug hooks exist for diagnosis. Cache tests cover manager semantics, but edge scheduling itself needs broader solver integration tests outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/edge.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/compatibility.go -->
## sources/cloud-native/buildkit/solver/errdefs/compatibility.go

Purpose: typed error support for unsupported BuildKit compatibility-version features.

Important APIs/types/functions: init registers `CompatibilityFeature` with `typeurl`. `UnsupportedCompatibilityFeatureError` embeds the proto and wrapped error. `Error` formats `unsupported compatibility-version <version> feature <feature>` plus wrapped error text. `Unwrap` returns the cause. `ToProto` exposes the typed error payload. `NewUnsupportedCompatibilityFeatureError` constructs a standalone error. `CompatibilityFeature.WrapError` wraps an existing error with proto metadata.

Control flow: direct construction and formatting only.

State and persistence: type registration is global process state. Error proto can be serialized through BuildKit gRPC error utilities.

Dependencies and integration points: integrates with `grpcerrors.TypedErrorProto` and containerd typeurl for typed error propagation.

Risks and test signals: message formatting is part of user-facing diagnostics. Type URL string stability matters for remote clients. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/compatibility.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/context.go -->
## sources/cloud-native/buildkit/solver/errdefs/context.go

Purpose: normalizes cancellation detection across Go context errors, gRPC status codes, and known stream EOF/canceled string cases.

Important APIs/types/functions: `IsCanceled(ctx, err)` returns true when `err` is `context.Canceled`, gRPC code is `Canceled`, or the context cause is canceled and the error string contains `EOF` or the cancellation text.

Control flow: checks strong typed conditions first, then handles a known gRPC/containerd behavior where a canceled stream followed by `Recv` may produce EOF or untyped concatenated strings.

State and persistence: none.

Dependencies and integration points: uses BuildKit `grpcerrors.Code` and gRPC `codes.Canceled`. Helps solver callers decide whether an error should be treated as cancellation rather than failure.

Risks and test signals: string matching can produce false positives if an unrelated error contains EOF after context cancellation, but the context-cause guard narrows it. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/context.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/errdefs.pb.go -->
## sources/cloud-native/buildkit/solver/errdefs/errdefs.pb.go

Purpose: generated protobuf bindings for solver typed error metadata.

Important APIs/types/functions: defines message structs and getters for `Vertex`, `Source`, `Frontend`, `FrontendCap`, `CompatibilityFeature`, `Subrequest`, `Solve`, `FileAction`, `ContentCache`, `ProvenanceMaterialsIncomplete`, and `ProvenanceMaterialIncomplete`. `Solve` includes a oneof subject (`File` or `Cache`) and description map. Init builds a protobuf file descriptor and oneof wrappers.

Control flow: generated methods reset, reflect, stringify, compress descriptors, and expose field getters. No handwritten logic.

State and persistence: per-message protobuf runtime state plus unknown fields/size cache. Serialized forms carry error context across gRPC/typeurl boundaries.

Dependencies and integration points: generated from `errdefs.proto`, importing solver `pb` operation/source/range messages. Used by typed error wrappers in this package and BuildKit gRPC error serialization.

Risks and test signals: field numbers are compatibility-critical because they may cross process/version boundaries. Manual edits should be avoided. Tests in neighboring errdefs files cover some typed error round trips, but not all generated messages in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/errdefs.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/errdefs.proto -->
## sources/cloud-native/buildkit/solver/errdefs/errdefs.proto

Purpose: schema for typed solver errors and metadata attached to BuildKit gRPC errors.

Important APIs/types/functions: messages identify failing vertices, sources with ranges, frontends, frontend capabilities, compatibility features, subrequests, solve context, file actions, content cache entries, and incomplete provenance materials. `Solve` carries input IDs, mount IDs, the failing `pb.Op`, a oneof subject for file/cache, and description map.

Control flow: schema only; runtime wrappers in neighboring files attach these messages to errors and gRPC utilities serialize them.

State and persistence: serialized proto payloads can persist in error responses/logs, not as solver state.

Dependencies and integration points: imports `github.com/moby/buildkit/solver/pb/ops.proto`; generates `errdefs.pb.go` and vtproto variants. Used throughout solver/frontend error handling to preserve machine-readable context.

Risks and test signals: compatibility depends on stable field numbers and oneof membership. Adding fields is safe; renaming/removing/renumbering is not. Neighbor tests cover selected typed error propagation such as provenance.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/errdefs.proto -->
