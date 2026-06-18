# Research Report: subset-b-000398

This grouped report covers Longhorn Engine command-layer source files and integration test helpers/tests. Each section preserves the original source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/backup.go -->
# sources/control-plane/longhorn-engine/app/cmd/backup.go

## Purpose
Defines the `backup`/`backups` CLI command group for creating, restoring, inspecting, listing, removing, and checking Longhorn backups. It also wires backupstore-provided subcommands for cleanup, metadata, volume inspection, and backing image operations.

## Important APIs, Types, and Functions
- `BackupCmd()` assembles the command group and includes local commands plus `github.com/longhorn/backupstore/cmd` commands.
- `BackupCreateCmd()`, `BackupStatusCmd()`, `BackupRestoreCmd()`, and `RestoreStatusCmd()` define CLI flags and fatal error handling.
- `createBackup()` validates destination, snapshot, labels, block size, credentials, and delegates to `sync.Task.CreateBackup`.
- `checkBackupStatus()` locates the replica that owns a backup status, validates it is `types.RW`, then calls `sync.FetchBackupStatus`.
- `restoreBackup()` unescapes the backup URL, loads backup credentials, and calls `sync.Task.RestoreBackup`.
- `restoreStatus()` calls `sync.Task.RestoreStatus` and prints JSON.
- `getReplicaModeMap()` converts controller replica list output into address-to-mode lookup.

## Control Flow
CLI actions are thin wrappers: parse flags and args, construct controller or sync-task clients, call package-level services, marshal results to JSON, and log fatal errors on failure. Backup creation obtains object-store credentials before task creation and passes user labels, backing image metadata, compression method, concurrency, storage class, and `LonghornBackupParameterBackupBlockSize`. Backup status first lists controller replicas; if no `--replica` is supplied it probes RW replicas until one returns the requested backup status.

## State and Persistence Behavior
This file does not persist state directly. It initiates persistence in the backupstore via `sync.Task` and backupstore credentials. `backup-block-size` is converted from MiB to bytes through `resource.Quantity` and stored in backup parameters. Status and restore state are read from replica/controller task state and serialized to stdout.

## Dependencies and Integration Points
Depends on Longhorn backupstore, `go-common-libs/backup`, controller and replica clients, `pkg/sync`, `pkg/types`, and CLI/global flags such as `--url`, `--volume-name`, and `--engine-instance-name`. Integration tests call these paths through `integration/common/cmd.py` helpers such as `backup_create`, `backup_status`, `backup_restore`, and `restore_status`.

## Risks and Edge Cases
Replica auto-discovery for status ignores instance name and probes only RW replicas, so mixed health or stale backup status can affect discovery. A supplied `--replica` must still be RW according to controller state. Error reporting in restore attempts to marshal task errors and may print plain error strings for non-structured errors. Invalid labels and nonpositive block size are rejected early.

## Test Signals
Coverage is mostly integration-level: `integration/core/test_cli.py` exercises create/status/inspect/list/remove/restore flows, corrupt backup metadata handling, and backup volume deletion. `integration/data/test_backup.py` stresses incremental/full backup logic, backing-image backups, deletion/GC locks, block deduplication, S3 missing-backup behavior, and restore data integrity.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/backup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/controller.go -->
# sources/control-plane/longhorn-engine/app/cmd/controller.go

## Purpose
Defines the `controller` CLI command that starts a Longhorn engine controller process, configures backends/frontends/timeouts/snapshot limits, starts initial replicas when provided, exposes the controller gRPC server, and waits for shutdown.

## Important APIs, Types, and Functions
- `ControllerCmd()` declares all startup flags.
- `startController()` performs validation, constructs backend factories and frontend, creates `controller.Controller`, registers shutdown hooks, starts replicas and gRPC service, then waits.
- `getControllerClient()` creates `pkg/controller/client.ControllerClient` using global identity flags.

## Control Flow
The command requires a positional volume name and validates it with `util.ValidVolumeName`. It parses nominal and current sizes via `docker/go-units.RAMInBytes`, derives short/long engine-replica timeouts and iSCSI target timeout, validates rebuild sync concurrency, constructs requested backend factories (`file`, `tcp`), optionally creates a frontend, and attempts a best-effort filesystem unfreeze before controller construction. If initial replicas are supplied, `control.Start` runs before gRPC serving; no-backend startup errors map to `ENODATA`. The gRPC address and server are then assigned and `StartGRPCServer` is called before `WaitForShutdown`.

## State and Persistence Behavior
Persistent volume state is owned by controller/backends/replicas, not this file. Startup flags configure controller behavior that affects persisted replica chains, frontend device lifecycle, snapshot pruning limits, unmap marking, rebuild sync concurrency, and upgrade/salvage behavior. Shutdown uses a wait group so registered shutdown completion is observed before process exit.

## Dependencies and Integration Points
Depends on `pkg/backend/dynamic`, file/remote backend factories, `pkg/controller`, controller gRPC RPC package, `pkg/types`, and `pkg/util`. It is the process entry point used by integration helpers `create_engine_process` and by many tests that interact through generated controller clients.

## Risks and Edge Cases
Unsupported backend names call `logrus.Fatalf`, exiting instead of returning. Startup with replicas can exit directly with status 1 or ENODATA. Timeout derivation and filesystem unfreeze are safety-sensitive because they affect failure detection and crash recovery. Invalid snapshot max size or nonpositive rebuild sync limit aborts startup.

## Test Signals
`integration/core/conftest.py` and `integration/data/conftest.py` start controller processes. `test_controller.py` verifies replica list/create/delete/update, volume start/shutdown, and expansion. `test_cli.py` validates engine restart, bad replica startup, expansion, and snapshot behavior after reattachment.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/ls_replica.go -->
# sources/control-plane/longhorn-engine/app/cmd/ls_replica.go

## Purpose
Implements the `ls-replica`/`ls` CLI command to print controller-known replicas with their modes and disk chains.

## Important APIs, Types, and Functions
- `LsReplicaCmd()` defines the command.
- `lsReplica()` obtains controller replica list and prints `ADDRESS`, `MODE`, and `CHAIN` columns.
- `getChain(address, volumeName)` opens a replica client and returns `Replica.Chain`.

## Control Flow
`lsReplica` creates a controller client, gets `ReplicaList`, and iterates each replica. Replicas in `types.ERR` are printed without chain lookup. For others, it uses a replica client without instance-name validation to fetch the disk chain and emits a tabwriter table.

## State and Persistence Behavior
Read-only. It observes controller replica membership and replica disk-chain metadata. No mutations occur.

## Dependencies and Integration Points
Uses `getControllerClient`, `pkg/replica/client`, `pkg/types`, and stdout tabwriter output. `snapshot.go` reuses `getChain` to derive snapshot lists from replica chains.

## Risks and Edge Cases
Chain lookup failures are silently represented as an empty chain, which avoids breaking `ls` but can hide replica RPC issues. The function intentionally omits replica instance-name validation because caller does not know it.

## Test Signals
Indirectly tested by snapshot list paths and CLI integration tests that inspect chains. There is no dedicated `ls-replica` test in the listed subset.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/ls_replica.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/profiler.go -->
# sources/control-plane/longhorn-engine/app/cmd/profiler.go

