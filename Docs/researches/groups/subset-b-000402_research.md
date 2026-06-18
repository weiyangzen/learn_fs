# Research: subset-b-000402

Grouped research for Longhorn Engine data connections, REST/socket/tgt frontends, identity metadata interceptors, replica disk-chain/backup/hash/RPC logic, and selected sync backup/list tests.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/dataconn/server.go -->
# sources/control-plane/longhorn-engine/pkg/dataconn/server.go

Purpose: implements the server side of Longhorn's lightweight data connection protocol. It bridges a `net.Conn` carrying `dataconn.Message` records to a `types.DataProcessor` that supplies `ReadAt`, `WriteAt`, `UnmapAt`, and `PingResponse`.

Important APIs/types/functions: `Server` owns a `Wire`, a buffered `responses` channel, a `done` signal channel, and the backend processor. `NewServer` prepares the wire and channels. `Handle` starts the writer goroutine and runs the read loop. `readFromWire` decodes one request and launches a handler goroutine by message type. `handleRead`, `handleWrite`, `handleUnmap`, and `handlePing` invoke the backend. `pushResponse` normalizes backend results into `TypeResponse`, `TypeEOF`, `TypeENOSPC`, or `TypeError`. `write` serializes responses and attempts a best-effort `TypeClose` on stop.

Control flow: `Handle` returns when `read` returns an error or sees `done`. Each read operation is dispatched asynchronously, so multiple backend operations can be in flight and responses can be reordered only by channel scheduling, not by explicit sequencing. `pushResponse` mutates the request message into a response and queues it. The writer goroutine does not exit after receiving `done`; the code intentionally keeps accepting late responses from in-flight handlers after sending a close notification.

State and persistence: no durable state. Runtime state is the response queue and the done channel. Data mutations are delegated to the provided `DataProcessor`, usually a replica server or socket frontend wrapper.

Dependencies and integration points: depends on `Wire` in `wire.go`, message constants in `types.go`, `types.DataProcessor`, and `types.ErrNoSpaceLeftOnDevice`. It is used by the Unix socket frontend and replica data server over TCP or Unix sockets.

Risks: one goroutine is spawned per wire read plus one per operation; sustained high request rates can create many goroutines. `write` never returns on stop, so connection lifetime relies on outer connection close/process shutdown. Unknown message types are silently ignored but still produce `nil` from `readFromWire`, which can leave callers waiting. The shared `done` channel is used both to stop reads and signal from `Handle` defer, making ordering subtle.

Test signals: no direct tests in this file. Behavior is indirectly covered through frontend/replica data paths and dataconn client/server integration if present elsewhere.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/dataconn/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/dataconn/types.go -->
# sources/control-plane/longhorn-engine/pkg/dataconn/types.go

Purpose: defines the in-memory message model and numeric command/status constants for the Longhorn data connection protocol.

Important APIs/types/functions: message types include `TypeRead`, `TypeWrite`, `TypeResponse`, `TypeError`, `TypeEOF`, `TypeClose`, `TypePing`, `TypeUnmap`, and `TypeENOSPC`. `MagicVersion` is `0x1b01` and is checked by `Wire.Read`. `Message` carries `Complete`, protocol header fields, payload `Data`, a private `transportErr`, and `journal.OpID` for sparse-tools operation tracking.

Control flow: this file has no executable control flow. The constants drive dispatch in `server.go`, client-side request handling, and wire serialization.

State and persistence: no persistence. `Message` is a transient request/response envelope. `Seq` and `ID` provide correlation/tracing state while the connection is live.

Dependencies and integration points: imports `github.com/longhorn/sparse-tools/stats` for operation IDs. `Wire` serializes a subset of `Message` fields; `Complete`, `transportErr`, and `ID` are local-only.

Risks: `messageSize` is marked unused and can drift from the actual header size computed in `wire.go`. Numeric message constants are untyped and not range-checked by `Wire.Read`, so callers must validate semantics. Adding fields to `Message` does not change the wire format unless `getRequestHeaderSize` and read/write code are also updated.

Test signals: no direct tests. The constants are compile-time inputs to dataconn client/server behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/dataconn/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/dataconn/wire.go -->
# sources/control-plane/longhorn-engine/pkg/dataconn/wire.go

Purpose: serializes and deserializes `Message` headers and payloads over a `net.Conn` using fixed little-endian fields plus a variable-length data payload.

Important APIs/types/functions: `Wire` wraps a connection, buffered writer/reader, and reusable header buffers. `NewWire` sizes buffers using package constants. `Write` emits `MagicVersion`, `Seq`, `Type`, `Offset`, `Size`, and payload length, then writes payload bytes and flushes. `Read` uses `io.ReadFull` for the header and payload, validates `MagicVersion`, allocates payload memory when length is nonzero, and converts mid-payload EOF into `io.ErrUnexpectedEOF`. `Close` closes the underlying connection. `getRequestHeaderSize` computes the fixed header size from Go field sizes plus a uint32 payload length.

Control flow: every read is all-or-error for the header. A clean EOF before any header byte propagates as `io.EOF`; partial header reads are wrapped. Payload allocation is based solely on the length field, then read fully.

State and persistence: no durable state. Header byte slices are reused per `Wire`, so concurrent calls to `Read` or concurrent calls to `Write` on the same `Wire` would race.

Dependencies and integration points: used by dataconn client/server and therefore by replica data server and socket frontend. It depends on `encoding/binary`, `bufio`, and `unsafe.Sizeof` for field widths.

Risks: there is no maximum payload length check before allocation, so a malformed peer can request large memory. The `Size` field and payload length can disagree; consumers decide what that means. Offset is serialized as uint64 then cast to int64, so negative offsets round-trip by two's-complement behavior but are not semantically validated here. The reusable buffers mean callers must serialize access externally.

Test signals: no direct tests. The robust distinction between clean EOF and unexpected payload EOF is a useful behavior to cover in dataconn tests.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/dataconn/wire.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/frontend/rest/frontend.go -->
# sources/control-plane/longhorn-engine/pkg/frontend/rest/frontend.go

Purpose: implements the optional REST frontend for a Longhorn engine device, exposing backend read/write actions over an HTTP API on localhost.

Important APIs/types/functions: `Device` stores name, size, sector size, `isUp`, and backend `types.ReaderWriterUnmapperAt`. It implements the frontend interface through `FrontendName`, `Init`, `Startup`, `Shutdown`, `State`, `Endpoint`, `Upgrade`, and `Expand`. `start` builds a `Server`, `mux.Router`, Rancher/gorilla handlers, and starts `http.ListenAndServe` on `localhost:9414` in a goroutine.

