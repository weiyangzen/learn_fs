# subset-b-000346 Research

Grouped research for the NVMe-oF CSI controller/node implementation and adjacent RBD QoS/clone helpers. Each section is source-tree aligned and intended to be split into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/controller/controllerserver.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/controller/controllerserver.go

Purpose: Implements the NVMe-oF CSI Controller service by delegating durable RBD image work to the existing RBD controller server and adding gateway-side NVMe-oF resource orchestration. It creates/deletes namespaces, subsystems, listeners, hosts, QoS, metadata, and publish context needed by the node server.

Important APIs/types/functions: `Server` embeds `csi.UnimplementedControllerServer` and owns `volumeLocks`, `hostLocks`, `subsystemLocks`, a lazy `SecurityKeyManager`, and an RBD backend controller. CSI methods include `CreateVolume`, `DeleteVolume`, `ControllerPublishVolume`, `ControllerUnpublishVolume`, `ControllerModifyVolume`, `ControllerExpandVolume`, `CreateSnapshot`, and `DeleteSnapshot`. Helper functions validate requests, parse mutable QoS/host parameters, connect to gateways, store/retrieve RBD metadata, and populate volume/publish contexts.

Control flow: `CreateVolume` validates NVMe-oF-specific parameters, locks by volume name, creates the RBD volume, creates gateway resources, stores metadata on the image, and rolls back RBD/NVMe-oF resources on downstream failure. `DeleteVolume` retrieves metadata, removes gateway namespace/subsystem resources, then deletes the RBD volume. Publish derives a host NQN from node ID, optionally sets up DH-CHAP keys, adds the host to the subsystem, and merges RBD service-account publish context. Unpublish retrieves stored metadata and removes the host only when the subsystem has no other namespace. Modify rejects RBD QoS, parses NVMe-oF QoS and host allow-list parameters, then performs gateway mutations through a common connection helper.

State and persistence: NVMe-oF state is persisted in RBD metadata under `.rbd.nvmeof.*` keys: subsystem NQN, namespace ID/UUID, serialized listeners, gateway management endpoint, DH-CHAP mode, and authentication KMS ID. Runtime state is lock maps and transient gateway connections. RBD image metadata is the durable recovery path for unpublish/delete and modify operations that do not receive volume context.

Dependencies and integration points: Depends on CSI protobufs, RBD controller/manager, Ceph NVMe-oF gateway client from `internal/nvmeof`, Kubernetes secrets for fallback controller publish secrets, RBD QoS parameter detection, `ghodss/yaml` for `allowHostNQNs`, and gRPC status mapping. It integrates tightly with node server volume context keys and with `nvmeof/errors` for metadata/QoS error conversion.

Risks: Rollback depends on named return variable `err`; future refactors must preserve that behavior. Host removal uses namespace count minus one, assuming the current volume namespace is still present and list results are consistent. `setupDHCHAPKeys` and host update paths can diverge: external host updates currently add hosts with empty DH-CHAP keys. Metadata writes skip empty values, so missing optional security fields are tolerated but missing required metadata later blocks cleanup. Gateway operations are only as idempotent as their wrapped status handling.

Test signals: Unit tests cover host NQN construction, metadata key prefixing, volume context population, gateway config parsing, QoS parsing, and host-list parsing. There is no direct unit coverage for full CSI create/delete/publish rollback sequences, gateway failure windows, or metadata corruption handling.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/controller/controllerserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/controller/controllerserver_test.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/controller/controllerserver_test.go

Purpose: Provides unit coverage for small controller helpers that shape the NVMe-oF CSI contract: host NQN derivation, RBD metadata key naming, volume context serialization, and gateway config extraction.

Important APIs/types/functions: Tests target `getHostNQNFromNodeID`, `toRBDMetadataKey`, `populateVolumeContext`, and `getGatewayConfigFromRequest`. It constructs `csi.Volume` and `nvmeof.NVMeoFVolumeData` values and validates serialized listeners with `encoding/json`.

Control flow: Table-driven subtests validate success and failure cases. `TestPolulateVolumeContext` builds a complete volume data object, calls the helper, and asserts all relevant volume context keys plus JSON listener fields. Gateway config tests cover missing address, default port behavior, and explicit port parsing.

State and persistence behavior: Tests do not touch persistent RBD metadata or live gateways. They validate in-memory volume context values that later become CSI response state and input to the node server.

Dependencies and integration points: Uses CSI protobuf types, `nvmeof.ListenerDetails`, and `testify/require`. These tests guard key compatibility between controller output and node-server input.

Risks: Coverage is helper-focused and does not assert cleanup behavior, metadata store/retrieve symmetry, or error-code mappings. There is a duplicate host NQN test case and the test name has a typo (`Polulate`), both low functional risk but signs of narrow coverage.

Test signals: Positive signal for serialization and input validation. Missing signal for gateway RPC orchestration and RBD manager interactions.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/controller/controllerserver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/controller/mutable_params_test.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/controller/mutable_params_test.go

Purpose: Tests parsing for CSI `mutable_parameters` consumed by NVMe-oF volumes: gateway QoS limits and external host allow lists.

Important APIs/types/functions: Exercises `parseQoSParameters`, `parseHostsParameters`, `AllowHostNQNs`, and `nvmeof.NVMeoFQosVolume`. Test helpers compare pointer-valued uint64 fields and YAML-decoded string slices.

Control flow: Table-driven QoS tests cover absent parameters, complete and partial limits, zero as an accepted unlimited value, empty strings ignored, invalid strings, negatives, overflow, floats, and mixed valid/invalid maps. Host tests distinguish absent key (`nil`, no modification), present empty key (empty slice, remove all hosts), YAML list formats, wildcard, and invalid YAML/map/string inputs.

