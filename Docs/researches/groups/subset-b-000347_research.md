# subset-b-000347 Research

Grouped research for the listed Ceph-CSI RBD files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/controllerserver.go -->
# sources/control-plane/ceph-csi/internal/rbd/controllerserver.go

## Purpose
Implements the RBD CSI controller service: volume create/delete/expand/modify, snapshot create/delete, controller publish/unpublish metadata handoff, fencing, and group-controller entrypoints through the shared `ControllerServer` state. It is the main orchestration layer between CSI requests, RADOS OMAP journals, librbd image operations, Kubernetes metadata, encryption, QoS, clone/snapshot repair, and mirroring-aware cleanup.

## Important APIs, Types, And Functions
`ControllerServer` embeds the common controller server and owns `VolumeLocks`, `SnapshotLocks`, `OperationLocks`, `VolumeGroupLocks`, and `ClusterName`. Validation and parsing are split across `validateVolumeReq`, `validateStriping`, `validateQoSParameters`, and `parseVolCreateRequest`. Main CSI RPCs include `CreateVolume`, `DeleteVolume`, `ValidateVolumeCapabilities`, `CreateSnapshot`, `DeleteSnapshot`, `ControllerExpandVolume`, `ControllerPublishVolume`, `ControllerUnpublishVolume`, and `ControllerModifyVolume`. Helpers such as `buildCreateVolumeResponse`, `checkContentSource`, `createBackingImage`, `flattenParentImage`, `repairExistingVolume`, `cleanupRBDImage`, `cleanUpImageAndSnapReservation`, `getServiceAccountRestriction`, `removeUserIdMapping`, and `fenceNode` hold much of the operational detail.

## Control Flow
Create-volume validates CSI capabilities and StorageClass parameters, builds an `rbdVolume`, initializes KMS/encryption state, resolves topology and QoS mutable parameters, connects to Ceph, takes a name lock, resolves optional snapshot or volume content source, checks/repairs existing images, flattens parent chains, reserves a journal entry, creates or clones the image, stores the image ID, applies QoS, writes Kubernetes metadata, and returns CSI volume context. Delete-volume validates the ID, handles migration IDs specially, locks by volume ID and request name, resolves the image from journal state, then either removes only OMAP for healthy mirrored secondaries or deletes temp image, image, and reservation. Snapshot creation validates the source, locks by snapshot name/source volume, reserves snapshot journal state, prepares the parent image, creates a temporary clone, snapshots the clone, stores image ID, writes snapshot metadata, and returns CSI snapshot data. Expansion and modify-volume validate volume IDs, lock against conflicting operations, resolve migration-aware volumes, adjust QoS when needed, and resize or update mutable attributes. Controller publish reads service-account restriction metadata for node-side enforcement, while unpublish removes node metadata and optionally Ceph-blocklists out-of-service nodes.

## State And Persistence
Persistent state is split across RADOS journal reservations (`volJournal`, `snapJournal`), RBD images and snapshots, image metadata keys for Kubernetes, mounter, encryption, service-account restrictions, client/user mappings, and Ceph blocklist entries. Locks are in-memory request guards only and protect idempotent operations from concurrent same-object changes. Several paths are explicitly restart/idempotency aware: existing create calls repair metadata/encryption/size, delete cleans orphaned OMAP when images are missing, and snapshot create resumes interrupted clone/flatten sequences.

## Dependencies And Integration Points
The file depends on CSI protobufs, `csicommon` capability validation, `util` credentials/ID/topology/lock helpers, Kubernetes metadata/secret helpers, go-ceph `rbd` and OSD admin APIs, RBD-specific errors, encryption helpers, QoS helpers, migration helpers, mirror wrappers, and journal globals from `globals.go`. It is instantiated by `internal/rbd/driver/driver.go` and shares volume/group abstractions with manager and group code.

## Risks And Test Signals
High-risk areas are cleanup/idempotency during partial failures, lock ordering across create/delete/clone/expand/modify, orphaned reservations, clone-depth flatten side effects, NBD-vs-cgroup QoS parameter ambiguity, mirroring secondary deletion semantics, Kubernetes-only fencing behavior, and secret lookup fallback in controller publish/unpublish. Tests in `controllerserver_test.go` cover striping validation, `ToCSI` required fields, and QoS parameter disambiguation, but the full RPC paths rely heavily on integration/e2e coverage with real Ceph and Kubernetes behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/controllerserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/controllerserver_test.go -->
# sources/control-plane/ceph-csi/internal/rbd/controllerserver_test.go

## Purpose
Provides focused unit coverage for controller helpers that can be exercised without a Ceph cluster: striping parameter validation, conversion of an `rbdVolume` into a CSI volume, and QoS mutable-parameter validation by mounter type.

## Important APIs, Types, And Functions
`TestValidateStriping` verifies paired `stripeUnit`/`stripeCount` rules and `objectSize` power-of-two parsing. `TestToCSIVolume` verifies `rbdVolume.ToCSI` rejects missing required identity fields and succeeds when volume ID, pool, journal pool, and image name are set. `TestValidateQoSParameters` covers the split between krbd cgroup QoS parameters and rbd-nbd QoS/max-limit parameters.

## Control Flow
Each test is table-driven and runs subtests in parallel. Inputs are plain maps or lightweight `rbdVolume` structs, so the tests stay isolated from external state. Assertions compare only error presence, not exact messages.

## State And Persistence
No persistent state is created. The tests rely on package constants for QoS keys and mounter names, which makes them sensitive to controller/QoS helper API changes.