Control flow: `Startup` assigns the backend then starts the listener and marks the device up. `Shutdown` only flips `isUp` through `stop`; it does not stop the HTTP server. `Endpoint` returns the fixed localhost URL only when `isUp` is true.

State and persistence: no durable state. Runtime state is the backend pointer and `isUp`. HTTP server lifetime is process-wide once started.

Dependencies and integration points: integrates with `rest/server.go`, `rest/router.go`, `types.Frontend`, gorilla handlers, and Rancher API helpers. The endpoint is a debugging/control surface rather than the main iSCSI path.

Risks: fixed port `9414` prevents multiple REST frontends in one process/host namespace. There is no server shutdown or listener handle, so repeated start/stop can leave a listener running. The API is bound to localhost and has no authentication; if exposed through host networking/proxies it allows raw volume reads and writes. Upgrade and expand are unsupported.

Test signals: no direct tests. REST behavior would need HTTP integration tests because shutdown and port collision behavior are not exercised here.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/frontend/rest/frontend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/frontend/rest/model.go -->
# sources/control-plane/longhorn-engine/pkg/frontend/rest/model.go

Purpose: defines Rancher API schemas and request/response models for the REST frontend.

Important APIs/types/functions: `Volume` describes the exposed volume resource. `ReadInput` accepts string-encoded `offset` and `length`; `ReadOutput` returns base64 `Data`. `WriteInput` accepts `Offset`, `Length`, and base64 `Data`; `WriteOutput` is empty aside from resource metadata. `NewVolume` creates volume resources with `readat` and `writeat` action links. `EncodeID`/`DecodeID` and `EncodeData`/`DecodeData` use standard base64. `NewSchema` registers the API resource types and action contracts. `Server` holds the `Device`.

Control flow: schema construction is static. Runtime handlers use base64 IDs to match the single configured volume and base64 data to move arbitrary bytes through JSON.

State and persistence: no persistence. Resource IDs are deterministic encodings of volume names.

Dependencies and integration points: used by `router.go` and `server.go`. Depends on `github.com/rancher/go-rancher/api` and `client` resource/schema types.

Risks: base64 standard encoding includes `/`, `+`, and `=`, which can be awkward in path segments unless URL escaped by clients. `ReadInput.Length` is int64 but later passed directly to `make([]byte, input.Length)` in `server.go`, risking bad allocation if negative or huge. `WriteInput.Offset` lacks `,string` while `ReadInput.Offset` uses it, making JSON conventions inconsistent.

Test signals: no direct tests. Encoding helpers and schema action presence are easy unit-test candidates.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/frontend/rest/model.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/frontend/rest/router.go -->
# sources/control-plane/longhorn-engine/pkg/frontend/rest/router.go

Purpose: wires the REST frontend's Rancher-style API routes and error handling.

Important APIs/types/functions: `HandleError` wraps handlers with `api.ApiHandler` and writes API errors through `apiContext.WriteErr`. `NewRouter` creates a strict-slash gorilla mux router with version/schema endpoints and volume list/get/read/write routes.

Control flow: requests first pass through Rancher API context setup, then handler errors are translated to API responses. Volume actions are POSTs to `/v1/volumes/{id}?action=readat` and `writeat`.

State and persistence: no state. Each `NewRouter` call builds a fresh schema set.

Dependencies and integration points: integrates with `rest/model.go` for schemas and `rest/server.go` for handlers. Uses gorilla/mux path variables and Rancher API version/schema handlers.

Risks: route set exposes only one volume but uses collection semantics. No middleware enforces auth, body size, or rate limits. `StrictSlash(true)` can redirect paths, which may interact poorly with action query clients.

Test signals: no direct tests. Route matching and error wrapper behavior are untested in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/frontend/rest/router.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/frontend/rest/server.go -->
# sources/control-plane/longhorn-engine/pkg/frontend/rest/server.go

Purpose: implements REST handlers for listing the volume and performing base64-encoded random reads and writes against the frontend backend.

Important APIs/types/functions: `ListVolumes` returns a `GenericCollection` with the single device volume. `GetVolume` resolves an encoded ID and returns 404 when it does not match. `ReadAt` decodes `ReadInput`, allocates a buffer of requested length, calls `backend.ReadAt`, and returns base64 data. `WriteAt` decodes `WriteInput`, validates decoded length, calls `backend.WriteAt`, and returns `WriteOutput`. Helpers `listVolumes` and `getVolume` build and locate the single volume.

Control flow: every action first validates the path ID against the current volume. `apiContext.Read` decodes request JSON into inputs. Errors from reads are wrapped with context, while write errors are returned directly after logging.

State and persistence: all durable effects are delegated to the backend. The server itself tracks only the `Device` pointer.

Dependencies and integration points: depends on Rancher API context, gorilla/mux variables, and the `Device.backend` `ReaderWriterUnmapperAt`. This handler layer is the actual REST integration point for volume data access.

Risks: `make([]byte, input.Length)` can panic or exhaust memory for invalid client-supplied lengths. Read ignores partial byte counts and returns the whole buffer even if backend read returns fewer bytes without error. Write ignores short-write counts if no error is returned. There is no request body cap, auth, or method-level locking.

Test signals: no direct tests. Boundary tests around invalid IDs, invalid base64, negative/large lengths, short reads/writes, and backend errors would be valuable.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/frontend/rest/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/frontend/socket/frontend.go -->
# sources/control-plane/longhorn-engine/pkg/frontend/socket/frontend.go

Purpose: implements a Unix-domain-socket frontend for Longhorn data IO. It creates `/var/run/longhorn-<volume>.sock`, accepts clients, and handles dataconn requests against a `ReaderWriterUnmapperAt` backend.

Important APIs/types/functions: `Socket` tracks volume metadata, `isUp`, socket path, and a `dataconn.Server` pointer. It implements frontend methods `Init`, `Startup`, `Shutdown`, `State`, `Endpoint`, `Upgrade`, and `Expand`. `GetSocketPath` builds the socket path. `startSocketServer` prepares the directory and removes a stale socket. `startSocketServerListen` accepts Unix connections forever. `handleServerConnection` creates a dataconn server per connection. `DataProcessorWrapper` adapts `ReaderWriterUnmapperAt` to `types.DataProcessor` and makes ping a no-op success.

Control flow: `Startup` launches the listener in a goroutine and immediately marks the frontend up. Each accepted connection runs in its own goroutine until dataconn `Handle` returns. `Shutdown` calls `Stop` on `t.socketServer` if set, but the field is never assigned by the listener path, so active per-connection servers are not centrally stopped.

State and persistence: no persistent state. It creates/removes the Unix socket path at startup. Backend mutations persist through the supplied backend.