State and persistence behavior: No persistent state. The tests encode semantic state transitions used by `ControllerModifyVolume`: nil hosts means leave current gateway hosts unchanged, empty slice means reconcile to no hosts.

Dependencies and integration points: Depends on `ghodss/yaml` behavior through the production parser and `testify` assertions. Guards the VolumeAttributesClass interface consumed by controller create/modify flows.

Risks: Tests do not validate higher-level rejection of RBD QoS on NVMe-oF volumes, nor gateway effects of parsed values. Host NQN strings are not semantically validated beyond YAML string decoding.

Test signals: Strong coverage for parser edge cases and sentinel semantics. Integration with gateway reconciliation remains untested here.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/controller/mutable_params_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/controller/security.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/controller/security.go

Purpose: Supplies controller-side DH-CHAP key setup and cleanup for NVMe-oF host publication. It bridges CSI secrets, KMS-backed key management, optional RBD metadata DEK storage, and gateway `AddHost` key parameters.

Important APIs/types/functions: `getOrInitSecurityKeys` lazily initializes/caches `nvmeof.SecurityKeyManager`. `setupDHCHAPKeys` returns `nvmeof.DHCHAPKeys` for unidirectional or bidirectional authentication. `cleanupDHCHAPKeys` removes stored host/subsystem keys after unpublish.

Control flow: Disabled modes return empty keys. Enabled modes read `authenticationKMSID` from volume context, initialize a KMS manager, and if `ErrDEKStoreNeeded` is returned, open the RBD volume and attach an `RBDVolumeDEKStore`. Host keys are always retrieved or created; subsystem keys are included only for bidirectional mode. Cleanup follows the same KMS/DEK setup path and attempts both removals, logging but not returning individual removal failures.

State and persistence behavior: Integrated-storage KMS managers may be cached on the controller. Metadata KMS managers are not cached because each call needs a fresh volume-specific DEKStore. Keys are persisted through the configured KMS/DEKStore; for metadata KMS that means RBD image metadata.

Dependencies and integration points: Depends on `internal/nvmeof` crypto/DH-CHAP helpers, RBD manager lookup by volume ID, CSI publish request secrets and volume context, and controller `backendServer.Driver.GetInstanceID()`.

Risks: The cache key is not scoped by KMS ID or secret set; once a cacheable manager exists, later volumes with different KMS IDs would reuse it. Metadata DEKStore removal currently delegates to a no-op store implementation, so cleanup may not actually delete metadata-backed keys. Comments mark metadata KMS as test-oriented, but code defaults to it when DH-CHAP lacks an explicit KMS.

Test signals: No direct tests in this file. DH-CHAP helper tests are absent, so KMS error handling, cache semantics, and RBD metadata fallback rely on integration coverage.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/controller/security.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/crypto.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/crypto.go

Purpose: Defines the KMS-backed abstraction for storing and retrieving NVMe-oF security keys, especially DH-CHAP secrets.

Important APIs/types/functions: Exports sentinel errors `ErrDEKStoreNotSet`, `ErrDEKStoreNeeded`, `ErrKeyNotFound`, owner constant `NVMeOFSecurityOwner`, interface `SecurityKeyManager`, `InitSecurityKeyManager`, and concrete `securityKeyManager` methods `StoreKey`, `GetKey`, `RemoveKey`, `SetDEKStore`, `GetID`, and `Destroy`.

Control flow: Initialization chooses `"metadata"` KMS when no ID is supplied, obtains a KMS through `kms.GetKMS`, then calls `newSecurityKeyManager`. Integrated KMS backends are expected to implement `kms.DEKStore` directly. Non-integrated backends return a usable manager plus `ErrDEKStoreNeeded`, requiring the caller to attach a DEKStore before key operations. Store encrypts plaintext via KMS then writes encrypted data to the DEKStore. Get fetches encrypted data then decrypts it. Remove delegates to the DEKStore.

State and persistence behavior: The manager holds a KMS instance and optional DEKStore. Persistence location depends on backend: integrated KMS, external storage, or caller-provided RBD metadata store. No in-memory key cache is kept.

Dependencies and integration points: Depends on Ceph-CSI `internal/kms` interfaces. Used by controller and node security helpers plus DH-CHAP key creation functions.

Risks: Error normalization assumes DEKStore implementations return `ErrKeyNotFound`; generic KMS stores may not. `Destroy` assumes `skm.kms` is non-nil. Callers must correctly handle the non-nil manager plus `ErrDEKStoreNeeded` pattern or all key operations fail with `ErrDEKStoreNotSet`.

Test signals: No direct tests. Behavior is indirectly exercised only through higher-level security paths if integration tests cover KMS.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/crypto.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/dhchap.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/dhchap.go

Purpose: Implements DH-CHAP key identity, generation, storage, lookup, and removal helpers for NVMe-oF authentication.

Important APIs/types/functions: Exports mode constants (`DHCHAPEmpty`, `DHCHAPModeNone`, `DHCHAPModeUniDirectional`, `DHCHAPModeBiDirectional`), hash constants, `DHCHAPKeys`, `GetOrCreateDHCHAPHostKey`, `GetOrCreateDHCHAPSubsystemKey`, `RemoveDHCHAPHostKey`, `RemoveDHCHAPSubsystemKey`, and internal helpers for key IDs and key generation.