## Dependencies And Integration Points
The file integrates with unexported helpers in `controllerserver.go` by being in package `rbd`. It indirectly exercises the shape expected by CSI response construction but does not marshal or call gRPC handlers.

## Risks And Test Signals
The tests give useful regression signals for validation rules that run before Ceph resources are created. Coverage gaps remain around full `CreateVolume`, delete, snapshot, fencing, mirroring, and journal cleanup paths. Because assertions are only boolean error checks, changed error codes/messages could regress user-facing CSI behavior without failing these tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/controllerserver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/diskusage.go -->
# sources/control-plane/ceph-csi/internal/rbd/diskusage.go

## Purpose
Adds disk-space reclamation support for RBD images through `rbdImage.Sparsify`, used by CSI-Addons reclaim-space workflows to punch out zero-filled extents and reduce backend usage.

## Important APIs, Types, And Functions
`(*rbdImage).Sparsify(ctx)` checks whether the image is in use, opens the image, reads image order from `Stat`, and calls go-ceph/librbd `Sparsify` with an object-size granularity of `1 << imageInfo.Order`. It returns `rbderrors.ErrImageInUse` when active I/O is detected.

## Control Flow
The function first calls `isInUse`; any check failure is wrapped. If the image is active, it refuses to sparsify. Otherwise it opens the image, defers close with warning logging on close failure, fetches image stats, and invokes librbd sparsification.

## State And Persistence
The operation mutates backend RBD allocation state by freeing zeroed blocks. It does not alter CSI journals or image metadata. The only local state is the temporary opened librbd image handle.

## Dependencies And Integration Points
Depends on `rbdImage` open/in-use helpers, go-ceph librbd image methods, package errors, and logging. The method is part of the broader RBD image abstraction consumed by CSI-Addons reclaim-space servers registered in the driver.

## Risks And Test Signals
Main risks are running against an image that is actively used despite `isInUse` checks, choosing a granularity inappropriate for some image layouts, and propagation of low-level librbd failures. This file has no direct unit test in the subset; meaningful coverage likely requires integration tests against a real image.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/diskusage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/driver/driver.go -->
# sources/control-plane/ceph-csi/internal/rbd/driver/driver.go

## Purpose
Bootstraps the RBD CSI driver process. It initializes global RBD settings and journals, constructs identity/controller/node servers, advertises CSI capabilities, starts the main non-blocking CSI gRPC server, registers CSI-Addons services, detects runtime librbd/kernel features, and optionally starts profiling and node healing.

## Important APIs, Types, And Functions
`rbdDriver` stores the common CSI driver and RBD identity/node/controller servers plus a CSI-Addons server. `NewDriver`, `NewIdentityServer`, `NewControllerServer`, and `NewNodeServer` allocate runtime components. `Run(conf)` is the main entrypoint. `setupCSIAddonsServer` registers CSI-Addons identity, fencing, reclaim-space, replication, volume-group, and encryption-key-rotation services according to controller/node roles. `startProfiling` starts metrics and pprof handlers when enabled.

## Control Flow
`Run` first copies config values into RBD package globals and initializes journals. It builds the common CSI driver, adds controller and volume capability modes when in controller mode, conditionally advertises group snapshot support after `features.SupportsGroupSnapGetInfo`, fetches Kubernetes node labels/topology when needed, creates server structs, detects krbd and rbd-nbd features on node processes, configures CSI-Addons, starts the CSI gRPC server with identity/controller/node/group/SMS services, starts profiling, optionally launches the volume healer goroutine, and waits for server shutdown.

## State And Persistence
The file mutates package-level global RBD configuration (`rbdHardMaxCloneDepth`, snapshot limits, `skipForceFlatten`, `krbdFeatures`) and global journal configs. It creates long-lived gRPC server sockets/endpoints and a CSI-Addons endpoint. Node-label/topology data is read from Kubernetes but not persisted here.

## Dependencies And Integration Points
Integrates `internal/csi-common`, `internal/driver`, `internal/rbd`, `internal/rbd/features`, CSI-Addons RBD services, Kubernetes helpers, util config, logging, and kernel/librbd feature detection. It is the process-level connection point between CLI/config startup and all lower RBD controllers.

## Risks And Test Signals
Risks include global settings making per-cluster variation difficult, feature detection failures changing advertised capabilities, fatal startup on Kubernetes/topology or krbd parsing errors, and lifecycle interactions between the main server and CSI-Addons server. `driver_test.go` only smoke-tests CSI-Addons socket startup; broader startup and capability behavior needs integration testing.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/driver/driver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/driver/driver_test.go -->
# sources/control-plane/ceph-csi/internal/rbd/driver/driver_test.go

## Purpose
Smoke-tests creation and startup of the RBD CSI-Addons server on a Unix socket endpoint.

## Important APIs, Types, And Functions
`TestSetupCSIAddonsServer` builds a temporary `unix://` endpoint, calls `(*rbdDriver).setupCSIAddonsServer`, checks that `drv.cas` is non-nil, verifies the socket file exists, and stops the server.

## Control Flow
The test uses `t.TempDir` to isolate the endpoint, creates a minimal `util.Config` with only `CSIAddonsEndpoint`, invokes setup, asserts success with `testify/require`, then performs filesystem existence validation.

## State And Persistence
The only state is a temporary Unix socket under the test temp directory. No Ceph, Kubernetes, or CSI main server state is required.

## Dependencies And Integration Points
Depends on the CSI-Addons server implementation and service registration being able to start with a minimal config. It indirectly validates that default registration paths do not panic when controller/node booleans are unset.

