# Research: subset-b-000399

Grouped research for Longhorn engine integration tests and RPC support files. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/data/test_ha.py -->
# sources/control-plane/longhorn-engine/integration/data/test_ha.py

## Purpose
This pytest module exercises high-availability behavior for Longhorn engine volumes under replica failure, rebuild, revision-counter divergence, backing-image rebuilds, volume expansion, expansion rollback, and replica-side corruption. It is a black-box integration suite over controller and replica gRPC fixtures plus CLI helper commands.

## Important APIs, types, and functions
- Test entry points: `test_ha_single_replica_failure`, `test_ha_single_replica_rebuild`, `test_ha_double_replica_rebuild`, `test_ha_revision_counter_consistency`, `test_snapshot_tree_rebuild`, backing-file rebuild variants, `test_ha_remove_extra_disks`, expansion/rebuild tests, and `test_replica_crashed_update_state_error`.
- Shared helper `ha_single_backing_replica_rebuild_test` factors backing raw/qcow2 rebuild checks.
- The file depends heavily on `common.core` helpers for lifecycle (`open_replica`, `cleanup_replica`, `cleanup_controller`), data I/O (`get_dev`, `get_blockdev`, `verify_data`, `verify_read`, `verify_async`), polling (`wait_for_rebuild_complete`, `wait_for_purge_completion`, `wait_for_volume_expansion`), and model helpers (`Snapshot`, `Data`).
- `common.cmd` exposes engine CLI calls such as `add_replica`, `snapshot_create`, `snapshot_info`, and `snapshot_purge`.
- Constants define stable volume names, replica directories, disk/head metadata names, page/volume sizes, backing volume names, and expansion target sizes.

## Control flow
Most tests start by opening one or more replica fixtures, starting a controller volume with those replica URLs, asserting all replicas are initially `RW`, then writing deterministic random data through the exported block device. Failure cases intentionally remove, close, or corrupt one replica, verify the controller marks it `ERR`, and continue I/O on the surviving replica. Rebuild flows delete the failed controller replica entry, reopen/recreate the replica backend, call `cmd.add_replica`, then wait until rebuild completion before asserting state and data.

The double-rebuild test creates asymmetric revision counters by closing replica2, doing additional writes on replica1, then closing replica1 and restarting the controller with reversed replica order. The expected behavior is that the lower revision-counter replica is listed but marked `ERR`, and rebuilding it synchronizes both revision counters.

Expansion tests write before and after expanding a volume from `SIZE` to `EXPANDED_SIZE`, delete/rebuild replicas, and verify old and expanded regions. Failure/rollback tests create directories at expected temporary expansion metadata paths so expansion metadata updates fail; they verify rollback state, absence of failed expansion artifacts, unchanged replica meta `Size`, and later successful retry.

## State and persistence behavior
The suite validates persistent disk chains, replica revision counters, snapshot metadata, replica JSON metadata, expansion artifact files, and volume-head data across process cleanup/restart. It checks both controller-visible state (`replica_list`, `volume_get`, snapshot info) and filesystem state in fixed replica directories, including `volume-head-000.img`, expansion disk files, temporary metadata, and `REPLICA_META_FILE_NAME`.

## Dependencies and integration points
These tests require the Longhorn engine/controller/replica integration fixtures, local block device frontend support, CLI wrappers in `common.cmd`, snapshot tree helper data, JSON metadata files in fixed replica directories, and backup/backing-file test fixtures. They cross the controller gRPC API, replica gRPC API, sync/rebuild path, backing-image path, frontend block device path, and Linux filesystem operations.

## Risks and edge cases
- The tests rely on exact revision counter increments, which can be sensitive to request coalescing or backend write count changes.
- Fixed-path metadata manipulation is intentionally invasive and can leave artifacts if cleanup fixtures fail.
- Expansion rollback assertions assume temporary metadata cleanup happens synchronously enough for immediate filesystem checks after polling volume expansion state.
- The backing rebuild helper contains snapshot purge expectations that encode a workaround for not removing the parent of `volume-head`; engine snapshot chain changes could break this.
- `test_replica_crashed_update_state_error` simulates disk corruption by deleting the head file and depends on fast asynchronous controller state updates.

## Test signals
Strong signals include replica mode transitions (`RW`, `WO`, `ERR`), preserved reads after failures, synchronized revision counters after rebuild, snapshot tree shape after purge, data integrity across backing formats, zero-filled expanded regions, accurate `last_expansion_error`/timestamp fields, replica meta `Size` values, and automatic state update to `ERR` after head-file removal.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/data/test_ha.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/data/test_restore.py -->
# sources/control-plane/longhorn-engine/integration/data/test_restore.py

## Purpose
This module validates Longhorn backup restore behavior, especially disaster-recovery no-frontend volumes, incremental restore chains, restore plus rebuild, expansion-aware restore, and restore failure recovery. It uses real backup targets and intentionally corrupts filesystem or backup-store state to verify restore status semantics.

## Important APIs, types, and functions
- Entry points: `test_restore_with_rebuild`, `test_restore_incrementally`, `test_inc_restore_with_rebuild_and_expansion`, `test_inc_restore_failure_delta_file_cleanup_error`, and `test_inc_restore_failure_invalid_block`.
- Helpers: `restore_inc_test`, `inc_restore_failure_cleanup_error_test`, and `compare_last_restored_with_backup`.
- `common.core` provides volume startup/cleanup, no-frontend DR volume helpers, backup creation/removal, restore polling, frontend expansion, block device checks, and raw no-frontend data verification.
- `common.cmd` provides CLI calls including `backup_restore`, `restore_status`, `backup_inspect`, `backup_volume_list`, `backup_volume_rm`, `snapshot_create`, `snapshot_info`, `snapshot_purge`, `verify_rebuild_replica`, and `sync_agent_server_reset`.
- The test uses `pytest.raises(subprocess.CalledProcessError)` for expected CLI failures and shell tools such as `chattr`, `find`, `mv`, and `rm`.

## Control flow
`test_restore_with_rebuild` creates a backup from a normal frontend volume, restores it to a no-frontend DR volume, adds a second replica with `restore=True`, then triggers a duplicate restore command. The old replica reports already restored, while the rebuilding replica performs full restore and is manually verified before the original replica is removed.

