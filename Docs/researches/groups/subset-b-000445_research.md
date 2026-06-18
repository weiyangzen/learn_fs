# subset-b-000445 Research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/pool.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/pool.go

This file implements Ceph pool lifecycle helpers for the Rook Ceph client package. Its public API covers listing pool summaries, reading pool details and stats, creating replicated or erasure-coded pools, deleting pools, setting pool properties/quotas/replica size, and cleaning unused CRUSH rules.

Important types are `CephStoragePoolSummary`, `CephStoragePoolDetails`, `CephStoragePoolStats`, and `PoolStatistics`, all JSON-bound to Ceph CLI or RBD CLI output. Creation flows route through `CreatePoolWithPGs()`: validate name, override applications for built-in pools, dispatch replicated versus erasure-coded, create EC profiles when needed, then set common properties. Replicated pools coordinate CRUSH rule creation/update under `crushRuleMutex` so `CleanupUnusedCrushRules()` cannot delete a rule between creation and pool attachment.

State is persisted in Ceph itself through `ceph osd pool`, `ceph osd crush`, `rbd pool stats`, pool quotas, pool app tags, mirroring settings, and temporary CRUSH map files. Integration points include Ceph command wrappers, erasure-code profile helpers, CRUSH map helpers, mirroring/snapshot scheduling helpers, Kubernetes resource quantity parsing, and cluster stretch/hybrid storage specs.

Risks center on CLI output shape, malformed multi-object JSON from `osd pool get all`, CRUSH cleanup races, partial failures in property application where some errors are logged but reconciliation continues, and destructive pool deletion. Tests in `pool_test.go` exercise EC/replicated creation, application tags, CRUSH update/cleanup behavior, statistics parsing, replica size confirmation flags, stretch/two-step/hybrid CRUSH rules, and optional `crushtool` paths.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/pool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/pool_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/pool_test.go

This test file validates the pool helper behavior by driving mocked Ceph/RBD commands and checking command arguments, branch decisions, and parsed results. It is the main signal for the pool creation and CRUSH rule logic in `pool.go`.

The tests cover EC pool creation with and without overwrite support, compression property application, application tag idempotency, replicated pool creation with failure domains, crush roots, device classes, and compression modes. `TestUpdateFailureDomain` checks when CRUSH updates are skipped, when stretch clusters bypass updates, and when a new failure-domain rule is created. `TestCleanupUnusedCrushRules` proves cleanup preserves in-use rules and `replicated_rule`, and `TestCleanupUnusedCrushRulesNoPools` protects the initial-cluster case where deleting defaults would be dangerous.

State is represented through mocked command output rather than a real Ceph cluster. The tests verify integration contracts with `ceph osd pool`, `ceph osd crush`, `rbd pool stats`, and `crushtool` where available. `hasCrushtool()` conditionally runs tests that need local CRUSH map compile/decompile binaries.

Risks surfaced include reliance on exact CLI argument order, map iteration differences avoided by targeted assertions, and gaps around real concurrent `crushRuleMutex` behavior. The file is strong at unit-level command construction and parsing but does not simulate real Ceph side effects or rollback from partially applied pool settings.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/pool_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/rados.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/rados.go

This file provides low-level RADOS object helpers used by higher-level Rook controllers for object locks, namespace object detection, and idempotent object deletion.

The lock API is `RadosLockObject()` and `RadosUnlockObject()`. Lock creation generates a random hex cookie, calls `rados lock get` with pool, namespace, tag, cookie, and duration, and returns the cookie as the caller's unlock handle. Unlock first queries `radosObjectLockInfo()`, treats mismatched locks or absent cookies as already-unlocked success, and uses `rados lock break` only when it finds a locker with the matching cookie. `findLockerWithCookie()` is a small lookup helper. `RadosNamespaceHasObjects()` builds finalized rados arguments and shells through `head -c 1` to avoid buffering an entire namespace listing. `RadosRemoveObject()` stats before removing and treats non-timeout stat errors as the object already being absent.

State is in RADOS object locks and objects; no Kubernetes state is written. Dependencies include cryptographic randomness, JSON parsing of lock info, command finalization, `NewRadosCommand`, and Ceph command timeouts.

Risks include shell command construction in `RadosNamespaceHasObjects()`, lock-cookie collision assumptions, and broad idempotency that treats most stat errors as absence. `rados_test.go` focuses on removal behavior, including timeout propagation, stat idempotency, remove errors, and successful removal.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/rados.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/rados_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/rados_test.go

This file tests `RadosRemoveObject()` using the mock executor and a minimal cluster context. It verifies the intended idempotent object deletion contract without requiring a real RADOS cluster.

`TestRadosRemoveObject` defines a helper that creates a `clusterd.Context` and `ClusterInfo`, then runs four subtests. The timeout case returns a fake timeout from the initial `stat` and asserts the wrapped error is still detectable by `exec.IsTimeout`. The stat-error case asserts that any non-timeout stat failure is treated as "already gone" and returns nil. The remove-error case makes `stat` succeed and `rm` fail, proving delete failures are returned. The success case verifies both `stat` and `rm` commands run with `--pool`, `--namespace`, and object name in the expected positions.

