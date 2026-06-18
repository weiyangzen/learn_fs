# subset-b-000401 Research

Work item `subset-b-000401` covers Longhorn Engine integration RPC helpers, packaging entrypoints, controller/backend runtime code, and data connection transport.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/spdkrpc/spdk_pb2_grpc.py -->
## sources/control-plane/longhorn-engine/integration/rpc/spdkrpc/spdk_pb2_grpc.py

Purpose: generated Python gRPC bindings for the SPDK service used by integration tests or Python control clients. It is not hand-authored business logic; it mirrors the SPDK protobuf service and exposes client stubs, server registration helpers, and experimental static call helpers.

Important APIs/types/functions: `SPDKServiceStub` builds unary and unary-stream channel callables for replica, engine, disk, log, backup, restore, rebuild, snapshot, and version RPCs. `SPDKServiceServicer` declares the server interface and returns `UNIMPLEMENTED` for every method by default. `add_SPDKServiceServicer_to_server` maps service methods to grpc handlers and serializers. `SPDKService` exposes static `grpc.experimental` helper calls.

Control flow: client construction binds method names like `/spdkrpc.SPDKService/ReplicaCreate` to request serializers from `spdk_pb2` and response deserializers from `spdk_pb2` or `empty_pb2`. Server registration builds a dictionary of method handlers and attaches it to a gRPC server. There is no persistence or local state beyond bound callables.

Dependencies and integration points: depends on `grpc`, `google.protobuf.empty_pb2`, and generated `spdkrpc.spdk_pb2`. It integrates with whatever SPDK engine implementation registers a concrete servicer. Because it is generated, schema changes should come from the proto compiler rather than manual edits.

Risks: generated files are easy to drift from the `.proto`; manual edits would be overwritten or leave bindings inconsistent. This file is large and mostly untested directly. During review, duplicate-looking generated lines were visible around `LogSetLevel` and `EngineReplicaList`; if present in the actual file, syntax/import validation should be run after regeneration. Security is delegated to the channel/server setup; this generated layer does not enforce identity or TLS.

Test signals: integration tests likely import this module through SPDK test clients. Direct unit tests are not indicated here; validation should compile/import the generated module and run RPC integration tests that exercise representative methods.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/spdkrpc/spdk_pb2_grpc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/sync/__init__.py -->
## sources/control-plane/longhorn-engine/integration/rpc/sync/__init__.py

Purpose: empty Python package marker for the integration RPC sync client package.

Important APIs/types/functions: none exported by this file.

Control flow, state, and persistence: no runtime behavior, no state, no persistence.

Dependencies and integration points: enables imports from `integration/rpc/sync`, especially `sync_agent_client.py`.

Risks: only packaging/import risk. Removing it can break Python 2 style or explicit package discovery assumptions in older integration test tooling.

Test signals: import-based tests for `rpc.sync.sync_agent_client` indirectly validate this file.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/sync/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/sync/sync_agent_client.py -->
## sources/control-plane/longhorn-engine/integration/rpc/sync/sync_agent_client.py

Purpose: small Python integration-test client for the Longhorn sync agent gRPC service.

Important APIs/types/functions: `SyncAgentClient.__init__` opens an insecure gRPC channel, wraps it with `IdentityValidationInterceptor`, and creates `SyncAgentServiceStub`. `replica_rebuild_status` calls `ReplicaRebuildStatus`. `sync_files` converts tuples into `common_pb2.SyncFileInfo` and invokes `FilesSync`. `file_send` invokes `FileSend`.

Control flow: methods construct protobuf request messages and synchronously call the stub. `sync_files` hardcodes `to_host='localhost'` and translates tuple fields `(from_file_name, to_file_name, actual_size)`.

State and persistence: instance state is limited to address, channel, intercepted channel, and stub. No filesystem writes.

Dependencies and integration points: depends on generated `ptypes.common_pb2`, `ptypes.syncagent_pb2`, `ptypes.syncagent_pb2_grpc`, `google.protobuf.empty_pb2`, and `common.interceptor.IdentityValidationInterceptor`. It integrates with sync-agent server tests and identity-validation tests.

Risks: channel is insecure and intended for local/integration use. Only a subset of service methods is implemented. Tuple-shaped sync file inputs are brittle and lack validation. Hardcoded localhost target may not cover remote topology tests.

Test signals: comment states it exists for `test_validation_fails_with_client`; additional coverage should exercise identity validation, tuple conversion, and timeout propagation.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/sync/sync_agent_client.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/setup.py -->
## sources/control-plane/longhorn-engine/integration/setup.py

Purpose: minimal Python packaging metadata for Longhorn integration tests.

Important APIs/types/functions: calls `distutils.core.setup` with name, version, empty `packages`, and ASL 2.0 license.

Control flow, state, and persistence: import-time setup declaration only.

Dependencies and integration points: uses `distutils`, which is legacy in newer Python distributions. It is likely consumed by tox or ad hoc integration test setup.

Risks: `packages=[]` means package discovery is disabled; this is fine for tests run from source but not for installable test libraries. `distutils` deprecation can become a portability issue.