Dependencies and integration points: uses `dataconn.Server`, `types.ReaderWriterUnmapperAt`, and filesystem/network primitives. It is embedded by the tgt frontend as the local data path backing a Longhorn iSCSI device.

Risks: `GetSocketPath` panics if called before volume initialization. The accept loop has no shutdown condition and continues logging accept errors. `Shutdown` does not close the listener or unlink the socket. `t.socketServer` does not represent per-connection servers, so stop behavior is incomplete. Upgrade and expand are unsupported at this layer.

Test signals: no direct tests. Lifecycle tests should check stale socket removal, listener shutdown, and dataconn ping/read/write/unmap behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/frontend/socket/frontend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/frontend/tgt/frontend.go -->
# sources/control-plane/longhorn-engine/pkg/frontend/tgt/frontend.go

Purpose: implements the iSCSI/tgt-facing frontend by combining a Longhorn device service with the local socket data frontend.

Important APIs/types/functions: `Tgt` stores a socket frontend, Longhorn device service, frontend name, state, and SCSI/iSCSI timeout settings. `New` constructs the socket and returns a `types.Frontend`. `Init` initializes the socket and creates/initializes a `longhorndev` device. `Startup` starts the socket server then the device. `Shutdown` unfreezes the filesystem at the endpoint, shuts down the device, and shuts down the socket. `Endpoint` returns the device endpoint when up. `Upgrade` creates a new device, runs `PrepareUpgrade`, initializes/starts the socket, then `FinishUpgrade`. `Expand` delegates to the device.

Control flow: data serving must start before the device is started or upgraded, because the device depends on the socket data path. Shutdown tolerates filesystem unfreeze failure but propagates device/socket shutdown errors. Upgrade is a multi-step device plus socket transition.

State and persistence: no direct durable state. Device service operations affect kernel/iSCSI target state. Socket state is delegated to `socket.Socket`.

Dependencies and integration points: integrates `github.com/longhorn/go-iscsi-helper/longhorndev`, `frontend/socket`, `types.Frontend`, and `util.UnfreezeFilesystemForDevice`. It is a primary frontend used by engine processes.

Risks: if socket startup succeeds but device start fails, the socket may be left running. `Endpoint` returns empty while down, so `Shutdown` calls unfreeze with an empty path when not up. Upgrade replaces `t.dev` before all steps succeed, which can complicate rollback. The socket frontend's shutdown limitations carry through here.

Test signals: no direct tests in this subset. Device lifecycle likely requires integration tests with iSCSI helpers and kernel state.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/frontend/tgt/frontend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/interceptor/interceptor.go -->
# sources/control-plane/longhorn-engine/pkg/interceptor/interceptor.go

Purpose: provides gRPC unary interceptors that attach and validate Longhorn volume and instance identity metadata on controller/replica RPCs.

Important APIs/types/functions: `WithIdentityValidationControllerServerInterceptor` and `WithIdentityValidationReplicaServerInterceptor` return server options with the server type in error messages. `identityValidationServerInterceptor` checks incoming `volume-name` and `instance-name` metadata when exactly one value is present and both sides have non-empty values. `WithIdentityValidationClientInterceptor` returns a dial option. `identityValidationClientInterceptor` appends outgoing metadata keys.

Control flow: server validation is permissive unless both client and server specify a value. Multiple metadata values are ignored rather than rejected. Mismatches return `codes.FailedPrecondition`; matches trace-log and call the underlying handler.

State and persistence: no state beyond closure-captured expected names.

Dependencies and integration points: used by replica and sync gRPC client/server constructors. Depends on gRPC metadata, status codes, and logrus.

Risks: validation is unary-only; streaming RPCs are not covered. Multiple metadata values bypass validation. Empty expected names disable enforcement, which is intentional for compatibility but weakens identity guarantees. Metadata is not cryptographic authentication.

Test signals: no direct tests here. Server/client interceptor tests should cover match, mismatch, empty fields, multiple values, and streaming exclusion.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/interceptor/interceptor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/meta/version.go -->
# sources/control-plane/longhorn-engine/pkg/meta/version.go

Purpose: centralizes engine build metadata and compatibility/version constants for CLI, controller API, and replica data format.

Important APIs/types/functions: constants define `CLIAPIVersion`, `CLIAPIMinVersion`, `ControllerAPIVersion`, `ControllerAPIMinVersion`, `DataFormatVersion`, and `DataFormatMinVersion`. Build variables `Version`, `GitCommit`, and `BuildDate` are filled externally by main/build flags. `VersionOutput` is the JSON shape returned to callers. `GetVersion` assembles the current output.

Control flow: no dynamic control beyond returning a struct literal.

State and persistence: build variables are process globals; no persistence.

Dependencies and integration points: consumed by CLI/API version reporting and compatibility checks with longhorn-manager and instance-manager.

Risks: compatibility depends on keeping min/current constants aligned with released components. Build variables default to empty strings if linker flags are missing. Comments note version history but enforcement lives elsewhere.

Test signals: no direct tests. A simple test could lock `GetVersion` field mapping but version values are release-managed.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/meta/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/qcow/libqcow.go -->
# sources/control-plane/longhorn-engine/pkg/qcow/libqcow.go

Purpose: wraps `libqcow` through cgo to provide read-only QCOW image access as a Longhorn diff-disk-like object.

Important APIs/types/functions: `Qcow` holds a `*C.libqcow_file_t`. `Open` initializes and opens a path with `LIBQCOW_OPEN_READ`. `toError` converts libqcow errors into Go errors. `ReadAt` calls `libqcow_file_read_buffer_at_offset`. `Size` calls `libqcow_file_get_media_size`. `Close` closes the file. `WriteAt`, `UnmapAt`, and `Fd` are unsupported/no-op for write-oriented integration.

Control flow: open initializes then opens, freeing the libqcow handle on open failure. Reads return `io.EOF` for zero bytes, convert negative return values to libqcow errors, and otherwise return the byte count.

State and persistence: the wrapper owns a native file handle. It does not write or persist Longhorn metadata.

Dependencies and integration points: links against `-lqcow -lz -pthread` and imports `libqcow.h`. Intended for backing or image layers that need `ReadAt`, `Size`, and `Close`.

Risks: `ReadAt` uses `&buf[0]` and will panic on zero-length buffers. `Close` does not free the libqcow file handle after close, which may leak native resources depending on libqcow expectations. Unsupported write/unmap make it unsuitable as an active layer. C library availability is a build/runtime requirement.

Test signals: no direct tests. Unit tests would need libqcow fixtures and should cover zero-length read, EOF, size, and close/free behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/qcow/libqcow.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/backup.go -->
# sources/control-plane/longhorn-engine/pkg/replica/backup.go