State is only mocked command state. The test integrates with Rook's executor test package and timeout classification helper. It does not cover object locking, namespace listing, shell piping, or JSON lock parsing. The main risk captured is preserving idempotency while still distinguishing timeout failures from absence-like stat failures.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/rados_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/radosnamespace.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/radosnamespace.go

This file manages RBD/RADOS namespaces within a pool. It exposes create, delete, list, and internal statistics checks used by pool deletion safety and namespace reconciliation.

`CreateRadosNamespace()` runs `rbd namespace create --pool --namespace`, treating `EEXIST` as success. `getRadosNamespaceStatistics()` runs `rbd pool stats --pool --namespace` with JSON output and treats `ENOENT` as an empty `PoolStatistics`. `checkForImagesInRadosNamespace()` reports whether images or snapshots exist. `DeleteRadosNamespace()` refuses deletion when the stats check reports images, then runs `rbd namespace remove`, treating `ENOENT` as successful absence. `ListRadosNamespacesInPool()` parses `rbd namespace list` JSON objects into a string slice.

State is persisted in Ceph's RBD namespace metadata and queried via RBD CLI. Dependencies include `PoolStatistics` from `pool.go`, syscall exit-code interpretation through `exec.ExitStatus`, and shared command wrappers. Integration points include `IsPoolEmpty()` in `pool.go`, which calls the image check for each namespace before deleting a pool.

Risks include interpreting exit codes consistently across RBD versions, returning `containsImages` with wrapped errors during delete preflight, and not checking trash counts in emptiness logic. There is no dedicated test file in this work item for namespace creation/deletion/listing, so coverage is indirect through pool emptiness logic and command-wrapper conventions.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/radosnamespace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/status.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/status.go

This file models and queries `ceph status` JSON, then provides health predicates used by upgrades and filesystem orchestration.

The core data structures are `CephStatus`, `HealthStatus`, `CheckMessage`, `MonMap`, `MgrMap`, `OsdMap`, `PgMap`, `Fsmap`, and nested entries matching Ceph status JSON. `Status()` uses `NewCephCommand` for normal admin command execution. `StatusWithUser()` finalizes explicit `ceph status --format json` args and returns richer command-output errors. `IsClusterClean()` compiles an optional PG-state regex, calls `isClusterClean()`, and reports a message plus boolean. The default regex accepts active clean, deep scrubbing, snaptrim, and snaptrim-wait variants. `getMDSRank()` finds an MDS by filesystem name while tolerating standby cases. `MdsActiveOrStandbyReplay()` allows active, standby-replay, and standby states. `IsCephHealthy()` treats `HEALTH_WARN` and `HEALTH_OK` as acceptable. `MuteHealthWarning()` best-effort mutes sticky health warnings.

State is read from Ceph and health mutes are persisted in Ceph monitor state. Dependencies are Ceph command wrappers, JSON decoding, regex matching, and shared logging.

Risks include partial modeling of status JSON, using array index rather than rank value in `getMDSRank()`, and broad health acceptance of warnings. `status_test.go` validates JSON unmarshalling, PG clean logic, MDS rank lookup, health-state decisions, and non-panicking mute behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/status_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/status_test.go

This test file verifies the status JSON model and health helper decisions. It uses static Ceph status JSON and direct helper calls to avoid a live cluster.

`TestStatusMarshal` unmarshals a Luminous-era `ceph status -f json` fixture and checks health checks, monitor map fields, OSD map counts, near-full state, and PG map counters. `TestIsClusterClean` builds synthetic PG states to check that all PGs must match the healthy regex and sum to `NumPgs`; it also verifies custom regex behavior does not accidentally mark mixed states clean. `TestGetMDSRank` parses a Nautilus-style fsmap fixture and asserts rank lookup. `TestIsCephHealthy` confirms `HEALTH_WARN` and `HEALTH_OK` are accepted and `HEALTH_ERR` is rejected. `TestMuteHealthWarning` ensures the command is built as `ceph health mute <warning> --sticky` and that command failure is logged rather than propagated.

The test signal is strongest for JSON compatibility and pure helper behavior. It does not exercise live command execution, custom regex compile errors, or all MDS transition branches. It documents that warning health is considered good enough for certain upgrade checks.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/status_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/subvolumegroup.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/subvolumegroup.go

This file manages CephFS subvolume groups and CSI cleanup helpers for subvolumes, snapshots, clones, and OMAP entries.