`restore_inc_test` builds five backups with controlled block-level changes. It first forces restore startup failure by marking fixed replica directories immutable and asserts restore status remains clean because failure happened before actual restore. It then restores backup0 through backup4 incrementally, checking data after each restore, last-restored metadata, delta-file cleanup, duplicate restore rejection, fallback to full restore after deleting an intermediate backup, and VFS temporary file cleanup.

The expansion test restores an initial backup, expands the source volume, creates a larger backup, verifies the DR restore rejects larger backups until the DR volume is expanded, handles mandatory snapshot purge before restore, manually expands a rebuilding DR replica, and verifies rebuild restore for the expanded size.

Failure tests simulate delta cleanup failure by pre-creating directory trees where delta files should be removed, and simulate invalid VFS backup blocks by temporarily moving block files out of the backup store while polling restore status for per-replica errors.

## State and persistence behavior
The file tracks backup objects and names, restore status maps, no-frontend replica data, backup volume size metadata, snapshot purge state, delta file presence/absence in fixed replica directories, VFS temporary files, and immutable directory state. It also explicitly resets sync-agent servers and cleans up volumes, replicas, and backups to prevent state leakage between backup targets.

## Dependencies and integration points
Tests integrate the engine controller, no-frontend DR controller, fixed-directory replicas, backupstore backends listed in `backup_targets`, local VFS backup directory constants, snapshot purge, replica rebuild verification, and sync-agent server reset. They require privileged filesystem operations for `chattr` and direct backup-store file mutation.

## Risks and edge cases
- The invalid-block case can wait up to ten minutes to match backupstore retry behavior.
- Tests assume exact CLI error strings such as "already restored backup", "need to expand the DR volume", and "failed to clean up the existing file".
- Direct mutation of backup blocks and immutable attributes can destabilize later tests if cleanup does not run.
- Incremental restore assertions depend on specific delta-file naming conventions based on backup names.
- The expansion path assumes DR rebuilding replicas are not auto-expanded and must be manually expanded before `restore=True` add succeeds.

## Test signals
Primary signals are correct restored bytes in no-frontend replicas, restore status fields (`isRestoring`, `backupURL`, `lastRestored`, `progress`, `state`, `error`), cleanup of obsolete delta/tmp files, fallback to full restore when an incremental base is unavailable, expected failures before status mutation, all replicas returning to `RW`, and expanded backup/volume size metadata.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/data/test_restore.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/data/test_restore_to_file.py -->
# sources/control-plane/longhorn-engine/integration/data/test_restore_to_file.py

## Purpose
This module verifies the `restore-to-file` engine command for raw and qcow2 output images, both with and without a backing file. It checks byte-level reconstruction of snapshot chains into standalone image files and guarantees that backing images remain unchanged.

## Important APIs, types, and functions
- Constants: `OUTPUT_FILE_RAW`, `OUTPUT_FILE_QCOW2`, `IMAGE_FORMAT_RAW`, and `IMAGE_FORMAT_QCOW2`.
- Helpers: `read_qcow2_file_without_backing_file`, `check_backing`, `check_empty_volume`, `restore_to_file_with_backing_file_test`, and `restore_to_file_without_backing_file_test`.
- Test entry points: `test_restore_to_file_with_backing_file` and `test_restore_to_file_without_backing_file`.
- Uses `pyqcow.file()` to read generated qcow2 outputs and backing qcow2 data without relying on backing-file support in the library.
- Uses `common.cmd.restore_to_file`, snapshot/backup helpers, snapshot revert, snapshot removal, and checksum utilities.

## Control flow
The backing-file path starts from an empty volume whose content equals the backing file, creates a backup, restores it to raw and qcow2 output, compares content and full-volume checksums, and removes output files. It then repeats with one snapshot containing changed data and with a two-snapshot chain where newer data partially overwrites older data. Between phases it reverts to the initial snapshot, removes snapshots/backups, and rechecks backing file integrity.

The no-backing path creates one and then two snapshots on a normal volume, creates backups, restores to raw/qcow2 without passing a backing file, and verifies that the output contains only the expected snapshot-chain data. It also uses snapshot revert and backup cleanup between phases.

## State and persistence behavior
The tests create temporary output files in the integration utility path and assert they are removed after validation. Persistent state under test includes snapshot disk chains, backup objects, backing raw/qcow2 file data, restored output image bytes, and device checksums. Snapshot reverts reset the tested volume to a known baseline before subsequent chains.

## Dependencies and integration points
The file depends on engine controller/replica fixtures, backing-file fixtures, backup targets, pyqcow, Longhorn CLI restore-to-file support, local file utilities, and backing file constants. It bridges live block-device data, backupstore data, generated image files, and qcow2 decoding.

## Risks and edge cases
- The qcow2 reader helper explicitly cannot handle qcow2 files with backing files, so it reads generated images as standalone content and relies on restore-to-file producing self-contained images.
- There is a likely typo in the final backing qcow2 assertion: it concatenates `output1_qcow2_backing` instead of `output2_qcow2_backing`, so the expected value works only if those backing ranges are equivalent.
- Raw output for the second no-backing phase is not removed before qcow2 restore, leaving cleanup dependent on later test/fixture behavior.
- Tests use string decoding for bytes read from qcow2, which assumes test data is compatible with UTF-8-like generated strings.

## Test signals
Signals include exact byte equality between output images and expected snapshot/backing composition, matching volume checksums, non-empty volume/backing reads, absence of output files after cleanup, preserved backing-file bytes after restore-to-file, and correct behavior across both raw and qcow2 formats.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/data/test_restore_to_file.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/data/test_snapshot.py -->
# sources/control-plane/longhorn-engine/integration/data/test_snapshot.py

## Purpose
This module exercises Longhorn snapshot lifecycle semantics: create, list, revert, remove, purge/coalesce, tree branching, backing-file snapshots, expansion across snapshots, mounted filesystem freezing, snapshot pruning, and filesystem trim/unmap behavior.