Purpose: manages replica-side backup status and read-only snapshot access for backup creation and incremental mapping.

Important APIs/types/functions: `BackupStatus` tracks backup identity, backing file, opened read-only replica, volume/snapshot IDs, progress, URL, state, and incremental/open flags. `NewBackup` normalizes backup and snapshot names. `UpdateBackupStatus` validates the volume/snapshot pair, updates progress/URL/error, and forces complete/error terminal states. `OpenSnapshot`, `ReadSnapshot`, `CloseSnapshot`, and `CompareSnapshot` expose snapshot contents and changed-block mappings. `findIndex` maps snapshot disk names to active disk-chain indexes, with empty compare snapshot resolving to base/backing index.

Control flow: backup reads open a read-only replica rooted at the snapshot disk in the current working directory. `CompareSnapshot` asserts the snapshot is open, locks the replica, preloads sector locations, and emits block-size-aligned mappings for sectors whose owning disk index is newer than the compare snapshot and at or below the requested snapshot.

State and persistence: `BackupStatus` is in-memory, but `OpenSnapshot` reads existing replica metadata and disk files. It does not persist backup status itself; external backupstore/sync agents own durable backup metadata.

Dependencies and integration points: depends on `backingfile`, backupstore mapping types, backupstore name generation, and disk name helpers. Used by sync-agent backup create/status paths.

Risks: `OpenSnapshot` depends on process current working directory, making caller cwd critical. `CompareSnapshot` assumes `Preload(false)` has accurate FIEMAP support and that block size alignment semantics are acceptable; it coalesces only adjacent sectors with identical aligned offset. `UpdateBackupStatus` ignores later updates after terminal state, so late correction is impossible.

Test signals: `backup_test.go` covers full and incremental mapping across multi-snapshot chains, reads of snapshot data, and backing-file behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/backup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/backup_test.go -->
# sources/control-plane/longhorn-engine/pkg/replica/backup_test.go

Purpose: tests backup snapshot reading and changed-block mapping for replica chains with and without backing files.

Important APIs/types/functions: constants define MiB and default 2 MiB backup block size. `TestBackup` builds a simple replica, snapshots data, opens it through `BackupStatus`, and verifies mappings. `TestBackupWithBackups`, `TestBackupWithBackupsAndBacking`, and helper `testBackupWithBackups` construct a layered write/snapshot pattern and compare mappings between snapshot pairs.

Control flow: tests create temporary replica directories, chdir into them because backup open code uses cwd, write deterministic byte regions, snapshot, open snapshots through `NewBackup`, read full snapshot contents, and compare returned mappings against expected offsets.

State and persistence: creates temporary sparse disk files, snapshot metadata, optional backing file, and removes them afterward. Changes process cwd and does not restore it in this file, which can affect later tests if not isolated by the test runner.

Dependencies and integration points: exercises `New`, `Snapshot`, `BackupStatus.OpenSnapshot`, `ReadSnapshot`, `CompareSnapshot`, and `CloseSnapshot`. Uses test backing-file helpers from `replica_test.go`.

Risks: cwd mutation is global. Tests depend on filesystem FIEMAP behavior through preload/mapping, so unusual filesystems may fail. They validate mapping offsets/sizes but not backup upload or remote backupstore behavior.

Test signals: strong coverage for incremental mapping semantics, base/backing comparisons, and read-only snapshot reconstruction.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/backup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/client/client.go -->
# sources/control-plane/longhorn-engine/pkg/replica/client/client.go

Purpose: provides the Go client wrapper used by controllers/tasks to call replica and sync-agent gRPC services.

Important APIs/types/functions: `ReplicaClient` stores replica and sync-agent URLs, host, volume name, and instance name. `NewReplicaClient` normalizes the replica gRPC address and derives sync-agent address as replica port plus two. Lazy contexts `ReplicaServiceContext` and `SyncServiceContext` hold `grpc.ClientConn`, generated clients, and a custom `util.Once`. Conversion helpers map protobuf disk/replica/sync-file records into engine `types`. Methods cover replica lifecycle (`GetReplica`, `OpenReplica`, `CloseReplica`, `ReloadReplica`, `ExpandReplica`), disk operations, rebuild/sync file operations, backup create/status/remove/restore, restore reset/status, purge/clone/hash operations, and hash lock state.

Control flow: each RPC method lazily initializes the appropriate gRPC client, creates a context with either a common 3-minute timeout or long 24-hour/custom timeout, sends a generated protobuf request, and wraps errors with operation context. File sync and clone methods support custom gRPC timeout seconds. `SyncFiles` populates both modern `FromAddressMap` and deprecated `FromAddress` for backward compatibility.

State and persistence: client state is connection state only. Server-side methods mutate replica files, backups, restore status, and snapshot hash jobs.

Dependencies and integration points: depends on generated `enginerpc`, gRPC insecure credentials, identity metadata client interceptor, `types`, and `util.GetGRPCAddress`. It is the central typed API used by sync tasks and controllers.

Risks: sync-agent port derivation assumes a fixed port layout. `Close` ignores individual close errors. All connections use insecure transport; identity metadata is validation, not encryption/authentication. Many operations intentionally omit `instanceName` in callers that do not know it, weakening server identity validation. Long default timeouts can hide stuck operations.

Test signals: no direct tests in this file. Behavior is indirectly exercised by higher-level sync/replica tests and would benefit from fake gRPC server tests for conversion, timeouts, and error wrapping.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/client/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/diff_disk.go -->
# sources/control-plane/longhorn-engine/pkg/replica/diff_disk.go

Purpose: implements Longhorn's layered differencing disk read/write/unmap logic over a chain of sparse disk files.

Important APIs/types/functions: `diffDisk` stores a sector-to-file `location` cache, ordered `files`, `sectorSize`, `size`, and `rmLock`. `WriteAt` handles aligned writes directly and unaligned writes through read-modify-write. `fullWriteAt` writes to the active head and marks locations as the newest file. `ReadAt` and `fullReadAt` resolve sectors across files and coalesce reads by target. `lookup` discovers unknown sectors using FIEMAP from newest layer toward the base. `UnmapAt` trims sector-aligned ranges across the head and contiguous removed parent snapshots. `Expand`, `RemoveIndex`, `initializeSectorLocation`, and `preload` maintain location/files state.

Control flow: unaligned writes read the whole affected sector, modify the caller's byte range, and write the full sector to the active head. Reads split unaligned boundaries into sector-aligned reads. `lookup` treats file index 1 as the guaranteed base/backing layer if no newer file has an extent. `read` pads zeros when a disk is shorter than the volume and returns `io.ErrUnexpectedEOF` only past volume size.