Control flow: Get-or-create first attempts lookup through `SecurityKeyManager`. Only `ErrKeyNotFound` triggers generation; other errors abort to avoid replacing existing keys during KMS/storage failures. Generation builds a deterministic key ID from key prefix, node ID, and a 16-character SHA-256 hash of subsystem NQN, then invokes `nvme gen-dhchap-key` and stores the resulting key string.

State and persistence behavior: Key values are persisted encrypted through `SecurityKeyManager`. Key IDs are deterministic per node/subsystem and split host versus subsystem direction. Raw random bytes are generated in-process but the actual key output comes from `nvme gen-dhchap-key`; the generated `keyBytes` are not passed to that command.

Dependencies and integration points: Depends on `crypto/rand`, SHA-256 hashing, `util.ExecCommandWithTimeout`, `nvme` CLI availability, shared `connectTimeout`, and Ceph-CSI logging. Controller uses returned keys for gateway host configuration; node uses the same key IDs to set `nvme connect` DH-CHAP arguments.

Risks: The allocated random bytes are unused, so entropy comes from `nvme gen-dhchap-key`, not the local buffer. Key ID includes raw node ID; unusual characters may propagate into backend key names. The code assumes missing keys map to `ErrKeyNotFound`. External KMS backends with different not-found errors could prevent key generation.

Test signals: No direct unit tests for key ID format, hashing, generation validation, or command invocation. Security correctness depends on integration and manual validation.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/dhchap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/driver/driver.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/driver/driver.go

Purpose: Entry point for running the NVMe-oF CSI driver. It initializes shared RBD globals/journals, CSI identity, controller, and node servers, then starts the nonblocking gRPC server.

Important APIs/types/functions: `nvmeofDriver`, `NewDriver`, and `Run`. `Run` configures RBD clone/flatten limits, creates a `csicommon.CSIDriver`, advertises controller and volume access capabilities, chooses node/controller servers based on config flags, starts gRPC, and optionally starts metrics/profiling.

Control flow: If running as controller or combined, controller capabilities include create/delete volume, publish/unpublish, modify, expand, and snapshot create/delete. Access modes include single-node writer, multi-node multi-writer, single-node single-writer, and single-node multi-writer. Server selection is mutually exclusive for node-only and controller-only modes; default starts both.

State and persistence behavior: Persistent data lives in RBD journals and server-specific metadata; this file only sets process-wide RBD globals and creates service instances.

Dependencies and integration points: Integrates with `internal/driver`, `csi-common`, NVMe-oF controller/identity/node packages, RBD driver globals, util config, metrics, profiling, and slow-GRPC middleware configuration.

Risks: RBD global setup is process-wide and shared with any RBD code paths. Capability advertisement must stay aligned with actual method behavior. Node server construction can fail due to kernel module, kernel version, or mount-cache initialization checks, causing process fatal startup.

Test signals: No direct tests for driver startup or capability registration in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/driver/driver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/errors/errors.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/errors/errors.go

Purpose: Centralizes NVMe-oF-specific sentinel errors and maps them to gRPC status codes.

Important APIs/types/functions: Exports `ErrRbdQoSExists`, `ErrMetadataNotFound`, `ErrMetadataCorrupted`, `errorToGRPCCode`, and `ToGRPCError`.

Control flow: `ToGRPCError` returns nil for nil input, checks `errors.Is` against known sentinels, and returns mapped `status.Error`. Unknown errors become `codes.Internal`.

State and persistence behavior: No persistent state. The package is a pure error classification layer.

Dependencies and integration points: Used by controller metadata retrieval, QoS modification, and unpublish/delete error handling. Depends on gRPC `codes/status` and Go `errors`.

Risks: The map uses error values as keys and iteration order is undefined, though the current sentinels are distinct. New sentinel errors need explicit mapping or they degrade to Internal.

Test signals: No direct tests, but controller paths use these conversions for NotFound, Internal, and InvalidArgument status behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/errors/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/identity/identityserver.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/identity/identityserver.go

Purpose: Implements the NVMe-oF CSI Identity service by wrapping the default identity server and overriding plugin capability reporting.

Important APIs/types/functions: `Server` embeds `*csicommon.DefaultIdentityServer`; `NewIdentityServer` constructs it; `GetPluginCapabilities` reports controller service and online volume expansion support.

Control flow: Capability response is static and independent of request content. Other identity methods are inherited from `DefaultIdentityServer`.

State and persistence behavior: No persistent state beyond the embedded driver metadata.

Dependencies and integration points: Used by the NVMe-oF driver startup. Depends on CSI protobufs and common identity server implementation.

Risks: Capability reporting must stay aligned with controller/node advertised capabilities. If online expansion behavior changes, this static response must be updated.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/identity/identityserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/nodeserver/nodeserver.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/nodeserver/nodeserver.go

Purpose: Implements the NVMe-oF CSI Node service: connects NVMe-oF subsystems, stages filesystem/block devices, publishes bind mounts, unstages and disconnects controllers when safe, and performs filesystem resize.

Important APIs/types/functions: `NodeServer` holds default node server, per-volume locks, `NVMeInitiator`, DH-CHAP kernel support status, security manager, node ID, `MountCache`, and `GroupLock`. CSI methods include `NodeGetCapabilities`, `NodeStageVolume`, `NodePublishVolume`, `NodeUnpublishVolume`, `NodeUnstageVolume`, and `NodeExpandVolume`. Helpers include `getNvmeConnection`, `connectToSubsystem`, `stageTransaction`, rollback, mount path creation, staging mount, mount-cache initialization, and path/device lookup.

