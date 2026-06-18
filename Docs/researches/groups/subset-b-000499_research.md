<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/entry.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/msg/entry.go

Purpose: defines BeeGFS entry/metadata BeeMsg payloads and wire serializers for directory creation, file unlink, directory listing, owner lookup, entry info, stripe pattern manipulation, file state changes, refresh, and lookup intent. It is a protocol-bound file: field order, integer widths, C-string alignment, and message IDs must match BeeGFS C++/kernel expectations.

Important APIs/types/functions: request/response structs implement `MsgId`, `Serialize`, or `Deserialize` for message IDs 2001/2002, 2007/2008, 2029/2030, 2035/2036, 2045/2046, 2047/2048, 2053/2054, 2123/2124, 2131/2132, 2055/2056, and 2059/2060. Shared protocol types include `EntryInfo`, `EntryInfoWithDepth`, `Path`, `StripePattern`, `PathInfo`, and `RemoteStorageTarget`. `SetDirPatternRequest.SetUID/GetUID` hides the UID field so the feature flag cannot be forgotten.

Control flow: serializers write primitive fields through `beeserde`, nested structs serialize themselves, and some messages set serializer feature flags while writing optional data. Deserializers read the same order and fail through `Deserializer.Fail` on unsupported states such as RAID10 patterns, missing pool IDs, unsupported RST versions, or non-basic lookup-intent response flags. `GetEntryInfoResponse` composes `StripePattern`, `PathInfo`, `RemoteStorageTarget`, session counts, and file state.

State and persistence: no local persistence; all state is transient wire payload state. `EntryInfo` includes `structs.HostLayout` and is also consumed by ioctl code, so its layout is a cross-package ABI surface. `StripePattern.Serialize` backfills its own length after writing the pattern body. `RemoteStorageTarget.Serialize` mutates private version fields when RST intent is present, including the important distinction between nil and empty `RSTIDs`.

Dependencies and integration points: depends on `common/beegfs` enums and `beeserde`; integrates with `util.AssembleBeeMsg`, `NodeStore` RPCs, and ioctl `GetEntryInfoV2` which manually assembles the same `GetEntryInfoResponse` shape. Comments explicitly note incomplete support for file events, buddy mirror secondary flags, RAID10, non-basic lookup intents, and some mkdir/unlink optional fields.

Risks: exact wire order is fragile; C layout coupling makes field reordering dangerous. `ListDirFromOffsetResponse` checks sequence lengths with `typesLen != entryIDsLen && entryIDsLen != namesLen`, which only fails when both comparisons are true and may miss a mismatch between types and IDs if IDs and names match. Unsupported legacy patterns/RST versions intentionally fail. Optional feature flag behavior must stay synchronized with header backfill in `AssembleBeeMsg`.

Test signals: `entry_test.go` round-trips representative RAID0/BuddyMirror stripe patterns and uses reflection to guard `RemoteStorageTarget` field count/order/kinds, but most individual messages rely on integration tests or protocol compatibility rather than direct unit coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/entry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/entry_test.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/msg/entry_test.go

Purpose: unit tests for the most layout-sensitive helpers in `entry.go`.

Important APIs/types/functions: `TestStripePatternSerialize` builds two `StripePattern` values, serializes them through `beeserde`, deserializes, and checks equality. `TestRemoteStorageTargetSerialize` uses reflection to assert that `RemoteStorageTarget` still has six fields with expected kinds.

Control flow: each stripe-pattern test uses `NewSerializer`, calls `Serialize`, finishes, then feeds bytes to `NewDeserializer` and checks the deserialized object. The RST test inspects struct metadata rather than serialized bytes.

State and persistence: no persistence; tests cover in-memory wire buffers and Go type shape.

Dependencies and integration points: depends on `testify/assert`, `beegfs` stripe pattern constants, and `beeserde`. It acts as a guard for protocol compatibility with `entry.go` and ioctl assembly of `GetEntryInfoResponse`.

Risks: the tests cover only two happy-path patterns and do not exercise no-pool, RAID10, unknown pattern, lookup-intent, list-dir mismatch, or RST version failure paths. There is a likely copy-paste issue where the second pattern checks `s1.Finish()` instead of `s2.Finish()`.

Test signals: positive signal for stripe round-tripping and RST layout awareness, but limited breadth for the many message structs in `entry.go`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/entry_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/event.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/msg/event.go

Purpose: serializes a BeeWatch/protobuf file event payload into BeeMsg wire form.

Important APIs/types/functions: `FileEvent` contains protobuf event `Type`, path bytes, and optional target bytes. `Serialize` writes the event type, C-string path, and a boolean `targetValid` followed by target C-string when `Target != nil`.

Control flow: serialization rejects negative protobuf enum values before writing because BeeMsg expects an unsigned value. Target serialization is conditional on nil, not length, so an empty non-nil target still means target-present.

State and persistence: no persistence; event data is carried in a single serialized message body.

Dependencies and integration points: depends on `beeserde` and `github.com/thinkparq/protobuf/go/beewatch`. This is likely embedded in larger event-carrying messages, while `entry.go` comments show some file-event support is not implemented for certain entry messages.

Risks: there is no deserializer or direct tests here. The signed-to-unsigned enum assumption depends on protobuf event definitions staying non-negative.

Test signals: no direct test file in this subset; behavior is simple but protocol-facing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/event.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/header.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/msg/header.go

Purpose: defines the fixed 40-byte BeeMsg header and helpers for recognizing and patching serialized headers.

Important APIs/types/functions: `HeaderLen`, `MsgPrefix`, `Header`, `NewHeader`, `Serialize`, `Deserialize`, `IsSerializedHeader`, `ExtractMsgLen`, `OverwriteMsgLen`, and `OverwriteMsgFeatureFlags`.

Control flow: `NewHeader` pre-populates the message ID and prefix while using sentinel values for length and feature flags. `Serialize` and `Deserialize` write/read fields in the exact wire order. The overwrite helpers validate length and prefix before patching little-endian bytes in-place.

State and persistence: no persistence; state is a byte-level header prefix at the beginning of each BeeMsg. `MsgLen` includes header and body, and `MsgFeatureFlags` is finalized after body serialization.

Dependencies and integration points: used by `util.AssembleBeeMsg`, `ReadFrom`, `RequestUDP`, and tests. Depends on `encoding/binary` for direct little-endian patching and `beeserde` for structured serialization.

Risks: `IsSerializedHeader` only checks buffer length and prefix, not message length sanity or message ID validity. Any header layout change breaks transport and every message. Little-endian offsets are hard-coded but align with the serialized field order.

Test signals: `header_test.go` validates round-trip serialization and overwrite behavior for length and feature flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/header.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/header_test.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/msg/header_test.go

Purpose: unit tests for header serialization and in-place header mutation helpers.

