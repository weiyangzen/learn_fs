# Group Research: subset-b-000348

This grouped report covers the subset-b-000348 Ceph-CSI RBD source files. Each file section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/nodeserver.go -->
# sources/control-plane/ceph-csi/internal/rbd/nodeserver.go

## Purpose
`nodeserver.go` implements the CSI node-side lifecycle for RBD volumes: staging, publishing, unpublishing, unstaging, node expansion, node capabilities, volume stats, filesystem formatting, block and file encryption activation, cgroup QoS application, and node-local recovery hooks.

## Important APIs, Types, And Functions
`NodeServer` embeds `csicommon.DefaultNodeServer`, keeps per-volume and per-target `VolumeLocks`, and caches feature probes for ext4 prezeroed and xfs reflink support. `stageTransaction` records rollback state for stage failures. Main CSI entry points are `NodeStageVolume`, `NodePublishVolume`, `NodeUnpublishVolume`, `NodeUnstageVolume`, `NodeExpandVolume`, `NodeGetCapabilities`, and `NodeGetVolumeStats`.

Important helpers include `populateRbdVol`, `initStaticVol`, `initDynamicVol`, `stageTransaction`, `undoStagingTransaction`, `mountVolumeToStagePath`, `mountVolume`, `createStageMountPoint`, `createTargetMountPath`, `resizeNodeStagePath`, `processEncryptedDevice`, `getNodePublishCredentials`, `applyCgroupQoSIfConfigured`, `setUserIdMapping`, `setClientAddress`, and `getMkfsArgs`.

## Control Flow
`NodeStageVolume` validates the request, builds credentials, locks the volume ID, checks idempotent staging unless the request is a healer context, resolves static or dynamic RBD volume metadata, sets network namespace state, writes image metadata into the staging parent, then calls `stageTransaction`. The transaction flattens unsupported clone/deep-flatten chains if needed, maps the image, opens encryption when configured, creates the stage file or directory, mounts or bind-mounts the device, unlocks fscrypt directories, and optionally resizes.

`NodePublishVolume` validates the request and service-account restrictions, locks the target path and pod UID, creates the target path, bind-mounts the staged path to the pod path, and applies cgroup v2 QoS after mount. `NodeUnpublishVolume` unmounts and removes the target path. `NodeUnstageVolume` unmounts the staging path, removes it, reads `image-meta.json`, unmaps by image spec or device, and deletes the stash. `NodeExpandVolume` finds the staging path, reads stash metadata, locates the mapped RBD device, resizes encrypted mappings, and performs filesystem resize for non-block volumes.

## State And Persistence
Node-local persistent state is the staging directory and `image-meta.json` stash written by `stashRBDImageMetadata` and updated with the mapped device. Cluster state is touched through RBD image metadata keys for client address and user ID mapping. Runtime state includes per-volume locks, kernel feature probe caches, temporary mkfs probe files, and live device mappings. The code intentionally keeps static volumes out of some metadata writes.

## Dependencies And Integration Points
This file depends on CSI protobufs, Kubernetes mount utilities, Ceph RBD helpers in this package, `util` credential/config helpers, fscrypt, encryption helpers, Kubernetes secrets, RBD net namespace configuration, and cgroup QoS handlers. It integrates with kubelet CSI stage/publish paths, VolumeAttachment healer flow, Ceph fencing metadata, RBD NBD/krbd mapping, and VolumeAttributesClass-style QoS.

## Risks
The staging transaction spans local files, mounts, encrypted mapper devices, RBD mappings, and cluster metadata, so rollback ordering is critical. `cleanupRBDImageMetadataStash` treats missing stash as an error in rollback paths. QoS during publish is deliberately best-effort for missing credentials or volume initialization, but actual cgroup write errors are logged and returned only from the helper. `createDiff`-style resize paths depend on stash accuracy. `processEncryptedDevice` rejects unexpected pre-existing formats, protecting data but making migration/static cases sensitive. `mountVolumeToStagePath` trusts custom `mkfsOptions` from volume context.

## Test Signals
Existing tests cover `getStagingTargetPath`, boolean option parsing, read-affinity map option appending, and read-affinity config selection. Missing direct coverage includes full stage rollback, stash cleanup errors, encrypted stage/unstage, node publish credential fallback, cgroup QoS behavior, and node expansion against stale or missing mappings.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/nodeserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/nodeserver_test.go -->
# sources/control-plane/ceph-csi/internal/rbd/nodeserver_test.go

## Purpose
`nodeserver_test.go` provides focused unit tests for low-risk helpers in the RBD node server: staging-path construction, boolean option parsing, read-affinity map option composition, and csi-config/read-affinity integration.