## Important APIs, types, and functions
- Test entry points: `test_snapshot_revert`, `test_snapshot_rm_basic`, `test_snapshot_revert_with_backing_file`, `test_snapshot_rm_rolling`, `test_snapshot_tree_basic`, expansion tests with/without backing file, `test_snapshot_mounted_filesystem`, `test_snapshot_prune`, `test_snapshot_prune_with_coalesce`, and `test_snapshot_trim_filesystem`.
- Helpers: `snapshot_revert_test`, `volume_expansion_with_snapshots_test`, `snapshot_mounted_filesystem_test`, `filesystem_trim_test`, and `wait_for_snap_size_no_less_than_value`.
- Uses `Snapshot`/`Data` helper objects for writing data, snapshot creation, checksum verification, and refuting data after revert.
- Uses `common.cmd` snapshot commands and controller feature toggles such as `set_unmap_mark_snap_chain_removed`.
- Filesystem-level helpers manage host namespace mount, mkfs, sync, fstrim, checksum, and process log reading.

## Control flow
Snapshot revert tests build ordered snapshots with random data, revert to earlier points, and assert later snapshot data disappears while earlier data remains. Removal/purge tests mark snapshots removed, wait for purge, and verify snapshot-info tree shape and data preservation. Tree tests build a branchy snapshot graph, revert to a node, remove many branches, purge, then verify surviving nodes and rejection when reverting to a removed snapshot.

Expansion tests create snapshots before and after expanding the volume, write into the expanded region, revert to a pre-expansion snapshot, continue writing to expanded space, and purge a snapshot that coalesces with a larger successor.

Mounted filesystem tests create and mount ext4 on the Longhorn block device from the host namespace, take snapshots with the `freeze` flag, inspect engine logs for freeze/unfreeze messages, then revert snapshots and remount to validate file presence/content. Trim tests build branch snapshots with mounted filesystem files, delete files, run `fstrim`, verify only head size shrinks first, enable unmap marking, retrim, and then verify deeper snapshots are marked removed and shrunk while branch data remains restorable.

## State and persistence behavior
The module validates snapshot metadata (`parent`, `children`, `removed`, `usercreated`, `size`), volume-head parentage, branch snapshots, backing-file initial content, device bytes and checksums, engine process logs, mounted filesystem files, snapshot sizes after trim/prune, and feature toggle state for unmap behavior. It uses explicit mount/unmount around frontend shutdown/revert because reverts detach the device.

## Dependencies and integration points
Dependencies include controller/replica fixtures, backing-file fixtures, snapshot tree helpers, host namespace access via `nsenter`, ext4 tooling, `mount`, `umount`, `findmnt`, `fstrim`, engine process logs, and Longhorn snapshot CLI commands. It integrates engine snapshot APIs, frontend lifecycle, filesystem freeze hooks, Linux discard/unmap behavior, and backing-image read paths.

## Risks and edge cases
- Timing-sensitive size checks rely on polling and minimum thresholds because filesystem allocation is not exact.
- Mounted filesystem tests depend on `/host/tmp` bind-mount conventions and privileged host namespace operations.
- Log-count assertions require exactly three freeze and unfreeze log entries; unrelated logging or retries can break the signal.
- Snapshot pruning checks encode exact size deltas such as 4096 bytes and depend on filesystem block size.
- Trim behavior is only run for ext4 because the default test volume size is too small for xfs.
- The module uses exact tree-shape assumptions that will catch legitimate metadata model changes.

## Test signals
Signals include correct snapshot lists/info maps, successful and failed reverts, retained data after purge/coalesce, expected `removed` flags, size reduction after prune/trim, zeroed expanded regions, freeze/unfreeze log counts, filesystem checksum matches after revert, and preserved branch snapshot content after unmap-trim removal.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/data/test_snapshot.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/data/test_upgrade.py -->
# sources/control-plane/longhorn-engine/integration/data/test_upgrade.py

## Purpose
This file validates live engine binary upgrade and rollback behavior while preserving volume data and frontend endpoint continuity.

## Important APIs, types, and functions
- Single test: `test_upgrade`.
- Uses `get_dev`, `verify_data`, `upgrade_engine`, `get_process_address`, `wait_for_process_running`, `get_controller_version_detail`, `cleanup_replica`, and `open_replica`.
- Constants identify current and upgrade binaries, volume/device names, size strings, and Longhorn dev directory.
- The controller client method `client_upgrade` points the test client at the new engine process address after a successful upgrade.

## Control flow
The test obtains a device from fixed replicas and a controller, writes data, starts the volume with the fixed replicas, then launches an upgrade engine using extra replica fixtures pointed at the same underlying volume data. After verifying data remains readable, it upgrades the controller client to the upgrade engine address, waits for the named process to be running, fetches version details, and verifies the frontend endpoint path.

It then tries an invalid upgrade back to the original binary with a bogus replica URL and expects a gRPC error/rollback without data loss. Finally it cleans and reopens the fixed replicas, starts an engine with the original binary, verifies data, upgrades the controller client back, and checks endpoint/version again.

## State and persistence behavior
The test observes persistent data across engine process swaps, replica cleanup/reopen, and controller client address changes. It also verifies the stable frontend device path under `LONGHORN_DEV_DIR` and process manager state after upgrade.

## Dependencies and integration points
It integrates the engine manager process API, controller gRPC API, fixed and extra replica fixtures, binary paths for current and upgrade engines, and the Longhorn frontend device. It depends on helper semantics that create upgrade processes without destroying the live device.

## Risks and edge cases
- The same-binary upgrade check is commented out, so only wrong-replica rollback is actively tested.
- The test assumes extra replica fixtures reference the same volume backing as the fixed replicas.
- Upgrade success is inferred from process running, version detail fetch, endpoint path, and data integrity; deeper version compatibility is not asserted.

## Test signals
Signals include unchanged data before/after upgrade and rollback attempts, `upgrade_e.spec.binary` matching the upgrade binary, gRPC error on invalid replica upgrade, successful process running state, readable version detail, and stable endpoint `LONGHORN_DEV_DIR/VOLUME_NAME`.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/data/test_upgrade.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/instance/__init__.py -->
# sources/control-plane/longhorn-engine/integration/instance/__init__.py

## Purpose
This package initializer is empty. It exists to mark `integration/instance` as a Python package for imports and pytest discovery context.

## Important APIs, types, and functions
No APIs, types, functions, imports, or side effects are defined.

## Control flow
There is no runtime control flow.

## State and persistence behavior
No state is initialized or persisted.