Important APIs/types/functions: `TestHeaderSerialization`, `TestOverwriteMsgLen`, and `TestOverwriteMsgFeatureFlags`.

Control flow: the serialization test writes a header through `beeserde`, deserializes it, and compares all fields. Overwrite tests first assert failures for short or prefixless buffers, then install `MsgPrefix` and verify little-endian field updates.

State and persistence: in-memory byte slices only.

Dependencies and integration points: depends on `encoding/binary`, `testify/assert`, and `beeserde`. It protects `util.AssembleBeeMsg` because that function relies on the overwrite helpers after body serialization.

Risks: tests do not cover `ExtractMsgLen`, invalid message IDs, or malformed but correctly prefixed headers with impossible lengths.

Test signals: good coverage for the core happy path and validation gates of header overwrites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/header_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/msg.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/msg/msg.go

Purpose: declares the minimal interfaces that identify BeeGFS messages and connect them to the shared serializer/deserializer contracts.

Important APIs/types/functions: `Msg` requires `MsgId() uint16`; `SerializableMsg` embeds `Msg` and `beeserde.Serializable`; `DeserializableMsg` embeds `Msg` and `beeserde.Deserializable`.

Control flow: no executable flow; these interfaces are compile-time contracts consumed by transport helpers.

State and persistence: none.

Dependencies and integration points: ties `common/beemsg/msg` payloads to `common/beemsg/beeserde`. `util.AssembleBeeMsg`, `DisassembleBeeMsg`, `WriteTo`, `ReadFrom`, `RequestTCP`, `RequestUDP`, and `NodeStore` all depend on these interfaces.

Risks: all protocol correctness is delegated to implementing structs. A wrong `MsgId` compiles but causes runtime mismatch errors or server-side misinterpretation.

Test signals: indirectly exercised by all message, assembly, I/O, and communication tests that use `testMsg` or real message structs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/msg.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/resync.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/msg/resync.go

Purpose: BeeMsg request/response definitions for storage and metadata buddy resync status.

Important APIs/types/functions: `GetStorageResyncStats`, `GetStorageResyncStatsResp`, `GetMetaResyncStats`, `GetMetaResyncStatsResp`, `BuddyResyncJobState`, and `BuddyResyncJobState.String`.

Control flow: request serializers write target IDs. Response deserializers read state, timestamps, counters, and error/session/modification metrics in fixed order. `String` maps known enum values to user-facing status strings.

State and persistence: no local state; response structs snapshot remote resync state from BeeGFS nodes.

Dependencies and integration points: depends on `beeserde`; used by management code that sends message IDs 2093/2117 and expects 2094/2118 responses via `NodeStore`/transport utilities.

Risks: counter ordering must match server definitions. `String` returns `<unspecified>` for unknown values rather than surfacing raw code. There are no sanity checks on timestamp or counter consistency.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/resync.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/stats.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/msg/stats.go

Purpose: BeeMsg definitions for high-resolution server stats, client stats v1/v2, and dummy metadata/storage requests used to detect client-stats version support.

Important APIs/types/functions: `GetHighResStats`, `GetHighResStatsResp`, `HighResolutionStats`, `GetClientStats`, `GetClientStatsResp`, `Uint128`, `GetClientStatsV2`, `GetClientStatsV2Resp`, `RequestMetaData`, `RequestMetaDataRespDummy`, `RequestStorageData`, and `RequestStorageDataRespDummy`.

Control flow: request serializers write last-stat times, cookies, or `Uint128` low/high halves. `PerUser` sets message feature flag 1. Response deserializers read sequences; dummy deserializers only inspect feature flag 1 and reset the buffer so unprocessed response content is ignored.

State and persistence: no persistence; stats structs are remote snapshots. `UseClientStatsV2` is inferred from response header feature flags rather than body fields.

Dependencies and integration points: depends on `beeserde` sequence helpers and header feature-flag propagation from `DisassembleBeeMsg`. These messages integrate with management/monitoring paths selecting stats protocol versions.

Risks: dummy response types intentionally discard bodies, so they only remain valid while the caller truly needs feature flags only. `Uint128` field ordering differs from serialized order in comments/code: serializer writes Low then High and deserializer reads Low then High.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/storagebench.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/msg/storagebench.go

Purpose: BeeMsg definitions to start/query/control BeeGFS storage benchmark operations.

Important APIs/types/functions: `StorageBenchControlMsg` serializes action, type, block size, file size, thread count, O_DIRECT flag, and target IDs. `StorageBenchControlMsgResp` deserializes status, action, type, error code, target IDs, and per-target result values.

Control flow: request serialization writes fixed scalar fields followed by a total-size sequence of target IDs. Response deserialization mirrors fixed fields followed by two sequences.

State and persistence: no local persistence; it controls and reads benchmark state on storage targets.

Dependencies and integration points: depends on `common/beegfs` storage benchmark enums and `beeserde`; transported through the generic BeeMsg utilities.

Risks: there is no check that `TargetIDs` and `TargetResults` have the same length. Enum validity is not checked locally.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/storagebench.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/nodestore.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/nodestore.go

Purpose: thread-safe in-memory registry of BeeGFS nodes, aliases, legacy IDs, root metadata identity, buddy group metadata, and reusable TCP connections.

Important APIs/types/functions: `NodeStore`, `NewNodeStore`, `Cleanup`, `AddNode`, `SetMetaRootNode`, `GetMetaRootNode`, `SetMetaRootBuddyGroup`, `GetMetaRootBuddyGroup`, `HasMetaRootBuddyGroup`, `GetNode`, `GetNodes`, `RequestTCP`, `RequestUDP`, `getNodeAndConns`, and `resolveEntityId`.

Control flow: `AddNode` rejects duplicate UID, alias, legacy node ID, and connection-store entries before creating a `util.NodeConns`. Public getters resolve `beegfs.EntityId` by type under an RW mutex and return clones. TCP/UDP request methods resolve the node and connection pool under lock, release the lock, then perform network I/O.

State and persistence: all state is process-local maps and connection queues. `Cleanup` closes pooled TCP sockets. Root metadata and buddy group getters return clones to avoid caller mutation.

Dependencies and integration points: depends on `common/beegfs`, message interfaces, and `beemsg/util` connection helpers. It is the main integration layer between node metadata discovery and BeeMsg transport.

Risks: `Cleanup` iterates `connsByUid` without taking the store lock; callers must coordinate shutdown. `SetMetaRootBuddyGroup` assigns `nil` for UID 0 but then immediately assigns `&rootMirror`, so UID 0 does not clear as intended. `resolveEntityId` accepts raw `Uid` without checking node type. `GetNodes` order is map-random.

Test signals: `nodestore_test.go` covers add/get, duplicate rejection, entity ID resolution, node list length, and root metadata node validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/nodestore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/nodestore_test.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/nodestore_test.go

Purpose: unit tests for `NodeStore` registration, lookup, and root metadata behavior.