## Important APIs, Types, And Functions
Tests are `TestGetStagingPath`, `TestParseBoolOption`, `TestNodeServer_appendReadAffinityMapOptions`, and `TestReadAffinity_GetReadAffinityMapOptions`. The tests instantiate `csi.NodeStageVolumeRequest`, `csi.NodeUnstageVolumeRequest`, `rbdVolume`, `csicommon.CSIDriver`, and `NodeServer`.

## Control Flow
The tests exercise helper inputs in table-driven form. The read-affinity config test writes a temporary JSON csi-config file, constructs CLI read-affinity options from node labels, creates a minimal `NodeServer`, and verifies `util.GetReadAffinityMapOptions` output for enabled, disabled, empty-label, absent-cluster, and CLI-disabled cases.

## State And Persistence
State is test-local. The only filesystem write is the temporary csi-config JSON under `t.TempDir()`. No Ceph cluster or Kubernetes API is contacted.

## Dependencies And Integration Points
The tests depend on CSI protobuf request types, Ceph-CSI deployment config structs, `csicommon`, `util` read-affinity helpers, and `testify/require`. They validate integration between node labels, CLI read-affinity options, and cluster-level read-affinity settings.

## Risks
Coverage is intentionally narrow and does not exercise the CSI RPCs, mount operations, local stash files, encryption, or cgroup QoS. The read-affinity test mutates a shared temp config path across parallel subtests only for reads after one write; that is safe but relies on no later mutation.

## Test Signals
The file confirms helper idempotence and option-string construction. It does not protect the higher-risk staging, rollback, unstage, expand, or publish paths.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/nodeserver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/qos.go -->
# sources/control-plane/ceph-csi/internal/rbd/qos.go

## Purpose
`qos.go` implements traditional RBD/NBD QoS handling for mutable volume attributes. It parses user-facing QoS parameters, calculates capacity-adjusted limits, applies active limits through RBD image metadata, and persists the source policy for later adjustment after expansion.

## Important APIs, Types, And Functions
Constants map StorageClass or VolumeAttributesClass keys such as `baseIops`, `iopsPerGiB`, `maxIops`, and `baseVolSizeBytes` to Ceph metadata keys such as `rbd_qos_iops_limit` and saved-policy keys such as `rbd_base_qos_iops_limit`. `qosSpec` groups base, per-GiB, max, and target metadata fields. `nbdQoSHandler` implements `QoSHandler` with `HasParams`, `Validate`, `Apply`, and `Clear`. Key functions are `HasQoSParams`, `validateNBDQoSParams`, `parseQosParams`, `SetQOS`, `ApplyQOS`, `calcQosBasedOnCapacity`, `SaveQOS`, `getRbdImageQOS`, and `AdjustQOS`.

## Control Flow
`parseQosParams` recognizes base limits and attaches optional per-GiB and max limits. `SetQOS` records the base volume size, then calculates final RBD metadata limits for every present base limit. If per-GiB or base-size data is absent, the base limit is used directly. Otherwise, capacity over `baseVolSizeBytes` is multiplied by the per-GiB increment and capped by the max limit when provided. `ApplyQOS` writes `conf_` metadata entries consumed by RBD/NBD. `SaveQOS` stores the original policy metadata. `AdjustQOS` reloads saved policy and recalculates active limits after size changes.

## State And Persistence
Runtime state is `rv.QosParameters` and `rv.BaseVolSize`. Persistent state is RBD image metadata: active `conf_rbd_qos_*` values plus saved `rbd_base_qos_*`, `rbd_*_per_gib_limit`, max, and base-size keys. `Clear` calls `Apply` with empty parameters, which currently does not explicitly remove existing metadata keys.

## Dependencies And Integration Points
This file depends on go-ceph RBD errors for metadata-not-found handling and Ceph-CSI logging. It is integrated by `rbdVolume.modifyVolumeAttributes` and complements cgroup QoS handling in another file; controller validation is expected to prevent mixing QoS types.

## Risks
Capacity calculation uses integer GiB steps and ignores fractional capacity above the base size. Empty `Clear` does not remove old active or saved metadata in this file, so clearing semantics depend on downstream behavior or other handlers. Numeric validation accepts zero and rejects negatives, but `SetQOS` itself can still return parse errors if callers skip validation. Metadata writes are per-key and not atomic as a group.

## Test Signals
`qos_test.go` covers base-only, BPS and IOPS, capacity-adjusted, and max-capped calculations. It does not cover validation failures, `ApplyQOS`, `SaveQOS`, metadata readback, or clear behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/qos.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/qos_test.go -->
# sources/control-plane/ceph-csi/internal/rbd/qos_test.go

## Purpose
`qos_test.go` validates the pure calculation path for traditional RBD/NBD QoS limits.

