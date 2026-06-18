# Research: subset-b-000336

Grouped research for BeeGFS CSI driver control-plane sources and release tooling. Each file section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs_util.go -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs_util.go

Purpose: Provides operational helper logic shared by the BeeGFS CSI controller and node services. It converts BeeGFS volume IDs to URLs, renders per-mount BeeGFS client configuration files, mounts and unmounts BeeGFS filesystems, sanitizes mount options and filesystem names, validates CSI volume capabilities, and checks whether the BeeGFS kernel client module is available.

Important APIs/types/functions: package-level `fs` and `fsutil` wrap the host filesystem through `afero` and are swapped to in-memory or OS-backed filesystems by tests. `NewBeegfsURL` and `parseBeegfsURL` encode/decode `beegfs://host/path` IDs. `writeClientFiles` reads a template `beegfs-client.conf`, overrides only keys that already exist, writes optional `connInterfacesFile`, `connNetFilterFile`, `connTcpOnlyFilterFile`, `connRDMAInterfacesFile`, `connAuthFile`, and TLS certificate files, and handles BeeGFS 7/8 key compatibility for `connClientPortUDP` versus `connClientPort` and `connMgmtdPortTCP`/`UDP` versus `connMgmtdPort`. `squashConfigForSysMgmtdHost` overlays filesystem-specific config onto defaults. `mountIfNecessary`, `constructMountOptions`, `addContextToMountOptionsIfNecessary`, and `removeInvalidMountOptions` prepare and invoke Kubernetes mount-utils. `unmountAndCleanUpIfNecessary` and `cleanUpIfNecessary` remove mount/config directories with bind-mount protection. `getEphemeralPortUDP`, `sanitizeVolumeID`, `isValidVolumeCapabilities`, `isBeegfsClientModuleLoaded`, `isBeegfsClientModuleInstalled`, and `verifyBeegfsClientModuleIsAvailable` cover lower-level host concerns.

Control flow: Volume operations first construct a `beegfsVolume` elsewhere, then call `writeClientFiles` into the volume staging/config directory. That function selects an ephemeral UDP port by opening a temporary UDP socket, loads INI content, validates every configured override against the template, writes sidecar files when corresponding config slices/secrets are present, and finally emits the client config file. Mount flow computes safe options, creates the mount point if missing, skips already-mounted paths, then mounts source `beegfs_nodev` as fstype `beegfs`. Cleanup flow lists mounts to detect other bind mounts referencing the same client config and refuses to unmount if still in use, then calls `mount.CleanupMountPoint` and removes config contents.

State and persistence: Persistent effects are host filesystem writes under a volume-specific mount directory: `beegfs-client.conf`, optional networking/auth/cert files, and mountpoint directories. Runtime state is otherwise transient. `getEphemeralPortUDP` has an inherent race because another process can bind the returned port before BeeGFS uses it; the warning is documented in the source. `sanitizeVolumeID` preserves underscores by doubling them and hashes long IDs to fit filename limits.

Dependencies and integration points: Uses CSI protobuf types for capability validation, BeeGFS operator API config types, `go-ini` for config templates, `afero` for testable filesystem operations, `k8s.io/mount-utils` for mount behavior, `opencontainers/selinux` for SELinux mount contexts, and host commands `lsmod`/`modprobe` for kernel module checks. It is called from `controllerserver.go`, `nodeserver.go`, config parsing, and tests.

Risks: Template-key enforcement prevents silently adding unsupported BeeGFS config keys but makes upgrades sensitive to template drift. BeeGFS 8 migration logic only handles equal deprecated management TCP/UDP ports. Cleanup bind-mount detection depends on mount listing path and option contents, so unusual mount namespaces or option formatting can cause false refusal or missed references. Host command checks compare `modprobe` failure using an exact error string. The package-level mutable filesystem variables are convenient for tests but require careful reset between tests.

Test signals: `beegfs_util_test.go` covers URL parsing, file rendering, BeeGFS 8 compatibility and mismatch failure, config squashing, ephemeral port acquisition, volume ID sanitization, capability validation, SELinux context insertion, and mount option filtering. Sanity and server tests indirectly exercise logging and CSI flows built on these helpers.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs_util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs_util_test.go -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs_util_test.go

Purpose: Unit-tests the shared BeeGFS utility layer, especially URL formatting, client configuration rendering, BeeGFS 7/8 config compatibility, filesystem-specific config squashing, ephemeral port selection, mount option handling, and CSI capability validation.

Important APIs/types/functions: Defines `TestWriteClientFilesTemplate`, expected rendered config constants for BeeGFS 7 and 8 templates, and table-driven tests for `NewBeegfsURL`, `parseBeegfsURL`, `writeClientFiles`, `squashConfigForSysMgmtdHost`, `getEphemeralPortUDP`, `sanitizeVolumeID`, `isValidVolumeCapabilities`, `addContextToMountOptionsIfNecessary`, and `removeInvalidMountOptions`.

Control flow: Tests swap package-level `fs` and `fsutil` to `afero.NewMemMapFs` for client file rendering, create template/config directories, build `beegfsVolume` instances, call helpers, and read back generated files. The variable UDP client port is masked with a regex before comparing generated INI content. BeeGFS 8 tests verify `connClientPort` and `connMgmtdPort` handling, including failure when deprecated TCP/UDP management ports disagree.

State and persistence: Test state is isolated mostly in memory via `afero`, except `getEphemeralPortUDP` uses a real UDP socket. Tests mutate global filesystem variables and rely on later tests setting their own backing filesystem where needed.

Dependencies and integration points: Uses BeeGFS operator API config structs, CSI protobuf volume capability structs, package helpers from `beegfs_util.go`, and `afero`. The tests verify compatibility expectations that controller and node service operations depend on before mounting or calling `beegfs-ctl`.

Risks: The expected INI output is formatting-sensitive, so changes in `go-ini` rendering could break tests even if semantics are unchanged. Global filesystem mutation can leak between tests if a new test forgets to reset it. Capability validation tests are narrow: they assert block is rejected and mount is accepted but do not deeply examine all access modes because the driver accepts all CSI access modes for mounted volumes.

Test signals: Strong coverage for client file rendering and compatibility paths. The tests explicitly guard secret/auth file contents, networking filter files, RDMA interface files, hash fallback for long IDs, duplicate/cfgFile mount option removal, and default SELinux context insertion.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/beegfs_util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/config.go -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/config.go

Purpose: Adds driver-specific behavior around operator API configuration structs. It reads strict YAML config files, applies node-specific overrides, validates syntax, strips no-effect BeeGFS client options, and merges external connAuth and TLS certificate files into filesystem-specific config entries.

Important APIs/types/functions: `noEffectBeegfsConfOptions` lists client config keys removed because the driver controls them: `sysMgmtdHost`, client port keys, and `connPortShift`. `unsupportedBeegfsConfOptions` lists file-path options that are logged but not removed. `parseConfigFromFile` builds `beegfsv1.PluginConfig` from `PluginConfigFromFile`, overlays matching `NodeSpecificConfigs`, validates, and strips. `parseConnAuthFromFile` and `parseTLSCertsFromFile` attach secrets/certs to matching or newly appended `FileSystemSpecificConfigs`. `validateConfig` checks management hosts, gRPC port range, and IP/CIDR filters. `stripConfig`, `overwriteFileSystemSpecificConfigs`, and `overWriteBeegfsConfig` implement config normalization and precedence.

Control flow: `parseConfigFromFile` reads through `fsutil`, unmarshals with `yaml.UnmarshalStrict`, adds a targeted hint when `beegfsClientConf` values are unquoted integers/booleans, copies default and filesystem-specific config, then sequentially applies every node config whose node list contains the current node ID. Later matching node entries can overwrite earlier entries. Validation happens before no-effect stripping, then the final config is logged with secret-safe marshal behavior from the API package. Secret file parsing decodes `raw`/empty encodings by appending a newline and decodes `base64` exactly; invalid encodings and bad base64 fail.