Important APIs/types/functions: `TestAddAndGet`, `TestGetNodes`, and `TestMetaRootNode`.

Control flow: tests build a store, add metadata and storage nodes with overlapping numeric IDs but different node types, verify duplicate UID/alias/legacy ID rejection, resolve by legacy ID and alias, and check root metadata assignment rejects missing or non-meta nodes.

State and persistence: exercises in-memory store maps and connection store setup; no network I/O is performed.

Dependencies and integration points: depends on `testify/assert`, `beegfs` node identity types, and `NewNodeStore`.

Risks: does not cover `RequestTCP`, `RequestUDP`, buddy-group setters/getters, cleanup locking, clone isolation, or concurrent map access.

Test signals: good basic identity mapping coverage; transport and concurrency behavior are left to utility tests or integration usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/nodestore_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/assemble.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/util/assemble.go

Purpose: converts BeeMsg structs to/from complete on-the-wire messages containing a serialized header and body.

Important APIs/types/functions: `AssembleBeeMsg` and `DisassembleBeeMsg`.

Control flow: assembly writes a placeholder header, serializes the body, obtains the final buffer from the serializer, then overwrites header message length and feature flags. Disassembly verifies the output target is a pointer, deserializes the header, checks header message ID against `out.MsgId()`, then deserializes the body with header feature flags.

State and persistence: no persistence; transient byte buffers only. Serializer `MsgFeatureFlags` is the bridge from body serialization to header patching.

Dependencies and integration points: depends on `beeserde` and `msg` header helpers. It is called by `WriteTo`, `RequestUDP`, and all TCP/UDP transport paths.

Risks: disassembly assumes callers already split header/body and that buffers contain exactly one message. It does not compare header `MsgLen` to provided body length; length enforcement comes from callers and `beeserde.Finish`.

Test signals: `assemble_test.go` validates round-trip assembly/disassembly and rejects extra/truncated body data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/assemble.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/assemble_test.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/util/assemble_test.go

Purpose: unit test for full BeeMsg assembly and disassembly.

Important APIs/types/functions: `TestAssembleBeeMsg` uses the package-local `testMsg` from `io_test.go`.

Control flow: creates a message with fields and feature flags, assembles it, verifies header detection, disassembles into a new value, then mutates the buffer by appending or truncating data and expects disassembly errors.

State and persistence: in-memory byte buffers only.

Dependencies and integration points: depends on `msg.IsSerializedHeader` and the shared `testMsg` serializer/deserializer. It validates feature-flag propagation through header backfill and body deserialization.

Risks: no coverage for wrong message ID, non-pointer target, header corruption, or body serialization failures.

Test signals: useful transport-level smoke test for exact-buffer handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/assemble_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/auth.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/util/auth.go

Purpose: derives the 64-bit BeeMsg authentication secret from arbitrary input bytes.

Important APIs/types/functions: `GenerateAuthSecret` hashes input with SHA-256 and returns the first eight hash bytes interpreted as little-endian `uint64`.

Control flow: single-pass hash and byte conversion.

State and persistence: no state; deterministic pure function.

Dependencies and integration points: depends on `crypto/sha256` and `encoding/binary`. `ConnectTCP` uses an already-derived secret to send `AuthenticateChannel`; this helper likely feeds configuration parsing or secret setup elsewhere.

Risks: compatibility depends on matching other BeeGFS implementations' little-endian truncation. No salt/stretching is performed; this is protocol derivation, not password storage.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/auth.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/comm.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/util/comm.go

Purpose: low-level UDP request and TCP connection establishment helpers for BeeMsg communication.

Important APIs/types/functions: `MaxDatagramSize`, `RequestUDP`, `recvResponse`, `ConnectTCP`, and `connectLoop`.

Control flow: UDP opens an ephemeral socket, assembles the request once, sends it to every resolvable address, fails only if all sends fail, then optionally reads one response and disassembles it based on header `MsgLen`. TCP starts `connectLoop` in a goroutine, tries addresses in order with per-attempt timeout, returns the first successful connection or accumulated errors, and optionally authenticates by writing `AuthenticateChannel`.

State and persistence: no persistence. TCP connections returned here are later pooled by `NodeConns`; UDP sockets are per-request.

Dependencies and integration points: depends on `net`, contexts, `msg`, `types.MultiError`, and `AssembleBeeMsg`/`DisassembleBeeMsg`/`WriteTo`. Used directly by `NodeStore.RequestUDP` and indirectly by `NodeConns.RequestTCP`.

Risks: UDP response goroutine can remain blocked until socket close when context cancels; defer close eventually unblocks it. UDP accepts the first datagram without checking sender. `RequestUDP` with an empty address slice returns an all-sends-failed error via equality with zero errors/zero addrs. TCP timeout is per address while context is global.

Test signals: `comm_test.go` covers successful TCP connect with/without auth, TCP request reuse through `NodeConns`, UDP echo, and cancellation for TCP/UDP requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/comm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/comm_test.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/util/comm_test.go

Purpose: socket-level tests for TCP connection/authentication, pooled TCP requests, UDP requests, and cancellation.

Important APIs/types/functions: `TestConnect`, `TestRequestTCP`, `TestRequestTCPCancel`, `TestRequestUDP`, and `TestRequestUDPCancel`.

Control flow: tests create local TCP/UDP listeners, run server goroutines that accept/read/write BeeMsgs, then call client helpers with invalid and valid addresses. Cancellation tests cancel contexts before long operations and require prompt error return.

State and persistence: in-memory sockets and `NodeConns` queues only.

Dependencies and integration points: depends on local network stack, `testify/assert`, `msg.AuthenticateChannel`, `ReadFrom`, `WriteTo`, and `NodeConns`.

Risks: tests use goroutines with timeouts and can be sensitive to scheduling. They do not verify UDP sender validation, multiple-address duplicate responses, authentication failure behavior, or pooled connection cleanup.

Test signals: strong basic transport signal for local loopback behavior and context cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/comm_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/errors.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/util/errors.go

Purpose: central error sentinels for BeeMsg read/write transport failures.

Important APIs/types/functions: `ErrBeeMsgWrite` and `ErrBeeMsgRead`.

Control flow: no flow; `io.go` wraps blocking I/O errors with these sentinels and `NodeConns` uses `errors.Is(err, ErrBeeMsgWrite)` to decide whether retrying another connection is safe.

State and persistence: none.

Dependencies and integration points: depends only on `errors`; integrated into transport retry semantics.

Risks: correct wrapping matters. Serialization errors in `WriteTo` intentionally do not wrap `ErrBeeMsgWrite`, so retry logic can distinguish local encoding bugs from broken sockets.

Test signals: `io_test.go` asserts write sentinel behavior and non-wrapping for serialization/deserialization errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/io.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/util/io.go