Control flow: Construction loads `nvme_tcp`, verifies `/dev/nvme-fabrics`, records DH-CHAP kernel support, and initializes mounted-device cache from `findmnt`. Stage validates and locks, prevents stage/unstage interleaving with GroupLock group A, skips already mounted paths, parses controller-provided contexts, connects to listeners, creates staging path, mounts/formats the device, and caches the mounted device. Publish validates service-account restrictions, creates target file/dir, and bind mounts from staging path. Unstage locks GroupLock group B, resolves device from cache or `findmnt`, unmounts/removes staging path, updates cache, and calls `DisconnectIfLastMount`. Expand finds the device backing staging path and runs filesystem resize for filesystem volumes only.

State and persistence behavior: Persistent state is external: kernel NVMe connections, mount table, filesystem formatting, and CSI staging/target paths. In-memory state is lock maps and mount cache reconstructed at startup. CSI volume/publish context from controller is required for stage.

Dependencies and integration points: Depends on csi-common validation/mount option helpers, `internal/nvmeof` initiator and listener data, NVMe-oF utility mount discovery, Kubernetes service account restriction helpers, kernel-version utilities, mount-utils resize/format logic, and node security setup.

Risks: Mount cache is 1:1 by device and staging path; multipath or unusual device aliases could challenge disconnect decisions. GroupLock allows parallel staging operations and parallel unstaging operations, so shared initiator command behavior must be safe. `getNvmeConnection` requires HostNQN in publish context, coupling stage to successful ControllerPublish. DH-CHAP with older kernels fails staging as InvalidArgument. `os.Remove` expects staging path to be empty after unmount.

Test signals: This file lacks direct node-server unit tests in the subset. Related utility tests cover mount source parsing and mount cache behavior; integration coverage is needed for real mount and NVMe operations.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/nodeserver/nodeserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/nodeserver/security.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/nodeserver/security.go

Purpose: Provides node-side DH-CHAP authentication setup for `nvme connect` requests by retrieving or creating keys through the same KMS/DEKStore scheme as the controller.

Important APIs/types/functions: `getOrInitSecurityKeys` lazily initializes a `SecurityKeyManager`. `setupDHCHAPAuth` attaches `HostDhchapKey` and optional `SubsystemDhchapKey` to a `nvmeof.ConnectRequest`.

Control flow: The node initializes security keys using the requested KMS ID and CSI secrets. If the KMS needs an external DEKStore, it creates user credentials, resolves the RBD volume by volume ID, wraps it in `NewRBDVolumeDEKStore`, and attaches it. It then calls DH-CHAP get-or-create helpers using the node server's node ID, subsystem NQN, and connect host NQN. Bidirectional mode retrieves the subsystem key too.

State and persistence behavior: Cacheable KMS managers are stored on the `NodeServer`; metadata KMS requires a volume-specific DEKStore per call. Keys are persisted via the configured KMS/DEKStore, commonly RBD image metadata for metadata KMS.

Dependencies and integration points: Depends on `nvmeof` crypto/DH-CHAP, RBD volume resolution via `GenVolFromVolID`, user credential migration helper, CSI secrets, and the connection info built in `nodeserver.go`.

Risks: Same cache scoping concern as controller security: cached manager is not keyed by KMS ID or secret material. Because node can create keys if missing, node and controller key-generation races are possible if gateway AddHost and node connect overlap with missing metadata. Metadata KMS path requires valid RBD credentials on node.

Test signals: No direct tests. Behavior requires integration coverage with KMS, RBD metadata, and `nvme connect`.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/nodeserver/security.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/nvmeof.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/nvmeof.go

Purpose: Implements the management-plane gRPC client wrapper for the Ceph NVMe-oF gateway. It exposes higher-level operations for subsystems, namespaces, listeners, hosts, QoS, and gateway metadata conversion.

Important APIs/types/functions: `GatewayAddress`, `ListenerDetails`, `GatewayConfig`, `GatewayRpcClient`, `NewGatewayRpcClient`, `Destroy`, namespace operations, subsystem operations, host/listener operations, `UpdateHostsForSubsystem`, `ListNamespaces`, `ListListeners`, `ConvertListenersFromProto`, `generateSerialNumber`, and `findExistingNamespace`.

Control flow: Construction applies default management port 5500 and creates a gRPC client using insecure transport. Namespace creation calls `NamespaceAdd`, treats EEXIST by listing existing namespaces and matching pool/image, and returns namespace ID. Subsystem creation generates a random Ceph-prefixed serial, enables HA, optionally passes network masks, and treats EEXIST as success. Listener/host delete and add paths normalize several gateway status codes into idempotent success. QoS maps gateway EEXIST into `ErrRbdQoSExists`. Host update reconciles current versus desired hosts by remove-then-add.

State and persistence behavior: The client holds a gRPC connection and config only. Durable state is on the NVMe-oF gateway and backing RBD images. Serial numbers are generated randomly under gateway constraints.

Dependencies and integration points: Depends on `github.com/ceph/ceph-nvmeof/lib/go/nvmeof` protobufs, gRPC, gateway status codes expressed as errno values, `nvmeof/errors`, and controller orchestration.

Risks: Insecure gRPC transport is hard-coded. IPv4 address family is assumed for listeners. Gateway API status-code semantics are embedded in client behavior and must track gateway changes. Host reconciliation uses `slices.Contains`, so large host lists are O(n*m). `Destroy` clears config and client, making the object unusable after close.

Test signals: Unit tests cover address string formatting, deterministic serial edge case, NVMe list-subsys JSON parsing in the initiator package, and an environment-gated real gateway test covers a subset of subsystem/host/listener operations. Many gateway error/status branches are untested.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/nvmeof.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/nvmeof_initiator.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/nvmeof_initiator.go