## Purpose
Defines `profiler show|enable|disable` commands to control the engine process profiler through gRPC.

## Important APIs, Types, and Functions
- Constants `opShow`, `opEnable`, `opDisable`, and `profilerPortBase`.
- `ProfilerCmd()` and subcommand constructors.
- `getProfilerClient()` creates a `go-common-libs/profiler.Client` with identity validation interceptor.
- `showProfiler()`, `enableProfiler()`, `disableProfiler()` call `Client.ProfilerOP`.
- `validatePortNumber()` rejects explicit ports between 1 and 29999.

## Control Flow
`enableProfiler` validates a user-supplied port; if unset, it parses the controller gRPC port from `--url` and adds 20001 to avoid Longhorn reserved ranges. Each operation creates a profiler client, calls the operation with a port argument as needed, prints the result, and closes the client.

## State and Persistence Behavior
No on-disk state. It toggles runtime profiler server state inside the target engine process. The chosen port becomes active process state until disabled or process exit.

## Dependencies and Integration Points
Uses `go-common-libs/profiler`, gRPC dial options, and `pkg/interceptor.WithIdentityValidationClientInterceptor` with global volume/instance identity flags.

## Risks and Edge Cases
Default port derivation assumes `--url` is `host:port` and uses `strings.Split(grpcURL, ":")[1]`, which can fail for unusual address forms. Validation permits port 0 as auto mode and ports above 30000 but does not check upper TCP port bounds.

## Test Signals
No direct tests in the listed files. Identity behavior is analogous to `test_identity.py`, but profiler-specific enable/show/disable output is not covered here.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/profiler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/replica.go -->
# sources/control-plane/longhorn-engine/app/cmd/replica.go

## Purpose
Defines the `replica` CLI command that starts a Longhorn replica process, serving replica control gRPC, data server, and optionally an embedded sync-agent subprocess.

## Important APIs, Types, and Functions
- `ReplicaCmd()` declares replica startup flags.
- `startReplica()` validates directory, opens optional backing file, constructs `replica.Server`, optionally creates replica data files, computes service addresses, starts control/data servers, and optionally starts sync-agent.

## Control Flow
The command requires exactly one replica directory. It opens a backing file, parses snapshot max size, creates a cancellable context, and builds `replica.NewServer` with sector size and behavioral flags. If `--size` is supplied it validates backing image virtual size and calls `s.Create`. `util.GetAddresses` derives control, data, and sync addresses from volume, listen address, and data-server protocol. Goroutines run the gRPC control server and data server. If `--sync-agent` is true, the same binary is executed as `sync-agent` with a derived port range and `Pdeathsig=SIGKILL`. The first server/subprocess error returned on `resp` exits `startReplica`.

## State and Persistence Behavior
Creates and mutates replica disk files in the supplied directory. Backing file metadata influences initial virtual size validation. Runtime state includes gRPC/data listeners, optional sync-agent child process, and replica server state driven by later RPCs. Shutdown is coordinated by context cancellation and a signal hook placeholder.

## Dependencies and Integration Points
Depends on `pkg/backingfile`, `pkg/replica`, replica RPC server/data server, `pkg/types`, `pkg/util`, and disk sector constants. It is the process spawned by integration fixtures `create_replica_process` and tested through `ReplicaClient`.

## Risks and Edge Cases
The command returns as soon as any server goroutine exits; a sync-agent failure can terminate the replica command. Size must not be smaller than backing image virtual size. Address derivation and port ranges must match process-manager expectations. Temporary context cancellation only happens on startup error before goroutines take over.

## Test Signals
`integration/core/test_replica.py` covers create/open/close/snapshot/remove/reload/rebuilding state. `test_cli.py`, `test_identity.py`, and data tests start replica processes, validate chains, rebuilds, failure detection, and identity mismatches.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/replica.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/restore_to_file.go -->
# sources/control-plane/longhorn-engine/app/cmd/restore_to_file.go

## Purpose
Implements `backup restore-to-file`, restoring a Longhorn backup into a standalone raw or qcow2 image, optionally merging restored snapshot data with a qcow2 backing file.

## Important APIs, Types, and Functions
- Constants for default formats and temporary filenames.
- `RestoreToFileCmd()` defines CLI flags.
- `restore()` invokes backupstore delta restore into `backup.img` and displays progress.
- `restoreToFile()` orchestrates restore, backing-file handling, qemu conversion, rebase, commit, and cleanup.
- `outputFormatSupported()`, `CheckBackingFileFormat()`, `CopyFile()`, `CleanupTempFiles()`, `ConvertImage()`, `MergeSnapshotsToBackingFile()`, `rebaseSnapshot()`, `commitSnapshot()`.

## Control Flow
`restoreToFile` validates output format and backup URL, resolves output path, schedules temporary cleanup, restores the backup to `BackupFilePath`, then either converts the restored image directly to requested format or resolves/copies a backing file, converts backup to qcow2, rebases that qcow2 on the copied backing file, commits snapshot contents into the copied backing file, and converts the merged image to the requested output.

## State and Persistence Behavior
Creates local temporary files (`backup.img`, `backup.img.converted`, `backing.img.cp`) and the requested output image. Cleanup removes temps unless a temp path equals the output path. It does not mutate backupstore state, but reads backup contents and may copy/merge backing image data.

## Dependencies and Integration Points
Depends on backupstore delta restore APIs, `replica.NewRestore`, Longhorn exec wrapper, `qemu-img`, and `util.ResolveBackingFilepath`. It is called by `integration/common/cmd.py::restore_to_file` and likely exercised by backup data tests outside or around this subset.

## Risks and Edge Cases
`CleanupTempFiles` logs remove failures, which can happen when optional temp files were never created. External `qemu-img`, `cp`, and local working directory assumptions are critical. `CheckBackingFileFormat` uses textual `qemu-img info` output and only accepts qcow2. Progress loop relies on `RestoreDeltaBlockBackup` returning after kicking off restore object state; if progress never reaches terminal state it can wait indefinitely.

## Test Signals
Listed helpers expose `restore_to_file`; backup integration tests focus more on restore-to-volume, block integrity, backing image behavior, and backup metadata. There is no explicit unit test for qemu conversion helpers in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/restore_to_file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/rm_replica.go -->
# sources/control-plane/longhorn-engine/app/cmd/rm_replica.go

## Purpose
Implements `rm-replica`/`rm`, deleting a replica from the controller by address.

## Important APIs, Types, and Functions
- `RmReplicaCmd()` defines the CLI command.
- `rmReplica()` validates an address arg and calls `ControllerClient.ReplicaDelete`.

## Control Flow
The command requires at least one positional argument and ignores any extras. It opens a controller client with global flags, defers close logging, and delegates deletion.

## State and Persistence Behavior
Mutates controller in-memory replica membership and may trigger controller-side cleanup or frontend behavior. It does not directly remove replica disk files.

## Dependencies and Integration Points
Depends on `getControllerClient` and controller client RPC. Related test scenarios directly use gRPC `replica_delete`; CLI command behavior is analogous.

## Risks and Edge Cases
No validation of address scheme beyond server-side handling. Repeated deletes are handled by controller semantics; this wrapper does not special-case idempotency.