`CreateCephFSSubVolumeGroup()` builds `ceph fs subvolumegroup create` arguments from quota and data-pool layout, probes existing group info, resizes when an existing quota differs, and then creates the group. `resizeCephFSSubVolumeGroup()` uses `--no-shrink`. `getCephFSSubVolumeGroupInfo()` parses JSON quota, usage, and data-pool details. `DeleteCephFSSubVolumeGroup()` intentionally returns raw command errors so callers can inspect exit status. `PinCephFSSubVolumeGroup()` validates pinning, selects one of distributed/export/random/default distributed settings, and runs `ceph fs subvolumegroup pin`.

The pin validator enforces only one pinning type, export range `-1..256`, distributed values `0` or `1`, and random `0.0..1.0`. CSI cleanup helpers use `rados getomapval`, `rm`, and `rmomapkey`, plus `ceph fs subvolume rm`, snapshot rm, and clone cancel.

State is CephFS subvolume-group metadata, quotas, pinning state, RADOS OMAP keys/values, and subvolume/snapshot/clone records. Risks include creating after resize even when the group already exists, string parsing of `getomapval`, and partial coverage of CLI error semantics. `subvolumegroup_test.go` covers pin validation only.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/subvolumegroup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/subvolumegroup_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/subvolumegroup_test.go

This focused test file validates `validatePinningValues()` for CephFS subvolume-group pinning. It is the only direct test signal in this work item for `subvolumegroup.go`.

`TestValidatePinningValues` checks accepted and rejected distributed values, accepted and rejected random values, a pair of cases intended to cover export validation, multiple pinning types at once, and the no-pinning case. The important behavior under test is that only one pinning strategy may be set and each strategy is range-limited before CLI arguments are generated.

State is pure in-memory CRD spec data; no Ceph commands are mocked here. The test integrates with the Ceph API type `CephFilesystemSubVolumeGroupSpecPinning` and `testify/assert`.

One notable risk is that the "export" cases assign `Distributed` instead of `Export`, so export-specific range checks are not actually exercised despite the comments. The file also does not test create, resize, delete, OMAP cleanup, subvolume deletion, snapshot deletion, or clone cancellation command construction.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/subvolumegroup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/test/info.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/test/info.go

This helper file supports Ceph client tests by creating minimal local Ceph config material and synthetic `ClusterInfo` instances without importing higher-level test packages.

`CreateConfigDir()` creates a config directory, writes `client.admin.keyring` and `mon.keyring` with test keys, and wraps filesystem errors. `CreateTestClusterInfo()` constructs a `client.ClusterInfo` with FSID, namespace, monitor secret, admin credentials, internal/external monitor maps, owner info, and context. It populates up to five monitor IDs from a fixed list and assigns endpoints `1.2.3.N:3300`, then calls `SetName()` with the namespace.

State is test-local filesystem content and in-memory cluster metadata. Dependencies include `os`, `path`, `context`, Rook Ceph client types, and owner-reference helpers. Integration points are tests that need realistic config paths, keyrings, monitor maps, or owner information while avoiding cyclic dependencies.

Risks are mostly test-scaffold limitations: only five monitors are supported, credentials are hard-coded fixtures, and the generated endpoints are not meant to represent all messenger variants. There are no direct tests for this file in the work item, but it is a foundational fixture for other client tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/test/info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/test/mon.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/test/mon.go

This helper file generates JSON monitor-status responses for tests that need monitors in quorum. It keeps monitor fixtures near the client package while avoiding dependency cycles.

`MonInQuorumResponse()` returns a `client.MonStatusResponse` with one monitor named `a`, rank `0`, address `1.2.3.1`, and quorum `[0]`. `MonInQuorumResponseFromMons()` builds a response from a map of `MonInfo`, assigning incrementing ranks and quorum entries while deriving addresses from the loop index. `MonInQuorumResponseMany()` creates a response with monitors named `rook-ceph-monN`; it loops from zero through `count`, so it returns `count+1` monitor entries while quorum contains only rank `0`.

State is generated JSON only. Dependencies are `encoding/json`, `fmt`, and Ceph client monitor types. Integration points are monitor quorum tests and reconciliation code that parse `MonStatusResponse`.

Risks include nondeterministic map iteration order in `MonInQuorumResponseFromMons()` and the off-by-one-looking inclusive loop in `MonInQuorumResponseMany()`. Serialization errors are ignored because fixtures are built from marshalable structs. There are no direct tests here; value comes from consumers that parse the generated JSON.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/test/mon.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/upgrade.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/upgrade.go

This file provides upgrade safety helpers for Ceph daemon versions and ok-to-stop/ok-to-continue checks.

Version APIs include `GetCephMonVersion()` over `ceph version`, `GetAllCephDaemonVersions()` over `ceph versions`, and `LeastUptodateDaemonVersion()` which selects the lowest parsed version for a daemon type. `EnableReleaseOSDFunctionality()` runs `ceph osd require-osd-release`. `OkToStop()` handles special mon and OSD small-cluster bypasses, then retries `okToStopDaemon()` with daemon-specific retry config. `OkToContinue()` currently adds MDS-specific post-checks through `okToContinueMDSDaemon()`, which waits for active or standby-replay/standby MDS state.