Purpose: Implements node-side NVMe-oF initiator operations using kernel modules, the `nvme` CLI, sysfs/device paths, and mount-awareness for safe connect/disconnect.

Important APIs/types/functions: `NVMeInitiator`, `ConnectRequest`, `nvmeInitiator`, `NewNVMeInitiator`, `LoadKernelModules`, `ConnectSubsystem`, `DisconnectIfLastMount`, `GetNamespaceDeviceByUUID`, `ResolveListeners`, and helpers for `nvme list-subsys`, path matching, controller discovery, and namespace enumeration.

Control flow: Module loading modprobes `nvme_tcp` and validates `/dev/nvme-fabrics`. Connect lists existing subsystems when HostNQN is provided, skips gateways already in `live` or `connecting` state for the same host/subsystem/gateway, then attempts `nvme connect` against each listener with transport, NQN, address, port, controller-loss timeout, host NQN, and optional DH-CHAP secrets. Success requires at least one listener. Device lookup retries `/dev/disk/by-id/nvme-uuid.<uuid>` with dashed and original UUID variants. Disconnect discovers all controllers for a device, verifies no controller has other mounted namespaces from the passed cache, and disconnects every controller only if safe.

State and persistence behavior: Persistent/external state is kernel NVMe controller connections, `/dev` symlinks, and mount table state supplied by caller. The initiator itself is stateless.

Dependencies and integration points: Depends on `nvme` CLI, `findmnt`-derived mount cache from node server, `kmod.Modprobe`, `retry-go`, JSON output formats from `nvme list-subsys` and `nvme list-ns`, and listener resolution helper in `util.go`.

Risks: JSON parsing depends on CLI output stability. Disconnect safety uses cached mounted device paths, so stale or incomplete cache can leave connections lingering or, worse, disconnect when another namespace is actually mounted under an unrecognized path. `ResolveListeners` mutates the input listener slice when replacing `0.0.0.0`. The `connecting` state is treated as good to avoid duplicate connects, which can preserve a broken path until kernel timeout.

Test signals: Unit tests cover list-subsys JSON parsing and `hasPathToGateway` behavior, including `connecting` paths. No tests invoke real `nvme` commands except through broader integration environments.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/nvmeof_initiator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/nvmeof_test.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/nvmeof_test.go

Purpose: Unit tests for NVMe-oF address/string helpers, gateway serial generation, `nvme list-subsys` JSON parsing, and path matching used to avoid duplicate connections.

Important APIs/types/functions: Tests `GatewayAddress.String`, `GatewayRpcClient.generateSerialNumber`, custom JSON unmarshalling for `nvmePathAddress`, `nvmeHostConnections`, and `hasPathToGateway`.

Control flow: Table tests parse sample JSON for single hosts, multipath, connecting state, multiple hosts, invalid JSON, and empty arrays. Path matching tests validate host/subsystem/gateway/port matching and treat both `live` and `connecting` as usable states.

State and persistence behavior: No external state. Samples model `nvme list-subsys -o json` output used by the initiator.

Dependencies and integration points: Uses `encoding/json`, `math/big`, and `testify/require`. It guards the assumptions in `ConnectSubsystem` about existing connection detection.

Risks: Tests do not execute the `listSubsystems` command wrapper or validate disconnect helpers. The "path exists but not live" test name now expects `connecting` to be true, so future maintainers must read the assertion rather than rely on the name.

Test signals: Good coverage for JSON shape and duplicate-connect predicate. Missing coverage for CLI failures, malformed address fragments, and controller/namespace disconnect logic.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/nvmeof_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/qos.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/qos.go

Purpose: Defines NVMe-oF gateway QoS parameter names and the value object used by controller and gateway client code.

Important APIs/types/functions: `NVMeoFQosVolume` contains optional pointer fields for read/write IOPS and throughput limits. Constants define CSI mutable parameter keys: `rwIosPerSecond`, `rwMbytesPerSecond`, `rMbytesPerSecond`, and `wMbytesPerSecond`. `String` renders only configured limits or `no QoS limits`.

Control flow: This file has no parsing; controller `parseQoSParameters` builds the struct and gateway `SetQoSLimitsForNamespace` sends pointer fields to protobuf request.

State and persistence behavior: Pure in-memory DTO. Gateway or RBD metadata persistence is handled elsewhere.

Dependencies and integration points: Used by controller mutable-parameter parsing, create/modify volume flows, and gateway namespace QoS calls.

Risks: Pointer fields distinguish unset from explicit zero; callers must preserve that distinction. String labels differ slightly from parameter names but are log-only.

Test signals: Parser tests in `mutable_params_test.go` validate pointer construction and zero handling; no direct test for `String`.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/qos.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/rbd_dekstore.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/rbd_dekstore.go

Purpose: Implements `kms.DEKStore` over RBD image metadata for NVMe-oF DH-CHAP keys, mainly used by metadata KMS flows.

Important APIs/types/functions: `rbdVolumeDEKStore`, `NewRBDVolumeDEKStore`, `StoreDEK`, `FetchDEK`, and `RemoveDEK`.

Control flow: Store prefixes the key ID with `nvmeof.csi.ceph.com/` and writes encrypted data through `SetMetadata`. Fetch reads the same key and maps librbd not-found to `ErrKeyNotFound`. Remove is currently a no-op.

State and persistence behavior: Encrypted keys are persisted as RBD image metadata. Because `RemoveDEK` does nothing, metadata-backed keys remain until volume deletion or future explicit metadata removal support.