## Test Signals
`integration/core/test_controller.py` covers delete behavior through the gRPC client. `test_cli.py` includes removing ERR replicas before snapshot cleanup through controller client, not necessarily this CLI wrapper.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/rm_replica.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/shutdown.go -->
# sources/control-plane/longhorn-engine/app/cmd/shutdown.go

## Purpose
Provides global signal-hook registration for graceful shutdown of controller/replica-related command processes.

## Important APIs, Types, and Functions
- Package-level `hooks []func() error`.
- `addShutdown(f)` registers a hook and lazily starts signal handling.
- `registerShutdown()` listens for `SIGINT` and `SIGTERM`, runs all hooks, and exits with status 1 if any hook fails.

## Control Flow
The first call to `addShutdown` starts a goroutine reading from a buffered signal channel. On signal, each registered hook is invoked sequentially with logging around start/failure. The process exits after hooks finish.

## State and Persistence Behavior
Maintains process-global in-memory hook list. Persistence effects depend on registered hooks, notably controller shutdown flushing/closing volume state. No locking protects `hooks`; registrations are expected during startup.

## Dependencies and Integration Points
Uses Go signal APIs, `syscall`, logrus, and function path helper. `controller.go` registers real controller shutdown; `replica.go` registers an empty hook to enable signal logging/exit.

## Risks and Edge Cases
No mutex around hook mutation and iteration. Multiple signals can trigger concurrent hook execution because the loop remains active. `os.Exit` bypasses defers outside hooks.

## Test Signals
Integration tests simulate process cleanup and SIGKILL in `test_engine_restart_after_sigkill`; graceful signal hooks are not directly asserted in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/shutdown.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/snapshot.go -->
# sources/control-plane/longhorn-engine/app/cmd/snapshot.go

## Purpose
Defines the `snapshot`/`snapshots` CLI group for snapshot create, revert, list, remove, purge, info, clone, clone status, hash, hash cancel, and hash status operations.

## Important APIs, Types, and Functions
- `SnapshotCmd()` and subcommand constructors.
- `createSnapshot()`, `revertSnapshot()`, `rmSnapshot()`, `purgeSnapshot()`, `purgeSnapshotStatus()`.
- `lsSnapshot()` computes common snapshots across RW replicas.
- `infoSnapshot()` uses `sync.GetSnapshotsInfo`.
- `cloneSnapshot()` and `cloneSnapshotStatus()` use controller clients and sync clone helpers.
- `hashSnapshot()`, `cancelHashSnapshot()`, `hashSnapshotStatus()` use `sync.Task`.

## Control Flow
Command constructors bind actions to helper functions. Controller-client operations are used for create/revert/list/info/clone status, while multi-replica asynchronous work such as delete, purge, hash, and restore-style task operations go through `sync.NewTask`. Snapshot listing reads controller replicas, filters to RW replicas, intersects chains across replicas, strips `volume-snap-` and `.img`, and prints IDs newest-first. Clone requires source controller address and snapshot name, builds a second controller client, and delegates to `sync.CloneSnapshot`.

## State and Persistence Behavior
Mutates replica snapshot chains and metadata through controller/sync APIs. Delete marks or removes snapshots depending on chain relationships; purge coalesces removed snapshots. Clone/hashing create long-running state tracked by status maps. Revert requires frontend shutdown at higher levels/tests and changes the active head/parent chain.

## Dependencies and Integration Points
Depends on controller client, `pkg/sync`, `pkg/types`, `pkg/util`, and `go-common-libs/utils.Contains`. Reuses `getChain` from `ls_replica.go`. Extensively exercised by integration helpers and data snapshot-tree tests.

## Risks and Edge Cases
`revertSnapshot` explicitly handles no args and empty arg to avoid panic. `lsSnapshot` only shows snapshots common to all RW replicas; divergent chains or no prepared head can hide snapshots. Clone involves two controller identities and timeouts. Hash status requires snapshot arg and returns JSON. Delete loops over args and returns only the last error while reporting individual failures to stderr.

## Test Signals
`snapshot_test.go` unit-tests revert argument validation. `integration/core/test_cli.py` covers create, default list action, ls, info, rm, rm-empty, purge, purge head-parent limitation, expansion-created snapshots, restart/salvage scenarios. `integration/data/snapshot_tree.py` and `test_backup.py` validate branching snapshot relationships and backup restores from tree nodes.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/snapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/snapshot_test.go -->
# sources/control-plane/longhorn-engine/app/cmd/snapshot_test.go

## Purpose
Unit-tests argument validation for `revertSnapshot` to ensure invalid inputs return errors instead of panicking.

## Important APIs, Types, and Functions
- `TestRevertSnapshotWithNoArgs()`.
- `TestRevertSnapshotWithEmptyStringArg()`.
- Uses `flag.FlagSet` and `urfave/cli.NewContext` to call unexported command helper directly.

## Control Flow
The first test builds a CLI context with no args and asserts error text `snapshot name is required`. The second parses a single empty string argument and asserts `missing parameter for snapshot`.

## State and Persistence Behavior
No persistent state. It avoids controller client creation by failing before RPC setup.

## Dependencies and Integration Points
Depends on `testing`, Go `flag`, and urfave/cli. It protects the guard clause in `snapshot.go::revertSnapshot`.

## Risks and Edge Cases
The tests assert exact error strings, so message changes are breaking. They do not cover successful revert or controller-client failures.

## Test Signals
This file itself is the direct unit test signal for a known CLI panic/validation boundary.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/snapshot_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/stats.go -->
# sources/control-plane/longhorn-engine/app/cmd/stats.go

## Purpose
Defines the `journal` CLI command, which lists controller journal flush operations since the last flush.

## Important APIs, Types, and Functions
- `Journal()` returns a `cli.Command` with `--limit`.
- Action opens controller client and calls `JournalList(limit)`.

## Control Flow
The action creates a controller client, defers close, and invokes `JournalList`. Errors are fatal.

## State and Persistence Behavior
Read-only from this wrapper. It queries controller journal state; exact retention/flush behavior resides in controller implementation.

## Dependencies and Integration Points
Depends on `getControllerClient`, controller client `JournalList`, logrus, and urfave/cli.

## Risks and Edge Cases
No validation on `limit`; controller must interpret zero and negative values. Output formatting is owned by the client call.

## Test Signals
No direct tests in the listed subset. Metrics are covered in `integration/data/test_basic_ops.py`, but journal output is not.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/sync_agent.go -->
# sources/control-plane/longhorn-engine/app/cmd/sync_agent.go

## Purpose
Defines the `sync-agent` server command and `sync-agent-server-reset` control command used for replica rebuild/file sync workflows.

## Important APIs, Types, and Functions
- `SyncAgentCmd()` declares listen address, listen port range, replica address, and replica instance-name flags.
- `SyncAgentServerResetCmd()` resets sync agent state through a sync task.
- `startSyncAgent()` parses port range, listens on TCP, creates `sync/rpc.NewSyncAgentServer`, and serves.
- `doReset()` calls `sync.Task.Reset`.

## Control Flow
`startSyncAgent` splits `start-end`, parses both endpoints, creates a cancellable context, binds TCP, constructs a sync-agent RPC server with replica address and identity, then serves. `doReset` uses global controller URL/volume/engine identity to create a sync task and reset sync-agent server state.