Test signals: tox/integration test startup indirectly validates whether this packaging file is sufficient.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/setup.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/tox.ini -->
## sources/control-plane/longhorn-engine/integration/tox.ini

Purpose: tox configuration for Python integration tests and flake8.

Important APIs/types/functions: `[tox]` defines `envlist=flake8, py3`. default testenv installs `requirements.txt`, changes to tox root, runs `py.test core data instance --durations=20 {posargs} --exitfirst`, and passes backup-related environment variables. `testenv:flake8` installs flake8 requirements and checks `core data instance`, with generated RPC files excluded.

Control flow and state: tox creates virtualenvs and runs pytest/flake8; no application state.

Dependencies and integration points: integrates with integration test suites under `core`, `data`, and `instance`; relies on AWS/BACKUPTARGET environment variables for backup tests.

Risks: generated RPC exclusion list does not include SPDK generated files, so stale/generated formatting might be noisy if included elsewhere. `py.test` command naming and distutils-era packaging may be sensitive to newer Python environments. `--exitfirst` improves feedback but hides later failures in full validation.

Test signals: this is itself the test runner entrypoint for the integration directory.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/tox.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/main.go -->
## sources/control-plane/longhorn-engine/main.go

Purpose: main binary entrypoint for `longhorn`, wiring the CLI, metadata, logging, panic handling, optional CPU profiling, and `ssync` reexec registration.

Important APIs/types/functions: `main` defers `cleanup`, registers `ssync`, and runs `longhornCli` after `reexec.Init`. `ResponseLogAndError` prints/logs recoverable errors and runtime panics. `cleanup` converts panics to process exit. `longhornCli` configures `urfave/cli` flags and command list, sets version metadata, configures logrus caller formatting, honors `PPROFILE`, and registers controller, replica, sync-agent, backup, frontend, info, and profiler commands.

Control flow: process startup optionally enters a reexec child. Normal startup initializes cli app state, global flags (`url`, `volume-name`, `engine-instance-name`, `debug`), and command handlers from `app/cmd`, then runs with `os.Args`.

State and persistence: writes CPU profiles if `PPROFILE` is set. Sets global `meta` version variables from linker-injected `Version`, `GitCommit`, and `BuildDate`.

Dependencies and integration points: depends on `moby/sys/reexec`, `longhorn/sparse-tools/cli/ssync`, `urfave/cli`, `logrus`, and command packages. It is the user-facing binary copied into the container image.

Risks: panic handling prints to stdout and exits 1, which is useful for CLI but may expose messages in automation logs. `PPROFILE` file creation failures call `log.Fatal`. Version values depend on ldflags. Command registration drift can hide features.

Test signals: command package tests and packaging smoke tests should validate command availability. Runtime smoke should run `longhorn --version` and representative subcommands.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/package/Dockerfile -->
## sources/control-plane/longhorn-engine/package/Dockerfile

Purpose: multi-stage container build for Longhorn Engine runtime image on SUSE BCI 15.7.

Important build steps: builder stage updates zypper, adds snappy and network utilities repos, installs build tools, clones `longhorn/dep-versions`, optionally checks out `SRC_TAG`, builds `liblonghorn` and TGT, and downloads `grpc_health_probe` selected by `ARCH`. release stage installs NFS/CIFS/iSCSI/network/qemu/e2fsprogs tools, copies TGT binaries and health probe from builder, copies `bin/longhorn`, `bin/longhorn-instance-manager`, and launch scripts, adds Tini, and defaults to `longhorn`.

Control flow and state: image build pulls remote repositories and release assets, so output depends on branch/tag arguments and external availability. Runtime entrypoint is `/tini --`, command `longhorn`.

Dependencies and integration points: integrates with `dep-versions` scripts, TGT, liblonghorn, `longhorn-instance-manager`, health checks, and launch scripts.

Risks: `grpc_health_probe` uses GitHub latest release at build time, reducing reproducibility. `SRC_BRANCH=master` default can drift. zypper repo availability and GPG import are external dependencies. The image includes storage tools with privileged runtime expectations.

Test signals: image build in CI, container start smoke tests, `grpc_health_probe` availability, and simple launch script tests are primary signals.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/package/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/package/engine-manager -->
## sources/control-plane/longhorn-engine/package/engine-manager

Purpose: shell wrapper used as a container command for engine-manager style startup.

Important behavior: bind-mounts `/host/dev` over `/dev`, starts `tgtd -f` in background with logs tee'd to `/var/log/tgtd.log`, then execs `longhorn-instance-manager "$@"`.

Control flow and state: mutates mount namespace and starts a background TGT daemon before replacing the shell with instance-manager. Writes TGT logs.

Dependencies and integration points: depends on privileged mount access, `/host/dev`, TGT, and `longhorn-instance-manager`. It is copied into the runtime image.

Risks: no `set -e`, so failed mount or failed TGT startup may not stop execution. Requires privileged container permissions. TGT log can grow unless externally managed.