State and persistence: `location` is an in-memory cache; writes/unmaps persist to underlying sparse files. `RemoveIndex` closes and removes a layer from the chain and rewrites cached indexes.

Dependencies and integration points: used by `Replica` for all data IO. Depends on `types.DiffDisk`, `go-fibmap`, sparse file semantics, and disk utility helpers.

Risks: `fullWriteAt` marks all sectors as written even if the underlying write returns a partial count/error. `lookup` depends on FIEMAP support and does not lock around location updates in read paths. `location` is byte-indexed, limiting practical chain indexes to 255. Unmap returns actual-size reduction, not requested length, and may return zero if size accounting fails even after successful unmap. Overflow and bounds around `location[startSector+i]` rely on callers not writing beyond volume.

Test signals: `diff_disk_test.go` covers aligned/unaligned writes and nominal partial-write byte accounting. `replica_test.go` covers read/write, partial IO, unmap alignment, backing file shorter than volume, and reload reconstruction.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/diff_disk.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/diff_disk_test.go -->
# sources/control-plane/longhorn-engine/pkg/replica/diff_disk_test.go

Purpose: unit tests core `diffDisk` write alignment and partial-write accounting with an in-memory `types.DiffDisk` mock.

Important APIs/types/functions: `mockDiffDisk` implements `ReadAt`, `WriteAt`, `UnmapAt`, `Size`, `Close`, `Sync`, and `Fd`. Helpers `createTestDiffDisk`, `initializeSector`, and `initializeSectors` build layered test disks. `TestDiffDiskWriteAt` table-tests empty, aligned, unaligned, boundary, and multi-sector writes. `TestComputeNominalWrittenBytes` tests clamping of caller-visible bytes for read-modify-write partial writes.

Control flow: tests create a fresh mock chain per case, optionally prefill sectors and cache locations, execute `WriteAt`, and assert byte counts/errors. Nominal-written tests verify lower bound zero and upper bound buffer size.

State and persistence: uses in-memory byte slices only. Mock `Fd` returns zero, so FIEMAP lookup paths are not meaningfully exercised; tests prepopulate locations where needed.

Dependencies and integration points: directly exercises `diff_disk.go` without filesystem sparse files. Complements `replica_test.go`, which exercises real file behavior.

Risks: the write tests assert counts but do not deeply verify resulting data for every scenario. Mock `WriteAt` fails all write-beyond-size cases with zero bytes, so partial underlying writes are not simulated. FIEMAP and unmap actual-size behavior are outside this file.

Test signals: useful focused coverage for unaligned write decomposition and `computeNominalWrittenBytes`, especially regression protection around partial read-modify-write error reporting.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/diff_disk_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/extents.go -->
# sources/control-plane/longhorn-engine/pkg/replica/extents.go

Purpose: preloads a diff disk's sector location cache from filesystem extents using FIEMAP.

Important APIs/types/functions: `MaxExtentsBuffer` caps FIEMAP results at 1024 extents per call. `LoadDiffDiskLocationList` walks extents from a disk fd across the volume-sized logical range and marks every sector covered by each extent with `currentFileIndex`.

Control flow: the function repeatedly calls `fibmap.Fiemap` from the current logical start. It exits when no extents remain or when an extent has `FIEMAP_EXTENT_LAST`. For each extent, it advances in sector-size increments and updates `diffDisk.location`.

State and persistence: mutates only the in-memory location cache. It reads filesystem allocation state but does not write files.

Dependencies and integration points: called by `diffDisk.preload`, which is used by backup comparison and data layout export. Depends on `types.DiffDisk.Fd()` returning a valid fd and `go-fibmap`.

Risks: assumes extents align sufficiently with replica sector accounting; partial-sector extents are rounded through integer division. No explicit bounds check is performed before indexing `location`, so inconsistent FIEMAP ranges could panic. Filesystems without FIEMAP support fail replica preload-dependent operations.

Test signals: no direct tests here. Backup and reload tests indirectly depend on location preloading.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/extents.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/hash.go -->
# sources/control-plane/longhorn-engine/pkg/replica/hash.go

Purpose: implements asynchronous snapshot hashing, checksum-file persistence, and silent corruption detection for replica snapshots.

Important APIs/types/functions: `SnapshotHashStatus` records state, checksum, error, and silent-corruption flag behind a status lock. `SnapshotHashJob` carries context, cancel function, snapshot name, rehash flag, and status. `LockFile`/`UnlockFile` serialize hashing across the node using `/host/var/lib/longhorn/.lock/hash`. `Execute` drives change-time checks, cached checksum reuse, CRC64 hashing, checksum-file update, and corruption detection. Helpers read/write/delete checksum JSON files, get ctime, copy data with cancellation/existence checks, and create the `crc64` hash.

Control flow: `Execute` takes the node-wide lock, gets current ctime, returns early if silent corruption is already recorded, skips hashing when a valid checksum exists and rehash is false, otherwise hashes the snapshot. After hashing it detects same-ctime/different-checksum silent corruption and preserves the old checksum metadata while setting the flag. A deferred block updates job state and writes checksum metadata only when hashing actually occurred.

State and persistence: checksum metadata is persisted as JSON beside the snapshot disk using the disk checksum name. The node-wide lock file persists as a coordination artifact. Hashing reads the snapshot via direct sparse IO.

Dependencies and integration points: used by sync-agent snapshot hash RPCs and `SnapshotHashList`. Depends on `gofrs/flock`, sparse-tools direct IO and xattr-style hash info type, disk name helpers, and the process cwd for snapshot file paths.

Risks: cwd dependence means callers must run in the replica directory. `GetSnapshotChangeTime` assumes Linux `syscall.Stat_t.Ctim`. Error handling in `isSilentCorruptionAlreadyDetected` dereferences `err` in the `err != nil || info == nil` branch; if `info == nil` with nil error ever occurs, it would panic. A blocked file lock can stall a hash job indefinitely unless context cancellation is handled outside the lock call. CRC64 is fast but not cryptographically strong.

Test signals: no direct tests in this subset for hashing execution. `sync/rpc/list_test.go` covers hash job list retention, not file hashing correctness.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/hash.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/replica.go -->
# sources/control-plane/longhorn-engine/pkg/replica/replica.go

Purpose: implements the core Longhorn replica: disk-chain metadata, snapshot/revert/remove/replace operations, volume IO, expansion, backing-file insertion, metadata recovery, and data layout export.