## Dependencies and integration points
Its integration role is structural only: package recognition for tests such as `test_launcher_basic.py`.

## Risks and edge cases
Because it is empty, risk is limited to import/package layout. Removing it could affect Python versions or tooling that still rely on explicit package markers.

## Test signals
There are no direct test signals in this file; successful imports and pytest collection indirectly validate it.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/instance/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/instance/test_launcher_basic.py -->
# sources/control-plane/longhorn-engine/integration/instance/test_launcher_basic.py

## Purpose
This module validates instance-manager process launch, listing, deletion, error handling, engine/replica wiring, engine upgrade basics, and revision-counter compatibility checks at the process-management layer.

## Important APIs, types, and functions
- Test entry points: `test_start_stop_replicas`, `test_process_creation_failure`, `test_one_volume`, `test_multiple_volumes`, skipped `test_engine_upgrade`, and `test_engine_replica_revision_counter_mismatch`.
- Helper: `engine_replica_mismatch`.
- Uses process helpers from `common.core`: `create_replica_process`, `create_engine_process`, `delete_process`, process/deletion waiters, device existence waiters, `upgrade_engine`, `get_process_address`, `cleanup_process`, and delayed replica client construction.
- Uses `ProcessManagerClient`, `ReplicaClient`, and `ControllerClient` wrappers.
- Constants define process states, base names, binary paths, size strings, and the replica instance manager address.

## Control flow
Replica process tests create ten temporary replica directories, create replica processes, verify each can be fetched and listed, then delete them in order and wait for process disappearance. Failure tests create processes with a nonexistent binary and assert all land in `PROC_STATE_ERROR`.

Volume tests create replica processes, derive `tcp://localhost:<port>` replica URLs from process status, create engine processes, assert frontend devices exist, and then delete engines and replicas while checking process list counts. The multiple-volume test repeats this for five volumes and verifies device deletion after engine removal.

The skipped upgrade test covers a process-manager-level upgrade path using an upgrade binary and old/new replica processes. The active revision-counter mismatch test runs two cases: engine revision counter enabled and disabled. Each case creates two replica processes with opposite revision-counter settings, creates replica data, starts an engine with matching setting, starts a volume with both URLs, and asserts the mismatched replica is `ERR` while the matched replica is `RW`.

## State and persistence behavior
The tests manage process-manager state maps, process specs/statuses, assigned port ranges, frontend device nodes, temporary replica directories, replica-created volume state, and controller replica mode state. Cleanup calls remove engine and replica processes after mismatch scenarios.

## Dependencies and integration points
The module integrates instance-manager process-manager gRPC clients, engine manager and replica manager fixtures, Longhorn process binaries, controller and replica RPC clients, local device path checks, and temporary filesystem directories.

## Risks and edge cases
- Process-list count assertions assume a clean process manager at test start.
- Device existence/deletion waits rely on frontend attach/detach timing.
- The skipped upgrade test is not a live safety net unless unskipped.
- Revision-counter mismatch checks rely on correct pairing between engine flag and replica flag, and clean teardown through `cleanup_process`.
- `test_process_creation_failure` expects process records to remain visible in error state rather than being removed immediately.

## Test signals
Signals include process spec names, `PROC_STATE_RUNNING`/`STOPPING`/`STOPPED`/`ERROR`, list lengths, device node existence/deletion, idempotent engine delete behavior, upgrade process state in skipped coverage, and controller replica modes `RW` versus `ERR` for revision-counter mismatch.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/instance/test_launcher_basic.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/__init__.py -->
# sources/control-plane/longhorn-engine/integration/rpc/__init__.py

## Purpose
This package initializer adjusts Python import search paths so generated gRPC files under `integration/rpc` can resolve their relative-style imports.

## Important APIs, types, and functions
- Imports `os` and `sys`.
- Appends `os.path.abspath(os.path.join(os.path.split(__file__)[0], "."))` to `sys.path`.

## Control flow
At import time, the module computes the absolute path of the `rpc` directory and appends it to `sys.path`.

## State and persistence behavior
The only state change is process-global mutation of `sys.path`. It is not persisted beyond the Python process.

## Dependencies and integration points
Generated protobuf/gRPC modules import packages such as `imrpc`, `bimrpc`, and other generated peers without fully qualified package paths. This initializer supports those imports when tests import the `rpc` package.

## Risks and edge cases
- Repeated imports can append duplicate path entries.
- Process-global `sys.path` mutation can shadow other packages named `imrpc`, `bimrpc`, or `ptypes`.
- The approach depends on local filesystem layout and should be kept in sync with generated code import style.

## Test signals
Successful import of generated modules and RPC client wrappers is the main signal. Failures would appear as `ModuleNotFoundError` during pytest collection or client construction.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/bimrpc/bimrpc_pb2.py -->
# sources/control-plane/longhorn-engine/integration/rpc/bimrpc/bimrpc_pb2.py

## Purpose
This generated protobuf module defines Python message classes and descriptors for `bimrpc/bimrpc.proto`, the backing image manager API used by Longhorn integration code.

## Important APIs, types, and functions
- Generated messages include `BackingImageSpec`, `BackingImageStatus`, `BackingImageResponse`, `DeleteRequest`, `GetRequest`, `ListResponse`, `VersionResponse`, `SyncRequest`, `SendRequest`, `FetchRequest`, `PrepareDownloadRequest`, `PrepareDownloadResponse`, `BackupCreateRequest`, `BackupStatusRequest`, and `BackupStatusResponse`.
- `ListResponse.backing_images` is a generated map from string to `BackingImageResponse`.
- `BackupCreateRequest.credential` is a generated map for credentials; labels are represented as repeated strings in this generated contract.
- `DESCRIPTOR` is registered through `_descriptor_pool.Default().AddSerializedFile(...)`, then `_builder` builds message classes into module globals.

## Control flow
The module has import-time generated setup only: import protobuf runtime, register the serialized file descriptor, build descriptors/messages, and optionally assign serialized offsets/options when Python descriptors are used.

## State and persistence behavior
It mutates the process-global protobuf descriptor pool and symbol database. It does not persist data itself; message instances are used by gRPC callers and servers.