State and persistence: Config parsing itself has no persistent writes. It mutates the provided `PluginConfig` in secret/cert parsing and uses slices/maps from BeeGFS API types. Overwrite semantics copy slices but map values are assigned into the destination map; this assumes destination `BeegfsClientConf` maps are initialized by constructors or unmarshalling.

Dependencies and integration points: Uses `sigs.k8s.io/yaml`, BeeGFS operator API types, `afero` filesystem wrappers, Go networking parsers, and logging helpers. The resulting config feeds `newBeegfsVolume`, controller/node server setup, and `writeClientFiles`.

Risks: The domain regex is permissive and unusual because it includes a numeric-slash fragment; management host validation should be reviewed for intended DNS coverage. `stripConfig` builds a slice of configs by value; because maps are reference types, deletes affect underlying maps, but slice fields copied by value may not propagate for non-map future fields. Secret parsing intentionally appends newlines for raw auth and TLS certs, which must match user expectations. Strict YAML is useful but creates migration friction for schema changes.

Test signals: `config_test.go` validates strict quote failures, node default override precedence including double overrides, filesystem-specific node overrides, connAuth/TLS merging and base64 decoding, host/filter validation, stripping no-effect options, retaining unsupported options, and preserving explicit empty map values.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/config_test.go -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/config_test.go

Purpose: Exercises the driver configuration parser and merger against YAML fixtures and direct struct inputs. It documents expected precedence, strict string typing for `beegfsClientConf`, secret/certificate handling, validation errors, and strip behavior.

Important APIs/types/functions: `TestParseConfigFromFile` consumes all config fixture YAMLs. `TestParseConnAuthAndTLSCertsFromFiles` verifies raw/base64 connAuth and TLS cert merging. `TestValidateConfig` checks management host and IP/CIDR filter validation. `TestStripNoEffectConfig`, `TestStripCleanConfig`, and `TestStripUnsupportedConfig` assert stripping behavior. `TestOverwriteFromBeegfsClientConfEmptyValue` confirms explicit empty string overrides are retained.

Control flow: Tests set `fs` to `afero.NewOsFs` because fixture files live on disk. Table entries call `parseConfigFromFile`, compare structs with `reflect.DeepEqual`, and optionally match expected error regexes. Secret tests load a binary fixture for expected base64 decoding, mutate a starting config through `parseConnAuthFromFile` and optionally `parseTLSCertsFromFile`, then compare final config shape.

State and persistence: Tests read fixture files under `pkg/beegfs/testdata` and mutate in-memory config structs. They do not write persistent files. The parser mutates maps inside structs, so the tests create separate original and modified configs where strip behavior is being compared.

Dependencies and integration points: Depends on the BeeGFS operator API config struct definitions and the exact schema represented by testdata YAML. These tests form the main signal for how operator-generated config is consumed by the runtime CSI driver.

Risks: Deep equality on slices makes ordering part of the contract, particularly for appended filesystem-specific configs from secret files. The tests do not cover malformed base64 or invalid encoding branches. Hostname validation coverage includes a valid domain and a single invalid token but not IPv6 or edge-case DNS names.

Test signals: Strong evidence that node-specific config applies only to matching node IDs and later matching node-specific config overwrites earlier config. Quote-error tests protect the user-facing diagnostic for YAML scalar type mistakes. Strip tests ensure unsupported file-path options are only warned about, not removed.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/controllerserver.go -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/controllerserver.go

Purpose: Implements the CSI Controller service for BeeGFS volume lifecycle operations. It creates and deletes BeeGFS-backed volume directories, validates volume capabilities, reports controller capabilities, and supports capacity-resize metadata responses.

Important APIs/types/functions: `controllerCaps` advertises create/delete and expand volume. `controllerServer` stores the BeeGFS ctl executor, node ID, plugin config, client config template path, mounter, controller service data directory, per-volume in-flight lock, completion status map, and node unstage timeout. Constructors `newControllerServer` and `newControllerServerSanity` select real or fake executors/mounters. CSI methods include `CreateVolume`, `DeleteVolume`, `ControllerGetCapabilities`, `ValidateVolumeCapabilities`, and `ControllerExpandVolume`; other methods are explicitly unimplemented. Helper functions parse stripe and permission parameters, construct `beegfsVolume` instances, wait for node unstage tracking, and validate request parameters.

Control flow: `CreateVolume` validates name/capabilities/parameters, constructs a volume ID from `sysMgmtdHost`, base path, and volume name, short-circuits if status map says created, obtains an exclusive string lock, creates a temporary mount/config directory, writes client files, uses `beegfs-ctl` to create and stripe the volume directory, mounts only when special permission bits require OS `chmod`, optionally creates `.csi/.../nodes` tracking, marks created, and defers cleanup. `DeleteVolume` treats invalid/nonexistent volume IDs as successful idempotent delete, short-circuits status-deleted volumes, locks the volume, writes client files, mounts, calls `deleteVolumeUntilWait`, and records deletion only if delete and cleanup both succeed. `ValidateVolumeCapabilities` writes client files without mounting and uses `beegfs-ctl stat` to confirm the volume directory.

State and persistence: Persists BeeGFS directories for volumes and `.csi` tracking. Creates and removes controller data directory subtrees under `csDataDir`. `threadSafeStatusMap` is in-memory only and improves retry idempotency within one process lifetime. `volumeIDsInFlight` prevents concurrent operations on the same volume ID. Node tracking wait polls mounted filesystem state and deletes tracking directories before deleting the volume directory.

Dependencies and integration points: Depends on `beegfsCtlExecutorInterface` for BeeGFS directory/stat/pattern work, `writeClientFiles` and mount helpers from `beegfs_util.go`, `thread_safe.go`, CSI protobufs and gRPC status codes, BeeGFS API config, and Kubernetes mount-utils. It integrates with node tracking written by `nodeserver.go`.

Risks: `validateReqParams` mutates the passed parameter map by deleting recognized entries, which could surprise callers if they reuse the map. Create cleanup ignores cleanup failures after successful volume creation, potentially leaving local orphan state. Delete waits for node tracking only up to a configured timeout and then proceeds, so orphan mounts are possible by design. `ControllerExpandVolume` reads `req.CapacityRange.RequiredBytes` without guarding nil `CapacityRange`, which could panic on malformed calls. In-memory status maps are lost on restart, so idempotency still depends on BeeGFS filesystem state for process restarts.

Test signals: `controllerserver_test.go` covers parameter parsing, permission and stripe validation, delete wait behavior for tracking directories, and request parameter validation. CSI sanity tests exercise controller behavior via a fake executor.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/controllerserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/controllerserver_test.go -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/controllerserver_test.go

Purpose: Tests controller helper behavior around CreateVolume parameter parsing and DeleteVolume node-tracking cleanup. It defines the behavioral contract for stripe pattern parameters, permission parameters, volume deletion waiting, and required parameter validation.

Important APIs/types/functions: `TestGetStripePatternConfigFromParams`, `TestGetPermissionsConfigFromParams`, `TestDeleteVolumeUntilWaitEmptyNodesDir`, `TestDeleteVolumeUntilWaitNoCSIDir`, `TestDeleteVolumeUntilWaitNodesDirNeverEmpties`, `TestDeleteVolumeUntilWaitNodesDirEmptiesEventually`, and `TestValidateReqParams`.