Purpose: context-aware read/write helpers for complete BeeMsg frames over stream-like `io.Reader`/`io.Writer` objects.

Important APIs/types/functions: `goWithContext`, `WriteTo`, `ReadFrom`, and `WriteRead`.

Control flow: `goWithContext` runs a blocking function in a goroutine and returns either its error or context cancellation. `WriteTo` assembles a BeeMsg and writes all bytes through `bytes.Buffer.WriteTo`. `ReadFrom` reads exactly the header, extracts total message length, reads the body, and disassembles it. `WriteRead` writes a request and conditionally reads a response.

State and persistence: no persistence; transient buffers. Blocking goroutines are not forcibly stopped when context cancels; they may continue until the underlying I/O returns.

Dependencies and integration points: depends on `AssembleBeeMsg`, header length extraction, and error sentinels. Used by TCP connection authentication and request/response flow.

Risks: `ReadFrom` computes `make([]byte, msgLen-HeaderLen)` with unsigned arithmetic; a malicious header with `MsgLen < HeaderLen` can underflow to a very large allocation. Context cancellation does not close the underlying reader/writer. Short writes from `WriteTo` are not explicitly checked beyond returned error.

Test signals: `io_test.go` covers round-trip, serialization/deserialization error wrapping, cancellation, and timeout against a blocking read/write stub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/io.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/io_test.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/util/io_test.go

Purpose: tests BeeMsg stream I/O helpers and provides `testMsg` used by other utility tests.

Important APIs/types/functions: `testMsg`, `serdeFail`, `TestReadWrite`, `TestGoWithContext`, `blockingReadWriter`, `TestWriteTimeout`, and `TestReadTimeout`.

Control flow: `testMsg` serializes a uint32, C-string bytes, and feature flags; tests round-trip through `WriteTo`/`ReadFrom`, toggle `serdeFail` to force serializer/deserializer failures, and cancel contexts to verify sentinel wrapping. Timeout tests use a read/write stub that sleeps.

State and persistence: in-memory buffers only. `serdeFail` is a package-level mutable test switch, so tests should not be parallelized without isolation.

Dependencies and integration points: depends on `beeserde`, `testify/assert`, and utility read/write functions. `testMsg` is reused by `assemble_test.go` and `comm_test.go`.

Risks: global `serdeFail` can leak between tests if a failing test aborts early. Tests do not cover invalid header lengths or malicious allocation behavior.

Test signals: good coverage for normal stream framing, context returns, and error classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/io_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/nodeconns.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/util/nodeconns.go

Purpose: connection-pool wrapper for reusable BeeMsg TCP connections to one node.

Important APIs/types/functions: `NodeConns`, `NewNodeConns`, `TryGet`, `Put`, `CleanUp`, and `RequestTCP`.

Control flow: `RequestTCP` drains queued connections until one successfully completes `WriteRead`; write-related transport failures close the connection and retry, while non-write errors abort. If no pooled connection works, it opens a new TCP connection, performs the request, and puts the connection back on success.

State and persistence: maintains an in-memory thread-safe FIFO queue of `net.Conn`. `CleanUp` empties and closes all currently queued connections; checked-out connections are caller-owned until returned or closed.

Dependencies and integration points: depends on `queue`, `ConnectTCP`, `WriteRead`, message interfaces, and `ErrBeeMsgWrite`. Used by `NodeStore.RequestTCP`.

Risks: there is no connection limit despite comments noting infinite connection creation. Read-side protocol errors do not retry another connection. Connections can become stale while queued and are only detected on next use.

Test signals: `comm_test.go` verifies that two requests reuse the same accepted TCP connection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/nodeconns.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/queue.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/util/queue.go

Purpose: minimal thread-safe FIFO queue for arbitrary values.

Important APIs/types/functions: unexported `queue` with `tryGet` and `put`.

Control flow: `tryGet` locks, returns nil for empty, otherwise removes the first slice element. `put` locks and appends to the end.

State and persistence: in-memory slice protected by a mutex.

Dependencies and integration points: used by `NodeConns` to pool `net.Conn` values.

Risks: `nil` cannot be stored as a meaningful value because nil is also the empty sentinel. Popping from the front retains the underlying array until the queue is discarded, which can retain references under high churn.

Test signals: `queue_test.go` verifies FIFO order and empty behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/queue.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/queue_test.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/util/queue_test.go

Purpose: unit test for the internal FIFO queue.

Important APIs/types/functions: `TestQueuePutGet`.

Control flow: checks empty pop returns nil, pushes three values, and pops them in insertion order before returning nil again.

State and persistence: in-memory queue only.

Dependencies and integration points: depends on `testify/assert`; protects `NodeConns` queue ordering indirectly.

Risks: no concurrent access test and no test for nil values.

Test signals: basic FIFO behavior is covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/queue_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/configmgr/manager.go -->
# sources/distributed-fs/beegfs-go/common/configmgr/manager.go

Purpose: generic configuration manager that merges pflags, environment variables, optional TOML config files, validates application config, and pushes dynamic updates to listeners on SIGHUP.

Important APIs/types/functions: flags `FlagConfigFile`, `FlagVersion`, `FlagDumpConfig`; interfaces `Configurable` and `Listener`; type `ConfigManager`; functions/methods `New`, `AddListener`, `UpdateListeners`, `Get`, `Manage`, and `updateConfiguration`.

Control flow: `New` initializes the manager and performs an initial update, then subscribes to SIGHUP. `Manage` loops, refreshing configuration at startup and after each update signal until context cancellation. `updateConfiguration` constructs a fresh Viper, binds pflags, scans environment variables with the configured prefix, optionally reads/merges a TOML config file, removes manager-only keys, unmarshals exactly into a new `Configurable`, validates it, enforces `UpdateAllowed` after initial config, swaps `currentConfig`, and updates listeners.

State and persistence: state is in-memory current config, listener list, update signal channel, initial-config flag, and decode hooks. It intentionally does not persist config through Viper.

Dependencies and integration points: depends on `pflag`, `viper`, `mapstructure`, `zap`, and `types.MultiError`. Integrates with application configs implementing `Configurable` and components implementing `Listener`.

Risks: `AddListener` is not synchronized with `UpdateListeners`. Listener failures after `currentConfig` swap cannot roll back. Environment binding maps prefix-stripped names to lower-case dotted/kebab keys, so naming conventions are part of the API. `WithPKBase`-style bug is not here, but strict `UnmarshalExact` means manager-only keys must be deleted or config is rejected.

Test signals: no tests in this subset; behavior likely covered by downstream application tests if any.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/configmgr/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/common.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/common.go

Purpose: shared helpers for ranged file reads/writes and checksums used by filesystem providers.

Important APIs/types/functions: `writeSeekCloser`, `limitedFileWriter`, `newLimitedFileWriter`, `Write`, `Close`, `readFilePart`, and `getFilePartChecksumSHA256`.