## Dependencies and integration points
Depends on `google.protobuf` runtime and `google.protobuf.empty_pb2`. It pairs with `bimrpc_pb2_grpc.py`, whose stub/servicer serializers reference these message classes. It encodes the backing image manager service contract for delete/get/list/version/sync/send/fetch/download/backup/status/watch operations.

## Risks and edge cases
- This is generated code and should not be hand-edited; changes should come from the `.proto`.
- Runtime compatibility depends on the protobuf package version matching the generated style.
- API field names such as `gitCommit`, `buildDate`, and API version fields are part of the wire contract and can break callers if regenerated incompatibly.

## Test signals
Signals are import success, descriptor registration, message serialization/deserialization through `bimrpc_pb2_grpc`, and integration tests that call backing image manager APIs through clients built on this contract.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/bimrpc/bimrpc_pb2.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/bimrpc/bimrpc_pb2_grpc.py -->
# sources/control-plane/longhorn-engine/integration/rpc/bimrpc/bimrpc_pb2_grpc.py

## Purpose
This generated gRPC module defines client stubs, server base classes, registration helpers, and experimental static RPC helpers for `bimrpc.BackingImageManagerService`.

## Important APIs, types, and functions
- `BackingImageManagerServiceStub` exposes unary RPCs `Delete`, `Get`, `List`, `VersionGet`, `Sync`, `Send`, `Fetch`, `PrepareDownload`, `BackupCreate`, `BackupStatus`, and streaming `Watch`.
- `BackingImageManagerServiceServicer` provides unimplemented method stubs that set `grpc.StatusCode.UNIMPLEMENTED`.
- `add_BackingImageManagerServiceServicer_to_server` registers all service handlers with serializers/deserializers from `bimrpc_pb2` and `empty_pb2`.
- `BackingImageManagerService` offers experimental static wrappers for direct calls.

## Control flow
Stub construction binds channel methods to fully qualified RPC paths such as `/bimrpc.BackingImageManagerService/Delete`. Server registration builds a method handler dictionary and adds it as a generic handler. Base servicer methods only raise `NotImplementedError` until subclassed.

## State and persistence behavior
The module has no persistent storage. It stores bound callables on stub instances and registers service handlers against a supplied gRPC server.

## Dependencies and integration points
Depends on `grpc`, generated `bimrpc_pb2`, and `google.protobuf.empty_pb2`. It is the transport layer for backing image manager operations represented in `bimrpc_pb2.py`.

## Risks and edge cases
- Generated imports require the local `bimrpc` package path to be available, usually via package path setup.
- The watch method is `unary_stream`, so callers must handle iterator lifecycle.
- Hand edits would be lost on regeneration and could desynchronize serializers from message classes.

## Test signals
Import success, successful stub construction with a gRPC channel, correct method paths, and service calls against a backing image manager implementation validate this file.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/bimrpc/bimrpc_pb2_grpc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/controller/__init__.py -->
# sources/control-plane/longhorn-engine/integration/rpc/controller/__init__.py

## Purpose
This package initializer adjusts Python import paths for generated controller gRPC modules under `integration/rpc/controller`.

## Important APIs, types, and functions
- Imports `os` and `sys`.
- Appends the absolute controller package directory to `sys.path`.

## Control flow
The path append happens at import time using `os.path.split(__file__)[0]`.

## State and persistence behavior
The only state mutation is process-global `sys.path`; no persistent state is written.

## Dependencies and integration points
It supports generated controller modules that use relative-style imports and the `controller_client.py` wrapper that imports `ptypes.controller_pb2` and `ptypes.controller_pb2_grpc`.

## Risks and edge cases
Duplicate path entries can accumulate, and path mutation can shadow unrelated modules if names collide. Import correctness depends on generated file layout.

## Test signals
Successful import of `rpc.controller.controller_client.ControllerClient` and generated controller protobuf modules is the practical signal.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/controller/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/controller/controller_client.py -->
# sources/control-plane/longhorn-engine/integration/rpc/controller/controller_client.py

## Purpose
This wrapper provides a small Python client over the generated Longhorn controller gRPC service for integration tests. It normalizes request construction and maps controller replica messages into lightweight Python objects.

## Important APIs, types, and functions
- `ControllerClient.__init__(url, volume_name=None, instance_name=None)` creates an insecure gRPC channel, applies `IdentityValidationInterceptor`, and builds a `ControllerServiceStub`.
- Volume APIs: `volume_get`, `volume_start`, `volume_shutdown`, `volume_snapshot`, `volume_revert`, `volume_expand`, `volume_frontend_start`, `volume_frontend_shutdown`, and `version_detail_get`.
- Replica APIs: `replica_list`, `replica_get`, `replica_create`, `replica_delete`, and `replica_update`.
- Other APIs: `metrics_get` and `client_upgrade`.
- `ControllerReplicaInfo` exposes `address` and string `mode` using `controller_pb2.ReplicaMode.Name`.

## Control flow
Each method builds the corresponding protobuf request and immediately invokes the generated stub. `replica_list` transforms the repeated controller response into `ControllerReplicaInfo` objects. `client_upgrade` replaces the client's address/channel/stub with a new insecure channel to support engine upgrade tests.

## State and persistence behavior
The client stores `address`, `channel`, and `stub` in memory. It does not own server state but can create/delete replicas, start/shutdown frontend and volumes, expand volumes, and change replica modes through RPC side effects. The identity interceptor may add validation metadata when volume/instance names are supplied.

## Dependencies and integration points
Depends on `grpc`, generated `ptypes.controller_pb2` and `controller_pb2_grpc`, `google.protobuf.empty_pb2`, and `common.interceptor.IdentityValidationInterceptor`. It is used broadly by data and instance integration tests to interact with live Longhorn engine controllers.

## Risks and edge cases
- `volume_snapshot` uses a mutable default `labels={}`; the method does not mutate it, but the pattern is risky if changed later.
- `client_upgrade` recreates a raw insecure channel without reapplying the identity interceptor or preserving identity parameters.
- `replica_update` builds nested `ControllerReplica`/`ReplicaAddress` messages manually; field-shape changes in generated protobufs would break it.
- No deadlines are set on RPCs, so hung controller calls can stall tests.

## Test signals
Signals include successful volume start/shutdown/expand/frontend operations, returned replica modes, correct address after upgrade, metrics/version retrieval, and expected gRPC errors in negative upgrade/revert paths.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/controller/controller_client.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/disk/__init__.py -->
# sources/control-plane/longhorn-engine/integration/rpc/disk/__init__.py