## Risks And Test Signals
This is a useful lifecycle smoke test but does not call any CSI-Addons RPCs or validate role-specific services. Failures usually indicate endpoint binding, server startup, or registration regressions.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/driver/driver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/encryption.go -->
# sources/control-plane/ceph-csi/internal/rbd/encryption.go

## Purpose
Implements RBD encryption configuration, metadata migration, KMS integration, DEK storage through image metadata, LUKS device open/format helpers, and block-encryption key rotation.

## Important APIs, Types, And Functions
`rbdEncryptionState` models unknown, prepared, and encrypted states. Metadata keys include current and legacy encryption/DEK keys plus LUKS2 header-size metadata. Core helpers are `getLuksHeaderSizeMetadata`, `checkRbdImageEncrypted`, `ensureEncryptionMetadataSet`, `isBlockEncrypted`, `isFileEncrypted`, `IsFileEncrypted`, `setupBlockEncryption`, `copyEncryptionConfig`, `repairEncryptionConfig`, `encryptDevice`, `openEncryptedDevice`, `initKMS`, `parseCipherOptions`, `ParseEncryptionOpts`, `configureBlockEncryption`, `configureFileEncryption`, `StoreDEK`, `FetchDEK`, `RemoveDEK`, `GetEncryptionPassphraseSize`, and `RotateEncryptionKey`.

## Control Flow
Creation-time parsing starts with `ParseEncryptionOpts`, which interprets `encrypted`, KMS ID, and optional encryption type, then `initKMS` configures block or file encryption. Block encryption may parse cryptsetup cipher/key/integrity/sector options and uses KMS plus optional RBD metadata DEK store. `setupBlockEncryption` stores a new passphrase and marks metadata as prepared. Node/device paths use `encryptDevice` to format and mark encrypted, and `openEncryptedDevice` to map a LUKS device. Clone/snapshot flows use `copyEncryptionConfig` or `repairEncryptionConfig` to copy passphrases/configuration and metadata. `RotateEncryptionKey` validates encrypted state, opens ioctx, takes a RADOS lock based on object UUID, adds a backup LUKS key, generates/stores a new key, and removes the backup slot.

## State And Persistence
Persistent state lives in KMS backends, RBD image metadata (`encrypted`, DEK, LUKS header size), LUKS slots on the mapped device, and temporary RADOS locks for key rotation. Legacy metadata is migrated with `MigrateMetadata`. `RemoveDEK` intentionally leaves metadata untouched because image deletion typically removes it.

## Dependencies And Integration Points
Depends on KMS APIs, `util.VolumeEncryption`, cryptsetup wrappers, RBD metadata helpers, RADOS lock helpers, package mounter state, and wait-for-device path helpers. Controller create/clone/snapshot paths call KMS initialization and config copy, while node paths use device encryption/open helpers.

## Risks And Test Signals
Risks include metadata/KMS inconsistency after partial failures, unsupported file-encryption KMS behavior, unsafe key-rotation interruption after KMS update but before LUKS cleanup, mismatched volume IDs in DEK store methods, and LUKS header-size compatibility for older images. `encryption_test.go` covers option parsing and cipher validation but not live KMS, metadata migration, cryptsetup, or rotation.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/encryption.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/encryption_test.go -->
# sources/control-plane/ceph-csi/internal/rbd/encryption_test.go

## Purpose
Unit-tests the pure parsing layer for RBD encryption options: whether encryption is enabled, how KMS IDs and encryption types are resolved, and how cryptsetup cipher options are accepted or rejected.

## Important APIs, Types, And Functions
`TestParseEncryptionOpts` checks missing `encrypted`, false values, invalid booleans, and a valid KMS ID. `TestParseCipherOptions` checks nil options when no cipher is provided, allowed AES-XTS settings, integrity/key-size/sector-size handling, and rejection of unsafe AES-GCM style configuration. `valueToPointer` helps construct expected option fields.

## Control Flow
Both tests are table-driven and parallel. `TestParseCipherOptions` constructs an expected `cryptsetup.EncryptionOptions` using the same setter APIs used by production code, then compares the resulting struct to the parser output.

## State And Persistence
No external or persistent state is used. The tests do not instantiate KMS backends, RBD images, device mappings, or metadata.

## Dependencies And Integration Points
The file depends on `cryptsetup.EncryptionOptions`, `crypto.EncryptionType`, and `testify` assertions. It validates the front door used by `initKMS` before controller create proceeds.

## Risks And Test Signals
The tests are strong signals for rejecting invalid encryption configuration before resource creation. Coverage gaps include `configureBlockEncryption`, file encryption KMS compatibility, DEK storage, metadata migration, LUKS formatting/opening, and key rotation failure handling.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/encryption_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/errors/errors.go -->
# sources/control-plane/ceph-csi/internal/rbd/errors/errors.go

## Purpose
Centralizes sentinel errors and an optional error-code interface for RBD package operations. These errors let controller, group, migration, mirror, and utility paths classify expected failure modes with `errors.Is`.

## Important APIs, Types, And Functions
Sentinels include image/snapshot not found, volume-name conflict, invalid volume ID, missing stash, flatten in progress, migration volume-ID field errors, last-sync info missing, failed precondition, unavailable, aborted, invalid argument, image in use, group not connected/found, and unknown mounter. `ErrGroupNotConnected` and `ErrGroupNotFound` wrap go-ceph/rados or librbd errors to preserve lower-level classification. `ErrorCode` defines `ErrorCode() int` for error types that can expose numeric codes.

## Control Flow
The file is declarative. Runtime behavior comes from callers matching these sentinels and translating them into gRPC codes or retry decisions.