OSD bypass helpers use `OsdListNum()`, `HostTree()`, and `buildHostListFromTree()` to skip ok-to-stop in fewer-than-three-OSD clusters, all-in-one host layouts, or missing-host CRUSH maps. `daemonMapEntry()` maps Ceph version JSON fields to daemon-type strings. State is read from Ceph version, OSD list, OSD tree, and status; no Kubernetes state is written.

Risks include conservative bypasses that allow upgrades without Ceph ok-to-stop, version selection over unordered maps, and dependency on CRUSH tree shape. `upgrade_test.go` covers command construction, retry config, daemon-map lookup, host filtering, OSD check decisions, and deterministic least-version selection.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/upgrade.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/upgrade_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/upgrade_test.go

This test file validates upgrade helpers, especially command wiring and edge-case decisions for OSD and version handling.

Tests assert `ceph version`, `ceph versions`, and `ceph osd require-osd-release` command construction. `TestOkToStopDaemon` checks daemon ok-to-stop calls and no-error behavior. `TestOkToContinue` verifies non-MDS daemon types do not run extra checks. `TestFindFSName`, `TestDaemonMapEntry`, and `TestBuildHostListFromTree` cover pure helper parsing. `TestGetRetryConfig` documents default, OSD, and MDS retry/delay values.

`TestOSDUpdateShouldCheckOkToStop` uses fake OSD list/tree output to show that fewer than three OSDs skips checks, while three or more OSDs generally checks. `TestLeastUptodateDaemonVersion` loops 100 times over a versions map to ensure the least version is selected deterministically despite random map iteration.

State is mocked Ceph output only. Integration points include fake OSD output helpers, Ceph version parsing, and executor mocks. Gaps include full `OkToStop()` retry behavior, all-in-one OSD bypass through `osdDoNothing()`, MDS status retry, and real Ceph errors beyond induced mock failures.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/upgrade_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/agent.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/agent.go

This file defines the OSD provisioning agent state container and a few helpers used by OSD prepare flows.

`OsdAgent` carries the cluster info, node name, desired devices, metadata device, store config, ConfigMap key/value store, PVC-backed flag, replacement OSD info, force-format behavior, and whether devices from other clusters should be wiped. `NewAgent()` initializes this struct from operator-provided device and storage settings. `getDeviceLVPath()` shells out to `pvdisplay -C -o lvpath --noheadings <device>` and returns an empty string on failure after logging. `GetReplaceOSDId()` returns the replacement OSD ID when the provided block path matches `replaceOSD.BlockPath`, otherwise `-1`.

State is in-memory agent configuration plus external LVM metadata queried by `pvdisplay`. Integration points include `daemon.go` provisioning, operator OSD config types, Kubernetes ConfigMap status storage, and replacement OSD workflows.

Risks include `GetReplaceOSDId()` assuming `replaceOSD` is non-nil when called, failure masking in `getDeviceLVPath()`, and no direct tests in this work item for constructor field propagation or replacement lookup. Most behavioral coverage arrives indirectly through `daemon.go` tests that build `OsdAgent` values.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/agent.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/daemon.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/daemon.go

This file is the main OSD runtime/provisioning implementation for starting OSD daemons, discovering and filtering devices, invoking ceph-volume, and querying OSD info.

`StartOSD()` creates the OSD config directory, updates LVM config, activates PVC-backed volume groups when needed, runs `ceph-volume lvm activate --no-systemd`, starts `ceph-osd`, and releases LVM devices after shutdown. Signal handling kills the `ceph-osd` process by `fuser` on SIGTERM to help volume detach. `Provision()` handles encrypted PVC KEK setup, device-mapper version logging, orchestration-status updates, PVC/raw discovery versus host discovery, optional foreign-cluster wiping, available-device selection, ceph-volume configuration, CRUSH/topology assignment, LVM release, and final status updates.

`getAvailableDevices()` is the central device filter: skips mounted devices, filesystems, existing BlueStore signatures, unavailable ceph-volume inventory, unsupported encrypted partitions/LVs, loop/LVM misuse under filters, and non-matching desired devices. It recognizes PVC data/metadata/wal pseudo-types and persistent device links. `GetOSDInfoById()` searches both LVM and raw ceph-volume lists.

State spans host devices, LVM VGs/LVs, ceph-volume metadata, ConfigMap orchestration status, environment-driven encryption, and Ceph OSD metadata. Risks include many shell-dependent branches, careful PVC/LVM release timing, global `getOsdUUID` override in tests, and partial failure handling around `ceph-osd` exit. `daemon_test.go` heavily covers UUID detection, available-device selection, and volume-group name parsing.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/daemon.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/daemon_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/daemon_test.go

This large test file exercises OSD daemon helper behavior, especially device discovery and filtering.