## Purpose
This package initializer is empty. It marks `integration/rpc/disk` as a Python package.

## Important APIs, types, and functions
No APIs, imports, functions, or side effects are defined.

## Control flow
There is no runtime control flow.

## State and persistence behavior
No state is initialized or persisted.

## Dependencies and integration points
Its structural role is to support imports of disk RPC client code such as `rpc.disk.disk_client`.

## Risks and edge cases
Removing it could affect import behavior for tooling or Python execution modes that depend on explicit package markers.

## Test signals
Successful import of disk client modules is the indirect signal.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/disk/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/disk/disk_client.py -->
# sources/control-plane/longhorn-engine/integration/rpc/disk/disk_client.py

## Purpose
This wrapper provides a simple gRPC client for the instance-manager disk service used in Longhorn integration tests.

## Important APIs, types, and functions
- `DiskClient.__init__(url)` creates an insecure channel and `DiskServiceStub`.
- `version_get` calls service version.
- `disk_create`, `disk_get`, and `disk_delete` construct the corresponding disk protobuf requests.
- `disk_replica_instance_list` lists replica instances on a disk.
- `disk_replica_instance_delete` deletes a named replica instance from a disk.

## Control flow
Each public method synchronously invokes one generated stub method with a protobuf request from `imrpc.disk_pb2`. No response transformation is performed; generated protobuf responses are returned directly.

## State and persistence behavior
The client stores only address/channel/stub in memory. Server-side side effects include creating/deleting disks and deleting replica-instance records. No local persistence exists.

## Dependencies and integration points
Depends on `grpc`, `imrpc.disk_pb2`, `imrpc.disk_pb2_grpc`, and `empty_pb2`. It integrates tests with the instance-manager disk service contract.

## Risks and edge cases
- `disk_replica_instance_delete` passes `replcia_instance_name`, matching the misspelled generated proto field. This typo is wire-contract significant; correcting it only in the client would break calls until the proto changes.
- No RPC timeouts/deadlines are set.
- The wrapper does not validate disk type/name/uuid consistency before issuing destructive delete calls.

## Test signals
Signals include successful disk create/get/delete responses, version response fields, replica instance list contents, and expected server-side deletion of replica instances.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/disk/disk_client.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/imrpc/__init__.py -->
# sources/control-plane/longhorn-engine/integration/rpc/imrpc/__init__.py

## Purpose
This package initializer is empty. It marks generated instance-manager RPC modules as an importable `imrpc` package.

## Important APIs, types, and functions
No APIs, imports, functions, or side effects are defined.

## Control flow
There is no runtime control flow.

## State and persistence behavior
No state is initialized or persisted.

## Dependencies and integration points
It supports imports such as `from imrpc import disk_pb2` and generated peer imports in gRPC modules.

## Risks and edge cases
Package recognition depends on this file in environments that do not use implicit namespace packages.

## Test signals
Successful import of generated `imrpc` protobuf and gRPC modules is the indirect signal.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/imrpc/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/imrpc/common_pb2.py -->
# sources/control-plane/longhorn-engine/integration/rpc/imrpc/common_pb2.py

## Purpose
This generated protobuf module defines shared instance-manager enums used by other `imrpc` contracts.

## Important APIs, types, and functions
- Enum `BackendStoreDriver` with values `v1` and `v2`.
- Enum `DataEngine` with values `DATA_ENGINE_V1` and `DATA_ENGINE_V2`.
- `DESCRIPTOR` registers `imrpc/common.proto` with the protobuf descriptor pool.

## Control flow
At import time, protobuf runtime objects register the serialized descriptor and build enum descriptors into module globals.

## State and persistence behavior
The file mutates the process-global protobuf descriptor pool. It stores no external or persistent state.

## Dependencies and integration points
Depends on `google.protobuf` descriptor/builder runtime. It is imported by generated modules such as `instance_pb2.py` and `proxy_pb2.py` to share backend-store and data-engine enum types.

## Risks and edge cases
- The enum value names `v1`/`v2` are lowercase, which can be surprising for Python callers.
- Backward compatibility is important because these enums are embedded in multiple service requests.
- This generated file should be regenerated from `.proto`, not hand-edited.

## Test signals
Import success and successful serialization of messages that include `BackendStoreDriver` or `DataEngine` validate this module indirectly.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/imrpc/common_pb2.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/imrpc/common_pb2_grpc.py -->
# sources/control-plane/longhorn-engine/integration/rpc/imrpc/common_pb2_grpc.py

## Purpose
This generated gRPC companion for `imrpc/common.proto` contains only the generated header/import because the common proto defines shared enums but no services.

## Important APIs, types, and functions
No stubs, servicers, registration helpers, or methods are defined. It imports `grpc`.

## Control flow
Import-time behavior is limited to importing `grpc`.

## State and persistence behavior
No state is initialized except the normal imported module reference.

## Dependencies and integration points
It exists for generator consistency and may satisfy code that expects every proto to have a `_pb2_grpc.py` module. Shared message/enum definitions live in `common_pb2.py`.

## Risks and edge cases
There is no runtime RPC surface here. Risk is limited to import compatibility if generated file presence is assumed.

## Test signals
Successful import is the only direct signal.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/imrpc/common_pb2_grpc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/imrpc/disk_pb2.py -->
# sources/control-plane/longhorn-engine/integration/rpc/imrpc/disk_pb2.py

## Purpose
This generated protobuf module defines the instance-manager disk service messages and `DiskType` enum.

## Important APIs, types, and functions
- Messages: `Disk`, `ReplicaInstance`, `DiskCreateRequest`, `DiskGetRequest`, `DiskDeleteRequest`, `DiskReplicaInstanceListRequest`, `DiskReplicaInstanceListResponse`, `DiskReplicaInstanceDeleteRequest`, and `DiskVersionResponse`.
- Enum `DiskType` with `filesystem` and `block`.
- `DiskReplicaInstanceListResponse.replica_instances` is a map from string to `ReplicaInstance`.
- `DiskReplicaInstanceDeleteRequest` contains the misspelled field `replcia_instance_name`, which the client must use.