Control flow: Stripe tests pass maps with valid and invalid `stripePattern/...` keys and assert parsed config or errors. Permission tests parse UID/GID as 32-bit decimal values and mode as octal up to 12 bits. Delete tests set up an in-memory BeeGFS-like directory tree, optionally create node-tracking files, then call `deleteVolumeUntilWait` with zero or nonzero waits. One test removes a node tracking file asynchronously after two seconds to verify polling exits before timeout. Request parameter tests ensure `sysMgmtdHost` and `volDirBasePath` are required/normalized and unknown keys are rejected.

State and persistence: Uses `afero.NewMemMapFs` to build and remove directory trees in memory. Parameter parser tests mutate input maps because the production functions delete recognized keys; each table entry supplies fresh maps.

Dependencies and integration points: Depends on config constants and structs from other BeeGFS package files, `newBeegfsVolume`, and `afero`. It directly supports the controller's CSI Create/Delete request paths.

Risks: Some invalid stripe test cases use lowercase parameter keys, so they simultaneously exercise unknown-key and bad-value behavior. Deletion wait tests depend on real sleeps and wall-clock timing, which can be slow or flaky under heavy load. The tests focus helper functions rather than full `CreateVolume`/`DeleteVolume` CSI method behavior.

Test signals: Strong validation for boundary values: too-large UID/GID, non-octal modes, extra leading zeroes, empty base path normalized to `/`, extra unknown params rejected, and delete cleanup removing both `.csi` and volume directories under multiple node-tracking states.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/controllerserver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/identityserver.go -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/identityserver.go

Purpose: Implements the CSI Identity service for the BeeGFS driver. It returns plugin metadata, basic liveness probe response, and plugin capability declarations.

Important APIs/types/functions: `identityServer` stores driver `name` and `version` and embeds `csi.UnimplementedIdentityServer`. `newIdentityServer` constructs it. `GetPluginInfo` validates that name and version are configured before returning them. `Probe` returns an empty healthy response. `GetPluginCapabilities` advertises `CONTROLLER_SERVICE` and online volume expansion.

Control flow: Calls are simple request-response handlers. `GetPluginInfo` logs at debug level, returns `Unavailable` if either field is empty, and otherwise returns a `GetPluginInfoResponse`. Capabilities are assembled inline as CSI protobuf structures.

State and persistence: No persistence. State is immutable server metadata set at construction.

Dependencies and integration points: Registered by `server.go` into the gRPC server. Consumed by CSI sidecars and orchestrators during driver discovery. Uses gRPC status codes and the shared logging helpers.

Risks: Capability declarations must stay aligned with controller behavior; online volume expansion is advertised because `ControllerExpandVolume` returns a metadata-only success and `NodeExpandVolume` is unimplemented. Empty string validation makes misconfigured builds fail discovery clearly.

Test signals: Covered indirectly by CSI sanity tests. There is no dedicated identity unit test in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/identityserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/nodeserver.go -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/nodeserver.go

Purpose: Implements the CSI Node service for staging BeeGFS filesystems and bind-mounting volume directories into pod target paths. It also reports node identity and node service capabilities.

Important APIs/types/functions: `nodeCaps` advertises `STAGE_UNSTAGE_VOLUME`. `nodeServer` stores a BeeGFS ctl executor, node ID, plugin config, client config template path, and mounter. Constructors `newNodeServer` and `newNodeServerSanity` select real or fake dependencies. CSI methods include `NodeStageVolume`, `NodeUnstageVolume`, `NodePublishVolume`, `NodeUnpublishVolume`, `NodeGetInfo`, and `NodeGetCapabilities`; stats and node expansion are unimplemented.

Control flow: `NodeStageVolume` validates volume ID, staging path, and mount capability, builds a `beegfsVolume` from the staging path, requires the staging directory to exist, writes client config files, confirms the BeeGFS target directory with `beegfs-ctl stat`, mounts BeeGFS if needed, then best-effort writes an empty node tracking file under `.csi/.../nodes/<nodeID>`. `NodePublishVolume` validates inputs, reconstructs the staged volume, checks the target directory exists in BeeGFS via ctl stat, creates target path if missing, skips if already bind mounted, adds `bind` and optional `ro` to mount flags, sanitizes options, and bind-mounts the volume subdirectory to the target path. `NodeUnstageVolume` best-effort removes the node tracking file before unmounting and cleaning generated client files while leaving the staging directory for the CO. `NodeUnpublishVolume` cleans up the bind mount target.

State and persistence: Writes client config files into the staging path, mounts BeeGFS at staging path, bind-mounts volume directories at publish target paths, and creates/removes node tracking files in the mounted BeeGFS `.csi` tree. Node tracking is best effort: failures are logged but do not fail stage/unstage.

Dependencies and integration points: Uses CSI protobufs, gRPC status codes, BeeGFS ctl executor abstraction, `writeClientFiles`, `mountIfNecessary`, `unmountAndCleanUpIfNecessary`, and Kubernetes mount-utils. It coordinates with controller deletion waiting through `.csi/.../nodes` files.

Risks: Read-only bind mount behavior is documented as limited when running inside containers because read-only may not propagate outside the plugin container for all COs. Node tracking best-effort failures reduce delete safety. No in-flight lock is used on the node side, so concurrent publish/stage operations rely on mount idempotency and external CO behavior. `NodePublishVolume` uses fstype `beegfs` for a bind mount, which follows existing mount-utils behavior but may be platform-sensitive.

Test signals: CSI sanity tests exercise node methods through the full in-process driver. There are no dedicated node unit tests in this subset, so detailed edge cases rely on sanity coverage and helper tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/nodeserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/sanity_test.go -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/sanity_test.go

Purpose: Runs the Kubernetes CSI sanity test suite against an in-process BeeGFS driver configured with fake/sanity dependencies and an OS-backed temporary filesystem.

Important APIs/types/functions: `TestSanity` sets package filesystem globals to `afero.NewOsFs`, creates a temporary sanity directory, writes a minimal BeeGFS client config template, starts `NewBeegfsDriverSanity`, configures `sanity.NewTestConfig`, and invokes `sanity.Test`.

Control flow: The test creates controller data, staging, target, endpoint socket, and template paths under a temp directory. It starts the driver asynchronously on a Unix socket, supplies test volume parameters (`sysMgmtdHost=localhost`, `volDirBasePath=unittest`), runs the suite, and removes the temp directory.

State and persistence: Uses real temporary directories and a Unix-domain socket under the system temp directory. Cleanup removes the test root after sanity execution.

Dependencies and integration points: Depends on `github.com/kubernetes-csi/csi-test/v4/pkg/sanity`, Ginkgo reporter config, `afero`, the sanity driver constructor, and fake BeeGFS ctl behavior. It validates cross-service CSI behavior better than unit tests but still avoids real BeeGFS infrastructure.

Risks: Runs the driver in a goroutine without explicit stop coordination in the test body. It uses OS filesystem behavior, so environmental differences can surface. Sanity tests validate generic CSI contract but not BeeGFS-specific kernel module, mount namespace, or real `beegfs-ctl` behavior.

Test signals: Provides broad contract coverage across identity, controller, and node services with standard CSI sanity expectations. It is the main integration signal for unimplemented methods, idempotency, and required request validation.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/sanity_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/server.go -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/server.go

Purpose: Provides gRPC server plumbing and logging/error helpers for the BeeGFS CSI driver. It creates a non-blocking CSI gRPC server, parses endpoints, wraps requests with request IDs, sanitizes logged protobufs, and maps rich internal errors to gRPC status errors.

Important APIs/types/functions: `contextKey`, `ctxRequestIDKey`, and `requestIDCounter` implement request IDs. `grpcError` stores both a gRPC status error and an underlying `github.com/pkg/errors` cause with stack formatting; `newGrpcErrorFromCause` constructs it. `nonBlockingGRPCServer` exposes `Start`, `Wait`, `Stop`, `ForceStop`, and `serve`. `parseEndpoint` accepts `unix://` and `tcp://` endpoints. `logGRPC` is a unary interceptor. `generateRequestContext`, `logger`, `LogDebug`, `LogVerbose`, `LogError`, and `LogFatal` centralize logging.