## Important APIs, Types, And Functions
The helper `checkQOS` compares expected metadata keys with `rv.QosParameters`. `TestSetQOS` exercises `rbdVolume.SetQOS` with several mutable-parameter maps and requested volume sizes.

## Control Flow
The test starts with base IOPS limits, adds BPS limits, adds per-GiB growth with a base size, then verifies calculations for 20 GiB, 100 GiB, 200 GiB, and 600 GiB requested sizes, including max limit capping.

## State And Persistence
All state is in memory on a fresh `rbdVolume` per scenario. No RBD metadata is written.

## Dependencies And Integration Points
The test depends only on the RBD package constants and `oneGB`. It indirectly validates values later written by `ApplyQOS`.

## Risks
The tests do not check invalid numeric input, empty maps, missing base limits, metadata persistence, `AdjustQOS`, or clear semantics. Because expected values are hard-coded, the tests are good regression signals for formula changes.

## Test Signals
Strong signal for `calcQosBasedOnCapacity`; weak signal for handler integration and Ceph metadata side effects.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/qos_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/rbd_attach.go -->
# sources/control-plane/ceph-csi/internal/rbd/rbd_attach.go

## Purpose
`rbd_attach.go` maps and unmaps RBD images on a node through either krbd (`rbd device`) or `rbd-nbd`, including map/unmap option parsing, NBD feature discovery, mapped-device lookup, retry-before-map in-use checks, encrypted-device close handling, and NBD client log cleanup.

## Important APIs, Types, And Functions
Important constants define mounters, access types, default NBD `try-netlink`, `reattach-timeout`, and `io-timeout` behavior. `rbdDeviceInfo` models JSON output from `rbd device list` and `rbd-nbd list-mapped`. `detachRBDImageArgs` carries unmap mode, encryption, and log strategy. Key functions are `SetRbdNbdToolFeatures`, `parseMapOptions`, `NodeServer.getMapOptions`, `getDeviceList`, `findDeviceMappingImage`, `waitForPath`, `attachRBDImage`, `createPath`, `waitForrbdImage`, `detachRBDDevice`, and `detachRBDImageOrDeviceSpec`.

## Control Flow
On startup `SetRbdNbdToolFeatures` modprobes `nbd`, checks kernel cookie support, and checks `rbd-nbd --help` for cookie support. During staging, `getMapOptions` splits semicolon-delimited krbd/nbd options, applies the right side for the chosen mounter, and appends read-affinity map options for krbd. `attachRBDImage` first checks existing mappings, waits for image watchers to clear if absent, then builds and executes a map command. `createPath` chooses `rbd` or `rbd-nbd`, adds Ceph credentials, namespace execution, read-only flags, and default NBD options. On connection timeout it tries to unmap the image spec. Unmap closes encrypted mapper devices first, chooses krbd or nbd CLI syntax, treats missing image-spec mappings as success, and performs asynchronous NBD log cleanup.

## State And Persistence
Runtime state includes global `hasNBD` and `hasNBDCookieSupport`, kernel support detection, process execution output, and node device mappings. Persistent effects are mapped `/dev/rbd*` or `/dev/nbd*` devices, NBD log files, and encrypted mapper closure. This file reads no cluster OMAP directly but uses `isInUse` watchers via `rbdVolume`.

## Dependencies And Integration Points
It depends on `util.ExecCommand`, `ExecuteCommandWithNSEnter`, kernel version helpers, kmod, retry-go, go-ceph metadata through `isInUse`, and stash/log helpers from `rbd_util.go`. It is called from node staging, unstage, expansion, and healer flows.

## Risks
Command-line option composition is security- and correctness-sensitive because user options are passed to external CLIs. The missing-mapping success check applies only when unmapping by image spec, not device path. Global NBD feature flags are mutable package state. `waitForrbdImage` may fail legitimate multi-node filesystem use while intentionally bypassing watcher checks for multi-node block. Async log cleanup errors are only logged. In `flattenRbdImage` callers, map may race with in-progress flatten tasks.

## Test Signals
`rbd_attach_test.go` covers map option parsing, including old format, new krbd/nbd format, embedded colons, and unknown mounter errors. There is no unit coverage for command construction, NBD feature discovery, namespace execution, in-use retry, timeout cleanup, or encrypted unmap.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/rbd_attach.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/rbd_attach_test.go -->
# sources/control-plane/ceph-csi/internal/rbd/rbd_attach_test.go

## Purpose
`rbd_attach_test.go` unit-tests parsing of mounter-specific map and unmap options.

## Important APIs, Types, And Functions
The only test is `TestParseMapOptions`, which calls `parseMapOptions`.