## Control flow
The module registers the serialized `imrpc/disk.proto` descriptor, builds message/enum classes, and assigns serialized metadata at import time.

## State and persistence behavior
It mutates the process-global protobuf descriptor pool and symbol registry only. Disk state is remote service state represented by message instances.

## Dependencies and integration points
Depends on protobuf runtime and `empty_pb2`. It pairs with `disk_pb2_grpc.py` and the handwritten `rpc/disk/disk_client.py` wrapper.

## Risks and edge cases
- The misspelled field name is part of the generated Python API and likely the wire-compatible proto; changing it requires coordinated proto/server/client regeneration.
- Disk sizes and block counts are 64-bit integer fields, so callers must avoid lossy conversions.
- Generated code should not be hand-edited.

## Test signals
Signals include import success, construction of disk request/response messages, map field behavior for replica instances, and successful use through `DiskServiceStub`.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/imrpc/disk_pb2.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/imrpc/disk_pb2_grpc.py -->
# sources/control-plane/longhorn-engine/integration/rpc/imrpc/disk_pb2_grpc.py

## Purpose
This generated gRPC module defines the transport bindings for `imrpc.DiskService`.

## Important APIs, types, and functions
- `DiskServiceStub` exposes unary RPCs `DiskCreate`, `DiskDelete`, `DiskGet`, `DiskReplicaInstanceList`, `DiskReplicaInstanceDelete`, and `VersionGet`.
- `DiskServiceServicer` provides unimplemented server methods.
- `add_DiskServiceServicer_to_server` registers method handlers with serializers/deserializers.
- `DiskService` provides experimental static RPC helpers.

## Control flow
Stub construction binds request serializers and response deserializers to paths such as `/imrpc.DiskService/DiskCreate`. Server registration builds a handler map and attaches it to a supplied gRPC server. Default servicer methods raise unimplemented errors.

## State and persistence behavior
No persistent state is maintained. Stub instances store bound channel callables; servers receive registered handlers.

## Dependencies and integration points
Depends on `grpc`, `google.protobuf.empty_pb2`, and generated `imrpc.disk_pb2`. The handwritten `DiskClient` is a thin wrapper around this stub.

## Risks and edge cases
- No service-level retry/deadline behavior is embedded; callers handle call lifecycle.
- Generated imports require the `imrpc` package path to be resolvable.
- Hand edits would desynchronize from proto-generated message classes.

## Test signals
Signals include successful import/stub construction, correct method path binding, and integration tests successfully creating/getting/deleting disks or listing/deleting replica instances.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/imrpc/disk_pb2_grpc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/imrpc/imrpc_pb2.py -->
# sources/control-plane/longhorn-engine/integration/rpc/imrpc/imrpc_pb2.py

## Purpose
This generated protobuf module defines the process-manager API messages used by Longhorn instance-manager integration tests.

## Important APIs, types, and functions
- Messages: `ProcessSpec`, `ProcessStatus`, `ProcessCreateRequest`, `ProcessDeleteRequest`, `ProcessGetRequest`, `ProcessResponse`, `ProcessListRequest`, `ProcessListResponse`, `LogRequest`, `ProcessReplaceRequest`, `LogResponse`, and `VersionResponse`.
- `ProcessStatus.conditions` is a string-to-bool map.
- `ProcessListResponse.processes` is a string-to-`ProcessResponse` map.
- `ProcessResponse.deleted` marks deleted process records.
- `VersionResponse` carries instance-manager and proxy API version/min-version fields.

## Control flow
The module registers the serialized `imrpc/imrpc.proto` descriptor and builds message classes at import time. There is no custom control flow beyond generated protobuf setup.

## State and persistence behavior
It registers descriptors in memory. Actual process state lives in the remote instance manager and is represented by message instances.

## Dependencies and integration points
Depends on protobuf runtime and `empty_pb2`. It pairs with `imrpc_pb2_grpc.py` and handwritten process manager clients used by launcher tests and common helpers.

## Risks and edge cases
- The generated service package path is `/ProcessManagerService/...` rather than `/imrpc.ProcessManagerService/...`, so clients and servers must agree on this path.
- Map field semantics may hide ordering; tests should avoid assuming process map order.
- Generated code should be regenerated, not hand-edited.

## Test signals
Signals include import success, correct construction of process specs/responses, process list map behavior, and gRPC serialization through `ProcessManagerServiceStub`.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/imrpc/imrpc_pb2.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/imrpc/imrpc_pb2_grpc.py -->
# sources/control-plane/longhorn-engine/integration/rpc/imrpc/imrpc_pb2_grpc.py

## Purpose
This generated gRPC module defines client/server bindings for the instance-manager `ProcessManagerService`.

## Important APIs, types, and functions
- `ProcessManagerServiceStub` exposes unary RPCs `ProcessCreate`, `ProcessDelete`, `ProcessGet`, `ProcessList`, `ProcessReplace`, and `VersionGet`; streaming RPCs `ProcessLog` and `ProcessWatch`.
- `ProcessManagerServiceServicer` defines unimplemented server methods.
- `add_ProcessManagerServiceServicer_to_server` registers method handlers.
- `ProcessManagerService` provides experimental static RPC helpers.

## Control flow
Stub initialization binds channel methods to paths such as `/ProcessManagerService/ProcessCreate`. Server registration maps method names to unary or unary-stream handlers. Default servicer methods set `UNIMPLEMENTED` and raise.

## State and persistence behavior
The module stores no persistent state. Stub instances hold channel callables; process state is remote in instance-manager implementations.

## Dependencies and integration points
Depends on `grpc`, `empty_pb2`, and generated `imrpc_pb2`. It backs process-manager clients used by `test_launcher_basic.py` and common lifecycle helpers.

## Risks and edge cases
- The service path lacks the `imrpc.` package prefix, unlike disk/instance/proxy services; this is contractually important.
- `ProcessLog` and `ProcessWatch` are streaming APIs, so consumers need to manage iterators and cancellation.
- No deadlines or retries are generated.

## Test signals
Signals include successful process create/delete/get/list calls, process log/watch streams, replacement calls, version responses, and the launcher tests' observed process state transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/imrpc/imrpc_pb2_grpc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/imrpc/instance_pb2.py -->
# sources/control-plane/longhorn-engine/integration/rpc/imrpc/instance_pb2.py