Test signals: container startup and iSCSI frontend smoke tests should validate this script.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/package/engine-manager -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/package/launch-simple-file -->
## sources/control-plane/longhorn-engine/package/launch-simple-file

Purpose: simple demo/dev launcher that starts an instance-manager daemon and creates an engine backed by one local file backend.

Important behavior: requires `volume`; defaults size to `1g` and frontend to `tgt-blockdev`; bind-mounts `/host/dev`; truncates `/volume/volume.img`; waits for instance-manager health at `localhost:8500`; then runs `longhorn-instance-manager engine create` with `--enable-backend file --replica file://$img`.

Control flow and state: creates or resizes `/volume/volume.img`, starts a background readiness-and-create function, then execs `longhorn-instance-manager daemon`.

Dependencies and integration points: uses `grpc_health_probe`, `truncate`, instance-manager engine create API, file backend support, and frontend support.

Risks: unquoted `[ -z $volume ]` style tests can misbehave for unusual values. Truncating the image path is destructive for existing data. Background engine creation races with daemon readiness by polling health only.

Test signals: manual/demo smoke test with a mounted `/volume` and health probe. Not a production orchestration path.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/package/launch-simple-file -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/package/launch-simple-longhorn -->
## sources/control-plane/longhorn-engine/package/launch-simple-longhorn

Purpose: simple demo/dev launcher that starts one Longhorn replica process and one controller process under instance-manager.

Important behavior: requires `volume`; defaults size to `1g` and frontend to `tgt-blockdev`; bind-mounts `/host/dev`; waits for instance-manager health; starts TGT; creates a replica process with 15 ports; sleeps five seconds; creates controller process with one port and replica `tcp://localhost:10000`.

Control flow and state: background setup performs process creation while foreground execs `longhorn-instance-manager daemon`.

Dependencies and integration points: integrates TGT, instance-manager process create, `longhorn replica`, `longhorn controller`, and health probe.

Risks: fixed sleep for replica readiness is brittle. Hardcoded localhost port assumptions can collide. Unquoted shell tests are fragile. Script is suitable for simple local launch, not resilient orchestration.

Test signals: local container smoke tests covering instance-manager health, replica creation, controller creation, and frontend startup.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/package/launch-simple-longhorn -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/backend/dynamic/dynamic.go -->
## sources/control-plane/longhorn-engine/pkg/backend/dynamic/dynamic.go

Purpose: dynamic backend factory dispatcher that chooses a concrete backend implementation from an address scheme.

Important APIs/types/functions: `Factory` holds a map of scheme to `types.BackendFactory`. `New` wraps the map. `Create` splits `address` on `://`, looks up the scheme, strips it, and delegates creation with volume name, protocol, shared timeouts, upgrade flag, and expected size.

Control flow and state: stateless beyond the factories map. Invalid or unknown schemes return an error.

Dependencies and integration points: depends on `types.BackendFactory`; used by controller startup/add-replica paths to support `tcp://`, `file://`, and other backend schemes through one factory.

Risks: address parsing is intentionally simple; malformed addresses or schemes containing `://` are rejected. The factories map is not copied, so external mutation can affect dispatch.

Test signals: backend creation tests should cover known schemes, unknown schemes, and malformed addresses.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/backend/dynamic/dynamic.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/backend/file/file.go -->
## sources/control-plane/longhorn-engine/pkg/backend/file/file.go

Purpose: local file-backed implementation of the Longhorn backend interface, mainly for simple/demo/test paths.

Important APIs/types/functions: `New` returns `Factory`. `Factory.Create` opens/creates an address as an `os.File` and wraps it. `Wrapper` embeds `*os.File` and implements backend methods: `UnmapAt`, `Snapshot`, revision counter setters/getters, rebuild reset, snapshot limit setters, monitor methods, `Size`, `Expand`, and metadata queries.

Control flow: reads/writes come from the embedded file. `Expand` validates the requested size, refuses shrink, truncates to the new size, and wraps rollback errors with Longhorn `types.Error` helpers if truncation or rollback fails.

State and persistence: persists data directly in the backing file. Most Longhorn-specific metadata methods return constants or no-ops: revision counter `1`, sector size `4096`, snapshot usage dummy values, state `open`, no monitor channel.

Dependencies and integration points: used by dynamic backend for `file://` addresses and by `launch-simple-file`. Depends on `os`, `logrus`, and `pkg/types`.

Risks: no real snapshotting, unmap, rebuild, or revision counter semantics; this backend should not be treated as equivalent to replica backends. Opening with `O_CREATE` can silently create new empty storage. No direct monitoring means controller cannot detect file-level failures through monitor channel.

Test signals: simple file backend smoke tests and expand behavior tests are most relevant.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/backend/file/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/backend/remote/remote.go -->
## sources/control-plane/longhorn-engine/pkg/backend/remote/remote.go

Purpose: remote replica backend implementation that combines gRPC control-plane calls with a dataconn data-plane client.