## Control Flow
The table covers old unlabeled format, new `krbd:` and `nbd:` labels, omitted `krbd:` label, NBD-only options, option values that themselves contain `:`, and unknown mounter labels.

## State And Persistence
No state persists; tests are pure string parsing.

## Dependencies And Integration Points
The test depends on standard `testing` and `strings`. It protects `NodeServer.getMapOptions` input semantics and StorageClass option compatibility.

## Risks
It does not validate command-line argument rendering or interaction with actual `rbd`/`rbd-nbd` commands. The error assertion only checks substring when an error exists, so unexpected nil error in an expected-error case would not be caught as directly as it could be.

## Test Signals
Good regression signal for delimiter handling and backward compatibility; weak signal for attach/unmap behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/rbd_attach_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/rbd_healer.go -->
# sources/control-plane/ceph-csi/internal/rbd/rbd_healer.go

## Purpose
`rbd_healer.go` implements a node-side recovery loop for `rbd-nbd` volumes. It reconstructs `NodeStageVolume` requests from Kubernetes `VolumeAttachment` and `PersistentVolume` objects so previously attached NBD devices can be reattached after node-server restart or NBD process loss.

## Important APIs, Types, And Functions
Key functions are `accessModeStrToInt`, `getSecret`, `formatStagingTargetPath`, `NodeServer.callNodeStageVolume`, and `NodeServer.RunVolumeHealer`. `fsTypeBlockName` identifies block-mode PVs.

## Control Flow
`RunVolumeHealer` lists `VolumeAttachment` objects, filters to the current node and driver, loads bound non-deleting PVs, skips non-CSI and non-`rbd-nbd` volumes, rechecks the attachment is still attached, and launches concurrent `callNodeStageVolume` calls. `callNodeStageVolume` derives the Kubernetes 1.24+ staging path using a SHA-256 hash of the volume handle, fetches the node-stage secret, adds `volumeHealerContext=true`, builds a CSI `NodeStageVolumeRequest`, sets block or mount access type, and invokes `NodeStageVolume`. In healer context, `NodeStageVolume` only reattaches using stashed device metadata.

## State And Persistence
The healer relies on Kubernetes API state and existing node-local `image-meta.json` under the hashed staging path. It mutates the PV volume attributes map in place by adding `volumeHealerContext`. No new independent persistent state is introduced.

## Dependencies And Integration Points
It depends on Kubernetes API helpers, CSI protobufs, RBD node staging, secrets, and kubelet staging path conventions. It integrates tightly with `rbd_attach.go` NBD attach support and the stash created by `nodeserver.go`.

## Risks
The staging path format is version-sensitive and currently assumes the hash-based path. `pv.Spec.AccessModes[0]` is accessed without checking length. The unbuffered channel with goroutines is drained after launcher completion starts; this works because receives begin after the launcher loop but can serialize goroutine completion. Mutating `VolumeAttributes` in place can surprise callers if reused. Only `rbd-nbd` volumes are healed.

## Test Signals
There are no direct tests in this subset. Useful tests would mock Kubernetes objects, staging path derivation, missing secrets, access-mode conversion, nil PV/CSI fields, and healer-context `NodeStageVolume` behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/rbd_healer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/rbd_journal.go -->
# sources/control-plane/ceph-csi/internal/rbd/rbd_journal.go

## Purpose
`rbd_journal.go` coordinates Ceph-CSI journal/OMAP reservations for RBD volumes and snapshots. It validates in-memory objects, detects existing reservations, repairs stale or incomplete transactions, generates CSI IDs, updates topology and image IDs, and regenerates journal state for static or migrated volumes.

## Important APIs, Types, And Functions
Validation helpers are `validateNonEmptyField`, `validateRbdSnap`, and `validateRbdVol`. Core operations are `checkSnapCloneExists`, `rbdVolume.Exists`, `repairImageID`, `reserveSnap`, `reserveVol`, `undoSnapReservation`, `undoVolReservation`, `updateTopologyConstraints`, `RegenerateJournal`, and `rbdVolume.storeImageID`. `getEncryptionConfig` maps configured block/file encryption to journal fields.

## Control Flow
Reservation lookup uses `volJournal` or `snapJournal` to connect to RADOS OMAPs. Existing snapshot reservations are rolled back if backing images are missing, or rolled forward by recreating missing snapshots and storing image IDs. Existing volume reservations are checked against topology, image existence, parent-clone recovery, size compatibility, and encryption configuration before returning generated CSI IDs. New reservations allocate names and UUIDs with pool IDs, then generate CSI volume/snapshot handles. `RegenerateJournal` decomposes an existing volume handle, maps cluster IDs, reserves or repairs OMAP state, updates owner and metadata, and returns a regenerated volume handle.