Important APIs/types/functions: `Replica` owns a `diffDisk`, metadata maps (`diskData`, `diskChildrenMap`, `activeDiskData`), revision counter state, read-only flag, unmap/snapshot limits, and `Info`. Constructors `New`, `NewReadOnly`, and `construct` create/open replicas. Public operations include `Snapshot`, `Revert`, `RemoveDiffDisk`, `MarkDiskAsRemoved`, `PrepareRemoveDisk`, `ReplaceDisk`, `Expand`, `WriteAt`, `ReadAt`, `UnmapAt`, `ListDisks`, `Preload`, and `GetDataLayout`. Internal helpers manage atomic metadata writes, new head creation, old-head linking, disk graph updates, live-chain opening, metadata read/recovery, and cleanup.

Control flow: construction creates the directory, recovers `volume.meta` if missing/empty, reads disk metadata, initializes revision counter, opens the live chain or creates initial disk, validates FIEMAP support, and inserts backing file if present. Snapshot/expand create a new head and optionally link the old head as a snapshot, with rollback functions around file and metadata operations. Revert creates a new head pointing at the chosen snapshot, updates `volume.meta`, removes old head, and reloads. Disk removal rewires parent/child metadata and removes active-chain indexes when applicable. IO delegates to `diffDisk` under locks and increments the revision counter asynchronously.

State and persistence: persists `volume.meta`, per-disk `.meta` files, snapshot/head sparse image files, checksum files, and `revision.counter`. In-memory state mirrors disk graph and sector locations. `Close` writes clean dirty state, while most mutations write dirty metadata first.

Dependencies and integration points: used by `replica.Server`, backup/status logic, sync-agent operations, and data servers. Depends on sparse-tools direct IO, FIEMAP, Longhorn backing files, disk utility naming, and Longhorn type/error helpers.

Risks: file operations are complex and rollback is best-effort; crashes mid-operation can leave metadata requiring recovery. `diskPattern` matches only one digit because `(\d)+` captures a single repeated digit group, which can break next-file parsing for multi-digit heads. Revision counter increments are not atomic with data writes and can overcount on failed writes by design. Location indexes are bytes. Many methods depend on process cwd indirectly through helpers. Expansion snapshot creation consumes snapshot count and metadata budget.

Test signals: `replica_test.go` provides broad coverage for create/snapshot/revert/remove/prepare-remove/read/write/backing/partial IO/unmap behavior. Some high-risk areas, such as crash recovery, multi-digit head parsing, revision counter races, and rollback failures, are not fully covered here.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/replica.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/replica_test.go -->
# sources/control-plane/longhorn-engine/pkg/replica/replica_test.go

Purpose: broad behavioral test suite for replica disk-chain lifecycle and IO semantics.

Important APIs/types/functions: defines constants `b` and `bs`, `TestBackingFile`, `NewTestBackingFile`, gocheck suite registration, byte/hash comparison helpers, and many `TestSuite` methods. Covered scenarios include create, snapshot metadata, revert graph shape, leaf/middle/root/out-of-chain removal, prepare-remove actions, basic reads/writes, backing file reads, partial write/read, force removal, unmap with removed-chain marking, and unmap alignment.

Control flow: tests create temp replica directories, instantiate replicas, perform snapshots/reverts/writes/unmaps, and assert active disk arrays, metadata maps, children maps, chain output, file sizes, and read data. Some tests sleep one second to create unique timestamps.

State and persistence: creates real disk and metadata files under temp dirs, optionally with backing files. Tests close/remove dirs via defers. Some helper tests print to stdout and use real filesystem sparse behavior.

Dependencies and integration points: exercises `New`, `Snapshot`, `Revert`, `RemoveDiffDisk`, `MarkDiskAsRemoved`, `PrepareRemoveDisk`, `ReadAt`, `WriteAt`, `UnmapAt`, backing-file insertion, and reload behavior.

Risks: tests are time-sensitive due to one-second timestamp sleeps and can be slow. They use real filesystem behavior, so sparse/FIEMAP assumptions can vary by environment. Some cleanup assertions happen in deferred functions and can mask original failures if cleanup also fails.

Test signals: strong coverage for core replica graph invariants and IO edge cases. Missing signals include crash/restart during rollback, multi-digit snapshot/head naming, revision-counter concurrency, and encrypted expansion.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/replica_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/restore.go -->
# sources/control-plane/longhorn-engine/pkg/replica/restore.go

Purpose: tracks replica-side restore progress and mutable status for backup restore operations.

Important APIs/types/functions: `RestoreStatus` stores replica address, progress, error, backup URL, state, target temp file, final snapshot disk name, last/current backup IDs, and a one-shot stop channel. `NewRestore` initializes in-progress status. `StartNewRestore` resets fields for a new restore and optionally clears last restored. `OpenVolumeDev` recreates the destination file. `UpdateRestoreStatus`, `FinishRestore`, `Revert`, `DeepCopy`, `Stop`, and `GetStopChan` manage state.

Control flow: restore starts in progress at zero. Status updates set progress and append/prepend errors, transitioning to error on non-nil error. Finish marks complete only if not already errored. Revert restores a previous snapshot of status when a failed restore did not modify files. Stop closes the channel once.

State and persistence: status is in-memory. `OpenVolumeDev` creates/removes a file path used as restore data target; durable rename/finalization occurs in sync-agent code outside this file.

Dependencies and integration points: used by sync-agent restore RPC implementation and sync task status reporting. Depends on logrus and Cockroach errors for file cleanup errors.

Risks: `DeepCopy` omits `replicaAddress`, `stopChan`, and `stopOnce`, which is fine for status revert but not a full clone. `OpenVolumeDev` logs "WithError(err)" when `err` is nil after successful stat. Error concatenation order can be surprising. No persistence means process restart loses in-progress status unless reconstructed elsewhere.

Test signals: no direct tests in this subset. Restore behavior is indirectly exercised by sync-agent restore tests if present elsewhere.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/restore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/revision_counter.go -->
# sources/control-plane/longhorn-engine/pkg/replica/revision_counter.go

Purpose: persists and caches a replica revision counter used to compare replica write freshness.

Important APIs/types/functions: constants define `revision.counter`, file mode, and 4096-byte block size. `readRevisionCounter`, `writeRevisionCounter`, `openRevisionFile`, `initRevisionCounter`, `IsRevCounterDisabled`, `GetRevisionCounter`, and `SetRevisionCounter` implement counter lifecycle. A package-level aligned buffer `revisionCounterBuf` is reused for direct IO writes.

Control flow: initialization creates or opens the counter file, writes zero if new, reads the current value into `revisionCache`, then launches a goroutine that consumes increment requests and writes `cache+1` to disk before atomically adding one. `WriteAt`/`UnmapAt` send requests and wait for an ack after data IO succeeds.