## State and Persistence Behavior
The server maintains runtime sync-agent state and coordinates file sync/rebuild operations against the configured replica. Reset mutates sync-task/sync-agent runtime state. No direct disk writes occur here, but sync operations invoked via server affect replica files.

## Dependencies and Integration Points
Used by `replica.go` as an optional child process. Depends on `pkg/sync` and `pkg/sync/rpc`. Integration helpers call `sync_agent_server_reset` during cleanup and no-frontend reset flows.

## Risks and Edge Cases
Port range parsing accepts any two integers without verifying ordering or free ports. A listen failure aborts startup. Identity flags are important because `test_identity.py` verifies sync-agent volume/instance validation.

## Test Signals
`integration/core/test_identity.py` validates sync-agent identity failures and replica address mismatches. Many integration tests call reset as cleanup before controller/replica teardown.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/sync_agent.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/system_backup.go -->
# sources/control-plane/longhorn-engine/app/cmd/system_backup.go

## Purpose
Exposes backupstore system-backup operations under the Longhorn CLI.

## Important APIs, Types, and Functions
- `SystemBackupCmd()` returns `system-backup` with upload, delete, download, list, and get-config subcommands from `github.com/longhorn/backupstore/cmd`.

## Control Flow
No local action logic. The CLI delegates entirely to backupstore command constructors.

## State and Persistence Behavior
Persistence is owned by backupstore system-backup commands and their target stores. This wrapper only mounts them into Longhorn CLI.

## Dependencies and Integration Points
Depends directly on backupstore CLI package. It integrates system-level backups distinct from per-volume backup commands.

## Risks and Edge Cases
Local validation is absent; any argument, credential, or storage errors are handled by backupstore subcommands.

## Test Signals
No tests for system-backup commands appear in the listed subset.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/system_backup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/update_replica.go -->
# sources/control-plane/longhorn-engine/app/cmd/update_replica.go

## Purpose
Implements `update-replica`/`update` for changing a controller replica mode.

## Important APIs, Types, and Functions
- `UpdateReplicaCmd()` defines the CLI and `--mode` flag.
- `updateReplica()` validates address and mode, then calls `ControllerClient.ReplicaUpdate`.

## Control Flow
The helper requires a replica address and only accepts `types.WO`, `types.RW`, or `types.ERR`. It opens a controller client and delegates update, returning updated `ControllerReplicaInfo`.

## State and Persistence Behavior
Mutates controller replica mode state. This can affect IO routing, rebuild eligibility, and failure semantics; direct persistence is controlled by controller internals.

## Dependencies and Integration Points
Depends on `pkg/types` mode constants and `getControllerClient`. It mirrors gRPC operations tested in controller integration tests.

## Risks and Edge Cases
Usage text says RO/RW/ERR, but validation accepts WO/RW/ERR. This mismatch can confuse callers and is a documentation/API risk.

## Test Signals
`integration/core/test_controller.py::test_replica_change` covers mode update through gRPC. No direct CLI test for `update-replica` appears here.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/update_replica.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/volume.go -->
# sources/control-plane/longhorn-engine/app/cmd/volume.go

## Purpose
Defines volume-level CLI commands: `info`, `expand`, `unmap-mark-snap-chain-removed`, and `frontend start|shutdown`.

## Important APIs, Types, and Functions
- `InfoCmd()`, `ExpandCmd()`, `UnmapMarkSnapChainRemovedCmd()`, `FrontendCmd()`, `FrontendStartCmd()`, `FrontendShutdownCmd()`.
- Helpers `info()`, `expand()`, `startFrontend()`, `shutdownFrontend()`, and `unmapMarkSnapChainRemoved()`.

## Control Flow
All helpers open a controller client, defer close, and call one controller RPC. `info` marshals `VolumeGet` as indented JSON. `expand` reads `--size` as int64. `frontend start` requires a frontend name positional arg. The unmap mark command requires exactly one of `--enable` or `--disable`.

## State and Persistence Behavior
`info` is read-only. `expand` changes volume size and triggers controller/replica expansion workflows. Frontend start/shutdown changes exposed block device/socket state. Unmap mark toggles controller behavior for removing snapshot chains during unmap.

## Dependencies and Integration Points
Uses controller client APIs and logrus. Integration helpers `info_get` and `set_unmap_mark_snap_chain_removed` wrap these commands. Data tests verify frontend device creation, endpoint reporting, and frontend switching.

## Risks and Edge Cases
`expand` does not locally reject zero or shrinking sizes; controller must enforce. Unmap mark command rejects both/no flags. Frontend start validates missing name but frontend type validity is server-side.

## Test Signals
`integration/data/test_basic_ops.py` validates `info` endpoint output, device creation, metrics after IO, and cleanup of leftover block devices. `test_frontend.py` validates no-frontend start/shutdown persistence. Expansion is tested in `test_controller.py` and `test_cli.py`.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/volume.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/volume_export.go -->
# sources/control-plane/longhorn-engine/app/cmd/volume_export.go

## Purpose
Implements `export-volume`/`export`, exporting a snapshot from a healthy replica to an external receiver.

## Important APIs, Types, and Functions
- `ExportVolumeCmd()` declares snapshot name, receiver address/port, backing image export, and HTTP timeout flags.
- `exportVolume()` validates args, finds an RW replica, verifies the snapshot disk exists, and calls `ReplicaClient.ExportVolume`.

## Control Flow
The helper validates required flags, loads controller volume info, lists replicas, picks the first `types.RW` replica, creates a replica client without instance-name validation, reads replica info, checks `rInfo.Disks` for `diskutil.GenerateSnapshotDiskName(snapshotName)`, logs export context, then invokes replica export RPC.

## State and Persistence Behavior
Read-only on the source replica snapshot data, but it streams or transfers data to the receiver. It does not alter controller/replica membership. Exported backing image inclusion is controlled by flag.

## Dependencies and Integration Points
Depends on controller client, replica client, `pkg/types`, and disk name utilities. Related to snapshot clone/file sync receiver workflows.

## Risks and Edge Cases
Choosing the first RW replica can fail if that replica lacks the snapshot while another has it; the function does not search all RW replicas. Receiver reachability and timeout handling are delegated to replica RPC. Missing snapshot disk is caught before export.

## Test Signals
No direct tests in the listed subset. Snapshot clone tests and backup tests exercise adjacent export/file-sync concepts but not this CLI path directly.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/volume_export.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/codecov.yml -->
# sources/control-plane/longhorn-engine/codecov.yml

## Purpose
Configures Codecov reporting policy for the Longhorn Engine repository.

## Important APIs, Types, and Functions
- `comment: off` disables Codecov PR comments.
- `coverage.status.project.default.informational: true` makes project coverage informational.
- `coverage.status.patch: off` disables patch coverage status.

## Control Flow
Declarative YAML consumed by Codecov; no executable code.

## State and Persistence Behavior
No runtime state. It affects CI coverage status behavior for submitted reports.

## Dependencies and Integration Points
Integrates with Codecov service and CI upload configuration elsewhere.

## Risks and Edge Cases
Because coverage gates are informational/off, regressions may not block merges through Codecov status. YAML is minimal and sensitive to indentation.