Dependencies and integration points: Depends on RBD volume interface from `internal/rbd/types`, `go-ceph/rbd` not-found errors, and `internal/kms` DEKStore contract. Used by controller and node security helpers when `InitSecurityKeyManager` returns `ErrDEKStoreNeeded`.

Risks: Key cleanup is incomplete by design. Stored metadata keys do not use the `.rbd.` non-copy prefix used for NVMe-oF volume metadata, so clone/snapshot propagation behavior should be reviewed if DH-CHAP metadata must not be copied. Error matching uses `librbd.ErrNotFound`, while other RBD paths use both NotFound and NotExist variants.

Test signals: No direct tests for store/fetch/remove behavior or metadata key naming.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/rbd_dekstore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/tests/nvmeof_test.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/tests/nvmeof_test.go

Purpose: Environment-gated integration test for the real NVMe-oF gateway client.

Important APIs/types/functions: `TestRealGateway` uses `nvmeof.NewGatewayRpcClient`, `CreateSubsystem`, `AddHost`, `SubsystemExists`, `CreateListener`, `DeleteListener`, `RemoveHost`, `DeleteSubsystem`, and `Destroy`.

Control flow: The test skips in short mode and skips when required environment variables are missing. It creates a gateway client from env-provided management endpoint, sets up cleanup in reverse order, then exercises subsystem create, host add, subsystem exists, listener create/delete, host remove, subsystem delete, and final absence check. Namespace create/delete are present but commented out.

State and persistence behavior: Mutates a real gateway using fixed test NQN and host NQN. Cleanup attempts to remove host, listener, subsystem, and close the client even if assertions fail.

Dependencies and integration points: Requires live NVMe-oF gateway address/port/hostname/listener port. Uses `testify/require` and production gateway client.

Risks: Fixed test identifiers can collide across concurrent integration runs. The test skips rather than fails without environment, so CI may not cover gateway integration. Namespace behavior, QoS, auto-listeners, DH-CHAP, and RBD-backed namespace creation are not exercised.

Test signals: Useful smoke test for gateway CRUD basics when explicitly configured. Limited default CI signal.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/tests/nvmeof_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/util.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/util.go

Purpose: Provides small NVMe-oF utility helpers for UUID normalization and hostname-to-IP resolution.

Important APIs/types/functions: `formatUUID` removes dashes and parses a UUID into standard dashed format, returning the original input if parsing fails. `ResolveIPAddress` calls `net.LookupHost` and returns the first address.

Control flow: `formatUUID` is used by namespace device lookup to try `/dev/disk/by-id/nvme-uuid.*` symlink variants. `ResolveIPAddress` is used when listener address is `0.0.0.0` and nodes must resolve the gateway hostname.

State and persistence behavior: No persistent state. DNS resolution depends on node runtime resolver state.

Dependencies and integration points: Depends on `google/uuid` and Go `net`. Integrated with `nvmeof_initiator.ResolveListeners`.

Risks: `ResolveIPAddress` returns the first record only and has a TODO for IPv6 behavior. Invalid UUIDs are silently passed through, which is intentional but can delay failure to device lookup.

Test signals: `util_test.go` covers UUID formatting for dashed, malformed, and empty strings. DNS resolution is not unit tested.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/util/mounter.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/util/mounter.go

Purpose: Discovers NVMe device paths from mount points and builds an initial set of mounted NVMe-oF CSI staging devices.

Important APIs/types/functions: `FindmntResult`, `FindmntFilesystem`, `FindmntSource`, `FindmntSource.UnmarshalText`, `parseNVMEDeviceFromRawSource`, `GetDeviceFromMountpoint`, and `GetAllNVMeMountedDevices`.

Control flow: `findmnt -J` output is decoded into structs. Source parsing handles direct `/dev/nvme...` filesystem mounts and block-volume `devtmpfs[/nvmeXnY]` syntax. `GetDeviceFromMountpoint` queries one mountpoint and returns the parsed device or empty. `GetAllNVMeMountedDevices` lists all mounts and filters to Ceph NVMe-oF CSI staging paths for filesystem and block volumes.

State and persistence behavior: Reads live mount table through `findmnt`; no persistent writes. Results seed/update the node server mount cache.

Dependencies and integration points: Depends on `util.ExecCommandWithTimeout`, `findmnt`, JSON output stability, and Ceph-CSI logging. Directly supports node unstage disconnect safety.

Risks: Path filtering is string-based and Kubernetes path layout dependent. Device parser only recognizes `nvme\d+n\d+` and direct `/dev/nvme` prefixes, not partition suffixes or alternate symlink paths. Errors from `findmnt` are surfaced, which can block node server startup when cache initialization fails.

Test signals: `mounter_test.go` covers raw source parsing. No tests mock full `findmnt -J` output for `GetAllNVMeMountedDevices`.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/util/mounter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/util/mounter_cache.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/util/mounter_cache.go

Purpose: Thread-safe in-memory bidirectional cache mapping NVMe devices to CSI staging paths.

Important APIs/types/functions: `MountCache` interface, concrete `mountCache`, `NewMountCache`, `Add`, `GetDevice`, `RemoveByDevice`, `RemoveByMountPoint`, and `GetCopyAllDevices`.

Control flow: `Add` refuses to overwrite an existing staging path or device mapping. Remove operations delete both map directions. `GetCopyAllDevices` returns a cloned device-to-path map so callers can make disconnect decisions without holding the cache lock.

State and persistence behavior: Runtime-only memory state. Node server rebuilds cache on startup from live mount information.

Dependencies and integration points: Used by node stage/unstage rollback and disconnect logic. Depends only on Go `sync` and `maps`.