## Purpose
This generated protobuf module defines the newer instance service data model for process and SPDK instances in Longhorn instance-manager.

## Important APIs, types, and functions
- Messages: `ProcessInstanceSpec`, `SpdkInstanceSpec`, `InstanceSpec`, `InstanceStatus`, `InstanceCreateRequest`, `InstanceDeleteRequest`, `InstanceGetRequest`, `InstanceResponse`, `InstanceListResponse`, `InstanceLogRequest`, and `InstanceReplaceRequest`.
- `SpdkInstanceSpec.replica_address_map` is a generated string-to-string map.
- `InstanceStatus.conditions` is a string-to-bool map.
- `InstanceSpec` carries name, type, volume name, port metadata, process/SPDK one-of-like nested specs, and `data_engine`.
- Some `backend_store_driver` fields are marked deprecated in generated options.

## Control flow
At import time, the module imports shared `common_pb2` and process-manager `imrpc_pb2`, registers `imrpc/instance.proto`, builds descriptors/messages, and applies serialized options.

## State and persistence behavior
It mutates the protobuf descriptor pool. Actual instance lifecycle state is remote and represented by generated messages.

## Dependencies and integration points
Depends on protobuf runtime, `empty_pb2`, shared `imrpc.common_pb2`, and `imrpc.imrpc_pb2` for `LogResponse`/`VersionResponse` references in the gRPC companion. It supports process-backed and SPDK-backed instance management.

## Risks and edge cases
- Deprecated `backend_store_driver` fields remain in request messages for compatibility; callers should prefer `data_engine` where applicable.
- Both process and SPDK specs are ordinary fields, so caller/server validation must enforce valid combinations.
- Generated code should not be hand-edited.

## Test signals
Signals include import success, correct construction/serialization of instance requests, map-field behavior for SPDK replica addresses and conditions, and use through `InstanceServiceStub`.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/imrpc/instance_pb2.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/imrpc/instance_pb2_grpc.py -->
# sources/control-plane/longhorn-engine/integration/rpc/imrpc/instance_pb2_grpc.py

## Purpose
This generated gRPC module defines transport bindings for `imrpc.InstanceService`.

## Important APIs, types, and functions
- `InstanceServiceStub` exposes unary RPCs `InstanceCreate`, `InstanceDelete`, `InstanceGet`, `InstanceList`, `InstanceReplace`, and `VersionGet`; streaming RPCs `InstanceLog` and `InstanceWatch`.
- `InstanceServiceServicer` provides unimplemented base methods.
- `add_InstanceServiceServicer_to_server` registers service handlers.
- `InstanceService` provides experimental static RPC helper methods.

## Control flow
Stub initialization binds serializers/deserializers to `/imrpc.InstanceService/...` method paths. Server registration creates unary and streaming handlers. Default servicer implementations set unimplemented status and raise.

## State and persistence behavior
No persistent state is stored. Stub instances hold channel-bound methods; server instances receive registered handlers.

## Dependencies and integration points
Depends on `grpc`, `empty_pb2`, generated `imrpc.imrpc_pb2` for log/version response types, and `imrpc.instance_pb2` for request/response types. It is the transport surface for instance lifecycle APIs in newer instance-manager flows.

## Risks and edge cases
- `InstanceWatch` streams `Empty` messages according to this generated contract, unlike process watch which streams `ProcessResponse`; consumers must not assume identical semantics.
- Streaming methods require iterator lifecycle management.
- Generated import paths require `imrpc` to be importable.

## Test signals
Signals include import/stub construction, successful instance create/delete/get/list/replace calls against an implementation, streaming log/watch behavior, and version responses.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/imrpc/instance_pb2_grpc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/imrpc/proxy_pb2.py -->
# sources/control-plane/longhorn-engine/integration/rpc/imrpc/proxy_pb2.py

## Purpose
This generated protobuf module defines the instance-manager proxy engine API, which forwards engine operations such as volume control, snapshots, backups/restores, replica rebuilds, metrics, and remounts through a proxy service.

## Important APIs, types, and functions
- Core selector: `ProxyEngineRequest` carries engine address, engine name, volume name, backend-store driver, and data engine.
- Volume messages include version/get responses, expand requests, frontend start requests, snapshot requests/responses, unmap mark, max snapshot count/size setters.
- Snapshot messages include list response, `EngineSnapshotDiskInfo`, revert/purge/purge-status, clone/clone-status, remove, hash/hash-status, backup/backup-status.
- Restore messages include backup restore request/response/status and finish request.
- Replica messages include add/list/verify-rebuild/rebuild-status/remove/mode-update.
- Other messages include metrics get response and `RemountVolumeRequest`.
- Imports generated `ptypes.controller_pb2`, `ptypes.syncagent_pb2`, and shared `imrpc.common_pb2`.

## Control flow
The module performs generated protobuf import-time setup: registers the serialized `imrpc/proxy.proto` descriptor, builds message classes, map-entry descriptors, and serialized options. There is no handwritten logic.

## State and persistence behavior
It stores no external state, but message classes represent high-impact remote state transitions: volume expansion/frontend lifecycle, snapshot graph mutation, backup/restore task state, replica membership/modes, rebuild status, and metrics. Descriptor registration mutates the in-process protobuf registry.

## Dependencies and integration points
Depends on protobuf runtime, `empty_pb2`, Longhorn controller/sync-agent protobuf types, and shared `imrpc.common_pb2`. It is consumed by the generated proxy gRPC companion and any proxy clients that need to drive engine operations through instance-manager rather than connecting directly to controllers.

## Risks and edge cases
- The module is large and generated; manual edits are brittle and should be replaced by `.proto` regeneration.
- Some fields preserve compatibility concerns, including deprecated backend-store-driver usage and data-engine routing.
- Many request messages wrap ptypes controller requests; API drift in imported `ptypes` modules can break proxy serialization.
- Backup/restore status includes raw task errors and map statuses, so callers must handle partial per-replica failure states.

## Test signals
Signals include import success, construction/serialization of proxy requests, compatibility with `proxy_pb2_grpc` serializers, and higher-level tests that exercise snapshot, backup/restore, replica add/rebuild, expansion, metrics, and remount operations through proxy services.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/imrpc/proxy_pb2.py -->