Control flow: `Start` increments a wait group and launches `serve`. `serve` parses endpoint, removes stale Unix socket files, listens, constructs a gRPC server with `logGRPC`, registers non-nil identity/controller/node services, and serves until stopped or fatal error. `logGRPC` assigns a request ID, logs a sanitized request, invokes the handler, logs sanitized response or full error, and unwraps `grpcError` to send only the status error over gRPC.

State and persistence: State includes the active `grpc.Server`, a wait group, request ID counter, and optional Unix socket file removal. Logging writes through klog/klogr. Fatal logging exits the process with status 255.

Dependencies and integration points: Uses CSI protobuf service registration, gRPC, CSI lib `protosanitizer` for secret stripping, `go-logr`/`klogr` for logging, and shared `pkg/errors` stack traces. All CSI service implementations rely on `newGrpcErrorFromCause` and logging helpers.

Risks: `Stop` and `ForceStop` assume `s.server` is initialized; calling before `serve` assigns it could panic. `serve` logs `grpc.ErrServerStopped` as an error even though it can be normal shutdown. Request ID counter wraps at 65536, which is acceptable for log correlation but not globally unique. `parseEndpoint` does not validate protocol beyond prefix or address content beyond nonempty suffix.

Test signals: `server_test.go` specifically checks secret redaction through logging infrastructure. CSI sanity tests exercise server registration and request handling.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/server_test.go -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/server_test.go

Purpose: Verifies that shared logging infrastructure redacts sensitive BeeGFS configuration values before they reach klog output.

Important APIs/types/functions: `TestStripSecretsFromLogs` configures klog flags to write verbose logs to a buffer, creates a `beegfsv1.BeegfsConfig` with `ConnAuth` and `TLSCert`, then calls `LogError`, `LogDebug`, and `LogVerbose`.

Control flow: The test initializes a fresh flag set for klog, sets verbosity to include all tested log levels, disables stderr logging, captures output in a bytes buffer, and checks after each log call that the plaintext secret is absent and the redaction marker appears.

State and persistence: Mutates global klog configuration and output for the process. Uses in-memory buffer only.

Dependencies and integration points: Depends on BeeGFS operator API JSON/marshal redaction behavior and the server logging helpers. It protects `logGRPC` and other service logs indirectly because they use the same logging path.

Risks: Global klog state can interact with other tests if run in the same package and order-dependent settings leak. The test checks one secret string and one redaction marker, not every sensitive field or every logged request type.

Test signals: Strong targeted signal that `ConnAuth` is not emitted in plaintext at error, debug, or verbose levels and that redaction remains visible.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/server_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/basic.yaml -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/basic.yaml

Purpose: Positive configuration fixture for `parseConfigFromFile`. It defines a complete default BeeGFS config and one filesystem-specific config with the same values.

Important data: Top-level `config` sets `grpcPort`, `connInterfaces`, `connNetFilter`, `connTcpOnlyFilter`, and string-valued `beegfsClientConf` keys `connMgmtdPort` and `connUseRDMA`. `fileSystemSpecificConfigs` contains `sysMgmtdHost: 127.0.0.0` with equivalent nested config.

Control flow: Consumed by `TestParseConfigFromFile`, `TestValidateConfig`, and strip tests to establish a valid baseline. The parser should strictly unmarshal it, validate IP/CIDR values, and preserve all supported config entries.

State and persistence: Static test fixture, no runtime writes.

Dependencies and integration points: Mirrors the operator API YAML schema consumed by `config.go`. It feeds expected runtime config used by `writeClientFiles`.

Risks: Because it duplicates default and filesystem-specific config, fixture changes must be reflected in expected structs in tests. It only covers IPv4-style filters, not IPv6 or DNS host cases.

Test signals: Baseline passing config for parsing, validation, stripping no-effect options, stripping clean configs, and retaining unsupported options when tests inject them.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/basic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/connauthfile-base64.yaml -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/connauthfile-base64.yaml

Purpose: Secret fixture for `parseConnAuthFromFile` covering base64-encoded BeeGFS connection auth values, including a simple text secret and a multiline binary-like secret.

Important data: Contains two list entries keyed by `sysMgmtdHost`. The first decodes to `secret1\n`. The second uses a YAML block scalar for a longer base64 payload representing binary data and targets `127.0.0.1`.

Control flow: `parseConnAuthFromFile` unmarshals the list, selects `encoding: base64`, decodes the content exactly, and writes decoded strings into matching filesystem-specific configs. It does not append the raw-mode newline in the base64 branch.

State and persistence: Static test fixture. Secrets are sample data but still exercise secret-safe logging paths through API marshal behavior.

Dependencies and integration points: Used by `config_test.go` alongside a binary fixture to assert exact decoded bytes. Represents the recommended secret material flow into `writeClientFiles`.

Risks: Multiline base64 formatting depends on YAML preserving block content in a way accepted by Go's base64 decoder. Bad base64 and invalid encoding are not covered by this fixture.

Test signals: Confirms base64 decoding supports both normal text and binary connAuth files and applies values by `sysMgmtdHost`.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/connauthfile-base64.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/connauthfile.yaml -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/connauthfile.yaml

Purpose: Minimal raw connAuth fixture for `parseConnAuthFromFile`.

Important data: One list entry maps `sysMgmtdHost: 127.0.0.0` to `connAuth: secret1` with no explicit encoding, which is treated as raw.

Control flow: Parser appends a newline for raw/empty encoding and either updates an existing filesystem-specific config for the host or appends a new one.

State and persistence: Static test fixture. No writes.

Dependencies and integration points: Feeds tests for raw auth and combined TLS cert merging. The resulting `ConnAuth` is later written by `writeClientFiles` to `connAuthFile` with mode `0400`.

Risks: The implicit newline is intentional but can surprise users comparing literal YAML value to generated file content. The fixture only covers one host and no explicit `encoding: raw` spelling.

Test signals: Confirms raw connAuth defaults and host matching/append behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/connauthfile.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/no-quotes-boolean.yaml -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/no-quotes-boolean.yaml

Purpose: Negative YAML fixture proving `beegfsClientConf` values must be strings even when they look like booleans.

Important data: Sets `config.beegfsClientConf.connUseRDMA: true` without quotes.

Control flow: `yaml.UnmarshalStrict` attempts to decode this boolean into a `map[string]string` value and fails. `parseConfigFromFile` recognizes the resulting error pattern and wraps it with a specific likely-missing-quotes diagnostic.

State and persistence: Static test fixture.

Dependencies and integration points: Protects user-facing config validation in `config.go` and documents the schema expected by the operator API type.

Risks: The enhanced diagnostic depends on matching the unmarshalling error string. If the YAML library changes wording, the parser may still fail correctly but lose the tailored hint.

Test signals: `TestParseConfigFromFile` expects an error containing "likely missing quotes around an integer or boolean beegfsClientConf value".
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/no-quotes-boolean.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/no-quotes-integer.yaml -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/no-quotes-integer.yaml

Purpose: Negative YAML fixture proving numeric `beegfsClientConf` values must be quoted strings.

Important data: Sets `config.beegfsClientConf.connMgmtdPort: 8000` as an integer instead of `"8000"`.

Control flow: Strict YAML unmarshal fails because the destination type is string. `parseConfigFromFile` adds the missing-quotes hint when the error matches its regex.

State and persistence: Static fixture.

Dependencies and integration points: Documents runtime config contract for values later written into `beegfs-client.conf`, where all BeeGFS client config overrides are string values.

Risks: Same diagnostic-string coupling as the boolean fixture. It does not test quoted numeric strings with leading zeroes or empty values; those are covered elsewhere.