## State And Persistence
No state is persisted. The sentinel values are process-global constants by convention.

## Dependencies And Integration Points
Imports standard errors/fmt plus go-ceph `rados` and `rbd` error values. `controllerserver.go`, `group/util.go`, `manager.go`, `migration.go`, `mirror.go`, and disk usage paths use these sentinels for idempotency, cleanup, and status mapping.

## Risks And Test Signals
Risk comes from changing or wrapping errors in a way that breaks `errors.Is` checks in controller cleanup and retry paths. This file has no direct tests, but many table tests and integration paths depend on stable sentinel identity.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/errors/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/features/dlsym.go -->
# sources/control-plane/ceph-csi/internal/rbd/features/dlsym.go

## Purpose
Provides a small cgo helper for dynamic symbol detection in already loaded native libraries. It lets Ceph-CSI decide whether optional librbd functions are available at runtime.

## Important APIs, Types, And Functions
`dlsym(symbol string) error` converts the symbol to a C string, clears `dlerror`, calls `dlsym(nil, symbol)`, reads `dlerror`, and returns nil only when lookup succeeds.

## Control Flow
The helper checks the global process symbol table rather than opening a specific library handle. It frees the allocated C string with `C.free` and wraps any dynamic-loader message in a Go error.

## State And Persistence
No persistent state is stored. It observes process-loaded shared libraries and their exported symbols.

## Dependencies And Integration Points
Depends on cgo, `libdl`, and unsafe pointer conversion. `features.go` calls this after forcing librbd to load so it can gate group snapshot and snapshot-diff capabilities.

## Risks And Test Signals
Risks include platform/linker differences, cgo availability, and interpreting non-undefined-symbol `dlerror` values. It is indirectly exercised by `features_test.go`, which calls feature detection against the test runtime’s librbd.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/features/dlsym.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/features/features.go -->
# sources/control-plane/ceph-csi/internal/rbd/features/features.go

## Purpose
Detects optional librbd runtime capabilities used to advertise CSI/CSI-Addons features only when the installed native library supports them.

## Important APIs, Types, And Functions
`SupportsGroupSnapGetInfo` checks for `rbd_group_snap_get_info`, enabling VolumeGroupSnapshot support. `SupportsRBDSnapDiffByID` checks for `rbd_diff_iterate3`, enabling Snapshot Metadata service support. Package-level `sync.Once` values cache support booleans and errors.

## Control Flow
Each detector first calls `rbd_image_options_create/destroy` through cgo to force librbd to load, then calls `dlsym`. Undefined-symbol errors are treated as unsupported but non-fatal; other loader errors are returned. Results are cached for the process lifetime.

## State And Persistence
State is in-memory only: once guards, cached errors, and cached booleans. There is no disk or cluster persistence.

## Dependencies And Integration Points
Depends on cgo linking with `-lrbd`, `dlsym.go`, and string inspection of loader errors. `driver.go` uses group snapshot detection before advertising group-controller capability; `identityserver.go` uses both detectors when returning plugin capabilities.

## Risks And Test Signals
Runtime library upgrades after process start will not be observed because results are cached. Error-string matching for `undefined symbol` is environment-sensitive. `features_test.go` only logs support and fails on unexpected detection errors, making it an environment smoke test rather than deterministic feature assertion.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/features/features.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/features/features_test.go -->
# sources/control-plane/ceph-csi/internal/rbd/features/features_test.go

## Purpose
Smoke-tests librbd group snapshot capability detection in the current test environment.

## Important APIs, Types, And Functions
`TestSupportsGroupSnapGetInfo` calls `SupportsGroupSnapGetInfo`, fails if detection returns an unexpected error, and logs whether the symbol is supported.

## Control Flow
The test runs in parallel and does not assert a fixed support value, because installed librbd versions may differ across environments.

## State And Persistence
No persistent state is written. The test populates the package-level `sync.Once` cache in `features.go`, which can affect subsequent tests in the same process.

## Dependencies And Integration Points
Depends on cgo/native librbd availability and dynamic symbol detection. It verifies the detection path used by driver and identity capability advertisement.

## Risks And Test Signals
This catches broken dynamic loading but not incorrect capability wiring. Because it accepts both supported and unsupported states, it cannot detect accidental loss of support on environments that should provide the symbol.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/features/features_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/globals.go -->
# sources/control-plane/ceph-csi/internal/rbd/globals.go

## Purpose
Holds package-level RBD configuration and journal handles that are initialized by the driver and consumed across controller/node/helper code.

## Important APIs, Types, And Functions
Globals include `volJournal`, `snapJournal`, clone-depth limits, snapshot-count flatten thresholds, `skipForceFlatten`, and `krbdFeatures`. `SetGlobalInt` mutates known numeric settings, `SetGlobalBool` mutates known boolean settings, and `InitJournals` creates CSI volume and snapshot journal configs for the driver instance.

## Control Flow
Setters switch on string keys and panic for unknown variables, making startup misconfiguration fail fast. `InitJournals` builds journal configs but does not connect them until operation code calls `Connect`.

## State And Persistence
All state is process-global. The journal configs point to RADOS OMAP-backed persistent journal data, but this file only stores configuration objects and scalar runtime settings.

## Dependencies And Integration Points
Depends on `internal/journal`. `driver.go` sets these globals at startup; `controllerserver.go` and snapshot/volume helper paths use `volJournal` and `snapJournal`; clone/flatten behavior reads depth and snapshot thresholds.