## State And Persistence
Persistent state is Ceph-CSI journal OMAP data: request-name-to-image reservations, image attributes, image IDs, group IDs, owner fields, and pool IDs. The code also writes RBD image metadata during regeneration. Defer blocks restore in-memory reservation fields on error and undo OMAP reservations for failed creates.

## Dependencies And Integration Points
This file depends on `internal/journal`, RADOS pool ID helpers, Kubernetes metadata preparation, encryption configuration, topology matching, and snapshot/volume helpers from `rbd_util.go` and `snapshot.go`. It is a central integration point for controller create/delete volume and snapshot flows.

## Risks
The comments correctly warn that reservation checks must run under request-name locks; otherwise OMAP garbage collection and roll-forward/rollback can race. Journal pool ID conversion failures can leak images, as TODOs note. Recovery paths manipulate real images and snapshots when stale OMAP is detected. `RegenerateJournal` is complex and updates both OMAP and image metadata; partial failure handling depends on defer-based undo after reservation.

## Test Signals
No direct tests are included in this subset. Existing behavior is indirectly exercised by controller integration/e2e tests. High-value tests would mock journal connections for stale reservation cleanup, image ID repair, topology mismatch, owner reset, and journal regeneration idempotence.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/rbd_journal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/rbd_util.go -->
# sources/control-plane/ceph-csi/internal/rbd/rbd_util.go

## Purpose
`rbd_util.go` defines the core RBD domain model and most shared operations for RBD images, volumes, snapshots, feature validation, cluster connections, image creation/deletion, clone flattening, ID decoding, metadata stash management, resizing, QoS dispatch, log strategy, and utility interfaces.

## Important APIs, Types, And Functions
Primary types are `rbdImage`, `rbdVolume`, `rbdSnapshot`, `imageFeature`, `migrationVolID`, `rbdImageMetadataStash`, and `snapAndChildrenInfo`. Important constants define mounters, migration keys, metadata keys, stash filename, and krbd support file paths.

Major functions include `GetClientAddressKey`, `GetUserIDMappingKey`, `prepareKrbdFeatureAttrs`, `GetKrbdSupportedFeatures`, `HexStringToInteger`, `isKrbdFeatureSupported`, `Connect`, `Destroy`, `String`, `createImage`, `openIoctx`, `open`, `openReadOnly`, `isInUse`, `Delete`, `trashRemoveImage`, `DeleteTempImage`, `getCloneDepth`, `flattenRbdImage`, `checkImageChainHasFeature`, `GenVolFromVolID`, `generateVolumeFromVolumeID`, `generateVolumeFromMapping`, `genVolFromVolumeOptions`, `validateImageFeatures`, `genSnapFromSnapID`, `createSnapshot`, `deleteSnapshot`, `cloneRbdImageFromSnapshot`, `constructImageOptions`, `getImageInfo`, `stashRBDImageMetadata`, `lookupRBDImageMetadataStash`, `updateRBDImageMetadataStash`, `cleanupRBDImageMetadataStash`, `resize`, metadata getters/setters, `DeepCopy`, `DisableDeepFlatten`, `listSnapAndChildren`, `PrepareVolumeForSnapshot`, `getUsedBytes`, `UsesNBDMounter`, and `modifyVolumeAttributes`.

## Control Flow
Volume generation decomposes CSI IDs, resolves monitors, pools, namespace, journal attributes, encryption config, image info, data pool, and optional cluster/pool mappings. Image creation builds `librbd.ImageOptions`, creates the RBD image, and prepares encryption metadata. Deletion obtains the image ID, removes encryption DEKs, trashes the image, then queues or performs trash removal. Clone/snapshot helpers open IO contexts, set clone options, clean up failed clones, and repair image IDs. Metadata stash helpers write and read node-local JSON used by node unstage/expand. `modifyVolumeAttributes` selects cgroup or NBD QoS handlers and clears all handlers when no QoS parameters are supplied.

## State And Persistence
Persistent state includes RBD images and snapshots, RBD trash, RBD image metadata, Ceph-CSI OMAP journal attributes, encryption DEKs, local `image-meta.json`, and optional NBD client log files. Runtime state includes cluster connections, RADOS IO contexts, cached image fields, encryption helper objects, and QoS maps. Several methods lazily open and cache IO contexts or connections and require `Destroy` for cleanup.

## Dependencies And Integration Points
This file depends heavily on go-ceph `rados`, `rbd`, and `rbd/admin`, CSI types, Kubernetes volume helpers, Ceph-CSI util packages, kernel feature helpers, encryption helpers, journal code, and QoS handlers. It is used by controller, node, snapshot, replication, migration, and manager code.