Test signals: Negative parsing path used by `TestParseConfigFromFile`.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/no-quotes-integer.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/node-default-override-double.yaml -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/node-default-override-double.yaml

Purpose: Fixture documenting sequential node-specific override precedence when more than one node-specific config applies to the same node.

Important data: Top-level default config sets base networking and management port values. Two `nodeSpecificConfigs` entries both list `testnode`; the first overrides values to the `1` variants and the second overrides them again to the `2` variants. Top-level `grpcPort` is intentionally absent to show node-specific config can add it.

Control flow: `parseConfigFromFile` loops through node-specific configs in file order. Both matching entries apply, so later values win. `overWriteBeegfsConfig` copies only non-empty fields and map keys from each override.

State and persistence: Static fixture.

Dependencies and integration points: Tests the precedence semantics that node-local driver config depends on when multiple node selectors overlap.

Risks: Ordering becomes meaningful in YAML. Overlapping node entries can be powerful but may be confusing operationally because the last matching entry wins without warning.

Test signals: `TestParseConfigFromFile` expects final values from the second override and confirms a missing default `grpcPort` can be supplied by node override.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/node-default-override-double.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/node-default-override.yaml -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/node-default-override.yaml

Purpose: Fixture for node-specific default config override behavior.

Important data: Top-level `config` sets `grpcPort`, interface/filter values, and `connMgmtdPort` with `0` variants. A single `nodeSpecificConfigs` entry for `testnode` supplies `1` variants for the same fields.

Control flow: When `nodeID` is `testnode`, `parseConfigFromFile` overlays the node config onto `DefaultConfig`. When the node ID does not match, top-level defaults remain unchanged.

State and persistence: Static fixture.

Dependencies and integration points: Demonstrates how a single config file can adjust driver behavior per node, affecting later BeeGFS client file generation and mount behavior.

Risks: Node matching is exact string equality against `nodeList`. Missing or differently-cased node IDs prevent override application.

Test signals: Positive and negative node match cases in `TestParseConfigFromFile`.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/node-default-override.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/node-filesystem-override.yaml -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/node-filesystem-override.yaml

Purpose: Fixture for node-specific filesystem-specific override behavior.

Important data: Top-level default config sets base networking values and management port. A node-specific entry for `testnode` contains `fileSystemSpecificConfigs` for `sysMgmtdHost: 127.0.0.1` with `grpcPort` and `1` variants for networking and port config.

Control flow: For matching node ID, `parseConfigFromFile` merges the node-specific filesystem config into the plugin's filesystem-specific list via `overwriteFileSystemSpecificConfigs`. Because there is no pre-existing filesystem-specific entry for that host, it appends a new entry.

State and persistence: Static fixture.

Dependencies and integration points: Models per-node and per-filesystem config overrides that later get selected by `squashConfigForSysMgmtdHost` for a mounted BeeGFS filesystem.

Risks: If multiple entries target the same `sysMgmtdHost`, merge behavior overwrites fields in place; ordering matters. Top-level `grpcPort` is absent, so tests verify override can introduce it only for the specific filesystem.

Test signals: `TestParseConfigFromFile` expects default config unchanged and one appended filesystem-specific config for `127.0.0.1`.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/node-filesystem-override.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/tlscerts.yaml -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/tlscerts.yaml

Purpose: Minimal TLS certificate fixture for `parseTLSCertsFromFile`.

Important data: One list entry maps `sysMgmtdHost: 127.0.0.0` to `tlsCert: "cert1"`.

Control flow: Parser appends a newline to the cert value and writes it into a matching or new filesystem-specific config. Unlike connAuth, there is no encoding field in this fixture.

State and persistence: Static fixture.

Dependencies and integration points: The parsed `TLSCert` is later written by `writeClientFiles` to the per-volume TLS cert path with mode `0400`, but not inserted into `beegfs-client.conf`.

Risks: Only the simplest cert value is covered; multiline PEM-style certs are not represented here. Automatic newline addition must match how BeeGFS client expects cert file content.

Test signals: Used in `TestParseConnAuthAndTLSCertsFromFiles` to verify TLS cert append/merge behavior alongside connAuth.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/tlscerts.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/thread_safe.go -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/thread_safe.go

Purpose: Provides small concurrency-safe in-memory structures used by the controller to serialize operations per volume and remember successful lifecycle checkpoints.

Important APIs/types/functions: `threadSafeStringLock` holds a mutex-protected set of strings with `obtainLockOnString` and `releaseLockOnString`. `volumeStatus` is a string type with constants `statusCreated` and `statusDeleted`. `threadSafeStatusMap` holds a mutex-protected map from volume ID to status with `writeStatus` and `readStatus`.

Control flow: `obtainLockOnString` takes an exclusive mutex, inserts the string only if absent, and reports success. `releaseLockOnString` deletes the string. `threadSafeStatusMap` uses exclusive locking for writes and read locking for reads. Controller operations read status for idempotent short-circuiting and use the string lock to return CSI `Aborted` for concurrent operations on the same volume.

State and persistence: All state is in memory and process-local. It is lost on driver restart and is not shared across multiple controller instances.

Dependencies and integration points: Uses only Go `sync`. Integrated directly by `controllerServer` for `volumeIDsInFlight` and `volumeStatusMap`.

Risks: The string lock is not reentrant and has no ownership tracking; a mistaken release can unlock another operation's string if used incorrectly. In-memory status can hide filesystem reality within one process if a later external change removes or recreates a volume after status is recorded. There is no TTL or cleanup for status entries.

Test signals: `thread_safe_test.go` validates contention behavior for locks and map blocking under a held mutex.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/thread_safe.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/thread_safe_test.go -->
# sources/control-plane/beegfs-csi-driver/pkg/beegfs/thread_safe_test.go

Purpose: Tests concurrency behavior of `threadSafeStringLock` and `threadSafeStatusMap`.

Important APIs/types/functions: `TestThreadSafeStringLock`, `TestThreadSafeStatusMapNoContention`, and `TestThreadSafeStatusMapContention`.

Control flow: The string-lock test launches several goroutines per lock string after random sleeps and expects exactly one success per string until release, then verifies relocking after release. The status-map no-contention test checks empty reads, writes, and reads. The contention test manually holds the map mutex, starts read and write goroutines, verifies neither completes while the lock is held, releases the lock, and expects completion.

State and persistence: Uses in-memory maps and goroutines only. Randomized sleep introduces scheduling variation to exercise contention.

Dependencies and integration points: Directly validates synchronization primitives used by `controllerServer` for per-volume concurrency and idempotent status memory.

Risks: The contention test's select/default plus elapsed-time check does not actually loop until timeout, so under unlucky scheduling it can miss late completions or fail to wait as intended. Random sleeps make test timing nondeterministic, though bounded.

Test signals: Confirms the intended invariant that only one goroutine can hold a given volume lock and that reads/writes block under the mutex.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/pkg/beegfs/thread_safe_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/.prow.sh -->
# sources/control-plane/beegfs-csi-driver/release-tools/.prow.sh

Purpose: Prow entrypoint for testing the `csi-release-tools` repository itself, rather than a normal Go CSI component repository.

Important APIs/types/functions: Shell script invokes `./verify-shellcheck.sh`, `./verify-spelling.sh`, and `./verify-boilerplate.sh` against the current working directory.

Control flow: Runs with `bash -e`, so the first failing verification script exits the job. It assumes it is executed from the release-tools repo root.

State and persistence: No persistent state except whatever called verification scripts write to stdout/stderr or temp files.

Dependencies and integration points: Depends on verification scripts existing in the current directory. It is distinct from `prow.sh`, which is imported by normal component repos.