## Risks And Test Signals
Global mutable state limits multi-cluster or per-StorageClass tuning and can make tests order-sensitive. Panic-on-unknown-key catches programmer errors but is not recoverable. There are no direct tests for this file.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/globals.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/group.go -->
# sources/control-plane/ceph-csi/internal/rbd/group.go

## Purpose
Adapts `rbdVolume` to the volume-group interfaces used by the RBD group package and CSI-Addons volume-group workflows.

## Important APIs, Types, And Functions
`(*rbdVolume).AddToGroup` validates current group membership and calls `librbd.GroupImageAdd`. `RemoveFromGroup` calls `librbd.GroupImageRemove`. `GetVolumeGroupID` reads librbd group information for an image and asks a resolver to construct a CSI volume-group ID.

## Control Flow
Add opens the image, reads its current group, rejects membership in a different group, then adds the image to the requested group using the group IO context and image IO context. Removal resolves the group name and IO context, then removes the image. ID lookup opens the image, reads group info, returns `ErrGroupNotFound` if none is set, otherwise resolves the backend pool/name into a CSI handle.

## State And Persistence
These methods mutate or read librbd group membership. They do not directly write the RADOS journal; higher-level `group/volume_group.go` updates journal volume maps after successful membership changes.

## Dependencies And Integration Points
Depends on go-ceph/librbd, RBD image open helpers, `types.VolumeGroup`, `types.VolumeGroupResolver`, and group errors. It is called by the `internal/rbd/group` package when creating/removing groups and by manager comparison logic.

## Risks And Test Signals
Risks include inconsistent state if librbd membership succeeds but journal updates fail, or if image group info is stale during concurrent group operations. There are no direct unit tests for these methods; behavior is best covered by group snapshot and CSI-Addons integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/group.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/group/group_snapshot.go -->
# sources/control-plane/ceph-csi/internal/rbd/group/group_snapshot.go

## Purpose
Implements the `types.VolumeGroupSnapshot` abstraction backed by RBD group snapshots and RADOS volume-group journal mappings.

## Important APIs, Types, And Functions
`volumeGroupSnapshot` embeds `commonVolumeGroup` and tracks snapshot objects plus snapshots it owns for cleanup. `GetVolumeGroupSnapshot` resolves an existing group snapshot from a CSI ID and journal volume map. `NewVolumeGroupSnapshot` records newly created snapshot IDs/names in the journal and stores the group ID on each snapshot. Methods `ToCSI`, `Destroy`, `Delete`, and `ListSnapshots` expose CSI conversion, cleanup, deletion, and enumeration.

## Control Flow
Lookup initializes common group state, fetches journal attributes, resolves each snapshot ID through the provided resolver, and stores resolved snapshots for later destruction. Creation initializes common state, validates existing attributes, builds a snapshot ID-to-name map, updates each snapshot with its group ID, and writes the mapping through `AddVolumesMapping`. Delete iterates all child snapshots and deletes them before removing the common journal reservation.

## State And Persistence
Persistent state includes journal attributes and volume maps, snapshot image metadata linking snapshots to the group ID, and backend snapshot images themselves. In-memory `snapshotsToFree` prevents leaks for resolved snapshot handles.

## Dependencies And Integration Points
Depends on CSI group snapshot protobufs, common group journal utilities, `types.SnapshotResolver`, `types.Snapshot`, and RBD error sentinels. It is created and resolved by `manager.go` and returned by `group_controllerserver.go`.

## Risks And Test Signals
Risks include partial creation where some snapshots have group metadata but journal mapping fails, delete stopping on the first failed child snapshot, and map iteration order producing non-deterministic CSI snapshot ordering. No direct tests exist in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/group/group_snapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/group/util.go -->
# sources/control-plane/ceph-csi/internal/rbd/group/util.go

## Purpose
Provides shared state and helpers for RBD volume groups and volume group snapshots: CSI ID decomposition, cluster/pool/namespace resolution, journal connection, IO context management, common getters, journal deletion, creation-time lookup, and retry classification for mapped clusters.

## Important APIs, Types, And Functions
`commonVolumeGroup` stores IDs, names, creation time, cluster/pool/namespace details, credentials, cached connection/ioctx, driver instance, and journal. Key methods are `generateVolumeGroup`, `generateVolumeGroupFromMapping`, `initCommonVolumeGroup`, `Destroy`, `getVolumeGroupAttributes`, `String`, `GetID`, `GetName`, `GetRequestName`, `GetPool`, `GetClusterID`, `getConnection`, `getJournal`, `GetIOContext`, `Delete`, `GetCreationTime`, and `ShouldRetryVolumeGroupGeneration`.

## Control Flow
Initialization decomposes the CSI ID, resolves monitors/namespace/pool, reads journal attributes, and if retryable errors occur tries cluster and pool ID mappings. Journal attributes populate request name, backend group name, and creation time. Connections, journals, and IO contexts are created lazily and cached. Destroy releases ioctx, connection, credential reference, and journal. Delete removes the journal reservation for the group.

## State And Persistence
Persistent state is the RADOS volume-group journal reservation and volume map. Runtime state includes cached credentials references, cluster connection, IO context, and journal handle. The helper intentionally does not own credential deletion; callers that allocated credentials must delete them.

## Dependencies And Integration Points
Depends on RADOS, journal volume-group APIs, util cluster mapping and ID helpers, logging, and RBD group errors. It underpins both `volume_group.go` and `group_snapshot.go`.

## Risks And Test Signals
Risks include returning `ErrGroupNotFound` for missing/empty journal attributes, retrying across cluster mappings incorrectly, leaking handles if Destroy is missed, and confusing journal pool versus data pool in cleanup. `util_test.go` verifies retry classification for known errors but not cluster mapping or journal behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/group/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/group/util_test.go -->
# sources/control-plane/ceph-csi/internal/rbd/group/util_test.go