## Test Signals
Not tested by application tests; validation would be through CI/Codecov behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/codecov.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/common/cli.py -->
# sources/control-plane/longhorn-engine/integration/common/cli.py

## Purpose
Defines pytest fixtures for process-manager clients used by integration tests.

## Important APIs, Types, and Functions
- `em_client` fixture connects to engine instance manager.
- `pm_client` fixture connects to replica instance manager.

## Control Flow
Each fixture constructs `ProcessManagerClient` for a configured address and registers `cleanup_process` as finalizer.

## State and Persistence Behavior
No persistent state. It ensures spawned processes are deleted after tests via process-manager cleanup.

## Dependencies and Integration Points
Depends on `common.core.cleanup_process`, `common.constants` instance-manager addresses, and generated `ProcessManagerClient`.

## Risks and Edge Cases
Default fixture arguments bind addresses at definition time. Cleanup asserts all processes are gone, so lingering process-manager failures fail tests.

## Test Signals
Used as shared fixture infrastructure; no direct assertions here beyond cleanup behavior in `common.core`.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/common/cli.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/common/cmd.py -->
# sources/control-plane/longhorn-engine/integration/common/cmd.py

## Purpose
Provides Python subprocess wrappers around the Longhorn CLI for integration tests, normalizing binary path, command construction, JSON parsing, retries, and simple assertions.

## Important APIs, Types, and Functions
- `_bin()` resolves `integration/bin/longhorn`.
- Volume/snapshot wrappers: `info_get`, `snapshot_create`, `snapshot_rm`, `snapshot_revert`, `snapshot_ls`, `snapshot_info`, `snapshot_purge`, `snapshot_purge_status`.
- Backup wrappers: `backup_create`, `backup_status`, `backup_restore`, `backup_inspect_volume`, `backup_inspect`, `backup_volume_rm`, `backup_volume_list`, `restore_status`, `restore_to_file`.
- Replica/rebuild wrappers: `add_replica`, `replica_rebuild_status`, `verify_rebuild_replica`, `sync_agent_server_reset`, `set_unmap_mark_snap_chain_removed`.

## Control Flow
Each helper builds an argv list and calls `subprocess.check_output` or `check_call`. JSON-producing commands are parsed immediately. `backup_create` asserts fields in returned create info, then polls `backup_status` until complete/error or retry exhaustion.

## State and Persistence Behavior
Mutates test volumes through CLI commands: snapshots, backups, restores, replica additions, sync-agent reset, and controller flags. It also observes backup metadata and volume state.

## Dependencies and Integration Points
Central bridge between Go CLI command files and Python tests. Depends on `RETRY_COUNTS`, `RETRY_INTERVAL`, and `SIZE` constants. Many tests import as `common.cmd`.

## Risks and Edge Cases
Helpers assert expected response fields, so CLI output schema changes break tests early. Some functions accept labels as dict but `create_backup` in `common.core` passes `[]`, which makes `backup_create` iterate zero keys. Retry exhaustion in `backup_status` returns empty output rather than explicitly failing unless callers assert later.

## Test Signals
All CLI-oriented integration tests use this file, giving strong signal for command syntax and JSON contracts.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/common/cmd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/common/constants.py -->
# sources/control-plane/longhorn-engine/integration/common/constants.py

## Purpose
Collects integration test constants for instance-manager addresses, binary paths, retry intervals, volume/engine/replica names, sizes, backup paths, backing files, frontend type, and metadata filenames.

## Important APIs, Types, and Functions
- Instance-manager addresses/types and process states.
- Size constants: `SIZE`, `EXPANDED_SIZE`, `BLOCK_SIZE`, `PAGE_SIZE`.
- Name constants derived from required `TESTPREFIX` environment variable.
- Backup/backing paths such as `BACKUP_DIR`, `VFS_DIR`, qcow2/raw backing file paths.
- Metadata names such as `REPLICA_META_FILE_NAME`, expansion disk names, and `LOGS_DIR`.

## Control Flow
Module import reads `TESTPREFIX` from environment and builds deterministic names.

## State and Persistence Behavior
No runtime mutation, but constants determine test-created process names, volume names, filesystem paths, and backup bucket locations. Missing `TESTPREFIX` fails import.

## Dependencies and Integration Points
Imported by nearly all integration helpers and tests. Values must align with container/test environment paths and generated fixtures.

## Risks and Edge Cases
Hardcoded `/tmp`, `/data/backupbucket`, `/dev/longhorn`, and `/engine-binaries` paths assume a specific integration environment. `TESTPREFIX` lookup via `dict(os.environ)["TESTPREFIX"]` raises `KeyError` if not set.

## Test Signals
Constants are indirectly validated whenever integration tests run; mismatched paths fail process creation, device lookup, or backup operations.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/common/constants.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/common/core.py -->
# sources/control-plane/longhorn-engine/integration/common/core.py

## Purpose
Provides the main integration-test harness for process lifecycle, controller/replica setup, cleanup, retry polling, block device IO verification, backup/snapshot helpers, volume expansion, checksum utilities, and host namespace filesystem interactions.

## Important APIs, Types, and Functions
- Process lifecycle: `cleanup_process`, `wait_for_process_running`, `wait_for_process_error`, `create_replica_process`, `create_engine_process`, `delete_process`, `wait_for_process_deletion`, `upgrade_engine`.
- Controller/replica cleanup and access: `cleanup_controller`, `cleanup_replica`, `get_replica`, `get_controller_version_detail`.
- Volume/test data helpers: `reset_volume`, `get_dev`, `get_blockdev`, `write_dev`, `read_dev`, `verify_data`, `verify_read`, `verify_async`.
- Backup/snapshot helpers: `create_backup`, `rm_backups`, `rm_snaps`, `snapshot_revert_with_frontend`, `restore_with_frontend`, `wait_for_purge_completion`, `wait_for_restore_completion`, `wait_for_rebuild_complete`.
- Expansion and filesystem helpers: `expand_volume_with_frontend`, `wait_for_volume_expansion`, `check_block_device_size`, `get_nsenter_cmd`, `checksum_filesystem_file`, `write_filesystem_file`, `remove_filesystem_file`.
- Data models: `Data` and `Snapshot`.

## Control Flow
Most helpers wrap eventual consistency with retry loops and assertions. Process helpers create processes through instance-manager RPCs and poll state. Cleanup shuts down controllers, deletes replicas, waits for iSCSI session cleanup, then removes process-manager entries. Data helpers write/read through block devices, calculate whole-device checksums, and coordinate frontend shutdown around restore/revert/expansion operations.

## State and Persistence Behavior
Actively mutates process-manager process state, replica directories, block devices, backup directories, Longhorn frontend devices, and host filesystem files. It performs cleanup of backend files and replica directories and resets volumes repeatedly to isolate tests.

## Dependencies and Integration Points
Imports generated controller and process-manager clients, `common.cmd`, `common.frontend`, `common.util`, constants, grpc, pytest, subprocess, tempfile, fcntl/ioctl, and threading. It is the central dependency for core and data integration suites.

## Risks and Edge Cases
Many helpers use asserts for control flow, making failures immediate but sometimes low-context. Race workarounds use sleeps. Global `thread_failed` must be reset after async verifier failures. Cleanup includes shell `rm -r dir + "*"`, process-manager deletion retries, and host namespace commands that require privileged environment.