Risks: The 1:1 constraint simplifies safety but may ignore legitimate cases where one device appears at multiple staging paths or aliases. `sync.Mutex` is used for read and write paths; performance is adequate for CSI operation volume but not optimized for high read concurrency.

Test signals: Dedicated tests cover add/get/remove, concurrency, non-existent removal, empty cache, and overwrite refusal.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/util/mounter_cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/util/mounter_cache_test.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/util/mounter_cache_test.go

Purpose: Unit tests for `MountCache` correctness and basic concurrency safety.

Important APIs/types/functions: Tests `NewMountCache`, `Add`, `GetDevice`, `RemoveByDevice`, `RemoveByMountPoint`, and duplicate-device overwrite prevention.

Control flow: Tests add mappings, retrieve them, remove by both directions, attempt removals from empty or missing entries, spawn concurrent add goroutines, and verify that adding a second staging path for the same device is ignored.

State and persistence behavior: All state is in-memory cache state. No external dependencies.

Dependencies and integration points: Uses `testify/require`. These tests support confidence in node server disconnect decisions that depend on cache consistency.

Risks: Concurrency test only covers concurrent adds with unique keys and does not run under explicit race detector here. It does not test concurrent add/remove/read interleavings.

Test signals: Strong signal for intended 1:1 semantics and basic locking behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/util/mounter_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/util/mounter_test.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/util/mounter_test.go

Purpose: Tests raw `findmnt` source parsing for NVMe device discovery.

Important APIs/types/functions: Exercises `parseNVMEDeviceFromRawSource`.

Control flow: Table cases cover direct `/dev/nvme0n2`, block-volume `devtmpfs[/nvme1n1]` and `devtmpfs[/nvme0n1]`, non-NVMe devtmpfs, and unrelated strings.

State and persistence behavior: Pure parser tests; no mount table reads.

Dependencies and integration points: Uses `testify/require`. Guards node utility behavior used by mount cache and unstage disconnect decisions.

Risks: Does not cover `devtmpfs[nvme0n1]` without slash despite parser support, full JSON unmarshalling, or partition paths.

Test signals: Focused coverage for the most important source string formats.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/util/mounter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/util_test.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/util_test.go

Purpose: Unit tests for UUID normalization used during NVMe namespace device lookup.

Important APIs/types/functions: Tests `formatUUID`.

Control flow: Cases cover a compact UUID, dash-heavy UUID input, leading/trailing dashes, invalid input, and empty string. Valid inputs are normalized to standard dashed UUID form; invalid inputs are returned unchanged.

State and persistence behavior: Pure function test.

Dependencies and integration points: Uses `testify/require`. Supports `GetNamespaceDeviceByUUID` behavior in the initiator.

Risks: Does not test actual `/dev/disk/by-id` lookup or retry behavior.

Test signals: Good signal for normalization compatibility with UUID symlink naming.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/volume.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/volume.go

Purpose: Defines the controller-to-node NVMe-oF volume data model and parses StorageClass/CreateVolume parameters into that model.

Important APIs/types/functions: `NVMeoFVolumeData`, `NVMeoFSecurityConfig`, `SetListenersWithDefaults`, `SetupListeners`, and `SetFromParameters`.

Control flow: `SetFromParameters` fills subsystem NQN, gateway management address/port, DH-CHAP mode, authentication KMS ID, and listener info. If subsystem NQN is absent it defaults to `nqn.2016-06.io.ceph:subsystem.<volumeID>`. Listener JSON may be absent, but if present must be non-empty and each listener needs hostname. Missing listener address defaults to `0.0.0.0`; missing port defaults to 4420. DH-CHAP without KMS ID defaults to `"metadata"`.

State and persistence behavior: Pure data construction. The controller later persists these values in RBD metadata and CSI volume context.

Dependencies and integration points: Used by controller `createNVMeoFResources`, node server context parsing, and gateway listener/subsystem creation. Depends on JSON parsing and DH-CHAP constants.

Risks: Default metadata KMS is marked by surrounding code as test-oriented, but this model applies it automatically for DH-CHAP. `SetupListeners("")` is valid only because `networkMask` can drive auto-listeners; request validation must enforce that separately. Listener address default `0.0.0.0` requires node-side hostname resolution before connect.

Test signals: `volume_test.go` covers listener defaults, setup validation, gateway parsing, DH-CHAP default KMS, invalid port/listeners, and default subsystem NQN.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/volume.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/volume_test.go -->
# sources/control-plane/ceph-csi/internal/nvmeof/volume_test.go

Purpose: Unit tests for NVMe-oF volume data parsing, listener validation, defaults, and DH-CHAP KMS defaulting.

Important APIs/types/functions: Tests `SetListenersWithDefaults`, `SetupListeners`, and `NVMeoFVolumeData.SetFromParameters`.

Control flow: Listener default tests cover combinations of missing address and port. Listener setup tests cover valid JSON, invalid JSON, missing hostname, empty array, and absent listeners. Parameter tests cover explicit subsystem/gateway/listeners, DH-CHAP with explicit KMS, DH-CHAP with default metadata KMS, invalid port, invalid listeners JSON, and default subsystem NQN from volume ID.

State and persistence behavior: Pure in-memory tests for values later persisted by controller.

Dependencies and integration points: Uses `testify/require`. Guards StorageClass parameter semantics used by controller create.

Risks: Tests do not cover `networkMask` validation, XOR listeners/networkMask validation, or node-side resolution of default `0.0.0.0` listeners.

Test signals: Good coverage for volume parameter model and defaults.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nvmeof/volume_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/cgroup_qos.go -->
# sources/control-plane/ceph-csi/internal/rbd/cgroup_qos.go