Important APIs/types/functions: `Remote` holds the data path (`types.ReaderWriterUnmapperAt`), replica service URL, monitor/close channels, and volume name. Control methods include `open`, `Close`, `Snapshot`, `Expand`, `SetRevisionCounter`, metadata getters through `info`, `SetUnmapMarkSnapChainRemoved`, `ResetRebuild`, snapshot limit setters, and `StopMonitoring`. `Factory.Create` resolves control/data addresses, validates the replica is closed, opens multiple data connections, wraps them in `dataconn.Client`, calls `ReplicaOpen`, and starts ping monitoring. `connect` supports TCP and Unix sockets. `monitorPing` periodically sends dataconn pings.

Control flow: each control operation creates a short-lived gRPC client with insecure credentials and identity-validation interceptor, applies a timeout from replica client constants, invokes the replica service RPC, and closes the connection. Data I/O is delegated to `dataconn.Client`. Ping failures set a client error and publish on monitor channel.

State and persistence: does not persist locally; all durable state is in the remote replica. Holds live sockets and goroutines. `Close` closes dataconn and calls `ReplicaClose`.

Dependencies and integration points: integrates with `enginerpc.ReplicaService`, identity interceptors, address utilities, `dataconn`, and `pkg/replica/client` conversion helpers. It is the controller's normal TCP/Unix replica backend.

Risks: frequent one-shot gRPC connections add overhead but isolate calls. Insecure transport relies on trusted environment plus identity validation. Create validates initial state must be closed, so lifecycle mismatches fail add/start. Monitor semantics intentionally do not mark ERR merely because no ping response arrives within interval; data timeout and TCP keepalive are part of failure detection. Review visible duplicate/extra statements in this file should be validated by `go test`/`go test ./pkg/backend/remote` if this tree is expected to compile.

Test signals: controller start/add-replica integration tests, replica service gRPC tests, dataconn timeout tests, and monitor failure tests.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/backend/remote/remote.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/backingfile/backingfile.go -->
## sources/control-plane/longhorn-engine/pkg/backingfile/backingfile.go

Purpose: opens and describes optional backing image files for backup/snapshot operations.

Important APIs/types/functions: `BackingFile` records physical size, virtual size, sector size, path, and `types.DiffDisk`. `OpenBackingFile` resolves the path, uses qemu-img metadata to detect format, opens qcow2 through `qcow.Open` or raw through sparse direct I/O, validates size alignment, and returns a populated descriptor.

Control flow and state: empty path returns nil. Unsupported image formats fail. The backing file is opened read-only for raw files; qcow handling is delegated. Persistent state remains in the backing file.

Dependencies and integration points: depends on `go-common-libs/backingimage`, `sparse-tools/sparse`, Longhorn `qcow`, util path resolution, and disk sector constants. Used by backup creation to include backing image data in delta backup operations.

Risks: qemu-img availability and backing file path resolution are environmental dependencies. Direct I/O requires sector alignment; misaligned files fail. Only raw and qcow2 are supported.

Test signals: backing image tests should cover empty path, raw/qcow2 open, unsupported formats, and misaligned size.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/backingfile/backingfile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/backup/import_backupstores.go -->
## sources/control-plane/longhorn-engine/pkg/backup/import_backupstores.go

Purpose: blank-import registry file for Longhorn backupstore drivers.

Important APIs/types/functions: imports Azure, CIFS, NFS, S3, and VFS backupstore packages for side-effect registration.

Control flow, state, and persistence: no functions. Import side effects register supported backup target backends in the backupstore package.

Dependencies and integration points: required by backup create/restore paths so URLs for those stores resolve.

Risks: removing or build-tag excluding this file can silently remove backup target support. Blank imports make support implicit.

Test signals: backupstore URL integration tests for each provider validate this file indirectly.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/backup/import_backupstores.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/backup/main.go -->
## sources/control-plane/longhorn-engine/pkg/backup/main.go

Purpose: backup/restore helper logic for Longhorn replica delta backups.

Important APIs/types/functions: `CreateBackupParameters` captures backup request fields. `ResponseLogAndError` and `ResponseOutput` provide CLI-friendly error/output formatting. `DoBackupInit` validates inputs, parses labels, reads volume metadata, opens optional backing file, creates `replica.BackupStatus`, and assembles `backupstore.DeltaBackupConfig`. `DoBackupCreate` calls `backupstore.CreateDeltaBlockBackup`. `DoBackupRestore` and `DoBackupRestoreIncrementally` call backupstore restore functions. `CreateNewSnapshotMetafile` atomically writes a minimal snapshot meta file.

Control flow: backup init requires volume name, snapshot name, and destination URL, validates volume naming, reads `volume.meta` from cwd through `replica.ReadInfo`, and packages metadata. Restore unescapes backup URLs and delegates to backupstore with concurrency limits.

State and persistence: reads current working directory metadata, may open backing files, writes `<file>.tmp` then renames in `CreateNewSnapshotMetafile`, and backupstore operations read/write backup targets and local delta files.

Dependencies and integration points: integrates with `github.com/longhorn/backupstore`, `pkg/replica`, `pkg/backingfile`, and util label/time/url helpers.