## Test Signals
This file is test infrastructure rather than tests. Its behavior is transitively validated by all integration suites; failures here often indicate environment, process lifecycle, or eventual-consistency assumptions.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/common/core.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/common/frontend.py -->
# sources/control-plane/longhorn-engine/integration/common/frontend.py

## Purpose
Provides low-level block device access utilities for integration tests, including direct IO read/write helpers and a small `blockdev` wrapper.

## Important APIs, Types, and Functions
- `readat_direct(dev, offset, length)` and `writeat_direct(dev, offset, data)` perform page-aligned direct IO.
- `get_socket_path(volume)` and `get_block_device_path(volume)` build frontend paths.
- `blockdev` class exposes `readat`, `writeat`, and `ready`.

## Control Flow
Direct reads/writes align offsets to `PAGE_SIZE`, use `os.O_DIRECT`, `os.lseek`, and `directio`. `writeat_direct` reads the full page first, overlays encoded data into an mmap buffer, and writes a full page. `blockdev.ready` checks existence and block-device mode before IO.

## State and Persistence Behavior
Writes mutate Longhorn block devices. Reads observe data persisted by controller/replica IO. Socket and device paths are deterministic from constants.

## Dependencies and Integration Points
Used by `common.core.get_blockdev`, data tests, and frontend tests. Depends on Linux block devices, `directio`, `mmap`, and Longhorn device/socket directories.

## Risks and Edge Cases
Direct write helper does not support writes crossing page boundaries except full-page writes. It encodes strings as UTF-8, so arbitrary binary test data would need adaptation. `blockdev.readat` currently uses normal file IO, not direct IO, which may affect cache-sensitive tests.

## Test Signals
`integration/data/test_basic_ops.py`, `test_frontend.py`, and backup tests use these helpers for data integrity assertions.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/common/frontend.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/common/interceptor.py -->
# sources/control-plane/longhorn-engine/integration/common/interceptor.py

## Purpose
Defines a Python gRPC unary-unary client interceptor that injects Longhorn identity metadata (`volume-name`, `instance-name`) into outgoing requests.

## Important APIs, Types, and Functions
- `_ClientCallDetails` namedtuple implementing `grpc.ClientCallDetails`.
- `IdentityValidationInterceptor` with `intercept_unary_unary`.

## Control Flow
For each unary request, existing metadata is copied, optional volume and instance metadata are appended, a new `_ClientCallDetails` is built, and continuation is invoked with the original request.

## State and Persistence Behavior
No persistence. It affects request metadata used by server-side identity validation.

## Dependencies and Integration Points
Used by generated or wrapper clients in integration tests to exercise identity validation. Mirrors Go-side identity validation used by CLI clients.

## Risks and Edge Cases
`next(iter((request,)))` is an unusual way to pass the request but returns the original object. Only unary-unary RPCs are intercepted; streaming calls would need other interceptors.

## Test Signals
`integration/core/test_identity.py` validates volume and instance mismatch failures across controller, replica, sync-agent, and CLI paths.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/common/interceptor.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/common/util.py -->
# sources/control-plane/longhorn-engine/integration/common/util.py

## Purpose
Provides general integration-test filesystem and checksum helpers.

## Important APIs, Types, and Functions
- `file(f)` resolves paths relative to integration root.
- `findfile(start, name)` and `finddir(start, name)` search recursively.
- `read_file(file_path, offset, length)` reads a slice from a text file.
- `checksum_data(data)` returns SHA-512 hex digest.
- `get_process_log_lines(process_name)` reads instance log lines.

## Control Flow
Search helpers walk directories and return first matching file/dir. Checksum helper hashes the provided bytes/string-like object.

## State and Persistence Behavior
Read-only, except it relies on file state produced by tests and process logs.

## Dependencies and Integration Points
Used by backup tests to find backup metadata/block dirs, by core checksum helpers, and for process log assertions.

## Risks and Edge Cases
`findfile`/`finddir` return `None` if no match, leaving callers to assert. `read_file` opens in text mode, unsuitable for arbitrary binary data. `checksum_data` expects data compatible with `hashlib.sha512`.

## Test Signals
Backup tests heavily use `finddir`/`findfile` to manipulate backupstore files and assert metadata behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/common/util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/core/__init__.py -->
# sources/control-plane/longhorn-engine/integration/core/__init__.py

## Purpose
Marks `integration/core` as a Python package for pytest/import purposes.

## Important APIs, Types, and Functions
No code, APIs, or runtime declarations.

## Control Flow
No control flow.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Enables package-style imports such as `from core.test_cli import bin` used by identity tests.

## Risks and Edge Cases
Empty package marker only; removal could affect imports depending on Python package discovery configuration.

## Test Signals
Its presence is indirectly validated by successful pytest collection/import.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/core/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/core/conftest.py -->
# sources/control-plane/longhorn-engine/integration/core/conftest.py

## Purpose
Defines pytest fixtures for core integration tests: process-manager clients, default controller client, and default replica clients.

## Important APIs, Types, and Functions
- `process_manager_client`, `engine_manager_client`.
- `grpc_controller_client`.
- `grpc_replica_client`, `grpc_replica_client2`.

## Control Flow
Fixtures create process-manager clients with cleanup finalizers. Controller fixture starts an engine process, constructs a `ControllerClient`, and waits for version detail. Replica fixtures start replica processes, construct `ReplicaClient`, and clean them to initial state.

## State and Persistence Behavior
Creates and deletes engine/replica processes through instance managers and initializes replica directories. Cleanup is finalizer-driven.

## Dependencies and Integration Points
Depends on `common.core` process creation/cleanup helpers, constants, generated clients, and pytest. Used by core tests.

## Risks and Edge Cases
Fixture cleanup depends on process-manager reliability. Default fixture names and ports are shared, so tests rely on cleanup isolation and `TESTPREFIX`.

## Test Signals
All `integration/core` tests use these fixtures; fixture failures block test collection/execution.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/core/conftest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/core/test_cli.py -->
# sources/control-plane/longhorn-engine/integration/core/test_cli.py

## Purpose
Large integration suite validating Longhorn CLI behavior for replica add/rebuild/failure, snapshots, backups, expansion, restart recovery, replica removal/recreation, and mismatched sizes.

## Important APIs, Types, and Functions
- Fixtures: `backup_targets`, `random_str`, session `bin`.
- Helpers: `setup_module`, `getNow`, `backup_core`, local `random_num`.
- Tests include `test_replica_add_start`, `test_replica_add_rebuild`, `test_replica_add_after_rebuild_failed`, `test_replica_failure_detection`, `test_revert`, snapshot CRUD/list/info/purge variants, `test_backup_cli`, expansion tests, restart/failure recovery tests, and `test_replica_with_mismatched_size_add_start`.

## Control Flow
Tests start engines/replicas via fixtures or process managers, open replicas, start volumes, invoke CLI commands via subprocess or `common.cmd`, then assert controller/replica gRPC state, snapshot chain filenames, backup metadata, and output text/JSON. Several tests simulate detach/reattach by deleting processes and recreating them with the same replica dirs. Backup tests manipulate backupstore config files to test corrupt/missing metadata behavior.