## Purpose
Tests the retry classifier used when resolving volume groups across cluster and pool mappings.

## Important APIs, Types, And Functions
`Test_shouldRetryVolumeGroupGeneration` validates `ShouldRetryVolumeGroupGeneration` for nil, `util.ErrPoolNotFound`, `util.ErrConfigNotFound`, `rbderrors.ErrGroupNotFound`, `rados.ErrPermissionDenied`, and an arbitrary unknown error.

## Control Flow
The table-driven parallel test calls the helper with each error and compares the returned boolean to the expected continue/stop decision.

## State And Persistence
No persistent state is used. The test only checks sentinel identity through `errors.Is` in the implementation.

## Dependencies And Integration Points
Depends on RADOS, RBD group errors, and util error sentinels. It protects the mapped-cluster fallback path in `commonVolumeGroup.initCommonVolumeGroup`.

## Risks And Test Signals
This test is a narrow but valuable signal: overly broad retry classification could hide real failures, while overly narrow classification could break failover mapping lookup. It does not exercise actual mapping data or journal reads.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/group/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/group/volume_group.go -->
# sources/control-plane/ceph-csi/internal/rbd/group/volume_group.go

## Purpose
Implements the `types.VolumeGroup` abstraction backed by librbd groups and RADOS journal mappings, including group creation/deletion, volume membership management, CSI-Addons conversion, and group-consistent snapshot creation.

## Important APIs, Types, And Functions
`volumeGroup` embeds `commonVolumeGroup` and tracks member volumes plus owned volume handles. `GetVolumeGroup` resolves an existing group and its member volumes from journal mappings. Methods include `ToCSI`, `Destroy`, `Create`, `Delete`, `AddVolume`, `RemoveVolume`, `ListVolumes`, and `CreateSnapshots`.

## Control Flow
Lookup initializes common group state, loads journal attributes, resolves member volume IDs, and arranges cleanup ownership. Create calls `librbd.GroupCreate`, tolerating existing groups. Delete calls `librbd.GroupRemove`, tolerating missing groups, then removes the journal reservation. Add/remove operations update librbd membership first and then update the journal volume map. `CreateSnapshots` creates a temporary librbd group snapshot, reads group snapshot info, removes the temporary group snapshot on exit, matches returned snapshot entries to known volumes by image name, and creates CSI snapshot images from librbd snapshot IDs.

## State And Persistence
Persistent state includes the librbd group, image membership, snapshot images created from group snapshots, and RADOS journal reservation/membership mapping. The temporary librbd group snapshot is deliberately removed after per-volume snapshot images are created.

## Dependencies And Integration Points
Depends on go-ceph rados/librbd, CSI and CSI-Addons volume group protobufs, common group utilities, `types.Volume`, and journal mappings. It is used by `manager.go` and the controller group snapshot RPC path.

## Risks And Test Signals
Risks include split-brain between librbd membership and journal mapping, non-deterministic snapshot ordering from librbd info, partial snapshot creation cleanup, name-based matching between group snapshot entries and volumes, and tolerating `ErrExist`/`ErrNotFound` in ways that may mask stale state. No direct tests exist in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/group/volume_group.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/group_controllerserver.go -->
# sources/control-plane/ceph-csi/internal/rbd/group_controllerserver.go

## Purpose
Implements CSI group-controller RPCs for RBD volume group snapshots: create, delete, and get. It orchestrates volume resolution, temporary or existing librbd group usage, consistent group snapshot creation, cleanup, and CSI response conversion.

## Important APIs, Types, And Functions
`CreateVolumeGroupSnapshot` handles request validation, locking, manager setup, volume resolution, group matching, optional existing group reuse, temporary group creation, volume preparation, group snapshot lookup/create, and response assembly. `DeleteVolumeGroupSnapshot` resolves and deletes a group snapshot by ID. `GetVolumeGroupSnapshot` resolves and returns a group snapshot by ID.

## Control Flow
Create validates group-controller capability and locks by requested group snapshot name. It resolves all source volume IDs via `NewManager`, ensures volumes are all in the same group or no group, reuses an existing group if the first volume already belongs to one, returns an existing group snapshot if found by name, prepares each volume for snapshot, creates a temporary group when needed, adds volumes if the group is empty, asks the manager to create the group snapshot, converts to CSI, and uses defers to remove volumes/delete temporary groups on failure or after use. Delete/get validate capability, lock by group snapshot ID, resolve through the manager, translate not-found into CSI success for delete or NotFound for get, and call delete or conversion.

## State And Persistence
Persistent state is handled through manager/group code: RBD groups, group snapshots, per-volume snapshot images, journal reservations, and volume maps. In-memory `VolumeGroupLocks` prevent concurrent operations on the same group snapshot name/ID. Temporary groups are normally deleted after the operation to avoid images being stuck in a single group.

## Dependencies And Integration Points
Depends on CSI group-controller protobufs, manager abstractions, RBD group errors, common CSI capability validation, util locks, credentials, and logging. Feature availability is gated earlier by driver/identity librbd symbol detection.

## Risks And Test Signals
Risks include cleanup failures leaving images in temporary groups, incomplete idempotency checks for existing group snapshots, all-or-nothing preparation across multiple volumes, and FIXME gaps around delete request validation. There are no direct unit tests for this file; it needs integration coverage with librbd group snapshot support.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/group_controllerserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/identityserver.go -->
# sources/control-plane/ceph-csi/internal/rbd/identityserver.go