`TestGetOsdUUID` creates temporary files containing only the BlueStore signature, signature plus UUID, no signature, unreadable content, and a missing path. It verifies UUID extraction and error behavior for old `lsblk` compatibility detection. `TestAvailableDevices` configures a mock executor for `lsblk`, `blkid`, `udevadm`, `dmsetup`, `ceph-volume inventory`, LVM list, and raw list. It checks use-all-devices, no devices, regex filters, exact devices, LVM selection restrictions, metadata devices, device path filters, persistent `/dev/disk` links, PVC-backed devices, raw OSD re-detection, and loop-device handling. `TestGetVolumeGroupName` validates parsing of `/dev/<vg>/<lv>`.

State is mocked host inventory plus temporary files. Integration points include sys device helpers, ceph-volume output parsing from other OSD test fixtures, Ceph version gates, and environment `CEPH_VOLUME_ALLOW_LOOP_DEVICES`.

Risks captured are broad but still unit-level: real udev/ceph-volume quirks, global mutation of `getOsdUUID`, status ConfigMap updates, provisioning side effects, and SIGTERM handling are not fully simulated.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/daemon_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/device.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/device.go

This file defines OSD device data structures and device-class selection logic.

`Device` is a small JSON-bound device descriptor. `DesiredDevice` carries user configuration such as name/filter, OSDs per device, metadata device, database size, device class, initial weight, and filter flags. `DeviceOsdMapping` maps device names to `DeviceOsdIDEntry`; its `String()` marshals the mapping to JSON for logging/debugging. `DeviceOsdIDEntry` tracks data OSD ID, metadata OSD IDs, matched config, persistent paths, low-level `sys.LocalDisk` info, and restore state.

`DesiredDevice.UpdateDeviceClass()` applies priority order for CRUSH device class: explicit device-level value first, PVC-backed `ROOK_OSD_CRUSH_DEVICE_CLASS` environment next, non-PVC store config next, and finally `sys.GetDiskDeviceType()` from sysfs-derived disk data. This feeds `getAvailableDevices()` and later ceph-volume configuration.

State is in-memory, except for environment reads in PVC mode. Dependencies include operator OSD env var names, storage config, and sys disk classification. `device_test.go` covers class priority and bootstrap keyring behavior from `init.go`. Risks include default classification depending on incomplete `LocalDisk` data and using JSON marshal while ignoring errors in `String()`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/device.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/device_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/device_test.go

This test file covers two related OSD helpers: bootstrap keyring creation and desired-device class assignment.

`TestOSDBootstrap` uses a temporary config directory and mock executor returning a key JSON payload. It calls `createOSDBootstrapKeyring()` and asserts that `bootstrap-osd/ceph.keyring` contains the bootstrap client header, key, and monitor caps. This indirectly verifies `init.go`'s template and integration with `cephclient.CreateKeyring()`.

`TestUpdateDeviceClass` checks the class priority order in `DesiredDevice.UpdateDeviceClass()`: preserve an explicit class, use PVC-backed environment class, fall back to sys disk type, use sys disk type for non-PVC when no store config is set, and prefer store config when provided.

State is test-local filesystem and environment variables. Dependencies include mock executor, temporary directories, Ceph cluster test info, operator OSD env var constants, and `sys.LocalDisk`. Gaps include no direct tests for `DeviceOsdMapping.String()`, `DesiredDevice` filter fields, or device class behavior with richer disk rotational metadata.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/device_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/encryption.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/encryption.go

This file implements dm-crypt/LUKS support for OSD devices and KMS key injection into ceph-volume.

Device operations include `CloseEncryptedDevice()`, `RemoveEncryptedDevice()`, `openEncryptedDevice()`, `dmsetupVersion()`, `setLUKSLabelAndSubsystem()`, `dumpLUKS()`, and `isCephEncryptedBlock()`. Key-slot management includes `removeEncryptionKeySlot()`, `ensureEncryptionKey()`, and `addEncryptionKey()`, all using temporary passphrase files and `cryptsetup` commands with timeouts. `addEncryptionKey()` handles full slots by checking if the desired key already matches, removing the old slot if needed, and retrying.

`setKEKinEnv()` reconstructs KMS config from environment variables, adds IBM API key from env, reads KMIP cert/key files from `/etc/kmip`, initializes a KMS config, fetches the key for the PVC name, and sets the ceph-volume encrypted-key environment variable. LUKS labels store `ceph_fsid=<fsid>` and `pvc_name=<pvc>` metadata for later ownership detection.

State includes dm devices, LUKS headers/labels/key slots, temporary passphrase files, KMS secrets, and process environment. Risks include parsing human `cryptsetup luksDump` output due to missing JSON support, temporary secret handling, env-dependent KMS reconstruction, and recursive key-add retry. `encryption_test.go` covers core command handling and FSID detection.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/encryption.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/encryption_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/encryption_test.go

This file tests the LUKS/dm-crypt command helpers with mocked executor behavior.