Control flow: the limited writer seeks to `offsetStart` on the first write, tracks bytes written, rejects writes that exceed inclusive `[offsetStart, offsetStop]`, delegates accepted writes, and closes exactly once. `readFilePart` seeks then reads a fixed-size buffer. The checksum helper returns base64-encoded SHA-256.

State and persistence: `limitedFileWriter` mutates an underlying file and tracks closed/written state in memory. Reads load the requested file part into memory.

Dependencies and integration points: used by `BeeGFS.ReadFilePart`, `BeeGFS.WriteFilePart`, and mock equivalents. Depends on standard `io`, `os`, `sha256`, and `base64`.

Risks: `readFilePart` uses `file.Read(buf)` once rather than `io.ReadFull`, so short reads can silently return partially filled buffers without an error. Offset validation is absent; negative or inverted ranges can cause seek/read/allocation errors. `ErrNoSpaceForWrite` message includes a trailing space from `errors.go`.

Test signals: `fs_test.go` validates writing multiple fixed ranges and reading/checksumming the full file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/doc.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/doc.go

Purpose: package documentation for the filesystem abstraction.

Important APIs/types/functions: no executable APIs; documents `filesystem.Provider`, `New`/mount initialization pattern, and optional singleton-style usage by applications.

Control flow: none.

State and persistence: none.

Dependencies and integration points: explains how applications initialize BeeGFS or mock providers and references logger behavior in example text.

Risks: documentation mentions a `New()` function and `MountPoint` global, while this subset shows `NewFromMountPoint`/`NewFromPath`; doc drift should be checked against the rest of the package.

Test signals: no tests; documentation only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/errors.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/errors.go

Purpose: sentinel errors for filesystem provider operations.

Important APIs/types/functions: `ErrNoSpaceForWrite`, `ErrUnmounted`, `ErrInitFSClient`, and `ErrUnsupportedFileSystem`.

Control flow: no flow; other package files wrap or return these errors.

State and persistence: none.

Dependencies and integration points: used by `limitedFileWriter`, `UnmountedFS`, `NewFromMountPoint`, and `NewFromPath`.

Risks: `ErrNoSpaceForWrite` includes a trailing space in its string, which can affect exact-message tests or UI output. Callers should use `errors.Is`.

Test signals: indirectly exercised by filesystem tests; no dedicated sentinel test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/filter.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/filter.go

Purpose: implements a user-facing file filter DSL that compiles to an `expr` program over filesystem stat metadata.

Important APIs/types/functions: `FileInfo`, `FileInfoFilter`, `CompileFilter`, `preprocessDSL`, `setFileType`, `normalizeOctal`, `StatToFileInfo`, `ago`, `parseExtendedDuration`, `parseBytes`, `globMatch`, `regexMatch`, `ApplyFilter`, and `ApplyFilterByStatT`.

Control flow: `CompileFilter` preprocesses DSL text by normalizing octal mode/permission literals, expanding `type == ...` into bitmask expressions, rewriting age comparisons into `ago(...)`, wrapping size units in `bytes(...)`, and mapping lower-case identifiers to exported `FileInfo` fields. It compiles with helper functions, then returns a runtime filter that enforces boolean results. `ApplyFilter` obtains `Lstat`, converts `syscall.Stat_t`, and evaluates the filter.

State and persistence: no persistence; compiled expression objects are captured by returned closures. `now`/`ago` use current wall time at evaluation.

Dependencies and integration points: depends on `expr-lang/expr`, regex/path helpers, and provider `Lstat`. Integrated into `StreamPathsLexicographically` to filter walked paths.

Risks: regex preprocessing is complex and order-sensitive. `sizeRe` includes `=` but not `==`, so unit handling around equality depends on `expr` syntax after rewrite. `parseExtendedDuration` indexes the last byte without guarding empty strings, though regex normally prevents empty duration. `ApplyFilter` is Linux-specific due to `syscall.Stat_t`.

Test signals: `filter_test.go` covers valid expressions, type expressions, invalid type syntax, invalid expressions, time/size units, and preprocessing rewrites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/filter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/filter_test.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/filter_test.go

Purpose: unit tests for the filesystem filter DSL.

Important APIs/types/functions: `TestCompileFilter_ValidExpressions`, `TestCompileFilter_TypeExpressions`, `TestCompileFilter_InvalidTypeExpressions`, `TestCompileFilter_InvalidExpression`, `TestCompileFilter_TimeAndSizeUnits`, and `TestPreprocessDSL_Rewrites`.

Control flow: tests compile DSL expressions, run them against synthetic `FileInfo` values, and compare booleans. Type tests vary raw mode bits. Rewrite tests inspect preprocessed output substrings.

State and persistence: no persistence; time-based tests use `time.Now()` and relative timestamps.

Dependencies and integration points: depends on `testify/assert/require`; validates filter behavior used by path streaming.

Risks: time tests can be sensitive near exact thresholds, though chosen offsets are broad. Tests do not cover `ApplyFilter` with real `syscall.Stat_t`, empty strings in helper parsers, or all invalid unit combinations.

Test signals: broad signal for DSL correctness and regression protection around octal/type/time/size rewrites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/filter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/flags.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/flags.go

Purpose: exposes the CLI/config flag name for file filtering.

Important APIs/types/functions: `FilterExprFlag = "filter-files"`.

Control flow: none.

State and persistence: none.

Dependencies and integration points: consumed by command/config packages that expose the filter DSL from `filter.go`.

Risks: changing the constant is a user-facing flag compatibility break.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/flags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/fs.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/fs.go

Purpose: defines the filesystem provider interface and the real BeeGFS provider implementation for path normalization, file creation, ranged I/O, directory walking, metadata copying, atomic overwrite, and symlink reading.

Important APIs/types/functions: `Provider`, `NewFromMountPoint`, `NewFromPath`, `BeeGFS`, `GetMountPath`, `GetRelativePathWithinMount`, `Stat`, `Lstat`, `CreatePreallocatedFile`, `CreateWriteClose`, `Remove`, `Open`, `ReadFilePart`, `WriteFilePart`, `CreateDir`, `WalkDir`, `CopyXAttrsToFile`, `CopyContentsToFile`, `CopyOwnerAndMode`, `CopyTimestamps`, `OverwriteFile`, and `Readlink`.

Control flow: provider detection uses `statfs` magic for exact mount paths or walks parents comparing device IDs to find a mount point. BeeGFS methods join the mount point with in-mount paths and delegate to OS/unix syscalls. Xattr copy lists names, dynamically sizes the value buffer, and copies each value. Metadata copy uses chown/chmod and timestamp syscalls. `WalkDir` dispatches to normal or lexicographic walking based on options.

State and persistence: operations mutate the mounted filesystem. Preallocation uses truncate because BeeGFS lacks fallocate support, creating sparse files. Copy/overwrite methods affect content, xattrs, ownership, mode, and timestamps on disk.