Risks: cwd-sensitive volume metadata can break if invoked from the wrong directory. Backup labels and provider parameters need validation by downstream backupstore. Atomic metafile write only covers same-directory rename; partial cleanup of `.tmp` on errors is not explicit.

Test signals: backup CLI/integration tests, backupstore provider tests, and snapshot metafile unit tests.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/backup/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/client/controller_client.go -->
## sources/control-plane/longhorn-engine/pkg/controller/client/controller_client.go

Purpose: Go client wrapper for the Longhorn controller gRPC service.

Important APIs/types/functions: `ControllerServiceContext` owns `grpc.ClientConn` and generated client. `NewControllerClient` builds a service URL, opens an insecure gRPC client with identity-validation interceptor, and returns `ControllerClient`. Conversion helpers map `enginerpc.Volume`, `ControllerReplica`, and `SyncFileInfo` to internal `types`. Methods wrap volume lifecycle, snapshots, revert, expand, frontend control, unmap/snapshot limits, replica CRUD, rebuild prepare/verify/limit, journal, version detail, health check, and metrics.

Control flow: each method creates a `context.WithTimeout` using `GRPCServiceTimeout` and calls the generated client, wrapping errors with contextual messages. Health check opens a separate health client connection.

State and persistence: no persistence. Holds one client connection until `Close`.

Dependencies and integration points: integrates CLI/manager code with `enginerpc.ControllerService`, health service, identity interceptors, meta/version structs, and internal `types`.

Risks: insecure transport relies on local/trusted networking and identity metadata. Malformed server responses are now guarded for replica address nils, but other response fields may still be assumed. A visible duplicate context line around `VolumeUnmapMarkSnapChainRemovedSet` should be validated by compilation in this checkout.

Test signals: `controller_client_test.go` covers malformed `ControllerReplica` responses. Broader gRPC integration tests should exercise every wrapper and identity validation.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/client/controller_client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/client/controller_client_test.go -->
## sources/control-plane/longhorn-engine/pkg/controller/client/controller_client_test.go

Purpose: unit tests for defensive decoding in the controller client.

Important APIs/types/functions: `fakeClientConn` implements enough of grpc client connection behavior to fake `ControllerReplicaCreate` returning a malformed successful response. `TestGetControllerReplicaInfoRejectsMalformedResponses` checks nil and missing-address responses. `TestReplicaCreateRejectsMalformedReplicaResponse` verifies `ReplicaCreate` turns malformed payloads into decode errors.

Control flow and state: tests avoid real network by using generated client with `fakeClientConn`.

Dependencies and integration points: depends on `enginerpc`, `grpc`, `types`, and Go testing. It validates the client-side guard used by controller manager/CLI callers.

Risks: coverage is narrow to one malformed response class. The fake only supports one method, so other client methods are untested here.

Test signals: strong signal for the regression where rebuild storms yielded empty successful replica responses. Additional table tests could cover `ReplicaGet`, `ReplicaUpdate`, and list decoding.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/client/controller_client_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/control.go -->
## sources/control-plane/longhorn-engine/pkg/controller/control.go

Purpose: central Longhorn engine controller: manages replica backends, frontend lifecycle, snapshots, expansion, read/write/unmap routing, rebuild interactions, error handling, metrics, and filesystem freeze support.

Important APIs/types/functions: `Controller` stores volume size, replicas, backend replicator, frontend, upgrade/revision/salvage flags, shared timeouts, snapshot limits, rebuild sync limit, gRPC server, metrics, and expansion errors. Constructors and lifecycle methods include `NewController`, `StartGRPCServer`, `WaitForShutdown`, `Start`, `Shutdown`, `StartFrontend`, `ShutdownFrontend`, `AddReplica`, `RemoveReplica`, `SetReplicaMode`, and `ListReplicas`. I/O methods are `ReadAt`, `WriteAt`, `UnmapAt`. Policy methods include snapshot creation/freeze, expansion, revision counter checks/salvage, unmap flag propagation, snapshot limit setters, no-space handling, and metrics helpers.

Control flow: `Start` validates duplicate addresses, creates backends, filters invalid state/size/sector mismatches, adds good replicas as RW and missing/bad ones as ERR, then validates flags/revision counters and starts the frontend. Writes use read lock, validate bounds, and either write normally or read-modify-write aligned sectors when a WO rebuilding replica exists. Snapshots optionally bind-mount/freeze a mounted filesystem, sync if not frozen, re-check limits under lock, and snapshot all backends. Expansion marks `isExpanding`, runs async sync and backend expansion, records partial failure information, then expands frontend and clears state. Errors from `BackendError` can mark replicas ERR, with special ENOSPC handling that preserves a consistent maximal written-byte group.

State and persistence: controller state is in memory, while backend operations persist data, snapshots, revision counters, and flags in replicas. Metrics rotate every second in a goroutine. Expansion errors are retained in memory for API reporting.

Dependencies and integration points: integrates backend factories, `replicator`, frontend implementations, gRPC server, mount utilities, namespace sync, Longhorn disk utilities, identity/rpc layers, and type/error helpers.