State and persistence: persists ASCII integer data in a direct-IO file padded with NULs. Caches the value in `atomic.Int64`. Uses channels on the `Replica` for request/ack coordination.

Dependencies and integration points: called during `Replica` construction and IO paths. Depends on sparse-tools direct IO and context cancellation.

Risks: package-level `revisionCounterBuf` is shared across replicas and goroutines, so concurrent `writeRevisionCounter` calls on different replicas can race. If `writeRevisionCounter` fails, the ack channel is closed; later send/receive behavior can panic or return zero values. The counter is intentionally not atomic with data writes and can overcount on failed data writes. `SetRevisionCounter` assumes no pending IO, enforced only by callers.

Test signals: no direct tests here in this subset. Revision counter persistence and concurrency are important untested risk areas.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/revision_counter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/rpc/dataserver.go -->
# sources/control-plane/longhorn-engine/pkg/replica/rpc/dataserver.go

Purpose: exposes replica data IO over Longhorn's dataconn protocol on either TCP or Unix-domain sockets.

Important APIs/types/functions: `DataServer` stores protocol, address, and replica `Server`. `NewDataServer` constructs it. `ListenAndServe` dispatches to `listenAndServeTCP` or `listenAndServeUNIX`. Each listener accepts connections and wraps them in `dataconn.NewServer(conn, s.s)`.

Control flow: listeners run infinite accept loops. Each accepted connection is handled in a goroutine with deferred close. EOF from a remote/local close is logged at info and treated as normal; other dataconn errors are warnings.

State and persistence: no durable state. It exposes the underlying replica server's persistent IO operations.

Dependencies and integration points: integrates `dataconn.Server`, `replica.Server`, and `types.DataServerProtocol`. This is the data-plane peer for engine/controller replica IO.

Risks: listeners are never closed by this type and accept loops have no context cancellation. Unix sockets are not unlinked here. There is no backoff on repeated accept errors. TCP listener accepts any peer at the bound address; authentication/encryption is outside this protocol.

Test signals: no direct tests in this file. Network lifecycle and dataconn error behavior require integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/rpc/dataserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/rpc/server.go -->
# sources/control-plane/longhorn-engine/pkg/replica/rpc/server.go

Purpose: implements the gRPC management API for replica lifecycle, disk-chain operations, configuration flags, health checks, reflection, and profiling.

Important APIs/types/functions: `ReplicaServer` embeds the generated unimplemented server and holds a `*replica.Server`. `NewReplicaServer` registers replica service, health, reflection, and profiler with identity validation. `getReplica` converts server status and replica metadata to `enginerpc.Replica`. RPC methods cover create/delete/get/open/close/reload/revert/snapshot/expand, disk remove/replace/prepare/mark, rebuilding flag, revision counter, unmap-mark flag, and snapshot max settings. `ReplicaHealthCheckServer` implements gRPC health methods.

Control flow: handlers mostly validate required fields, call the corresponding `replica.Server` method, and return a fresh `getReplica` response. `ReplicaExpand` wraps errors as JSON-encoded Longhorn typed errors with `codes.Internal`. Health returns serving when the `ReplicaServer` has a non-nil `s` pointer, not when the underlying replica is open.

State and persistence: persistent effects happen inside `replica.Server`/`Replica`. gRPC server state is registration only.

Dependencies and integration points: used by replica process startup and `replica/client`. Depends on generated Longhorn protobufs, gRPC health/reflection, profiler RPC, interceptors, and replica package types.

Risks: most errors are raw Go errors except expand's typed JSON path, so client error handling is inconsistent. Health check does not reflect replica state error/closed conditions. `getReplica` ignores `DisplayChain` errors. Snapshot/revert require non-empty name/created but do not validate naming beyond replica internals.

Test signals: no direct tests in this subset. Client/server contract tests would cover protobuf conversion and error code consistency.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/rpc/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/server.go -->
# sources/control-plane/longhorn-engine/pkg/replica/server.go

Purpose: provides a concurrency-safe service wrapper around `Replica`, enforcing replica state transitions and exposing the `types.DataProcessor` data path.

Important APIs/types/functions: `Server` stores context, active replica, directory, sector/backing settings, revision/unmap/snapshot flags, and encryption flag. `NewServer` constructs it. Lifecycle methods include `Create`, `Open`, `Reload`, `Status`, `Close`, and `Delete`. Management methods delegate snapshot/revert/expand/disk/revision/flag operations. Data methods `WriteAt`, `ReadAt`, `UnmapAt`, and `PingResponse` are used by dataconn.

Control flow: `Create` only acts from initial state and closes the newly created replica. `Open` refuses if already open, reads closed status info, and constructs a new replica. `Status` reads `volume.meta` when closed and maps dirty/rebuilding/error fields to replica states. Mutating methods lock the server and usually no-op when no replica is open. Data methods take an `RLock` and fail if the replica no longer exists.

State and persistence: owns the live `Replica`; durable state is in replica disk files and metadata. Server-level flags persist only while the process runs unless written through replica metadata elsewhere.

Dependencies and integration points: used by gRPC management server and data server. Integrates backing files, Longhorn replica states, and dataconn data processor expectations.

Risks: several management calls silently no-op when no replica is open, which can hide caller sequencing bugs. `Delete` only deletes when `s.r` is non-nil, so closed-on-disk replicas are not removed through this path. `Status` recovery around invalid/missing metadata is subtle and can classify empty metadata as initial. `PingResponse` depends on state but does not verify data-path health beyond metadata state.

Test signals: broad indirect coverage through `replica_test.go`, but server state machine and closed-replica delete/no-op behavior are not directly tested here.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/types.go -->
# sources/control-plane/longhorn-engine/pkg/replica/types.go

Purpose: defines shared progress state strings for backup, restore, purge, clone, rebuild, and hash status reporting inside replica/sync packages.

Important APIs/types/functions: `ProgressState` is a string alias with constants `ProgressStateInProgress`, `ProgressStateComplete`, and `ProgressStateError`.

Control flow: no executable control flow. Other files compare and serialize these constants.

State and persistence: values are persisted or returned as JSON/RPC strings by status objects in backup, restore, and sync-agent code.

Dependencies and integration points: consumed by `BackupStatus`, `RestoreStatus`, `SnapshotHashJob`, sync RPC list retention, and status responses.

Risks: string constants are part of external API contracts; changing them would break clients. There is no enum validation helper, so arbitrary strings can still be assigned to `ProgressState`.

Test signals: indirectly tested wherever status transitions assert these values.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/replica/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/sync/backup.go -->
# sources/control-plane/longhorn-engine/pkg/sync/backup.go