## Risks
The file is a broad shared surface, so small behavior changes have high blast radius. IO context lifecycle has FIXME comments in clone-chain traversal. Image deletion relies on Ceph manager task support with fallback and can leave trash entries if both paths fail. Feature validation is string-driven and mounter-dependent. Local stash cleanup returns errors on missing files. `modifyVolumeAttributes` clears both QoS strategies when no QoS params are supplied, which must stay aligned with controller validation. Metadata writes and OMAP updates are not atomic with image changes.

## Test Signals
`rbd_util_test.go` covers snapshot feature detection, image feature validation and dependencies, client log filename formatting, log strategy actions, krbd feature bit checks, image feature empty validation, and retryable volume-generation errors. It does not cover real RADOS/RBD operations, OMAP interactions, stash JSON behavior, deletion fallback, clone flattening, or QoS handler dispatch.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/rbd_util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/rbd_util_test.go -->
# sources/control-plane/ceph-csi/internal/rbd/rbd_util_test.go

## Purpose
`rbd_util_test.go` provides unit coverage for pure or local helper behavior in `rbd_util.go`.

## Important APIs, Types, And Functions
Tests include `TestHasSnapshotFeature`, `TestValidateImageFeatures`, `TestGetCephClientLogFileName`, `TestStrategicActionOnLogFile`, `TestIsKrbdFeatureSupported`, `Test_checkValidImageFeatures`, and `Test_shouldRetryVolumeGeneration`.

## Control Flow
The tests build `rbdVolume` values with feature sets and mounters, assert validation errors for missing dependencies and NBD-required journaling, create temporary log files to verify remove/compress/preserve behavior, initialize `krbdFeatures` for feature support checks, and verify retry classification for known errors.

## State And Persistence
Filesystem effects are limited to temporary log files and gzip output under `t.TempDir()`. The package-level `krbdFeatures` variable is mutated in parallel subtests, which is a test-global side effect.

## Dependencies And Integration Points
The tests depend on go-ceph RBD feature parsing and errors, RADOS permission errors, Ceph-CSI internal errors, util sentinel errors, and `testify/require`.

## Risks
The tests avoid real Ceph connections. Parallel tests mutating package-level `krbdFeatures` could become flaky if additional tests assume a different value concurrently. The file does not cover JSON stash, image deletion, RBD metadata migration, or volume ID generation.

## Test Signals
Good signal for feature validation and local log policy; weak signal for backend behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/rbd_util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/replication.go -->
# sources/control-plane/ceph-csi/internal/rbd/replication.go

## Purpose
`replication.go` contains small RBD-specific helpers for mirrored/replicated volumes: repairing image IDs after resync and safely disabling mirroring depending on local primary/secondary state.

## Important APIs, Types, And Functions
`rbdVolume.RepairResyncedImageID` updates the OMAP image ID after a mirror resync replaces the local image. `DisableVolumeReplication` operates on the `types.Mirror` interface and validates primary/secondary behavior against go-ceph mirroring states.

## Control Flow
`RepairResyncedImageID` returns immediately unless the resync is ready, connects to the volume journal, then calls `repairImageID` with `force=true`. `DisableVolumeReplication` allows a secondary image to succeed only when global status reports local site `up` and `replaying`; otherwise it returns invalid-argument style errors. For primary images it disables mirroring, then verifies the image reports disabled state.

## State And Persistence
Persistent state is Ceph-CSI volume journal OMAP image ID and Ceph RBD mirror state. Runtime state is the mirror status returned by the `types.Mirror` implementation.

## Dependencies And Integration Points
It depends on go-ceph RBD mirror status constants, internal RBD errors, the volume journal, and the replication/mirroring interfaces under `internal/rbd/types`. It is used by replication controller/server flows outside this subset.

## Risks
After disabling mirroring, state may remain transitional; the function treats non-disabled state as aborted. Secondary cleanup success is deliberately narrow and depends on global status semantics. Repairing image IDs assumes the resynced image is accessible and journal credentials are valid.

## Test Signals
No direct tests in this subset. Mirror status tests should cover primary disable success, disabled-state lag, healthy secondary replaying success, unhealthy secondary failures, and image ID repair only when ready.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/replication.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/sms_controllerserver.go -->
# sources/control-plane/ceph-csi/internal/rbd/sms_controllerserver.go

## Purpose
`sms_controllerserver.go` implements CSI Snapshot Metadata Service streaming RPCs for RBD snapshots: allocated metadata for one snapshot and delta metadata between two snapshots.

## Important APIs, Types, And Functions
Key functions are `normalizeMaxResults`, `validateMetadataAllocatedReq`, `ControllerServer.GetMetadataAllocated`, `validateMetadataDeltaReq`, and `ControllerServer.GetMetadataDelta`. `defaultMaxResults` caps streamed batch size at 128.