`TestCloseEncryptedDevice` validates `cryptsetup --verbose luksClose`. `TestRemoveEncryptionKeySlot` checks successful slot removal and ignored "Keyslot N is not active" errors. `TestEnsureEncryptionKey` verifies the `luksChangeKey` probe returns true on success and false without error when output says no key is available for the passphrase. `TestAddEncryptionKey` covers empty slots, full slots containing the desired key, and full slots requiring removal plus recursive add. `TestDmsetupVersion` validates `dmsetup version`. `TestIsCephEncryptedBlock` parses a realistic LUKS dump fixture and distinguishes matching versus different Ceph FSIDs.

State is mocked command output and temporary passphrase files created by the implementation. Integration points include Rook's mock executor and timeout command path. Gaps include no tests for KMS environment loading, KMIP file reads, LUKS label setting, open/remove dm-device failures, or temporary file permission inspection. The tests strongly document accepted cryptsetup output strings used for error classification.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/encryption_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/init.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/init.go

This small file creates the bootstrap OSD keyring used by OSD provisioning.

It defines `bootstrapOsdKeyring` as `bootstrap-osd/ceph.keyring` and `createOSDBootstrapKeyring()`, which builds username `client.bootstrap-osd`, a keyring path under the provided root directory, monitor access `allow profile bootstrap-osd`, and a template renderer based on `bootstrapOSDKeyringTemplate` from `device.go`. It delegates actual key creation and persistence to `cephclient.CreateKeyring()`.

State is the keyring file written under the Ceph config/root directory and the Ceph auth key created or fetched by the shared keyring helper. Dependencies include `clusterd.Context`, `cephclient.ClusterInfo`, path joining, and the client keyring creation API.

Integration point is the OSD prepare/init path, where ceph-volume needs bootstrap credentials with limited monitor privileges. Risks are mostly inherited from `CreateKeyring()` and filesystem permissions; the local function has little branching. `device_test.go` verifies the file contains the bootstrap client stanza, key value, and monitor caps.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/init.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/key_rotation.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/key_rotation.go

This file implements online key-encryption-key rotation for encrypted OSD devices.

`RotateKeyEncryptionKey()` takes a KMS config, secret name, and device paths. It fetches the current key from KMS and rejects empty values. It first ensures the current key is also present in LUKS slot `1` on every device, then generates a new dm-crypt key with `oposd.GenerateDmCryptKey()`. For each device, it removes slot `0` using the current key and adds the new key to slot `0`. It then updates the KMS secret to the new key, fetches it back for verification, and finally removes the old key from slot `1` on every device using the new key.

State changes span LUKS key slots on all device paths and the external KMS secret. The sequence is designed to keep an unlockable key available during rotation: current key in slot 1, new key in slot 0, then old slot cleanup after KMS verification.

Risks include non-atomic multi-device rotation, failures after some devices or KMS state have changed, reliance on `addEncryptionKey()` idempotency, and no direct unit test in this work item for rollback or partial failure behavior. Integration points are `encryption.go` slot helpers and KMS `GetSecret`/`UpdateSecret`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/key_rotation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/azure.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/azure.go

This file initializes Azure Key Vault as a KMS backend and adapts Kubernetes client-certificate secrets into the file-based format expected by the Azure secrets library.

`IsAzure()` checks whether the provider is `secrets.TypeAzure`. `InitAzure()` calls `azureKVCert()` to prepare connection details, defers certificate cleanup, converts `map[string]string` to `map[string]interface{}`, and constructs the Azure secrets client with `azure.New()`. `azureKVCert()` requires `AZURE_CERT_SECRET_NAME`, fetches that Kubernetes Secret from the provided namespace, writes the `CLIENT_CERT` key to a temporary `cert.pem` file with mode `0400`, and stores the generated path in `azure.AzureClientCertPath`. It returns a cleanup function built from the shared temp-file cleanup helper and eagerly removes files on setup errors.

State includes a temporary certificate file and the mutable connection-details map. Dependencies include Kubernetes CoreV1 Secrets, libopenstorage Azure secrets, and clusterd context. Risks include expecting a specific `CLIENT_CERT` key, mutating caller config, cleanup timing while initializing the client, and typoed mandatory details variable name. `azure_test.go` validates missing secret name, missing secret, successful temp file creation, and cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/azure.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/azure_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/azure_test.go

This test file validates Azure Key Vault certificate preparation against a fake Kubernetes client.

`Test_AzureKVCert` runs three subtests. The first omits `AZURE_CERT_SECRET_NAME` and expects an error. The second provides a secret name that does not exist, while a differently named Secret is present, and expects an error. The third creates a matching Secret with `CLIENT_CERT` data, calls `azureKVCert()`, asserts the returned config contains an existing `azure.AzureClientCertPath`, then invokes the cleanup function and asserts the file is gone.

State is a fake Kubernetes Secret store and a temporary certificate file. Dependencies include Rook's operator test clientset, Kubernetes core Secret types, and libopenstorage Azure constants.