Dependencies and integration points: depends on `golang.org/x/sys/unix`, standard filesystem/syscall packages, `common.go` ranged I/O helpers, and `walk.go` traversal. Other packages use `Provider` to abstract real, mock, and unmounted filesystems.

Risks: `GetRelativePathWithinMount` trims `MountPoint` as a string prefix, so `/mnt/beegfs2` with mount `/mnt/beegfs` can be misclassified. `CopyXAttrsToFile` allocates only 255 bytes for the full xattr name list, but Linux listxattr size can exceed that. Symlink detection in `CopyTimestamps` uses `linuxStat.Mode&syscall.DT_LNK`, which mixes file mode bits and dirent type constants. Sparse preallocation does not reserve storage.

Test signals: `fs_test.go` covers sparse file creation and ranged write/read/checksum on a temp directory using `BeeGFS{MountPoint: temp}`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/fs_test.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/fs_test.go

Purpose: filesystem-provider tests that do not require an actual BeeGFS mount.

Important APIs/types/functions: `tempPathForTesting`, `TestBeeGFSCreatePreallocatedFile`, and `TestBeeGFSWriteAndReadFileParts`.

Control flow: tests create temp directories under `/tmp`, instantiate `BeeGFS` with that path as `MountPoint`, create a sparse file, write fixed byte ranges through `WriteFilePart`, then read/checksum the full content.

State and persistence: creates and deletes temporary files/directories on local disk.

Dependencies and integration points: depends on `testify` and `BeeGFS` methods from `fs.go`/`common.go`.

Risks: tests do not exercise BeeGFS mount detection, xattrs, ownership/mode/timestamp copying, overwrite, walk behavior, or error paths for range overflow.

Test signals: useful coverage for the ranged I/O helpers and basic file creation semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/fs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/mock.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/mock.go

Purpose: in-memory/mock implementation of `Provider` for tests that need basic file operations without a mounted BeeGFS filesystem.

Important APIs/types/functions: `NewMockFS`, `MockFS`, and implementations for mount path, relative path, stat, create/write/read/remove/open/ranged I/O. Many advanced provider methods return `"not implemented"`.

Control flow: uses `afero.NewMemMapFs`; implemented methods delegate to Afero and shared ranged I/O helpers. `Lstat`, directory creation/walking, metadata copy, overwrite, and readlink are placeholders.

State and persistence: stores files in an in-memory Afero filesystem. No durable persistence.

Dependencies and integration points: depends on `github.com/spf13/afero` and the `Provider` interface. Useful for callers that only need simple file reads/writes in tests.

Risks: incomplete `Provider` implementation can fail when tests use newer filesystem features. `CreatePreallocatedFile` ignores `overwrite` semantics and uses `Create`, so behavior differs from real BeeGFS. `Lstat` is not implemented, which prevents filter/walk flows using this mock.

Test signals: indirectly used by external tests if any; no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/mock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/unmounted.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/unmounted.go

Purpose: `Provider` implementation for workflows where a BeeGFS mount may be optional, but most filesystem operations should fail explicitly.

Important APIs/types/functions: `UnmountedFS` implements all `Provider` methods. `GetMountPath` returns empty, `GetRelativePathWithinMount` normalizes paths, and all real operations return `ErrUnmounted`.

Control flow: no branching beyond path normalization; each unsupported operation returns the sentinel.

State and persistence: no state and no filesystem mutation.

Dependencies and integration points: used by callers that decide a missing mount is acceptable for a subset of behavior. It is never returned by `NewFromPath`/`NewFromMountPoint` automatically.

Risks: path normalization simply prefixes `/` and may not match BeeGFS provider edge cases. Callers must explicitly handle `ErrUnmounted` or they will fail at operation time.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/unmounted.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/utils.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/utils.go

Purpose: user-facing file type formatting helper.

Important APIs/types/functions: `FileTypeToString`.

Control flow: checks directory and regular file first, then mode type bits for symlink, pipe, socket, device/char device, irregular, and unknown fallback.

State and persistence: none.

Dependencies and integration points: depends on `os.FileMode`; useful for CLI/reporting code that should not expose Go's compact file-mode type strings directly.

Risks: ordering matters for device/char-device interpretation. Unknown types return `fmt.Sprintf` with raw mode type.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/walk.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/walk.go

Purpose: lexicographic filesystem walking and resumable path streaming that matches BadgerDB key ordering, including glob support and optional filtering.

Important APIs/types/functions: `WalkOptions`, `WalkOption`, `Lexicographically`, `WalkDirLexicographically`, `walkDirLexicographically`, `StreamPathResult`, `StreamPathsLexicographically`, `StreamPathsLexicographicallyWithDirs`, `streamPathsLexicographically`, `readDir`, `IsGlobPattern`, and `StripGlobPattern`.

Control flow: lexicographic walking recursively reads directories sorted by a custom name that appends `/` to directory names. Streaming normalizes `pattern` and `startAfter`, detects globs, expands glob directory patterns with `/**`, handles single-file patterns directly, finds a non-glob root, then launches a goroutine that walks sorted directories. It emits paths until `maxPaths` is reached, at which point it sends a resume token. Filtering is applied with `ApplyFilter`; directories may be emitted when `includeDirs` is true but are traversed even when not emitted.

State and persistence: no persistence; uses channel output and local `maxPaths` countdown. Reads filesystem directory contents and stat metadata.

Dependencies and integration points: depends on `doublestar` for glob matching, provider `Lstat/GetMountPath`, and filter helpers. `fs.go` uses `WalkDirLexicographically` when provider walk options request it. `walk_test.go` verifies ordering against `kvstore.MapStore`/Badger ordering.

Risks: walking runs in a goroutine; consumers must drain or cancel to avoid blocked sends. `maxPaths` is mutated inside the goroutine. Glob root discovery walks upward until an existing path but could behave unexpectedly for patterns rooted at missing trees. `readDir` filtering depends on string ordering with directory slash suffixes.

Test signals: `walk_test.go` covers custom walk order, Badger order comparison, glob patterns, resume behavior, max-path resume tokens, and deeply nested matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/walk.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/walk_test.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/walk_test.go

Purpose: tests lexicographic walking and resumable/glob path streaming.

Important APIs/types/functions: `TestWalkDirLexicographically` and `TestWalkSortedPathFileAndDirectory`.

Control flow: the first test creates a temp tree and a Badger-backed `MapStore` with matching keys, walks the tree, and compares walk order with expected order and Badger iterator order. The second builds a broader file set, then table-tests directory walks, glob patterns, single-file handling, resume tokens, max-path limits, and deep `**` behavior.

State and persistence: uses temporary directories and a temporary Badger database.

Dependencies and integration points: depends on `badger`, `kvstore`, `BeeGFS` provider, and `testify`. It explicitly validates the filesystem walker against the key order expected by `kvstore.MapStore`.