## Control Flow
Both RPCs first check `features.SupportsRBDSnapDiffByID`, validate IDs, secrets, starting offset, and max results, then create a manager with request secrets. `GetMetadataAllocated` resolves one snapshot and streams `ProcessMetadata` with no base snapshot. `GetMetadataDelta` resolves base and target snapshots and streams `ProcessMetadata` against the target with the base snapshot. Both reject starting offsets beyond the target volume size and wrap each sent batch in CSI response messages with variable-length block metadata and capacity.

## State And Persistence
The server does not write persistent state. It opens manager/snapshot resources and streams responses over gRPC. It depends on snapshot size and RBD diff iteration state from `snap_diff.go`.

## Dependencies And Integration Points
It depends on CSI snapshot metadata service protobufs, go gRPC status codes, feature probing, `NewManager`, RBD snapshot resolution, and `rbdSnapshot.ProcessMetadata`.

## Risks
The feature probe is runtime-gated and returns `Unimplemented` when unavailable. `maxResults` is capped internally, which can surprise callers requesting larger batches but protects memory. Secrets are mandatory. Starting offset is checked before LUKS header padding is applied in `ProcessMetadata`, so encrypted snapshots rely on downstream adjustment. Snapshot resolution errors are mapped to `NotFound` only for `ErrImageNotFound`.

## Test Signals
`sms_controllerserver_test.go` covers validation and max-results normalization. It does not test streaming RPCs, feature-gate failures, manager interactions, snapshot lookup, or send failures.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/sms_controllerserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/sms_controllerserver_test.go -->
# sources/control-plane/ceph-csi/internal/rbd/sms_controllerserver_test.go

## Purpose
`sms_controllerserver_test.go` validates request validation and max-results normalization for Snapshot Metadata Service controller methods.

## Important APIs, Types, And Functions
Tests are `Test_validateMetadataAllocatedReq`, `Test_validateMetadataDeltaReq`, and `Test_normalizeMaxResults`.

## Control Flow
The tests use table-driven CSI request objects to check valid input, missing IDs, negative starting offsets, negative max results, empty secrets, zero max defaulting, over-limit capping, and in-limit preservation.

## State And Persistence
All state is in memory. No RBD or gRPC stream is created.

## Dependencies And Integration Points
The file depends on CSI protobuf request types and package constants. It guards the input contract before snapshot manager and diff code run.

## Risks
It does not assert exact gRPC status codes for validation errors, only error presence. It does not cover nil request handling, feature-gate behavior, or the streaming methods.

## Test Signals
Good signal for basic request guards and batch-size cap; weak signal for end-to-end metadata streaming.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/sms_controllerserver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/snap_diff.go -->
# sources/control-plane/ceph-csi/internal/rbd/snap_diff.go

## Purpose
`snap_diff.go` implements RBD snapshot diff streaming for the CSI Snapshot Metadata Service. It uses librbd `DiffIterateByID` to report allocated or changed byte ranges in batches, with support for encrypted-volume LUKS header offset correction.

## Important APIs, Types, And Functions
The central method is `rbdSnapshot.ProcessMetadata`. Supporting helpers are `handleDiffIterateError` and `createDiffIterateByIDCB`.

## Control Flow
`ProcessMetadata` opens the snapshot image, resolves the target snapshot ID via `getRBDSnapID`, sets the image to that snapshot, optionally converts and resolves the base snapshot ID, reads LUKS header padding metadata, shifts the requested starting offset by that padding, and returns early if beyond volume size. It creates a callback that appends `csi.BlockMetadata`, flushes when `maxResults` is reached, then calls `image.DiffIterateByID`. After iteration, remaining blocks are sent.

## State And Persistence
No persistent state is written. Runtime state includes the open RBD image, snapshot selection, local `changedBlocks` batch slice, and callback return codes. The reported offsets subtract LUKS header padding so callers see user-data offsets.

## Dependencies And Integration Points
It depends on go-ceph RBD `DiffIterateByID`, CSI block metadata, gRPC codes used as callback status integers, RBD snapshot conversion from `snapshot.go`, encryption metadata helpers, and snapshot metadata controller methods in `sms_controllerserver.go`.

## Risks
`createDiffIterateByIDCB` subtracts `luksHeaderPadding` from an unsigned offset; if librbd reports an offset below the padding, it underflows before conversion to `int64`. `maxResults` must be positive or every callback will flush immediately because `len < maxResults` is false; controller validation permits zero only after normalization. Error-code handling depends on errors implementing the local `ErrorCode` interface. A send failure is surfaced through callback code `Unknown`, then wrapped.