Risks: high-concurrency lock ordering is critical. Snapshot freeze touches host/container mount state. Async expansion means API success only means expansion started. ENOSPC policy is subtle and must preserve data consistency. Visible duplicate lock/context snippets in this checkout should be checked by `go test`; if real, they would deadlock or fail compilation. `metricsStart` has an endless goroutine without stop semantics.

Test signals: `control_test.go` covers size selection, WO write alignment, and ENOSPC categorization/retention. Integration tests are needed for frontend startup, replica state transitions, snapshot freeze, expansion, and rebuild.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/control.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/control_test.go -->
## sources/control-plane/longhorn-engine/pkg/controller/control_test.go

Purpose: unit tests for controller sizing, WO write alignment, and ENOSPC replica error policy.

Important APIs/types/functions: test helpers include `fakeReader`, `fakeWriter`, `newMockReplicator`, byte-slice constructors, and gocheck suite. Tests cover `determineCorrectVolumeSize`, `writeInWOMode`, `handleDiskNoSpaceErrorForReplicas`, `categorizeOutOfSpaceReplicas`, and `listReplicasToErrOnEnospc`.

Control flow: tests construct fake sources and controller state without real replicas. WO writes verify read-modify-write alignment across 4096-byte sectors. ENOSPC tests assert which replicas stay RW or move ERR based on mode and written-byte groups.

State and persistence: purely in-memory test buffers and replica mode slices.

Dependencies and integration points: uses `gopkg.in/check.v1`, Go testing, `types`, and disk sector constants. It directly supports the controller no-space and rebuild write-path logic.

Risks: map iteration order can affect list order; tests mitigate some list comparisons by map conversion for `listReplicasToErrOnEnospc`, but some ordered list checks exist in categorization for deterministic replica traversal. These tests do not cover real backend errors, locks, frontend, freeze, or gRPC.

Test signals: strong focused signal for recently complex ENOSPC behavior and WO alignment. Needs integration complement for storage stack behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/control_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/errors.go -->
## sources/control-plane/longhorn-engine/pkg/controller/errors.go

Purpose: shared controller error message constants.

Important APIs/types/functions: `ControllerErrorNoBackendServiceUnavailable` and `ControllerErrorNoBackendReplicaError`.

Control flow/state: no behavior. Constants are used by controller startup to distinguish no backend availability due to service unavailability versus replica errors.

Dependencies and integration points: consumed by `Controller.Start` and likely callers/tests that interpret error strings.

Risks: string constants are brittle API surfaces if external code matches them. Prefer typed errors if behavior grows.

Test signals: startup failure tests should assert the correct class of failure.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/init_frontend.go -->
## sources/control-plane/longhorn-engine/pkg/controller/init_frontend.go

Purpose: frontend factory and timeout helper functions for controller frontends.

Important APIs/types/functions: `NewFrontend` supports `rest`, `socket`, `tgt-blockdev`, and `tgt-iscsi`. `DetermineEngineReplicaTimeout` bounds configured engine-replica timeout to 8-30 seconds with default 8 seconds. `DetermineIscsiTargetRequestTimeout` derives iSCSI request timeout as `2*engineReplicaTimeout * queueDepth + 30s`.

Control flow/state: stateless factory and calculations.

Dependencies and integration points: integrates REST/socket/TGT frontend packages and go-iscsi-helper frontend constants. Used during controller start/frontend start.

Risks: unsupported frontend strings fail at runtime. Timeout formula encodes Longhorn issue-specific behavior; changing defaults impacts I/O failure timing and iSCSI session behavior.

Test signals: unit tests should cover supported/unsupported frontend names and timeout bounds/formula.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/init_frontend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/multi_unmapper_at.go -->
## sources/control-plane/longhorn-engine/pkg/controller/multi_unmapper_at.go

Purpose: fan-out implementation of `types.UnmapperAt` across multiple replica backends.

Important APIs/types/functions: `MultiUnmapperAt` holds unmappers. `MultiUnmapperError` joins underlying errors. `UnmapAt` starts one goroutine per backend, collects errors, records one returned unmapped size, and warns if sizes differ.

Control flow: all unmap operations run concurrently; after `WaitGroup` completion the method returns first observed size and aggregated error if any backend failed.

State and persistence: no local persistence; unmap effects happen in backend replicas.

Dependencies and integration points: used by `replicator` for controller unmap fan-out. Depends on `types.UnmapperAt` and logrus.

Risks: if there are zero unmappers, returns size 0 nil. Size mismatch is only logged, not treated as error. Error type is distinct from `MultiWriterError`; `replicator.UnmapAt` currently checks for `MultiWriterError`, which looks like a bug because multi-unmap errors would not be decomposed per backend.

Test signals: should have unit tests for all-success, partial failure, zero unmappers, and mismatched sizes.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/multi_unmapper_at.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/multi_writer_at.go -->
## sources/control-plane/longhorn-engine/pkg/controller/multi_writer_at.go