## Purpose
Customizes the RBD CSI identity service by reporting plugin capabilities that depend on both static driver behavior and runtime librbd feature support.

## Important APIs, Types, And Functions
`IdentityServer` embeds the common default identity server. `GetPluginCapabilities` returns controller service, online volume expansion, and volume accessibility constraints by default, then conditionally adds group-controller service and snapshot-metadata service capabilities.

## Control Flow
The method builds a base capability slice, calls `features.SupportsGroupSnapGetInfo` and appends group-controller capability if supported, then calls `features.SupportsRBDSnapDiffByID` and appends snapshot metadata capability if supported. Detection errors are logged as warnings but do not fail the identity RPC.

## State And Persistence
No state is persisted. Feature detection uses cached in-memory state in the `features` package.

## Dependencies And Integration Points
Depends on CSI protobufs, `csicommon.DefaultIdentityServer`, feature detection, and logging. The advertised capabilities should match controller services registered by `driver.go`; mismatches can cause sidecars to call unsupported RPCs or miss available features.

## Risks And Test Signals
Risks include capability drift between identity and driver startup, runtime symbol detection differences, and silently degraded capability advertisement when detection errors are only logged. There are no direct tests for this file in the subset.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/identityserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/manager.go -->
# sources/control-plane/ceph-csi/internal/rbd/manager.go

## Purpose
Provides a high-level manager that connects CSI request parameters/secrets to RBD volumes, snapshots, volume groups, and volume group snapshots. It is the bridge between controller RPCs and lower-level RBD group/journal abstractions.

## Important APIs, Types, And Functions
`rbdManager` stores driver instance, parameters, secrets, cached credentials, and cached volume-group journal. It implements `types.Manager` through `NewManager`, `Destroy`, `GetVolumeByID`, `GetSnapshotByID`, `GetVolumeGroupByID`, `MakeVolumeGroupID`, `CreateVolumeGroup`, `GetVolumeGroupSnapshotByID`, `GetVolumeGroupSnapshotByName`, `CreateVolumeGroupSnapshot`, `RegenerateVolumeGroupJournal`, `CompareVolumesInGroup`, and `VolumesInSameGroup`. Helpers include `getCredentials`, `getVolumeGroupNamePrefix`, `getVolumeGroupJournal`, and `getGroupUUID`.

## Control Flow
Volume and snapshot lookup lazily create credentials and call existing RBD ID resolvers, wrapping common missing image/pool errors. Group creation validates cluster/pool parameters, connects the volume-group journal, checks or reserves a name/UUID, gets monitor and pool IDs, generates a CSI handle, resolves a group object, and creates the backend group. Group snapshot lookup by name reserves or reuses a group UUID, builds a CSI ID, resolves a group snapshot, and verifies it has snapshots. Snapshot creation reserves a UUID, generates a group ID, returns an existing complete snapshot if present, otherwise calls `vg.CreateSnapshots`, registers the new group snapshot in the journal, and cleans up child snapshots on failure. Regeneration rebuilds journal mappings after failover/migration using mapped cluster information and volume IDs.

## State And Persistence
Persistent state is the RADOS volume-group journal: reservations, generated UUIDs, group names, and volume maps. It also creates librbd groups/snapshots via lower layers. Runtime state includes cached credentials and journal handles cleaned by `Destroy`.

## Dependencies And Integration Points
Depends on journal APIs, util CSI ID/cluster/pool mapping helpers, RBD volume/snapshot resolvers, `internal/rbd/group`, and `types` interfaces. It is used by `group_controllerserver.go` and CSI-Addons RBD volume-group/replication services.

## Risks And Test Signals
Risks include inconsistent use of pool vs journalPool during undo paths, incomplete existing snapshot validation by length only, cached `mgr.creds` assumptions before some methods use it, partial journal regeneration on errors, and cleanup closure behavior when reservations are reused. `manager_test.go` covers only `MakeVolumeGroupID` formatting/error paths.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/manager_test.go -->
# sources/control-plane/ceph-csi/internal/rbd/manager_test.go

## Purpose
Tests CSI volume-group ID generation from manager parameters, pool ID, backend group name, and optional volume group name prefix.

## Important APIs, Types, And Functions
`TestMakeVolumeGroupID` constructs managers with nil, missing-cluster, default-prefix, and custom-prefix parameter maps and calls `MakeVolumeGroupID`.

## Control Flow
Each parallel subtest creates a manager, defers `Destroy`, calls `MakeVolumeGroupID`, verifies expected error presence, and compares the generated ID string for valid cases.

## State And Persistence
No Ceph or journal state is used. The test exercises deterministic string/CSI-ID generation only.

## Dependencies And Integration Points
Depends on `NewManager`, util cluster ID extraction, and `journal.MakeVolumeGroupID`. It protects the contract used by `rbdVolume.GetVolumeGroupID` and group creation flows.

## Risks And Test Signals
Good signal for handle-format regressions, especially prefix stripping. It does not cover credential creation, journal reservation, pool ID lookup, group creation, snapshot creation, or regeneration.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/migration.go -->
# sources/control-plane/ceph-csi/internal/rbd/migration.go

## Purpose
Supports deletion and resolution of Kubernetes in-tree-to-CSI migrated RBD volume IDs, which encode monitor hash, image UUID, and pool name differently from native CSI IDs.

## Important APIs, Types, And Functions
`isMigrationVolID` checks for required migration markers. `parseMigrationVolID` decodes the handle into a `migrationVolID` containing image name, pool name, and cluster ID. `deleteMigratedVolume` resolves and deletes the migrated image. `genVolFromMigVolID` builds and connects an `rbdVolume` from parsed migration fields.