Purpose: Adds cgroup v2 QoS support for krbd-mounted RBD volumes by storing QoS parameters in RBD metadata and applying them to Kubernetes pod cgroups during publish.

Important APIs/types/functions: `QoSHandler`, cgroup metadata constants, `cgroupQoSHandler`, `cgroupQoS`, `parseCgroupQoSParams`, `hasCgroupQoSParams`, `getDeviceID`, `formatIOMax`, `writeIOMax`, `findPodCgroupPath`, `applyCgroupQoS`, `validateCgroupQoSParams`, `rbdVolume.saveCgroupQoS`, `getCgroupQoS`, and `applyCgroupQoSForVolume`.

Control flow: Handler ignores cgroup QoS for `rbd-nbd` mounter so NBD QoS remains responsible. Save validates positive integer limits, writes provided values to `.rbd.csi.ceph.com/*` metadata, and removes omitted cgroup metadata keys for partial updates. Apply retrieves metadata, resolves device major:minor from `/proc/partitions`, finds the pod's cgroup path by trying Guaranteed, Burstable, and BestEffort slice layouts, formats an `io.max` line, and writes it to the pod cgroup.

State and persistence behavior: QoS intent persists in RBD image metadata with a dot-prefixed key intended not to copy to clones/snapshots. Runtime enforcement persists in kernel cgroup v2 `io.max` files for the pod cgroup.

Dependencies and integration points: Depends on RBD metadata methods, Kubernetes pod UID availability (`podInfoOnMount`), cgroup v2 filesystem layout, `/proc/partitions`, device symlink resolution, librbd not-found errors, and RBD publish flow.

Risks: Hard-coded cgroup path layouts may vary by distro, CRI, or cgroup driver. `getDeviceID` scans `/proc/partitions` by basename, which can fail for unusual device names. Missing pod UID silently skips enforcement. Metadata removal handles `ErrNotExist` while retrieval handles `ErrNotFound`, reflecting subtle librbd error differences.

Test signals: Dedicated tests cover parameter parsing, presence detection, io.max formatting, validation, pod path construction/order, and write behavior. Tests do not mock `/proc/partitions` or real cgroup application.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/cgroup_qos.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/cgroup_qos_test.go -->
# sources/control-plane/ceph-csi/internal/rbd/cgroup_qos_test.go

Purpose: Unit tests for cgroup v2 QoS parsing, validation, path construction, ordering, and `io.max` writes.

Important APIs/types/functions: Tests `parseCgroupQoSParams`, `hasCgroupQoSParams`, `cgroupQoS.formatIOMax`, `validateCgroupQoSParams`, `findPodCgroupPath` error cases, cgroup path construction logic, `qosClassInfo` ordering, and `writeIOMax`.

Control flow: Table tests validate full/partial/default QoS values, presence detection, all `io.max` combinations, invalid string/zero/negative values, empty pod UID and missing pod path errors, Kubernetes UID hyphen-to-underscore conversion, expected slice prefixes, and file write content.

State and persistence behavior: Tests use temp files for `io.max` writing but do not write real cgroup paths. They do not use RBD metadata.

Dependencies and integration points: Uses standard testing, temp dirs, filepath, and string utilities. Supports `cgroup_qos.go` assumptions about cgroup path layout and parameter validation.

Risks: Since `findPodCgroupPath` uses the real `/sys/fs/cgroup`, only negative cases are portable. No test covers successful cgroup detection with an injectable base path, nor device ID lookup from `/proc/partitions`.

Test signals: Good parser and formatter coverage. Limited system integration coverage by design.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/cgroup_qos_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/clone.go -->
# sources/control-plane/ceph-csi/internal/rbd/clone.go

Purpose: Implements PVC-to-PVC RBD clone creation using temporary clones and snapshots to manage clone depth, flattening, metadata cleanup, encryption config, and QoS adjustment.

Important APIs/types/functions: Methods on `rbdVolume`: `checkCloneImage`, `generateTempClone`, `createCloneFromImage`, `doSnapClone`; helper `isTempClonedImage`.

Control flow: `checkCloneImage` reconstructs or resumes clone state by checking a temporary clone and snapshot. Missing temp snapshot triggers `createRBDClone`; missing temp clone causes parent snapshot cleanup if needed; existing temp snapshot allows final clone creation and flatten task scheduling. `createCloneFromImage` connects to the journal, performs `doSnapClone`, obtains image ID, copies encryption config, stores image ID in the journal, expands to requested size, and adjusts RBD QoS. `doSnapClone` creates a temp clone from parent, clears Kubernetes volume metadata on the temp clone, creates the final clone from a temp snapshot, and copies encryption config.

State and persistence behavior: Mutates RBD images, snapshots, clone relationships, image metadata, encryption metadata, volume journal image IDs, resize state, and QoS state. Temporary clone names append `-temp`; temporary snapshots use related image names.

Dependencies and integration points: Depends on go-ceph/librbd features, RBD journal, snapshot helpers, cleanup helpers, Kubernetes volume metadata key list, encryption config copying, and QoS adjustment paths including cgroup/NBD handling.

Risks: Clone recovery is complex and depends on recognizing partially-created temp images/snapshots. Cleanup defers depend on shared `err` and `errClone` state. Temp clone naming must remain collision-free. Clearing metadata only removes configured Kubernetes metadata keys; other metadata may propagate. QoS adjustment after resize means clone QoS behavior depends on metadata and mounter-specific handlers.

Test signals: No direct tests in this subset. Existing broader RBD tests would be needed for partial clone recovery, cleanup, metadata propagation, encryption, and QoS interactions.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/clone.go -->