## State and Persistence Behavior
Creates real replica disk chains under temp directories, backup metadata under `BACKUP_DIR`, Longhorn frontend devices, and process-manager managed engine/replica processes. It mutates snapshot meta files, kills engine processes, expands volumes, purges snapshots, and removes backup volumes.

## Dependencies and Integration Points
Exercises Go CLI commands in `app/cmd`, generated controller/replica/process-manager clients, `common.core`, `common.cmd`, and backupstore filesystem layout. Backup targets come from `BACKUPTARGETS`.

## Risks and Edge Cases
Tests depend on timing, process cleanup, privileged environment, and exact CLI output formatting. Some retry loops are bounded but may be flaky on slow systems. Direct backup metadata corruption/removal assumes backupstore file layout. `test_expand_multiple_times` repeatedly creates clients/processes and can be expensive.

## Test Signals
Provides strong end-to-end signal for command-layer behavior: snapshot listing format, backup JSON contracts, rebuild completion, purge semantics, expansion snapshot handling, restart recovery after SIGKILL, and replica mode transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/core/test_cli.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/core/test_controller.py -->
# sources/control-plane/longhorn-engine/integration/core/test_controller.py

## Purpose
Validates controller gRPC operations for replica lifecycle, volume start/shutdown, and expansion using file backends.

## Important APIs, Types, and Functions
- Tests: `test_replica_list`, `test_replica_create`, `test_replica_delete`, `test_replica_change`, `test_start`, `test_shutdown`, `test_controller_expand`.

## Control Flow
Tests create temporary backend files, call controller client methods directly, assert replica list/mode counts, start volumes with file backends, expand with frontend helper, and verify backend file sizes.

## State and Persistence Behavior
Creates local sparse backend files, mutates controller replica membership/modes, starts/shuts down volume state, expands file sizes, and removes backend files during cleanup.

## Dependencies and Integration Points
Uses `common.core` backend-file helpers and expansion helpers, constants for sizes, generated `ControllerClient`, grpc, and pytest.

## Risks and Edge Cases
Relies on controller accepting only one WO replica at a time, idempotent duplicate create/delete semantics, and filesystem truncation behavior. Cleanup must remove temp backend files even after assertion failures through test framework behavior.

## Test Signals
Direct gRPC-level signal for controller APIs underlying `rm-replica`, `update-replica`, `expand`, and startup flows.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/core/test_controller.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/core/test_identity.py -->
# sources/control-plane/longhorn-engine/integration/core/test_identity.py

## Purpose
Validates identity metadata enforcement for controller, replica, sync-agent, and CLI operations.

## Important APIs, Types, and Functions
- `test_validation_fails_with_client`.
- `test_validation_fails_with_cli`.
- Uses controller, replica, sync-agent clients and Longhorn CLI subprocesses.

## Control Flow
The client test starts an engine and replica with expected identities, then constructs clients with wrong volume or instance names and asserts `FAILED_PRECONDITION`. It also tests a correct engine/sync-agent trying to communicate with a replica created for a different volume. The CLI test performs analogous checks through `longhorn --volume-name/--engine-instance-name` and `add-replica`.

## State and Persistence Behavior
Creates multiple engine/replica processes with distinct volume and instance identities. Mutates controller replica membership in the setup path. No persistent data validation beyond process state.

## Dependencies and Integration Points
Uses `common.core` process helpers, generated clients, sync-agent client, CLI binary fixture from `core.test_cli`, and gRPC status codes. Directly validates metadata added by Go and Python interceptors.

## Risks and Edge Cases
Asserts exact stderr/details fragments, so error wording changes are breaking. Relies on sync-agent address derivation from replica process port layout.

## Test Signals
Strong security/identity signal that wrong volume or instance metadata prevents cross-volume/cross-instance RPCs and CLI operations.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/core/test_identity.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/core/test_replica.py -->
# sources/control-plane/longhorn-engine/integration/core/test_replica.py

## Purpose
Validates replica gRPC lifecycle and disk-chain behavior: create, open, close, snapshot, disk removal, reload, and rebuilding state transitions.

## Important APIs, Types, and Functions
- Tests: `test_create`, `test_open`, `test_close`, `test_snapshot`, `test_remove_disk`, `test_remove_last_disk`, `test_reload`, `test_reload_simple`, `test_rebuilding`, `test_not_rebuilding`.
- Local `random_str`/`random_num` fixtures.

## Control Flow
Tests call replica client methods directly and assert returned state fields: `state`, `dirty`, `rebuilding`, `size`, `sector_size`, `parent`, `head`, `chain`, disk labels, and remove operation plans.

## State and Persistence Behavior
Creates replica files and metadata, snapshots disks, marks/removes disks, reloads from disk, and toggles rebuilding flags. These tests verify persistence across close/open/reload transitions.

## Dependencies and Integration Points
Uses fixture-provided `grpc_replica_client`, constants, grpc error assertions, and pytest. Exercises server created by `app/cmd/replica.go`.

## Risks and Edge Cases
Exact chain filenames and states are asserted, so changes in naming or state-machine semantics require test updates. Remove-disk tests cover active-head rejection and idempotent missing-disk preparation.

## Test Signals
Directly validates core replica state machine and persisted disk chain semantics used by snapshot, backup, rebuild, and purge flows.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/core/test_replica.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/data/__init__.py -->
# sources/control-plane/longhorn-engine/integration/data/__init__.py

## Purpose
Marks `integration/data` as a Python package for pytest/import purposes.

## Important APIs, Types, and Functions
No code, APIs, or runtime declarations.

## Control Flow
No control flow.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Supports package imports for data test modules and helpers such as `data.snapshot_tree`.

## Risks and Edge Cases
Empty package marker only; removal could affect imports depending on Python package handling.

## Test Signals
Indirectly validated by successful pytest collection/import.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/data/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/data/conftest.py -->
# sources/control-plane/longhorn-engine/integration/data/conftest.py

## Purpose
Defines pytest fixtures for data-path integration tests, including controllers with/without frontends, backing-file replicas, fixed-directory replicas, and shared process-manager clients.

## Important APIs, Types, and Functions
- Controller fixtures: `grpc_controller`, `grpc_controller_no_frontend`, `grpc_controller_device_name_test`, `grpc_backing_controller`.
- Replica fixtures: `grpc_replica1/2`, backing qcow2/raw replicas, fixed-dir replicas, extra replicas.
- Process fixtures: `process_manager_client`, `engine_manager_client`, generator fixtures `grpc_replica_client`, `grpc_controller_client`.
- `first_available_device` fixture and `dev` fixture.

## Control Flow
Generator fixtures create process-manager clients and return closures that start named engine/replica processes. Backing fixtures pass `--backing-file` args. Device-name fixture hard-links `/dev/null` to an available `/dev/sd*` name and removes it after test. `dev` starts a two-replica volume and returns a block device wrapper.

## State and Persistence Behavior
Creates and deletes processes, replica directories, backing-file-based replicas, fixed directories under `/tmp`, Longhorn block devices, and a temporary `/dev/sd*` hard link. Finalizers clean process and replica directory state.