Purpose: concurrent fan-out `io.WriterAt` for writing the same buffer to multiple replica backends.

Important APIs/types/functions: `MultiWriterAt` holds writers. `MultiWriterError` records writers, errors, and per-writer written bytes. `WriteAt` starts one goroutine per writer, waits, and returns `len(p)` if at least one writer succeeded, or aggregated errors with written-byte details if any failed.

Control flow: all writes run concurrently. Errors and short writes are recorded only when `err != nil`; successful short writes without error would be treated as full success.

State and persistence: no local persistence; writes persist in backend replicas.

Dependencies and integration points: used by `replicator.WriteAt`; `WrittenBytes` feeds ENOSPC consistency policy in `Controller.handleErrorNoLock`.

Risks: success return `n=len(p)` if any writer succeeds, even when others fail; this is intentional for degraded replica handling but must be paired with error handling. No locking around slice writes is safe because each goroutine writes a unique index. Successful short writes without error are not handled.

Test signals: unit tests should cover partial errors and written-byte propagation into `BackendError`.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/multi_writer_at.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/rebuild.go -->
## sources/control-plane/longhorn-engine/pkg/controller/rebuild.go

Purpose: controller-side logic for preparing and verifying replica rebuilds.

Important APIs/types/functions: `getCurrentAndRWReplica` finds target and healthy source. `VerifyRebuildReplica` compares disk chains, copies revision counter from RW source when enabled, and promotes WO to RW. `syncFile` launches a receiver on the target replica and sends a file from source. `PrepareRebuildReplica` resets target revision counter, computes snapshot/meta file sync list from source disks, removes extra target disks, and syncs head metadata under lock. `removeExtraDisks` deletes target disks not present in source. Rebuild sync limit setters/getters manage concurrency configuration.

Control flow: rebuild preparation and verification hold controller lock to block writes during critical metadata operations. Disk-chain comparison intentionally ignores head child differences. File sync uses replica clients and HTTP receiver/send path.

State and persistence: updates replica revision counters, removes extra snapshot disks, syncs metadata files, and changes in-memory replica mode.

Dependencies and integration points: depends on replica client APIs, disk utility naming, controller util `GetReplicaDisksAndHead`, and sync-agent/file-send infrastructure.

Risks: errors during verification mark target ERR even for some possibly recoverable conditions. Holding the controller lock during head metadata sync blocks I/O. Instance name is required for target validation but omitted for source as best effort. Extra disk removal is destructive for target rebuild state.

Test signals: rebuild integration tests should cover chain equality, extra disk cleanup, revision counter copy, sync list correctness, and failure-to-ERR behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/rebuild.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/replicator.go -->
## sources/control-plane/longhorn-engine/pkg/controller/replicator.go

Purpose: internal backend multiplexer for controller reads, writes, unmaps, snapshots, expansion, close, and per-backend settings.

Important APIs/types/functions: `replicator` tracks backend wrappers by address, mode, reader/writer/unmapper index maps, selected readers, and next read index. `BackendError` aggregates per-address errors and written bytes. Methods include `AddBackend`, `RemoveBackend`, `ReadAt`, `WriteAt`, `UnmapAt`, `buildReaderWriterUnmappers`, `SetMode`, `Snapshot`, `Expand`, `Close`, metadata aggregators, and per-backend setters/getters.

Control flow: reads round-robin RW readers and fall through on error. Writes fan out through `MultiWriterAt` to all non-ERR backends, including WO. Unmaps fan out similarly. Snapshot and expand run concurrently across non-ERR backends. Expansion returns whether any replica succeeded plus separate errors for out-of-sync handling versus recording.

State and persistence: stores in-memory backend registry and mode/index maps. Persistent effects happen in backend methods. `RemoveBackend` asynchronously closes backends after stopping monitoring.

Dependencies and integration points: used only by controller. Depends on backend interface, `MultiWriterAt`, `MultiUnmapperAt`, and Longhorn error classification.

Risks: no internal locking, so caller must hold controller locks. Map iteration means writer/read order is not deterministic. `UnmapAt` appears to check `*MultiWriterError` instead of `*MultiUnmapperError`, reducing per-backend error attribution. `backendsAvailable` is based on RW readers, so write-only-only states cannot serve reads.

Test signals: controller tests exercise some write behavior indirectly. Dedicated replicator tests should cover read failover, write error mapping, unmap error mapping, snapshot/expand partial failures, and mode transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/replicator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/revert.go -->
## sources/control-plane/longhorn-engine/pkg/controller/revert.go

Purpose: controller-side snapshot revert logic.

Important APIs/types/functions: `Revert` validates replica modes, verifies target snapshot exists and is not removed, opens clients for RW TCP replicas, refuses if frontend is up, then reverts each replica and marks failures ERR if at least one succeeds. `clientsAndSnapshot` builds replica clients and normalizes the requested snapshot name to disk name.

Control flow: revert is forbidden during rebuild (WO present), when all replicas are ERR, when frontend is up, or for non-TCP backends. It checks existence against replica disk metadata before performing revert. Actual revert operations run sequentially under controller lock.