Risks: the test sorts expected paths with `slices.Sort` for streaming cases, which can hide ordering expectations if custom order differs from standard sort for directories. It does not cover filters, context cancellation, directory emission mode, or readDir error paths.

Test signals: strong coverage for common path streaming and resume/glob combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/walk_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/api.go -->
# sources/distributed-fs/beegfs-go/common/ioctl/api.go

Purpose: idiomatic Go API over BeeGFS client ioctls for config file lookup, entry info, stripe-hint file creation, node ping, file state update, and enhanced entry info.

Important APIs/types/functions: `GetConfigFile`, `TrimEntryInfoNullBytes`, `GetEntryInfo`, `CreateFileWithStripeHints`, `PingNode`, `SetFileState`, and `GetEntryInfoV2`.

Control flow: functions open mount/directories/files, build ABI structs from `beegfs.go`, invoke `syscall.Syscall(SYS_IOCTL, ...)`, convert errno to Go errors, and translate raw fields into `beegfs`/`msg` types. `GetEntryInfoV2` chooses parent directory plus filename for non-directories, trims null bytes, handles partial metadata RPC results, validates RST version, and assembles `msg.GetEntryInfoResponse`.

State and persistence: mutates BeeGFS for file creation and file state changes. Other calls read kernel/client state. No Go-level persistence.

Dependencies and integration points: depends on `common/beegfs`, `common/beemsg/msg`, unsafe pointer syscall rules, and ABI structs/constants from `beegfs.go`. It bridges ioctl entry info to BeeMsg RPC-compatible structures.

Risks: feature flag bit checks use expressions like `arg.FeatureFlags&1>>0 == 1`; operator precedence should be audited for intended bit tests. `GetConfigFile` opens mount but does not close the file descriptor. Unsafe pointer lifetimes require `runtime.KeepAlive` in some functions but not all paths. `GetEntryInfoV2` slices arrays by kernel-provided counts without explicit bounds checks beyond fixed field types.

Test signals: `api_test.go` is build-tagged `beegfs` and covers these APIs against a real mounted BeeGFS filesystem.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/api_test.go -->
# sources/distributed-fs/beegfs-go/common/ioctl/api_test.go

Purpose: BeeGFS integration tests for ioctl API functions.

Important APIs/types/functions: build tag `beegfs`, constants for expected client config and mount point, `getTempBeeGFSPathForTesting`, `TestBeeGFSGetConfigFile`, `TestGetEntryInfo`, `TestCreateFileStripeHints`, and `TestSetAccessAndState`.

Control flow: tests create temporary directories under `/mnt/beegfs`, call ioctl APIs, and assert expected config path, entry types, non-invalid stripe pattern types, successful stripe-hint creation, and file state setting.

State and persistence: creates and deletes real BeeGFS files/directories; requires `/mnt/beegfs` and `/etc/beegfs/beegfs-client.conf`.

Dependencies and integration points: depends on build environment with BeeGFS mounted, `testify`, `beegfs` types, and API functions from `api.go`.

Risks: not run by default without `-tags beegfs`; environment constants are hard-coded. Tests do not assert detailed entry info fields because IDs vary by filesystem.

Test signals: valuable integration signal when the required BeeGFS test mount exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/api_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/beegfs.go -->
# sources/distributed-fs/beegfs-go/common/ioctl/beegfs.go

Purpose: Go translation of BeeGFS UAPI ioctl constants, command numbers, command encodings, and ABI argument structures.

Important APIs/types/functions: constants for buffer sizes and ioctl numbers, `beegfsIOCTypeID`, command variables `iocGetCfgFile`, `iocCreateFileV3`, `iocMkFileStripeHints`, `iocGetEntryInfo`, `iocPingNode`, `iocSetFileState`, `iocGetEntryInfoV2`, and unexported ABI structs such as `getCfgFileArg`, `mkFileV3Arg`, `makeFileStripeHintsArg`, `getEntryInfoArg`, `pingNodeArg`, `setFileStateArg`, and `getEntryInfoV2Arg`.

Control flow: no runtime flow beyond command variable initialization using `_ior`, `_iow`, and `_iowr` with `unsafe.Sizeof`.

State and persistence: no state, but struct layout defines the memory state exchanged with the kernel BeeGFS client.

Dependencies and integration points: depends on `structs.HostLayout` and `unsafe`; consumed by `api.go` and `createfile.go`. Must match BeeGFS client headers exactly.

Risks: any field order/type/size change can corrupt ioctl calls. Comments note architecture-sensitive ioctl bit sizes and pointer-to-uintptr concerns. `mkFileV3Arg.PrefTargetsLen` expects raw byte length; callers must provide exactly what the kernel expects.

Test signals: build-tagged ioctl integration tests exercise selected structs indirectly; no compile-time size assertions are present in this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/beegfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/createfile.go -->
# sources/distributed-fs/beegfs-go/common/ioctl/createfile.go

Purpose: user-friendly wrapper for BeeGFS `CreateFileV3` ioctl with functional options for file type, symlink target, permissions, ownership, preferred targets, and storage pool.

Important APIs/types/functions: `createFileConfig`, `FileType`, constants `S_REGULAR` and `S_SYMBOLIC`, option functions `SetType`, `SetSymlinkTo`, `SetPermissions`, `SetUID`, `SetGID`, `SetPreferredTargets`, `SetStoragePool`, and `CreateFile`.

Control flow: `CreateFile` initializes defaults, applies options, infers regular vs symlink type, rejects inconsistent symlink type, opens the parent directory, gets parent entry info through ioctl, builds null-terminated byte slices, conditionally builds symlink pointer, invokes `iocCreateFileV3`, and keeps slices alive until syscall returns.

State and persistence: creates a new BeeGFS file or symlink and may set mode, uid/gid, preferred targets, and storage pool depending on privileges/server setup.

Dependencies and integration points: depends on ABI `mkFileV3Arg`, `GetEntryInfo`, and unsafe syscall behavior. `SetPreferredTargets` appends a terminating zero required by the kernel API.

Risks: `PrefTargetsLen` is set to `len(cfg.preferredTargets) * 8` even though targets are `uint16`; this should be verified against the C ABI. `SetPreferredTargets` appends to the caller-provided slice and may mutate/reuse backing storage. Parent entry info from `GetEntryInfo` is untrimmed because ioctls need fixed arrays.

Test signals: `createfile_test.go` is build-tagged and verifies regular file and symlink creation/mode on a real BeeGFS mount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/createfile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/createfile_test.go -->
# sources/distributed-fs/beegfs-go/common/ioctl/createfile_test.go

Purpose: BeeGFS integration test for `CreateFile`.

Important APIs/types/functions: build tag `beegfs`; `TestCreateFile`.