## Test Signals
`snap_diff_test.go` covers callback batching, LUKS offset adjustment, cancellation, send errors, remainder handling, no-block behavior, and `handleDiffIterateError` mappings. It does not exercise real RBD diff iteration, snapshot ID lookup, LUKS metadata read, or base-snapshot delta setup.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/snap_diff.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/snap_diff_test.go -->
# sources/control-plane/ceph-csi/internal/rbd/snap_diff_test.go

## Purpose
`snap_diff_test.go` unit-tests the pure callback and error-handling parts of snapshot diff streaming.

## Important APIs, Types, And Functions
It defines `mockError` implementing `Error()` and `ErrorCode()`, `newMockError`, `Test_createDiffIterateByIDCB`, `Test_createDiffIterateByIDCB_errorAndEdgeCases`, and `Test_handleDiffIterateError`.

## Control Flow
The callback tests simulate librbd diff callbacks for single blocks, LUKS padding adjustment, max-result batching and slice reset, send errors, context cancellation, multiple batches with remainder, and zero-block cases. Error tests feed nil, OK, canceled, unknown/send failure, unrecognized code, and generic errors into `handleDiffIterateError`.

## State And Persistence
All state is in memory. The tests copy sent batches to avoid slice reuse hiding bugs.

## Dependencies And Integration Points
The tests depend on CSI `BlockMetadata` and gRPC `codes`, but do not require go-ceph or a live RBD image. They validate behavior used by `rbdSnapshot.ProcessMetadata`.

## Risks
The tests do not cover unsigned underflow when LUKS padding exceeds callback offset. They also do not cover actual `DiffIterateByID` integration, final remainder flushing by `ProcessMetadata`, or base snapshot ID handling.

## Test Signals
Strong signal for callback batching and error code translation; weak signal for backend diff behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/snap_diff_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/snapshot.go -->
# sources/control-plane/ceph-csi/internal/rbd/snapshot.go

## Purpose
`snapshot.go` implements RBD snapshot image creation, conversion between RBD volume and snapshot models, CSI snapshot rendering, snapshot deletion, snapshot image creation by parent snapshot ID, group snapshot association, and snapshot ID lookup for diff iteration.

## Important APIs, Types, And Functions
Important functions include `createRBDClone`, `cleanUpSnapshot`, `rbdVolume.toSnapshot`, `rbdSnapshot.toVolume`, `rbdSnapshot.ToCSI`, `rbdSnapshot.Delete`, `undoSnapshotCloning`, `rbdVolume.NewSnapshotByID`, `rbdSnapshot.SetVolumeGroup`, `rbdSnapshot.GetSize`, `rbdSnapFromSnapshot`, and `rbdSnapshot.getRBDSnapID`.

## Control Flow
`createRBDClone` creates a parent snapshot, clones it, and optionally deletes the temporary snapshot. `cleanUpSnapshot` removes both the RBD snapshot and backing image, ignoring not-found cases. `ToCSI` validates IDs, obtains creation time, and emits a ready CSI snapshot. `Delete` converts the snapshot to a volume, connects, removes snapshot image and snapshot, then undoes the journal reservation. `NewSnapshotByID` reserves a journal entry, forces layering and deep-flatten features, clones by source snapshot ID into a new image, creates a snapshot on that image, repairs the image ID in the journal, and uses defers to remove the snapshot image on failure.

## State And Persistence
Persistent state includes RBD snapshots, cloned snapshot backing images, journal reservations, journal image IDs, optional group IDs, and CSI-visible snapshot metadata. Runtime state includes copied encryption helpers and open IO contexts/images. Conversion helpers intentionally copy encryption pointers rather than using clone-copy helpers because volume and snapshot can share the same ID.

## Dependencies And Integration Points
It depends on go-ceph RBD clone/snapshot APIs, CSI snapshot protobufs, journal helpers in `rbd_journal.go`, shared image helpers in `rbd_util.go`, internal snapshot interfaces, and group snapshot support.

## Risks
Comments note a known modeling issue: snapshot resolution can set `RbdImageName` to the parent/source name, which can make deletion dangerous if not fixed by manager code. Defers in `NewSnapshotByID` remove images after failure and must not run after success. `createRBDClone` returns nil when clone fails and `deleteSnap` is false only after wrapping `err`, so callers must inspect behavior carefully. Snapshot deletion should run under request-name locks because it manipulates OMAP.

## Test Signals
Only `snapshot_test.go` outside this requested output directly covers `ToCSI` and `rbdSnapFromSnapshot`; this subset has no mapped snapshot test file. Backend clone/delete behavior needs integration testing with Ceph.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/snapshot.go -->