Risks: This subset does not include `verify-shellcheck.sh` or `verify-spelling.sh`, so this script's success depends on adjacent files outside the listed item. It assumes current working directory is correct.

Test signals: Provides CI coverage for release-tools quality checks: shellcheck, spelling, and boilerplate headers.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/.prow.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/boilerplate/boilerplate.py -->
# sources/control-plane/beegfs-csi-driver/release-tools/boilerplate/boilerplate.py

Purpose: Checks source files for required Kubernetes-style boilerplate headers. It supports multiple file extensions, strips language-specific preambles such as shebangs and Go build tags, normalizes years, and prints files that fail.

Important APIs/types/functions: CLI args include optional filenames, `--rootdir`, `--boilerplate-dir`, and `--verbose`. `get_refs` loads `boilerplate.*.txt` reference headers. `file_passes` performs the comparison. `file_extension`, `normalize_files`, `get_files`, and `get_regexs` support discovery and normalization. `main` prints failing filenames and returns zero regardless of failures, leaving callers to inspect output.

Control flow: The script gathers candidate files by explicit args or walking `rootdir`, prunes skipped dirs such as `.git`, `vendor`, `_output`, and `third_party`, filters by extensions/basenames with reference headers, then checks each file. For Go files it removes build constraints; for shell/Python it removes shebangs. It verifies the file is at least as long as the reference, rejects literal `YEAR`, replaces actual supported year values with `YEAR`, and diffs against the reference.

State and persistence: Reads source files and boilerplate reference files. Writes diagnostics to stdout and optional verbose details to stderr. No persistent writes.

Dependencies and integration points: Used by `verify-boilerplate.sh`. Depends on Python stdlib `argparse`, `glob`, `os`, `re`, `difflib`, and current date for the accepted year range.

Risks: Returning zero even when files fail means shell wrappers must treat non-empty output as failure; direct users may miss failures. Skipped directory matching uses substring checks, which can skip paths unexpectedly if they contain a skipped token. The default `rootdir` expression uses path arithmetic relative to this script and assumes release-tools layout.

Test signals: `verify-boilerplate.sh` invokes it with `--verbose` and fails if any filenames are returned. There are no direct unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/boilerplate/boilerplate.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/cloudbuild.sh -->
# sources/control-plane/beegfs-csi-driver/release-tools/cloudbuild.sh

Purpose: Thin Cloud Build entrypoint that sources release-tools Prow/build helpers and runs the Google Container Registry multi-architecture build flow.

Important APIs/types/functions: Sources `release-tools/prow.sh` and calls `gcr_cloud_build`.

Control flow: The script is expected to be invoked as `.cloudbuild.sh` from a repository that imports release-tools. `gcr_cloud_build` performs Docker credential setup, optional QEMU registration, derives revision metadata from `GIT_TAG`, and invokes `make push-multiarch`.

State and persistence: Effects are delegated to `gcr_cloud_build`: Docker auth config, buildx/QEMU setup, container builds, and pushed images.

Dependencies and integration points: Used by `cloudbuild.yaml` as the build step entrypoint. Depends on `release-tools/prow.sh`, `gcloud`, Docker, Go, and Makefile targets in the importing repository.

Risks: Because it sources the large `prow.sh`, all default config variables are evaluated in the Cloud Build environment. It assumes the working tree has a `release-tools/prow.sh` path and suitable Makefile.

Test signals: Covered by Cloud Build jobs using `cloudbuild.yaml`; no local unit tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/cloudbuild.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/cloudbuild.yaml -->
# sources/control-plane/beegfs-csi-driver/release-tools/cloudbuild.yaml

Purpose: Google Cloud Build configuration for Kubernetes CSI multi-architecture image builds.

Important APIs/types/functions: Sets `timeout: 7200s`, `substitution_option: ALLOW_LOOSE`, and one build step using `gcr.io/k8s-testimages/gcb-docker-gcloud:v20230623-56e06d7c18` with entrypoint `./.cloudbuild.sh`. Passes `GIT_TAG`, `PULL_BASE_REF`, `REGISTRY_NAME`, and `HOME` via environment. Defines default substitutions for `_GIT_TAG`, `_PULL_BASE_REF`, and `_STAGING_PROJECT`.

Control flow: Cloud Build expands substitutions, runs `.cloudbuild.sh`, and that script calls `gcr_cloud_build` from `prow.sh`. Repos importing this file are expected to symlink or copy it and provide compatible Dockerfiles and Makefile targets.

State and persistence: Produces pushed container images in the configured staging registry. No repository file writes are specified by the YAML itself.

Dependencies and integration points: Integrates Kubernetes test-infra image-pushing conventions, GCR staging projects, Docker buildx, and `make push-multiarch`.

Risks: Image builder version and staging project defaults can become stale. `ALLOW_LOOSE` avoids missing substitution failures but can hide misconfigured variables. Build timeout must remain high enough for multiple architectures.

Test signals: Operational signal comes from Cloud Build/Prow image-pushing jobs, not unit tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/cloudbuild.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/contrib/get_supported_version_csi-sidecar.py -->
# sources/control-plane/beegfs-csi-driver/release-tools/contrib/get_supported_version_csi-sidecar.py

Purpose: Helper script for determining currently supported Kubernetes CSI sidecar release versions from GitHub releases according to Kubernetes CSI support policy, with optional Docker image extraction for documentation updates.

Important APIs/types/functions: `check_gh_command` verifies GitHub CLI availability. `duration_ago` formats release age. `parse_version` parses `vX.Y.Z`. `end_of_life_grouped_versions` groups minor releases and chooses supported patch versions based on latest, one-year, and recent-patch windows. `get_release_docker_image` extracts a `docker pull` image from a release page. `get_versions_from_releases` shells out to `gh release list`. `main` parses repeated `--repo/-R`, `--display`, and `--doc`.

Control flow: For each repo, the script obtains all releases via `gh`, groups semantic versions by major/minor, sorts groups descending, always includes the latest minor's latest version, includes latest patch for minor releases whose first release is less than a year old, and includes older minors with a patch less than three months old. It prints versions and ages, and optionally release Docker image strings.

State and persistence: No persistent writes. Reads GitHub release data via the `gh` command and current local time.

Dependencies and integration points: Requires Python, `python-dateutil`, and GitHub CLI authentication/network access. Intended to support manual updates to Kubernetes CSI documentation tables.

Risks: Relies on the tabular output shape of `gh release list`, specifically timestamp position. `--display` defaults true and cannot be turned off by a paired false flag. The policy implementation is date-sensitive and should be checked against current CSI policy before relying on it. If a release description lacks a matching `docker pull` line, image output is blank.

Test signals: No tests in this subset. Manual output can be compared against GitHub release pages and CSI policy.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/contrib/get_supported_version_csi-sidecar.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/filter-junit.go -->
# sources/control-plane/beegfs-csi-driver/release-tools/filter-junit.go

Purpose: Command-line tool that filters and merges JUnit XML files so only testcases whose names match a regex remain, reducing noisy skipped tests in Prow artifacts.

Important APIs/types/functions: Flags `-o` selects output file or stdout and `-t` selects testcase-name regex. XML structs `TestResults`, `TestSuite`, `TestCase`, and `SkipReason` model enough JUnit XML for Ginkgo/Spyglass. `SkipReason` custom marshal/unmarshal preserves present-but-empty `<skipped></skipped>` elements.

Control flow: Parses flags, compiles regex, reads each input file or stdin, tries to unmarshal as `<testsuite>`, falls back to `<testsuites><testsuite>` for newer Ginkgo output, appends testcases, filters by regex into a map keyed by testcase name, and replaces skipped-only entries with real runs if available. It marshals the resulting testsuite with indentation and writes to stdout or file.

State and persistence: Reads input XML files and writes one output XML file. No other state.