The test is a good signal for required Kubernetes secret wiring and temp-file cleanup. It does not initialize the actual Azure client, validate certificate contents, test write failures, or check behavior when the `CLIENT_CERT` key is absent. It also does not validate the mandatory connection details list beyond the certificate secret path.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/azure_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/envs.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/envs.go

This file translates KMS configuration between CephCluster specs, Kubernetes pod environment variables, and runtime environment maps.

`vaultTokenEnvVarFromSecret()` and `ibmKeyProtectServiceAPIKeyEnvVarFromSecret()` create secret-backed env vars for sensitive tokens. `vaultTLSEnvVarFromSecret()` maps Vault TLS secret names to mounted file paths under `/etc/vault`. `ConfigToEnvVar()` handles provider-specific transformations: default Vault backend path insertion, removal of IBM API key from literal connection details and replacement with secret-backed env var, KMIP token details exclusion with non-secret fields prefixed as `KMIP_`, generic env insertion, Vault token injection, TLS env insertion, and deterministic sorting. `ConfigEnvsToMapString()` scans process env for known KMS prefixes (`VAULT_`, `IBM_`, `KMIP_`, `AZURE_`) and `KMS_PROVIDER`, trimming the KMIP prefix when reconstructing config. `sortV1EnvVar()` keeps output stable.

State is environment variable lists/maps and mutates the input spec's connection details in some paths. Dependencies include Vault API constants, libopenstorage Vault defaults, Ceph API KMS predicates, Kubernetes env var types, and set utilities.

Risks include accidental mutation of caller maps, prefix collisions, leaking non-secret values, and relying on env scanning for OSD-side KMS reconstruction. `envs_test.go` covers sorting, Vault defaults/TLS/token, IBM secret-backed API key, KMIP secret exclusion, and env scanning.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/envs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/envs_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/envs_test.go

This test file validates KMS environment-variable translation and reverse scanning.

`TestVaultTLSEnvVarFromSecret` checks Vault without TLS, Vault with TLS, and IBM Key Protect env generation. It asserts sorted envs, Vault default backend path, secret-backed Vault token, Vault TLS file path translation, and secret-backed IBM API key. `TestConfigEnvsToMapString` verifies that unrelated environment variables are ignored, `KMS_PROVIDER` is included, Vault-prefixed variables are collected, and the resulting map marks KMS as enabled in a ClusterSpec. `TestVaultConfigToEnvVar` table-tests exact env lists for Vault default/custom backend, Vault TLS, IBM API key removal from literal values, and KMIP token-detail removal with `KMIP_` prefixing.

State is process environment managed through `t.Setenv` and in-memory specs. Dependencies include Ceph API KMS predicates and Kubernetes `EnvVar` structures.

Risks surfaced include deterministic ordering and avoiding secret leakage through literal env values. Gaps include Azure env generation, multiple Vault TLS options beyond CACERT, mutation side effects on reused specs, and `ConfigEnvsToMapString()` behavior when KMIP-prefixed and unprefixed keys collide.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/envs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/ibm_key_protect.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/ibm_key_protect.go

This file initializes IBM Key Protect as a KMS backend.

It defines provider type `ibmkeyprotect`, configuration keys for service API key, instance ID, base URL, and token URL, plus mandatory connection/token detail slices and sentinel errors for missing required values. `InitKeyProtect()` reads required API key and instance ID using `GetParam()`, defaults base URL and token URL to IBM client defaults when omitted, constructs a `kp.ClientConfig` with verbose logging, and calls `kp.New()`. `IsIBMKeyProtect()` is the provider predicate on `Config`.

State is the constructed IBM Key Protect client configuration; the file does not persist secrets itself. Dependencies include `github.com/IBM/keyprotect-go-client`, Rook KMS config helpers, and wrapped sentinel errors. Integration points include `envs.go`, which ensures the API key is mounted from a Kubernetes Secret rather than left in literal connection details, and `encryption.go`, which injects the API key into runtime config for OSD-side KMS access.

Risks include verbose client logging, reliance on caller-provided API key handling, and no live network validation during construction. `ibm_key_protect_test.go` covers missing required fields and default/custom URL behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/ibm_key_protect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/ibm_key_protect_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/ibm_key_protect_test.go

This test file validates IBM Key Protect client initialization rules.

`TestInitKeyProtect` uses a mutable config map across subtests. It first verifies that missing `IBM_KP_SERVICE_API_KEY` returns `ErrIbmServiceApiKeyNotSet`, then adds the key and verifies missing `IBM_KP_SERVICE_INSTANCE_ID` returns `ErrIbmInstanceIdKeyNotSet`. After adding the instance ID, it checks that omitted base URL defaults to `kp.DefaultBaseURL`, custom base URL is honored, omitted token URL defaults to `kp.DefaultTokenURL`, and custom token URL is honored.

State is only the in-memory config map and constructed IBM client object. Dependencies include the IBM Key Protect Go client and `testify/assert`.