Purpose: orchestrates backup creation, backup status retrieval, restore fan-out, restore reset, and restore status aggregation across controller replicas.

Important APIs/types/functions: data structs `BackupCreateInfo`, `BackupStatusInfo`, and sync-level `RestoreStatus` define API output. `Task.CreateBackup` validates the target snapshot, gets volume info, finds an RW replica, and calls `createBackup`. `findRWReplica` scans controller replicas. `FetchBackupStatus` wraps replica backup status. `Task.RestoreBackup` validates volume/frontend/replica/purge state, determines restore snapshot layout and incremental mode, inspects backup metadata, validates volume size, and calls `restoreBackup` concurrently on all replicas. `Reset` and `RestoreStatus` manage/collect sync-agent restore state.

Control flow: backups are created from a single RW replica after verifying the snapshot disk exists there. Restores require the frontend to be down, no normal rebuilds, and no active purge. Snapshot layout determines whether a new random restore snapshot is needed, an existing system snapshot is reused, or purge must run first. Restore RPCs fan out concurrently and aggregate per-replica errors into `TaskError`.

State and persistence: orchestrator state is transient. Durable effects are remote backupstore objects and replica-side restore files/status. Backup inspect reads backupstore metadata. Restore status is collected from sync-agent servers.

Dependencies and integration points: depends on controller client APIs, `replica/client`, `backupstore`, Longhorn common LUKS size constants, UUID helper, and disk name utilities. It is a high-level control-plane bridge between controller state and replica sync-agent RPCs.

Risks: creating replica clients without instance names weakens identity validation. Incremental restore layout assumptions are strict and return BUG-style errors for unexpected chains. A restore can partially start on some replicas if others fail, with errors aggregated only after all goroutines finish. Size handling for encrypted volumes depends on caller-supplied correction flag. Snapshot purge may be started and then restore returns an error asking caller to retry later.

Test signals: no direct tests in this file. Restore/backup orchestration needs controller/replica fakes to cover fan-out, partial failures, snapshot layouts, and encrypted-size correction.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/sync/backup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/sync/rpc/list.go -->
# sources/control-plane/longhorn-engine/pkg/sync/rpc/list.go

Purpose: maintains bounded in-memory FIFO-like lists for backup status records and snapshot hash jobs in the sync-agent RPC server.

Important APIs/types/functions: `BackupList` stores `BackupInfo` entries keyed by backup ID. `BackupAdd`, `BackupGet`, `BackupDelete`, `remove`, and `refresh` implement CRUD and retention. `retainBackupStateCounts` keeps the newest 5 complete and 10 error backups. `SnapshotHashList` stores `SnapshotHashInfo` entries keyed by snapshot name. `Add`, `Get`, `Delete`, `GetSize`, `refresh`, `purgePartialRetained`, and `remove` implement job retention with `MaxSnapshotHashJobSize` per terminal state.

Control flow: adding a backup removes any existing record, appends, updates high-water mark, then refreshes terminal entries. Backup refresh walks from newest to oldest per terminal state and removes older entries beyond retention. Snapshot hash add rejects duplicate in-progress jobs, replaces completed/error jobs for the same snapshot, appends the new job, and refreshes completed/error retention. Get also refreshes before lookup.

State and persistence: state is process-local and protected by RWMutexes. No status survives process restart.

Dependencies and integration points: used by sync-agent backup and snapshot hash RPC handlers. Depends on replica progress states and hash job objects.

Risks: `backupListHighWaterMark` is package-global and not synchronized with list locks. Retention loops decrement indexes inside loops after removal, which is delicate. Snapshot hash retention keeps up to `MaxSnapshotHashJobSize` for each terminal state, not total. In-progress hash jobs are never purged by retention and can accumulate until completed/cancelled/deleted.

Test signals: `list_test.go` covers snapshot hash CRUD and retention refresh on add/get. BackupList retention is not covered in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/sync/rpc/list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/sync/rpc/list_test.go -->
# sources/control-plane/longhorn-engine/pkg/sync/rpc/list_test.go

Purpose: tests `SnapshotHashList` CRUD behavior and retention refresh triggers.

Important APIs/types/functions: registers a gocheck `TestSuite`. `TestSnapshotHashListCRUD` adds, gets, deletes, and verifies missing lookups. `TestSnapshotHashListRefreshTriggerByAdd` adds more than `MaxSnapshotHashJobSize` completed jobs and asserts size is capped. `TestSnapshotHashListRefreshTriggerByGet` marks jobs complete during gets and verifies refresh eventually shrinks the list.

Control flow: each test creates jobs with cancellable contexts, mutates job state directly to terminal complete, and observes list size after add/get operations.

State and persistence: in-memory only. Context cancel functions are created but not called, which is acceptable for these inert jobs but not representative of executing jobs.

Dependencies and integration points: exercises `SnapshotHashList` from `list.go` and `replica.NewSnapshotHashJob`.

Risks: does not test duplicate in-progress rejection, completed replacement for same snapshot, error-state retention, deletion idempotence, or `BackupList`. Directly mutating job state without locks is acceptable in tests but bypasses production status locking.

Test signals: good regression coverage for hash job retention cap and basic CRUD.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/sync/rpc/list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/sync/rpc/progress_tracker_test.go -->
# sources/control-plane/longhorn-engine/pkg/sync/rpc/progress_tracker_test.go

Purpose: regression tests for per-file sync progress tracking during retry, ensuring rebuild/file-sync progress does not exceed 100%.

Important APIs/types/functions: `mockSyncOps` records cumulative processed bytes and computes percentage. Tests instantiate `perFileProgressOps`, call `UpdateSyncFileProgress`, and use `detach` to subtract failed-attempt contributions and ignore late callbacks.

Control flow: `TestProgressExceeds100WithoutTracker` documents the old bug where retrying a file adds bytes twice. `TestProgressStaysCorrectWithTracker` detaches after a partial attempt and verifies retry reaches exactly 100%. `TestProgressMultipleFilesWithRetry` simulates two files with one retry. `TestDetachIgnoresLateCallbacks` and `TestDetachIdempotent` verify detach semantics.

State and persistence: in-memory counters only.

Dependencies and integration points: tests `perFileProgressOps` from sync-agent server code, which wraps `sparserest.SyncFileOperations` callbacks during file sync/rebuild.

Risks: only single-threaded callback sequences are tested; concurrent progress callbacks could still need race testing. The mock uses integer percentage truncation, matching coarse status semantics but not byte-level API output.

Test signals: strong targeted regression signal for retry progress accounting and detach idempotence.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/sync/rpc/progress_tracker_test.go -->