Dependencies and integration points: Called by `prow.sh` via `run_filter_junit` to merge step JUnit files into filtered artifacts. Uses Go stdlib XML, flags, regexp, and filesystem APIs.

Risks: Stdin reading uses `os.Stdin.Read(data)` with a nil slice, which will not read full stdin correctly; file input is the practical path used by Prow. Map iteration makes output testcase order nondeterministic. The XML model omits many JUnit attributes, so they are dropped on re-encode. Duplicate testcase names collapse to one result.

Test signals: No direct tests in this subset. It is exercised operationally by Prow jobs that produce final JUnit artifacts.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/filter-junit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/generate_patch_release_notes.sh -->
# sources/control-plane/beegfs-csi-driver/release-tools/generate_patch_release_notes.sh

Purpose: Manual automation for generating Kubernetes CSI patch release changelog PRs across selected repos.

Important APIs/types/functions: Requires environment variables `CSI_RELEASE_TOKEN` and `GITHUB_USER`. Contains an editable `releases` array of `repo version` pairs. Function `gen_patch_relnotes` runs `release-notes --discover=patch-to-latest` with GitHub token and writes `out.md`.

Control flow: For each configured release, the script parses the minor version, enters the repo's `CHANGELOG` directory, fetches upstream, creates/reset a `changelog-release-<minor>` branch from `upstream/release-<minor>`, generates release notes, prepends a new `# Release notes for v<version>` section plus docs link to `CHANGELOG-<minor>.md`, commits, force-pushes to the user's fork, and opens a GitHub PR with `release-note NONE`.

State and persistence: Deletes local `out.md` and `/tmp/k8s-repo`, modifies changelog files, creates/deletes branches, commits, pushes to GitHub, and opens PRs.

Dependencies and integration points: Requires `gh`, `release-notes`, git remotes named `upstream`/`origin`, authenticated GitHub access, and a local directory layout one level above the CSI repos.

Risks: Force-pushes and branch deletion are destructive for matching branch names. The hardcoded `releases` array is empty by default and must be edited. It does not update existing PRs. It assumes changelog files and branch naming conventions match Kubernetes CSI repos.

Test signals: No automated tests; intended for manual use with visible git and PR results.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/generate_patch_release_notes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/go-get-kubernetes.sh -->
# sources/control-plane/beegfs-csi-driver/release-tools/go-get-kubernetes.sh

Purpose: Updates Go module dependencies that originate from `kubernetes/kubernetes` staging modules to a specific Kubernetes release version, adding necessary replace statements to avoid fake `v0.0.0` module revisions.

Important APIs/types/functions: Supports `-p` to prune unused replace statements and `-h` for help. Fetches Kubernetes `go.mod` for a supplied `x.y.z` version, extracts staging module names, applies `go mod edit -replace`, enumerates imported `k8s.io` packages, and runs `go get` with `@kubernetes-<version>` or `@v<version>` for `k8s.io/kubernetes/...`.

Control flow: Validates exactly one version argument, downloads upstream Kubernetes `go.mod`, builds the staging module list, optionally prunes unused replacements based on `go mod graph`, determines actual module versions via `go mod download -json`, edits replacements, gathers package imports with `go list all` or fallback dependency listing, filters packages whose modules have replace entries, and runs `go get` for those packages.

State and persistence: Mutates `go.mod` and potentially `go.sum` in the current repository. Downloads module metadata and upstream files. No commits.

Dependencies and integration points: Used by `go-modules-update.sh` and manually during dependency updates. Requires curl, sed, grep, Go modules, network access to GitHub and module proxy/source, and a Go module repository.

Risks: Parsing upstream `go.mod` with sed is sensitive to format changes. `go list all` can fail before replacements are complete, hence fallback logic. The script modifies module replacements broadly unless pruned. It does not update non-Kubernetes-staging `k8s.io` modules such as `klog` or `utils`.

Test signals: Success is indicated by `SUCCESS` after `go get`. Downstream validation usually requires `go mod tidy`, vendoring, and project tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/go-get-kubernetes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/go-modules-update.sh -->
# sources/control-plane/beegfs-csi-driver/release-tools/go-modules-update.sh

Purpose: Batch automation for updating Kubernetes CSI sidecar repositories to a target Kubernetes dependency version and creating PRs.

Important APIs/types/functions: Accepts `-u` username and `-v` version. Uses `MAX_RETRY=10`. Iterates a hardcoded list of CSI repos and branches. Calls `gh auth login`, `git subtree pull` for release-tools, `release-tools/go-get-kubernetes.sh -p`, `go mod tidy`, `go mod vendor`, `make test`, git push, and `gh pr create`.

Control flow: For each repo/branch, it fetches origin, recreates a `module-update-<branch>` branch from `origin/<branch>`, refreshes release-tools via subtree. On subtree conflicts it replaces `release-tools` with an archive of `FETCH_HEAD` and commits the merge message. It retries Kubernetes dependency update with tidy/vendor cleanup, commits all changes, points origin at the user's fork, tests, force-pushes, and opens a PR against Kubernetes CSI upstream.

State and persistence: Performs extensive git mutations across many repositories: branch deletion/creation, subtree commits, module/vendor file edits, all-file commits, remote URL changes, force pushes, and PR creation.

Dependencies and integration points: Requires local checkouts of all listed repos, GitHub CLI, authenticated GitHub access, Go, Makefile test targets, and `go-get-kubernetes.sh`.

Risks: Highly destructive if run in a working tree with local changes. The PR head is hardcoded as `module-update-master` even inside a loop over branches, which may be wrong for non-master branches. It changes `origin` remote URL permanently. It does not resolve API incompatibilities automatically despite updating dependencies.

Test signals: Runs `make test` before pushing. Success is also visible through pushed branches and created PRs.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/go-modules-update.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/prow.sh -->
# sources/control-plane/beegfs-csi-driver/release-tools/prow.sh

Purpose: Main reusable Kubernetes CSI Prow and Cloud Build harness. It configures Go versions, builds component binaries/images, creates KinD clusters, deploys CSI drivers, installs snapshot components, runs unit/E2E/sanity tests, collects logs, filters JUnit artifacts, and supports multi-arch image pushing.

Important APIs/types/functions: Configuration is driven by `configvar`, with many `CSI_PROW_*` variables for build platforms, Go versions, Kubernetes/KinD versions, hostpath driver deployment, E2E focus/skip regexes, sanity settings, snapshotter version, and test selection. Helper functions include `get_versioned_variable`, `version_to_git`, `tests_enabled`, `ensure_paths`, `run_with_go`, `install_kind`, `install_ginkgo`, `install_dep`, `git_checkout`, `git_clone`, `start_cluster`, `delete_cluster_inside_prow_job`, `find_deployment`, `install_csi_driver`, `install_snapshot_crds`, `install_snapshot_controller`, `collect_cluster_info`, `start_loggers`, `patch_kubernetes`, `install_e2e`, `install_sanity`, `run_filter_junit`, `run_e2e`, `run_sanity`, `make_test_to_junit`, `version_gt`, `main`, and `gcr_cloud_build`.

Control flow: On sourcing/execution, defaults are set and logged. `main` creates a work/artifact area, optionally runs `make all`, `make -k test` converted to JUnit, and `make container`. If selected tests need KinD, it installs KinD, tags locally built images as `csiprow`, derives deploy environment variables and RBAC overrides, creates non-alpha and/or alpha clusters, installs snapshot CRDs/controller, deploys the CSI driver, collects cluster info, runs sanity, parallel, feature, serial, alpha, and sidecar E2E test lanes according to `CSI_PROW_TESTS`, exports logs on cleanup, and merges JUnit files. `gcr_cloud_build` sets Docker auth, registers QEMU if Dockerfiles contain `RUN`, derives `REV` from `GIT_TAG`, and runs `make push-multiarch`.