The test signal is clear for required configuration and defaults. It does not perform network calls, authentication, secret CRUD, verbose logging behavior, or interaction with `ConfigToEnvVar()` secret redaction. Because the same map is reused across subtests, ordering matters, but the sequence is intentional and documents incremental configuration requirements.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/ibm_key_protect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/k8s.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/k8s.go

This file implements Kubernetes Secrets as a KMS backend for OSD encryption keys.

`storeSecretInKubernetes()` generates an OSD encryption Secret and creates it in the cluster namespace, tolerating already-exists errors. `updateSecretInKubernetes()` fetches the Secret, updates `StringData` with the dmcrypt key, and writes it back. `getKubernetesSecret()` fetches the Secret and returns the `dmcrypt-key` data value. `generateOSDEncryptedKeySecret()` sets the generated name, namespace, `pvc_name` label, `StringData`, Rook Secret type, and owner reference through `clusterInfo.OwnerInfo`. `GenerateOSDEncryptionSecretName()` prefixes PVC names with `rook-ceph-osd-encryption-key`. `IsK8s()` accepts providers `kubernetes` and `k8s`.

State is Kubernetes Secret objects in the Ceph cluster namespace. Dependencies include the Kubernetes clientset, Rook owner-reference handling, `k8sutil.RookType`, and Ceph cluster info. Integration points are the generic KMS `Config` implementation and OSD encryption/key-rotation flows.

Risks include ignoring already-existing create conflicts without verifying content, returning an empty string when the expected key is absent, and relying on owner-reference setup. `k8s_test.go` covers only deterministic secret-name generation; CRUD behavior is not directly tested in this work item.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/k8s.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/k8s_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/k8s_test.go

This minimal test file verifies the naming convention for Kubernetes-backed OSD encryption key Secrets.

`TestGenerateOSDEncryptionSecretName` asserts that PVC name `set1-data-0-7dwll` becomes `rook-ceph-osd-encryption-key-set1-data-0-7dwll`. This protects the stable lookup contract used by `storeSecretInKubernetes()`, `updateSecretInKubernetes()`, and `getKubernetesSecret()`.

State is pure string transformation. Dependencies are only the local KMS package and `testify/assert`. The test does not cover Kubernetes Secret creation, update, fetch, owner references, labels, Secret type, already-exists handling, missing-key behavior, or provider aliases accepted by `IsK8s()`.

The main integration risk is that many callers depend on this exact generated name for idempotent storage and rotation. The test gives a small but important regression signal for that contract while leaving API-server interactions to broader KMS tests elsewhere.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/k8s_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/kmip.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/kmip.go

This file implements a KMIP 1.4 KMS backend over mutual TLS.

`InitKMIP()` validates endpoint, CA cert, client cert, and client key; reads optional TLS server name and read/write timeouts; bounds timeout values to `uint8`; builds a CA pool and client certificate; and creates a TLS config requiring TLS 1.2 or newer. `kmipKMS` methods implement secret lifecycle: `registerKey()` base64-decodes a value and registers it as an AES symmetric key with export usage; `getKey()` retrieves a symmetric key and returns base64; `deleteKey()` destroys an identifier. `connect()` opens TLS, sets deadlines, handshakes, and runs KMIP discover. `discover()` validates protocol version 1.4. `send()` TTLV-marshals a one-item request with a UUID batch ID, writes it, reads and decodes the response. `verifyResponse()` enforces one batch item, expected operation, matching batch ID, and success status.

State is remote KMIP server key material plus transient TLS connections. Dependencies include `gemalto/kmip-go`, TTLV encoding, TLS/x509, UUIDs, and base64. Risks include a likely write-timeout bug using `SetReadDeadline` instead of `SetWriteDeadline`, type assertions on response payload/key material, no retry logic, and strict one-version discovery. `kmip_test.go` covers missing required config only.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/kmip.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/kmip_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/kmip_test.go

This test file validates the first layer of KMIP configuration checks.

`TestInitKMIP` table-tests missing endpoint, missing CA certificate, missing client certificate, and missing client key. Each case calls `InitKMIP()` with progressively more config and asserts the exact sentinel error returned: `ErrKMIPEndpointNotSet`, `ErrKMIPCACertNotSet`, `ErrKMIPClientCertNotSet`, or `ErrKMIPClientKeyNotSet`.

State is in-memory configuration only. Dependencies are the local KMIP KMS package and `testify/assert`. The test deliberately stops before valid TLS material, so it does not exercise certificate parsing, timeout parsing, maximum timeout bounds, TLS config creation, connection setup, KMIP discover, TTLV request/response handling, register/get/delete, or response verification.

The useful signal is that required secret/token details fail fast with stable errors. Significant integration risk remains around live KMIP interoperability and the lower-level protocol code, which would require a KMIP test server or carefully constructed TTLV fixtures to validate.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/kmip_test.go -->