## Control Flow
Parsing splits the handle on the migration field separator, decodes the hex-encoded pool portion, extracts image suffix and monitor/cluster hash fields by prefix, then validates required fields. Deletion creates an RBD volume from the parsed handle, connects using monitors from CSI config, deletes the image, and logs delete failures.

## State And Persistence
The parser itself is stateless. `deleteMigratedVolume` mutates backend Ceph state by deleting the referenced RBD image but does not use native CSI OMAP reservations for migrated IDs.

## Dependencies And Integration Points
Used by `DeleteVolume` in `controllerserver.go` before normal CSI ID resolution. Depends on migration constants/types from other RBD files, util monitor lookup, credentials, and RBD errors.

## Risks And Test Signals
Risks include permissive substring checks in `isMigrationVolID`, malformed split fields, hex decode mapping to misleading missing-pool errors, and delete behavior that bypasses native CSI journal cleanup. `migration_test.go` covers valid/invalid identification and parsing cases.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/migration.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/migration_test.go -->
# sources/control-plane/ceph-csi/internal/rbd/migration_test.go

## Purpose
Unit-tests recognition and parsing of migrated in-tree RBD volume IDs.

## Important APIs, Types, And Functions
`TestIsMigrationVolID` checks valid and invalid marker/prefix combinations. `TestParseMigrationVolID` checks valid handles, missing monitor/image/pool fields, disallowed migration version strings, unallowed image names, missing monitor prefix, and pool names containing underscores.

## Control Flow
Both tests are table-driven and parallel. Parsing tests compare returned `migrationVolID` structs with `reflect.DeepEqual` and verify expected error presence.

## State And Persistence
No persistent state is used. Tests only parse static strings and do not resolve monitors or connect to Ceph.

## Dependencies And Integration Points
The tests protect the migration path used by controller delete for migrated volume handles. They depend on migration constants and `migrationVolID` field semantics.

## Risks And Test Signals
The tests provide good coverage for string-shape regressions but do not cover `genVolFromMigVolID` monitor lookup or actual deletion. They also do not assert exact sentinel errors for each malformed input.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/migration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/mirror.go -->
# sources/control-plane/ceph-csi/internal/rbd/mirror.go

## Purpose
Wraps librbd image mirroring operations and status parsing behind RBD `types.Mirror`, `types.GlobalStatus`, `types.SiteStatus`, and `types.SyncInfo` interfaces used by replication and controller cleanup flows.

## Important APIs, Types, And Functions
`HandleParentImageExistence` validates or flattens parent images before enabling mirroring. `rbdMirror` wraps `rbdImage`; `ToMirror` constructs it. Mirror operations include `EnableMirroring`, `DisableMirroring`, `GetMirroringInfo`, `Promote`, `Demote`, `Resync`, and `GetGlobalMirroringStatus`. Status wrappers include `ImageStatus`, `GlobalMirrorStatus`, `SiteMirrorImageStatus`, and `syncInfo`; `newSyncInfo` parses librbd status descriptions.

## Control Flow
Each mirror operation opens the image, defers close, invokes the corresponding librbd method, and wraps errors with image context. `HandleParentImageExistence` optionally force-flattens, rejects parents in trash, and requires existing parents to have mirroring enabled. `Resync` issues `MirrorResync`, then sleeps with exponential backoff while checking global status until the local site reports syncing or returns `ErrUnavailable` for retry. `newSyncInfo` splits a status description at the first comma, unmarshals JSON details, and requires a nonzero local snapshot timestamp.

## State And Persistence
Mirroring operations mutate persistent RBD mirror state: enabled/disabled flags, primary/secondary role, resync state, and image flattening. Status wrappers are read-only views over librbd structs. No journal state is written here.

## Dependencies And Integration Points
Depends on go-ceph/librbd, RBD image helpers, replication `types` interfaces, RBD error sentinels, and logging. `controllerserver.go` uses mirror status during delete to avoid deleting healthy secondary images, while CSI-Addons replication servers use these methods for failover/failback workflows.

## Risks And Test Signals
Risks include force-flatten side effects, parent mirroring precondition accuracy, open/close resource handling, parsing unstructured status descriptions, and resync timing/backoff behavior. `mirror_test.go` covers `newSyncInfo` parsing but not live librbd mirror operations.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/mirror.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/mirror_test.go -->
# sources/control-plane/ceph-csi/internal/rbd/mirror_test.go

## Purpose
Tests parsing of librbd mirror status description strings into `SyncInfo`.

## Important APIs, Types, And Functions
`TestValidateLastSyncInfo` exercises `newSyncInfo` through valid JSON, empty descriptions, missing optional fields, missing required local snapshot timestamp, zero duration, invalid JSON, and no-JSON descriptions.

## Control Flow
The table-driven parallel test calls `newSyncInfo`, checks whether returned errors contain expected substrings, and when a struct is returned compares last sync time, duration, and byte count through the `types.SyncInfo` interface.

## State And Persistence
No persistent state is used. Inputs are static status-description strings that model librbd output.

## Dependencies And Integration Points
Depends on RBD error sentinel `ErrLastSyncTimeNotFound` and `types.SyncInfo`. It protects the parser used by mirror status and resync flows.

## Risks And Test Signals
The test gives strong coverage for current description formats, including optional byte/duration fields. It cannot detect changes in live librbd status formatting beyond the included samples, and it does not cover mirror promote/demote/resync operations.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/mirror_test.go -->