State and persistence: persistent snapshot revert is performed by replica clients. Controller may mark failed replicas ERR.

Dependencies and integration points: depends on replica client API, disk utility naming, `GetReplicaDisksAndHead`, and frontend state.

Risks: only TCP backends support revert here; file backend cannot. Sequential revert under lock can block other operations. If some replicas fail and one succeeds, the volume proceeds degraded. Caller must ensure frontend shutdown before invoking.

Test signals: integration tests should cover frontend-up rejection, WO rejection, missing/removed snapshot rejection, partial replica failure, and non-TCP backend rejection.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/revert.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/rpc/server.go -->
## sources/control-plane/longhorn-engine/pkg/controller/rpc/server.go

Purpose: gRPC server adapter exposing `controller.Controller` as `enginerpc.ControllerService`, plus health, reflection, and profiler services.

Important APIs/types/functions: `GetControllerGRPCServer` creates a gRPC server with identity-validation interceptor and registers controller, health, reflection, and profiler services. `ControllerServer` converts internal replica/sync/volume/metrics structs to protobufs. RPC methods wrap volume start/shutdown/snapshot/revert/expand/frontend/flags/limits, replica list/get/create/delete/update/rebuild, journal list, version detail, and metrics. `ControllerHealthCheckServer` implements `Check`, `Watch`, and `List`.

Control flow: each RPC mostly delegates to controller methods and returns current volume/replica state. Health `Watch` sends status every second indefinitely. `JournalList` flushes sparse-tools operation journal.

State and persistence: server holds pointer to controller; no independent persistence. Controller operations may persist data in replicas.

Dependencies and integration points: generated `enginerpc`, gRPC health/reflection, profiler RPC, identity interceptors, metadata, sparse-tools journal, and controller package.

Risks: most errors are returned directly without gRPC status normalization, so clients see implementation strings. `ReplicaUpdate` dereferences `req.Address` without nil guard. Health check reports serving if controller pointer is non-nil, not necessarily if backend/frontend is healthy. `Watch` has no context cancellation handling in the loop.

Test signals: controller client integration tests, health probe tests, and identity validation tests. Unit tests should cover nil/malformed RPC payloads.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/rpc/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/util.go -->
## sources/control-plane/longhorn-engine/pkg/controller/util.go

Purpose: helper to query replica disk chain information and identify the current head.

Important APIs/types/functions: `GetReplicaDisksAndHead` opens a replica client, gets replica metadata, requires a non-empty chain, sets `head` to `Chain[0]`, and returns all disks except the head and backing file.

Control flow: client creation and RPC call errors are wrapped with address context. Client close errors are logged.

State and persistence: read-only metadata query; no persistence.

Dependencies and integration points: used by rebuild and revert logic. Depends on replica client and `types.DiskInfo`.

Risks: assumes `Chain[0]` is current head. Filtering excludes backing file and head, which is correct for snapshot chain comparison but not full disk inventory. Instance name is sometimes unknown and passed as empty for best-effort validation.

Test signals: rebuild/revert tests should validate disk filtering and empty-chain error.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/dataconn/client.go -->
## sources/control-plane/longhorn-engine/pkg/dataconn/client.go

Purpose: asynchronous data-plane client for replica read/write/unmap/ping operations over one or more network connections.

Important APIs/types/functions: `Client` owns request/send/response/end channels, sequence counter, pending message map, wires, peer address, and shared timeout tracker. `NewClient` wraps `net.Conn`s as `Wire`s, starts loop, writer goroutines, and reader goroutines. Public methods implement `TargetID`, `ReadAt`, `WriteAt`, `UnmapAt`, `Ping`, `SetError`, and `Close`. Internal methods include `operation`, `loop`, `nextSeq`, `replyError`, `handleRequest`, `handleResponse`, `write`, and `read`.

Control flow: public operations create a `Message`, enqueue it, and block until completion. The loop assigns sequence IDs, tracks pending journal operations, sends messages to wires, handles responses, and converts transport errors or shared timeout breaches into errors for all in-flight and future requests. A one-second ticker checks elapsed time while I/O is in flight and uses shared timeout accounting.

State and persistence: no persistent state. Maintains in-memory pending message map and operation journal entries via sparse-tools stats. Data persistence occurs in remote replica when messages are processed.

Dependencies and integration points: used by `backend/remote`. Depends on `Wire`, dataconn message constants, Longhorn shared timeout interface, `net.Conn`, and sparse-tools operation journal.

Risks: operations block until completion; channel buffers reduce but do not eliminate deadlock risk if the loop exits unexpectedly. Transport errors poison the client for future requests. Multiple wires share one send channel, so messages are distributed among writer goroutines. Visible duplicate `replyError` in one branch should be validated; duplicate completion could panic or block if real. `Close` closes wires then signals end; reader goroutines stop on read errors.

Test signals: transport tests should cover successful read/write/unmap/ping, timeout, transport error propagation to pending and future requests, close behavior, and multi-connection sequencing.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/dataconn/client.go -->