Control flow: temporarily sets umask to zero, creates a temp BeeGFS directory, calls `CreateFile` for a regular file and a symlink, then checks permissions and file type via `os.Stat`/`os.Lstat`.

State and persistence: creates real BeeGFS entries and removes them through the shared cleanup helper.

Dependencies and integration points: depends on the test mount constants/helper from `api_test.go`, `testify`, and actual BeeGFS ioctl support.

Risks: does not test UID/GID, preferred targets, storage pool, buddy-mirrored parent detection, or error cases. Requires root or environment capabilities for some untested options.

Test signals: good integration coverage for default regular files and symlink option behavior when run with `-tags beegfs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/createfile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/doc.go -->
# sources/distributed-fs/beegfs-go/common/ioctl/doc.go

Purpose: package documentation for BeeGFS ioctl helpers.

Important APIs/types/functions: no executable code; documents that syscall errors can be vague and that rebuilding the client module with `BEEGFS_DEBUG=1` can aid troubleshooting.

Control flow: none.

State and persistence: none.

Dependencies and integration points: contextualizes `api.go`/`createfile.go` error behavior.

Risks: documentation only; must stay aligned with actual package capabilities.

Test signals: no tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/ioctl.go -->
# sources/distributed-fs/beegfs-go/common/ioctl/ioctl.go

Purpose: Go equivalents of Linux `_IOC`, `_IOR`, `_IOW`, and `_IOWR` macros used to construct ioctl command numbers.

Important APIs/types/functions: constants for bit widths, masks/shifts, direction bits, and functions `_ioc`, `_ior`, `_iow`, `_iowr`.

Control flow: command constructors combine direction, type, number, and size using shifts and bitwise OR.

State and persistence: none; command values are pure calculations.

Dependencies and integration points: used by `beegfs.go` to initialize BeeGFS ioctl command variables.

Risks: bit widths and direction constants are architecture-sensitive as comments note. A mismatch yields ioctl numbers the kernel will reject or misinterpret.

Test signals: no direct tests; integration ioctl tests indirectly verify command numbers on the target architecture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/ioctl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/utils.go -->
# sources/distributed-fs/beegfs-go/common/ioctl/utils.go

Purpose: helper for converting fixed-size C string buffers to Go string lengths.

Important APIs/types/functions: `cStringLen`.

Control flow: scans a byte slice until the first null byte and returns that index; if none exists, returns the full length.

State and persistence: none.

Dependencies and integration points: used by `GetConfigFile` to trim the kernel-filled config path buffer.

Risks: no UTF-8 validation or trimming beyond the first null, which is appropriate for C paths.

Test signals: indirectly exercised by `api_test.go` when BeeGFS integration tests run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/ioctl/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/kvstore/errors.go -->
# sources/distributed-fs/beegfs-go/common/kvstore/errors.go

Purpose: sentinel errors for Badger-backed map store operations and locking failures.

Important APIs/types/functions: `ErrEntryAlreadyExistsInDB`, `ErrEntryNotInDB`, `ErrEntryLockAlreadyExists`, `ErrEntryAlreadyDeleted`, `ErrEntryLockAlreadyReleased`, and `ErrEntryIllegalKey`.

Control flow: no flow; `mapstore.go` returns/wraps these errors and tests can use `errors.Is`.

State and persistence: none.

Dependencies and integration points: depends on the unexported `reservedKeyPrefix` constant from `mapstore.go`, so error text changes with that reserved prefix.

Risks: exact messages are less stable than sentinels. `ErrEntryIllegalKey` is constructed from a package constant, so moving constants can affect initialization.

Test signals: mapstore tests outside this work item likely cover these sentinels; this subset includes only the error definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/kvstore/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/kvstore/mapstore.go -->
# sources/distributed-fs/beegfs-go/common/kvstore/mapstore.go

Purpose: generic, BadgerDB-backed, thread-safe key/value store with per-entry locks, optional auto-generated ordered primary keys, lexicographic iteration, delete/update commit options, and background value-log garbage collection.

Important APIs/types/functions: `EntryLock`, `badgerEntry[T]`, `BadgerItem[T]`, `MapStore[T]`, options `WithPKBandwidth`, `WithPKWidth`, `WithPKBase`, constructor `NewMapStore`, entry APIs `GenerateNextPK`, `CreateAndLockEntry`, `GetAndLockEntry`, `GetEntry`, `DeleteEntry`, `GetEntries`, commit options `WithDeleteEntry`, `WithUpdateOnly`, `WithHoldLockOnFailure`, and garbage-collection types/functions `badgerGarbageCollection`, `NewBadgerGarbageCollection`, GC option setters, `StartRunner`, `runner`, `attemptGarbageCollection`, `runGarbageCollection`, `getSleepInterval`, and `systemLoad.isSystemLoadHigh`.

Control flow: `NewMapStore` opens Badger, creates a reserved sequence, starts GC, and returns a close function that releases the sequence and closes DB. Entry creation/get obtains a per-key `EntryLock`, loads or initializes a gob-encoded `badgerEntry`, and returns a commit closure. Commit closures update, delete, optionally keep the lock for further updates, or hold the lock on failure. `GetEntries` creates a read transaction/iterator, seeks by prefix/start key, skips reserved internal keys, optionally stops at `stopKey`, decodes values, advances after each item, and provides cleanup. GC runs in a single goroutine, sleeps with jitter, defers when normalized load is high, forces after a threshold, and loops `RunValueLogGC` until no rewrite or load rises.

State and persistence: persistent state is Badger key/value data plus Badger's internal reserved sequence key. Values are gob-encoded `badgerEntry[T]`. In-memory state includes the `entryLocks` map, sequence object, config, and GC runner context/channel.

Dependencies and integration points: depends on `badger/v4`, `encoding/gob`, `types.MultiError`, `/proc/loadavg`, `runtime.NumCPU`, and `testify/mock` for test mocks in the production file. `filesystem/walk_test.go` uses `MapStore` to compare Badger lexicographic ordering with filesystem walking.

Risks: `WithPKBase` assigns `cfg.pkSeqWidth = base` instead of `cfg.pkSeqBase`, likely a bug. `WithValue` type asserts `cfg.value.(T)` and panics on wrong type. `DeleteEntry` may call `deleteEntry` with a nil lock if `getEntryLock` returns an unexpected error other than `ErrEntryAlreadyDeleted`. `GetEntries` cleanup can be called multiple times even after automatic cleanup; Badger iterator/txn double-close behavior should be verified. GC option `WithSystemLoadThreshold` replaces `systemLoad` without preserving `readFile`, but production default still uses `os.ReadFile`.

Test signals: mapstore tests are not in this item, but `mapstore.go` includes mock GC/load types and a testing constructor, and other files in the repository reference extensive tests/benchmarks. This subset directly sees integration through `filesystem/walk_test.go`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/kvstore/mapstore.go -->