## Dependencies and Integration Points
Depends on `common.core`, constants, generated clients, pytest, `tempfile`, and OS filesystem behavior. Feeds all `integration/data` tests.

## Risks and Edge Cases
Manipulating `/dev/sd*` requires privileged/test-isolated environment and careful cleanup. Fixed directories are shared constants; cleanup finalizers are essential. Fixture closures default mutable `args=[]`, but they do not mutate it directly here.

## Test Signals
Fixture correctness is transitively verified by data tests for frontend, backup, and basic IO behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/data/conftest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/data/snapshot_tree.py -->
# sources/control-plane/longhorn-engine/integration/data/snapshot_tree.py

## Purpose
Builds and verifies a branching snapshot tree used by data and backup tests to validate snapshot relationships and data restoration across branches.

## Important APIs, Types, and Functions
- `snapshot_tree_build()` creates a fixed branching topology with snapshots `0a` through `3c`.
- `snapshot_tree_create_node()` writes data and creates a snapshot.
- `snapshot_tree_verify()`, `snapshot_tree_verify_relationship()`, `snapshot_tree_verify_data()`, `snapshot_tree_verify_node()`.
- `snapshot_tree_verify_backup_node()` restores a backup and checks data for a named node.

## Control Flow
The builder writes data and snapshots along one branch, reverts to earlier snapshots to create side branches, then verifies relationships and data. Strict verification checks exact node count, head parent/children, and snapshot ls output. Data verification repeatedly reverts to each snapshot and checks block contents.

## State and Persistence Behavior
Mutates volume block data, creates snapshots, reverts frontend state, and in backup verification resets volumes and restores backups. It relies on persisted snapshot metadata and data contents.

## Dependencies and Integration Points
Uses `common.cmd` CLI wrappers and `common.core` data/restore/reset helpers. Consumed by `integration/data/test_backup.py`.

## Risks and Edge Cases
Strict relationship assertions encode exact pruning/list behavior. Repeated reverts require frontend shutdown/start by helper. Data offset/length must remain within page and volume constraints.

## Test Signals
Provides high-value signal for branchy snapshot lineage, snapshot listing after reverts, and backup restore correctness for non-linear snapshot histories.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/data/snapshot_tree.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/data/test_backup.py -->
# sources/control-plane/longhorn-engine/integration/data/test_backup.py

## Purpose
Comprehensive data-path backup integration suite covering backup/restore integrity, backing-file volumes, sparse holes, snapshot trees, incremental/full backup decisions, block deletion/GC, corrupt metadata, volume deletion/listing, backup locks, and backup type behavior.

## Important APIs, Types, and Functions
- Helpers: `backup_test`, `backup_with_backing_file_test`, `backup_hole_with_backing_file_test`, `snapshot_tree_backup_test`, `check_backup_volume_block_count`, lock helpers.
- Tests: `test_backup`, `test_backup_S3_latest_unavailable`, `test_backup_incremental_logic`, `test_snapshot_tree_backup`, backing-file qcow2/raw tests, block deletion/no-cleanup/corrupt deletion, volume deletion/list, `test_backup_lock`, and `test_backup_type`.
- Constants: lock names/types, backing image name/checksum.

## Control Flow
Tests create volumes, write random data, snapshot, create backups, inspect metadata, reset volumes, restore backups, and verify exact data/checksums. Several tests directly edit backupstore files: remove cfgs, corrupt cfg JSON, create in-progress backup cfgs, add bad filenames, remove volume.cfg, count `.blk` files, and create lock files. Lock tests assert operations fail while conflicting locks are acquired and succeed after removal.

## State and Persistence Behavior
Heavily mutates Longhorn volumes, backupstore filesystem under `BACKUP_DIR`, replica state, frontend state, and backup locks. It verifies persistent data by whole-device checksum and targeted reads. It also validates garbage collection of backup blocks and preservation when in-progress backup metadata exists.

## Dependencies and Integration Points
Uses `common.cmd`, `common.core`, `data.snapshot_tree`, constants, `common.util.finddir/findfile`, pytest, subprocess, JSON, pathlib. Exercises Go backup/snapshot/restore command surfaces and backupstore layout.

## Risks and Edge Cases
Tests assume backupstore on local filesystem even for S3-oriented cases enough to inspect `BACKUP_DIR`. Direct metadata manipulation is brittle to backupstore layout changes. Lock timeout tests depend on lock refresh/max wait constants and subprocess failures. Whole-device checksums on small test volumes are sensitive to expected zeroing semantics.

## Test Signals
Very strong signal for backup correctness: incremental vs full selection, backing image metadata, sparse holes, block deduplication/deletion, corrupt/missing metadata handling, lock conflict behavior, volume list resilience, and data restoration from branchy snapshots.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/data/test_backup.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/data/test_basic_ops.py -->
# sources/control-plane/longhorn-engine/integration/data/test_basic_ops.py

## Purpose
Validates basic data-path operations: block device creation, random read/write, metrics, boundary behavior, frontend endpoint reporting, and cleanup of leftover block-device files.

## Important APIs, Types, and Functions
- Tests: `test_device_creation`, `test_basic_rw`, `test_metrics`, `test_beyond_boundary`, `test_frontend_show`, `test_cleanup_leftover_blockdev`.

## Control Flow
Tests start volumes through fixtures, write/read random data at page-aligned offsets, query metrics before and after IO, attempt out-of-bounds writes/reads, inspect CLI `info`, and simulate a leftover blockdev path before volume start.

## State and Persistence Behavior
Creates Longhorn block devices, writes test data to volumes, reads metrics state, and manipulates a placeholder path under `/dev/longhorn`. Boundary test verifies write failure at volume end while controller/replica remain usable.

## Dependencies and Integration Points
Uses `common.cmd.info_get`, `common.core` IO and device helpers, frontend path helper, constants, pytest, and OS filesystem APIs.

## Risks and Edge Cases
Metrics assertions allow retry but require nonzero throughput/IOPS within a short window. Device-name tests rely on `/dev` manipulation and frontend behavior. Out-of-bounds error text `No space left` is environment/API dependent.

## Test Signals
Strong signal for frontend/device integration, controller metrics, IO correctness, boundary handling, and volume info endpoint contract.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/data/test_basic_ops.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/data/test_frontend.py -->
# sources/control-plane/longhorn-engine/integration/data/test_frontend.py

## Purpose
Tests switching a volume that starts without a frontend to a blockdev frontend, preserving data across frontend shutdown/start cycles.

## Important APIs, Types, and Functions
- `test_frontend_switch()`.

## Control Flow
The test opens two replicas, starts a no-frontend controller volume, asserts frontend is empty, starts `tgt-blockdev`, writes and verifies data, shuts frontend down, starts it again, and verifies data persists.

## State and Persistence Behavior
Mutates frontend runtime state and writes persistent volume data through the block device. Confirms data remains on replicas while frontend is down.

## Dependencies and Integration Points
Uses data fixtures, `common.core` helpers, and constants. Exercises `volume.go` frontend start/shutdown behavior through gRPC fixture methods.

## Risks and Edge Cases
Depends on frontend type availability and block device readiness. Only one write offset/length is checked.

## Test Signals
Focused signal for no-frontend startup and dynamic frontend lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/data/test_frontend.py -->