State and persistence: Creates temporary work directories under `GOPATH/pkg`, artifact directories, downloaded Go/KinD/Ginkgo binaries, cloned Kubernetes/driver/test repos, KinD clusters and Docker images, generated YAML/scripts for sanity commands, JUnit XML files, and cluster logs. It modifies checked-out Kubernetes test manifests when canary testing is enabled.

Dependencies and integration points: Depends on bash, Go, make targets, Docker, KinD, kubectl, ginkgo, csi-test, Kubernetes E2E tests, GitHub-hosted repos, snapshotter manifests, `filter-junit.go`, and optional imported repo deploy scripts. It is sourced by top-level repo Prow scripts and `cloudbuild.sh`.

Risks: Very broad environment-sensitive script. Many defaults are pinned to older versions and must be maintained. It uses extensive shell interpolation and intentional word splitting for env var lists. Network flakes affect Go/KinD/Kubernetes downloads. Cluster cleanup happens only inside Prow when `JOB_NAME` is set. YAML/image patching uses sed and kubectl dry-run assumptions. It can run lengthy tests and leave Docker/KinD state when interrupted.

Test signals: The script itself orchestrates validation. `make_test_to_junit` preserves unit-test failures as JUnit, `run_filter_junit` merges E2E outputs, and cluster logs are exported for failed deployments. No dedicated unit tests for the shell functions are present in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/prow.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/pull-test.sh -->
# sources/control-plane/beegfs-csi-driver/release-tools/pull-test.sh

Purpose: Prow helper for testing changes to `csi-release-tools` by importing them into another repository and running that repository's Prow script.

Important APIs/types/functions: Uses `CSI_RELEASE_TOOLS_DIR="$(pwd)"` and required `PULL_TEST_REPO_DIR`. Runs git subtree pull and then `exec ./.prow.sh`.

Control flow: Assumes it starts inside the updated release-tools repository. It changes to the target repo, hard-resets the target working tree, pulls the release-tools repo into `release-tools` prefix with `--squash`, prints recent log entries, and hands off to the target repo's `.prow.sh`.

State and persistence: Destructively resets the target repo working tree, updates its release-tools subtree, and may leave merge commits or working tree changes before tests.

Dependencies and integration points: Used by PR jobs for release-tools itself. Requires `PULL_TEST_REPO_DIR`, git subtree support, and a target repository with `.prow.sh`.

Risks: The `git reset --hard` is intentionally destructive. It assumes the source branch name `master` in subtree pull. Target repo local changes are discarded.

Test signals: The final test signal is the target repository's `.prow.sh` result after importing the release-tools changes.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/pull-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/update-vendor.sh -->
# sources/control-plane/beegfs-csi-driver/release-tools/update-vendor.sh

Purpose: Updates vendored dependencies for repositories using either dep or Go modules.

Important APIs/types/functions: Checks for `Gopkg.toml` to run `dep ensure`; checks for `go.mod` to run `release-tools/verify-go-version.sh "go"` followed by `GO111MODULE=on go mod tidy` and `go mod vendor`.

Control flow: Branches by dependency management file presence. For Go modules it warns on unexpected Go version before tidying and vendoring.

State and persistence: Mutates `vendor/`, `go.mod`, and `go.sum` for module repos, or dep-managed vendor state for dep repos.

Dependencies and integration points: Used manually or by release/update workflows. Requires `dep` for old repos or Go tooling for modules, plus local `release-tools/verify-go-version.sh`.

Risks: Does nothing silently if neither `Gopkg.toml` nor `go.mod` exists. Go version mismatches only warn, so output may differ across Go versions. Vendor updates can be large and require review.

Test signals: No built-in test run; callers should run project tests and inspect dependency diffs.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/update-vendor.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/util.sh -->
# sources/control-plane/beegfs-csi-driver/release-tools/util.sh

Purpose: Shared shell utility library imported by release tooling. It provides small helpers for dates, arrays, traps, downloads, job waits, joins, sorted-file checks, and terminal colors.

Important APIs/types/functions: `kube::util::sourced_variable`, `kube::util::sortable_date`, `kube::util::array_contains`, `kube::util::trap_add`, `kube::util::download_file`, `kube::util::wait-for-jobs`, `kube::util::join`, and `kube::util::check-file-in-alphabetical-order`. Defines color variables when unset.

Control flow: Functions are passive until sourced and called. `trap_add` prepends a new command to existing traps. `download_file` removes destination, retries curl up to five rounds with curl's own retry count, and reports success/failure. `wait-for-jobs` waits on all background jobs and returns number of failures as status. Color initialization declares readonly variables and marks them as intentionally sourced.

State and persistence: `download_file` writes/removes destination files. `trap_add` mutates shell trap state. Color definitions create readonly shell variables in the caller environment.

Dependencies and integration points: Based on Kubernetes release utility conventions. Uses bash features, curl, diff, sort, awk, and process substitution. Intended to be sourced by other release scripts.

Risks: Requires bash despite some release scripts using `/bin/sh`; this file should only be sourced from bash. `wait-for-jobs` returns failure count, which can exceed portable shell status range if many jobs fail. `download_file` has a typo-like redirection `2&> /dev/null` that is unusual and may not behave as intended in all shells.

Test signals: No direct tests in this subset. Behavior is exercised by scripts that source it.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/util.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/verify-boilerplate.sh -->
# sources/control-plane/beegfs-csi-driver/release-tools/verify-boilerplate.sh

Purpose: CI wrapper that verifies source files contain the expected boilerplate headers.

Important APIs/types/functions: Sets strict bash options, ensures `python` exists by creating an `update-alternatives` link to python3 if missing, locates `TOOLS` and `ROOT`, invokes `boilerplate/boilerplate.py --rootdir --verbose`, and fails if returned file list is non-empty.

Control flow: Creates a temp file and trap cleanup, runs the Python checker into a bash array with `mapfile`, prints each offending file, exits 1 on failures, or prints `Done` on success.

State and persistence: May modify system alternatives by installing `/usr/bin/python` link, which is a significant side effect in CI images. Creates and removes a temp file that is otherwise unused.

Dependencies and integration points: Called by `.prow.sh` and likely `make test` targets. Depends on bash, Python, and `boilerplate.py`.

Risks: Attempting `update-alternatives --install` requires permissions and assumes Debian-like systems. The temp file is not used except cleanup. Because `boilerplate.py` itself exits zero, this wrapper must correctly check output length.

Test signals: Emits offending file paths and exits nonzero when headers are wrong.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/verify-boilerplate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/verify-go-version.sh -->
# sources/control-plane/beegfs-csi-driver/release-tools/verify-go-version.sh

Purpose: Warns when the active Go toolchain version does not match the Go version expected by `release-tools/prow.sh`.

Important APIs/types/functions: Takes one argument, the path/name of a Go binary. Extracts major.minor from `$GO version`, sources `release-tools/prow.sh` to read `CSI_PROW_GO_VERSION_BUILD`, and prints a warning block if versions differ.

Control flow: Validates argument, runs Go version command, parses with sed, sources `prow.sh` with output suppressed, compares major.minor strings, and emits warning text. It does not fail on mismatch.

State and persistence: No file writes. Sourcing `prow.sh` evaluates config defaults in the current shell, but output is redirected for the expected-version read.

Dependencies and integration points: Used by `update-vendor.sh` before module tidy/vendor operations. Requires a local `release-tools/prow.sh` path and a working Go binary.

Risks: Sourcing a large script for one variable can run side-effectful top-level config evaluation and depends on relative working directory. It only compares major.minor, not patch. The warning text contains minor grammar issues but is operationally clear.

Test signals: Human-visible warning when Go version differs; no nonzero exit for mismatch.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/verify-go-version.sh -->
