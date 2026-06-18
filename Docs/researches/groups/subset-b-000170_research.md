# Research: subset-b-000170

Grouped research for the Moby daemon cluster/container executor and daemon command files in subset B. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned per-file output.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/container.go -->
## sources/cloud-native/moby/daemon/cluster/executor/container/container.go

Purpose: converts a SwarmKit `api.Task` into Docker Engine container, host, networking, volume, service-discovery, and event-filter structures. The central type is `containerConfig`, built by `newContainerConfig` and `setTask`; it validates runtime presence, enforces an image for container tasks, validates mounts, indexes task networks, and expands templated container specs against the node description.

Important APIs include `config`, `hostConfig`, `createNetworkingConfig`, `serviceConfig`, `networkCreateRequest`, `volumeCreateRequest`, `eventFilter`, `convertMount`, `getEndpointConfig`, and `ipamConfig` integration through `network.go`. Control flow is mostly pure translation from SwarmKit protobufs to Engine API types: labels merge user spec labels, task annotation labels, then reserved `com.docker.swarm.*` system labels; command and args are mapped into `Entrypoint` and `Cmd`; host-mode ports become exposed ports and bindings; DNS, ulimits, memory, swap, CPU, capabilities, security options, and logging settings flow into `HostConfig`.

State and persistence are indirect. The file mutates `c.task.Spec.Runtime` after template expansion and derives CSI cluster mount host paths from the dependency getter and task volume attachments. It does not persist data itself, but it feeds daemon create/network/service-binding calls that persist Engine resources and libnetwork service records.

Dependencies and integration points are broad: `github.com/moby/swarmkit/v2/api`, Engine API container/mount/network/volume structs, daemon cluster `convert`, executor backends, libnetwork scope, netip parsing helpers, generic resources, and SwarmKit template expansion. Risks include silent skipping of invalid host ports or endpoint addresses, best-effort JSON unmarshal of tmpfs options, possible missed CSI mount path if dependencies are unavailable, map-by-network-name collisions, and security-sensitive mapping of credential specs, SELinux, seccomp, AppArmor, and `no-new-privileges`.

Test signals come from `container_test.go`, which covers isolation conversion, reserved label precedence, credential-spec security options, and tmpfs option conversion. Mount validation behavior is covered in `validate*_test.go`; health/event behavior is covered separately in `health_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/container.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/container_test.go -->
## sources/cloud-native/moby/daemon/cluster/executor/container/container_test.go

Purpose: unit-tests key conversion invariants in `container.go` without requiring a live daemon. It constructs synthetic SwarmKit tasks and calls `containerConfig.hostConfig` or `labels` directly.

Important tests: `TestIsolationConversion` verifies SwarmKit isolation values map to Engine isolation modes; `TestContainerLabels` verifies system labels override user-specified labels in the reserved namespace; `TestCredentialSpecConversion` checks file, registry, and config credential specs become the expected `SecurityOpt` strings; `TestTmpfsConversion` verifies serialized tmpfs options are decoded into Engine mount options.

Control flow is table-driven with subtests. State is in-memory only; nil dependency getters are accepted because tested cases avoid CSI mounts. Dependencies include Engine container and mount API types, SwarmKit API structs, and `gotest.tools` assertions.

Risks captured by the tests are mostly regression risks in compatibility translation. Gaps include no coverage for port binding filtering, service config generation, network endpoint IP parsing, resource limits, and privilege subfields beyond credential specs. These tests are valuable because small translation changes can break existing swarm service behavior or label-based cleanup/status paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/container_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/controller.go -->
## sources/cloud-native/moby/daemon/cluster/executor/container/controller.go

Purpose: implements SwarmKit `exec.Controller` for Docker container tasks. The `controller` owns task lifecycle orchestration through a `containerAdapter`: prepare, start, wait, log streaming, shutdown, terminate, removal, status, and close.

Important APIs are `newController`, `Task`, `ContainerStatus`, `PortStatus`, `Prepare`, `Start`, `Wait`, `Shutdown`, `Terminate`, `Remove`, `Logs`, `Close`, `parseContainerStatus`, `parsePortStatus`, `parsePortMap`, `exitError`, and `checkHealth`. `Prepare` waits for node network attachments and cluster volumes, creates networks and volumes, optionally pulls the image asynchronously, handles pull cancellation/re-entry, and creates the container. `Start` refuses already-started containers, retries missing-network failures by recreating networks, and activates service bindings immediately for containers without healthchecks or after healthy events.

State lives in controller fields: `closed`, `err`, `pulled`, `cancelPull`, and `pullErr`. Shutdown and removal cancel any in-flight pull, deactivate service bindings, wait a gossip convergence delay, stop/remove containers, and clean managed networks. `Wait` races container exit status with health events to annotate non-zero exit errors with `ErrContainerUnhealthy` when known. Logs use a 10 MB/s token bucket and publish SwarmKit log messages with node/service/task context.

Dependencies include containerd errdefs, Engine event/container/network types, libnetwork errors, SwarmKit exec/log APIs, gogo protobuf timestamps, and `golang.org/x/time/rate`. Integration points are the adapter backend, daemon event stream, SwarmKit agent status reporting, service binding activation, and log subscription path.

Risks include event-channel reads that assume the channel keeps yielding, races between inspect and start, intentional background pull context not tied to task context, fixed waits for node attachments/cluster volumes/gossip convergence, health activation depending on event ordering, and log streams blocking if publisher context is not managed correctly. Tests in this subset cover health-event detection and mount/controller creation, but lifecycle integration mostly depends on higher-level daemon/swarm tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/errors.go -->
## sources/cloud-native/moby/daemon/cluster/executor/container/errors.go

Purpose: defines package-level sentinel errors used by the container executor. The exported values are `ErrImageRequired`, `ErrContainerDestroyed`, and `ErrContainerUnhealthy`.

APIs are simple `errors.New` variables. They integrate with `newContainerConfig` for missing images, `controller.Start` when a destroy event arrives before readiness, and `controller.Start`/`Wait`/`checkHealth` when healthchecks report unhealthy. `exitError.Unwrap` can expose the underlying health error to callers using `errors.Is`.

There is no persistent state. The risk is compatibility: callers and tests may match these sentinels, so changing text or replacing variables would alter behavior. Test signal is indirect through `health_test.go`, which expects `ErrContainerUnhealthy`, and through controller lifecycle paths that propagate these values.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/executor.go -->
## sources/cloud-native/moby/daemon/cluster/executor/container/executor.go

Purpose: implements the SwarmKit `exec.Executor` for Moby. It describes the local node to swarmkit, configures ingress and node network attachments, chooses the right task controller, propagates network encryption keys, and exposes dependency managers for secrets, configs, and volumes.

Important types and APIs: `executor`, `NewExecutor`, `Describe`, `Configure`, `Controller`, `SetNetworkBootstrapKeys`, `Secrets`, `Configs`, `Volumes`, and `sortedPlugins`. `Describe` queries daemon system info, normalizes labels, merges v1 and enabled v2 plugin capabilities, adds built-in overlay networking, queries CSI node info, and stores an `api.NodeDescription` under a mutex. `Configure` reads swarm node attachments, sets up or releases ingress, tracks removed or changed attachment IPs, deletes stale managed load-balancer networks when possible, updates the previous node object, and resets the backend attachment store.

Controller selection is runtime-dependent. Network attachment tasks use `newNetworkAttacherController`; generic plugin-runtime tasks require experimental mode and use the plugin controller; container tasks use `newController`; unsupported runtimes return errors. State includes backend references, a SwarmKit dependency manager, cached node description, and cached node object for attachment-diffing.

Dependencies include daemon executor backends, plugin backend, cluster convert package, libnetwork, network encryption types, SwarmKit agent/dependency/template APIs, and plugin discovery. Risks include ignored CSI node-info errors, malformed attachment entries that are skipped, stale `nodeObj` assumptions, partial cleanup when active endpoints prevent removal, and runtime behavior depending on experimental mode. Test coverage here is indirect; this file is exercised by swarm integration paths rather than direct unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/executor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/health_test.go -->
## sources/cloud-native/moby/daemon/cluster/executor/container/health_test.go

Purpose: validates that `controller.checkHealth` reacts only to unhealthy container health events for the matching task/container. It is Unix-only through `!windows`.

The test constructs an in-memory daemon event service, a task with swarm task labels, and a controller. It starts `checkHealth` in a goroutine, logs synthetic container events, and asserts that running, healthy, and die events are ignored while `ActionHealthStatusUnhealthy` produces `ErrContainerUnhealthy`.

State is in-memory channels and event subscriptions. Integration points include daemon `EventsService`, `LogContainerEvent`, Engine event actions, and controller event filtering by container name. Risks covered are false-positive health failures and missed unhealthy events. Gaps include service-binding activation on healthy events, behavior when the event stream closes, and shutdown after unhealthy detection.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/health_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/network.go -->
## sources/cloud-native/moby/daemon/cluster/executor/container/network.go

Purpose: converts SwarmKit `api.IPAMConfig` into Engine `network.IPAMConfig` while collecting parse errors. The single API is `ipamConfig`.

Control flow parses subnet and range with `netiputil.MaybeParseCIDR`, parses gateway with `MaybeParseAddr`, unmaps the gateway address, and returns `errors.Join` of all parse failures so callers can log a complete validation result. `container.go` uses this when building swarm network creation requests and `executor.go` uses it for ingress setup.

There is no persistent state. Dependencies are Engine network API types, SwarmKit IPAM structs, and daemon netip utilities. Risk is that callers often append the returned config even when errors are logged, so malformed fields may produce partially populated network create requests. Test coverage for this helper is indirect through network creation paths; no direct tests are in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/network.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/validate.go -->
## sources/cloud-native/moby/daemon/cluster/executor/container/validate.go

Purpose: validates SwarmKit mount specs before a task is accepted by `newContainerConfig`. The API is `validateMounts`.

Rules are type-specific: non-named-pipe targets must be absolute; bind sources must be absolute; volume sources must not be absolute; tmpfs sources must be empty; named pipe sources must be non-empty; cluster mounts are accepted; unknown mount types are rejected. This protects later Engine create behavior where absolute source paths can otherwise make volume and bind semantics ambiguous.

State is none. Dependencies are `filepath` and SwarmKit `api.Mount`. Risks are platform-specific path semantics because `filepath.IsAbs` follows the build target, and named-pipe target validation is intentionally looser. Tests in `validate_test.go`, `validate_unix_test.go`, and `validate_windows_test.go` cover the major rules.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/validate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/validate_test.go -->
## sources/cloud-native/moby/daemon/cluster/executor/container/validate_test.go

Purpose: tests mount validation through controller construction, which exercises `newContainerConfig` and `validateMounts` in a realistic path.

Important helpers and tests: `newTestControllerWithMount` creates a synthetic task with one mount; `TestControllerValidateMountBind` checks relative bind source rejection and absolute bind source acceptance even if nonexistent; `TestControllerValidateMountVolume` rejects absolute volume sources; `TestControllerValidateMountTarget` rejects relative targets; `TestControllerValidateMountTmpfs` rejects non-empty tmpfs sources; `TestControllerValidateMountInvalidType` rejects unknown mount types.

State is local temporary directories and synthetic daemon/task structs. Dependencies include daemon, random string IDs, SwarmKit API types, and platform constants from `validate_unix_test.go` or `validate_windows_test.go`. Risks covered are API ambiguity and cross-platform absolute-path handling. Gaps include cluster mounts, bind option validation, and deeper Engine-side mount availability.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/validate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/validate_unix_test.go -->
## sources/cloud-native/moby/daemon/cluster/executor/container/validate_unix_test.go

Purpose: supplies Unix path constants for the shared mount validation tests. The build tag is `!windows`.

APIs are package constants `testAbsPath` and `testAbsNonExistent`, set to Unix absolute paths. There is no control flow or state. The integration point is `validate_test.go`, where the constants make `filepath.IsAbs` checks target Unix semantics.

Risk is low but important for portability: without platform constants, shared validation tests could pass with paths that are not absolute on the active GOOS. Test signal is the shared test file itself.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/validate_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/validate_windows_test.go -->
## sources/cloud-native/moby/daemon/cluster/executor/container/validate_windows_test.go

Purpose: supplies Windows path constants and the Windows-only named-pipe mount validation test. The build tag is `windows`.

Important content: `testAbsPath` and `testAbsNonExistent` use drive-letter absolute paths, and `TestControllerValidateMountNamedPipe` verifies that named-pipe mounts reject an empty source even when the target is a pipe path. State is synthetic only.

Dependencies are SwarmKit API types and shared `newTestControllerWithMount`. Risks covered are Windows-specific mount semantics and the named-pipe exception to absolute target validation. Gaps include validating named-pipe target format beyond the empty-source rule.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/executor/container/validate_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/filters.go -->
## sources/cloud-native/moby/daemon/cluster/filters.go

Purpose: converts daemon filter arguments into SwarmKit list request filters for nodes, tasks, secrets, and configs. It also validates accepted filter keys.

Important APIs are `newListNodesFilters`, `newListTasksFilters`, `newListSecretsFilters`, and `newListConfigsFilters`. Node filters support name, id, label, role, membership, and node.label; role and membership strings are uppercased and mapped to SwarmKit enums. Task filters support name, id, label, service, node, desired-state, internal `_up-to-date`, and runtime, with an optional transform callback used by `tasks.go` to resolve service/node names to IDs and add default runtimes. Secret and config filters accept name/id/label, with secrets also accepting `names`.

State is none; filter arguments may be mutated by the transform callback. Dependencies include daemon internal filters and SwarmKit API protobuf filter structs. Risks include enum string mismatch, API-visible validation errors for unsupported filters, and `convertKVStringsToMap` treating labels without `=` as keys with empty values. Tests cover accepted and rejected secret/config filter keys, while node/task enum paths are less directly tested here.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/filters.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/filters_test.go -->
## sources/cloud-native/moby/daemon/cluster/filters_test.go

Purpose: verifies filter validation for list secrets and list configs. It focuses on accepted filter names and rejection of unsupported filter keys.

`TestNewListSecretsFilters` covers `name`, `id`, `label`, `names`, combined filters, and invalid `nonexist`. `TestNewListConfigsFilters` covers `name`, `id`, `label`, combined filters, and invalid `nonexist`. Control flow is direct loops over valid and invalid `filters.Args`.

State is none. Dependencies are daemon internal filters and the functions in `filters.go`. The tests signal that the API contract for these filters is intentionally narrow. Gaps include checking converted protobuf fields, label map conversion, node/task filters, enum validation, and transform callback behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/filters_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/helpers.go -->
## sources/cloud-native/moby/daemon/cluster/helpers.go

Purpose: centralizes lookup helpers for SwarmKit cluster objects by ID, name, or ID prefix. It also wraps not-found and ambiguous-match errors in daemon error definitions where appropriate.

Important APIs: `getSwarm`, `getNode`, `getService`, `getTask`, `getSecret`, `getConfig`, `getNetwork`, and `getVolume`. The common control flow is: try direct `Get*` by full ID, list by exact name, list by ID prefix, reject no matches, reject multiple matches as ambiguous, and return the single object. `getService` can re-fetch with `InsertDefaults`; `getNetwork` carries optional appdata for status requests; `getVolume` uses volume-specific not-found wrapping.

State is remote SwarmKit store state accessed through `swarmapi.ControlClient`; no local persistence. Integration points are all cluster CRUD files and log selector resolution. Risks include treating any direct get error as a reason to fall back to list, inconsistent not-found wrapping for networks compared with other object types, extra RPCs for defaults, and ambiguity behavior depending on SwarmKit prefix matches. Test coverage is indirect through higher-level API tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/internal/runtime/convert.go -->
## sources/cloud-native/moby/daemon/cluster/internal/runtime/convert.go

Purpose: converts Docker API swarm plugin runtime specs to and from the generated internal protobuf `PluginSpec` used as a generic runtime payload.

Important APIs are `FromAPI`, `ToAPI`, `privilegesFromAPI`, and `privilegesToAPI`. Control flow copies name, remote reference, disabled flag, environment values, and repeated runtime privileges between API structs and protobuf structs. The conversion preserves order and does not perform validation or deep normalization.

State is none. Dependencies are `github.com/moby/moby/api/types/swarm` and generated types from `plugin.pb.go`. Integration points are service create/update paths for `RuntimePlugin` and the plugin controller path selected by the container executor. Risks include nil privilege entries causing panics if ever present, lack of validation, and schema drift between API runtime spec and proto fields. No direct tests are in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/internal/runtime/convert.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/internal/runtime/gen.go -->
## sources/cloud-native/moby/daemon/cluster/internal/runtime/gen.go

Purpose: records the generation command for the runtime plugin protobuf bindings. It contains a `go:generate` directive for `protoc --gogofaster_out=import_path=runtime:. plugin.proto`.

There are no exported APIs, control flow, or runtime state. Its integration point is developer workflow: regenerating `plugin.pb.go` after `plugin.proto` changes. Risk is toolchain drift; if protoc/gogo versions differ, generated marshal/unmarshal behavior or formatting may change. Test signal is compile-time only through generated type consumers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/internal/runtime/gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/internal/runtime/plugin.pb.go -->
## sources/cloud-native/moby/daemon/cluster/internal/runtime/plugin.pb.go

Purpose: generated gogo/protobuf implementation for the plugin runtime payload defined in `plugin.proto`. It should not be edited by hand.

Important generated APIs include structs `PluginSpec` and `PluginPrivilege`, getter methods, proto registration, descriptor data, `Marshal`, `MarshalTo`, `MarshalToSizedBuffer`, `Size`, and `Unmarshal` routines. Control flow is standard generated protobuf serialization: fields are encoded in reverse-order sized buffers for marshal and decoded with unknown-field skipping for unmarshal.

State is per-message struct fields only. Dependencies are `github.com/gogo/protobuf/proto`, `fmt`, `io`, and math helpers. Integration points are `convert.go` and any generic runtime payload encode/decode path for swarm plugin services. Risks include generated code being stale relative to `plugin.proto`, manual edits being overwritten, and memory/compatibility assumptions from old gogo protobuf code. Test signal is compile-time compatibility and any service/plugin runtime tests outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/internal/runtime/plugin.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/internal/runtime/plugin.proto -->
## sources/cloud-native/moby/daemon/cluster/internal/runtime/plugin.proto

Purpose: defines the protobuf schema for Docker plugin runtime specs stored in SwarmKit generic task payloads.

The schema has `PluginSpec` with fields `name`, `remote`, repeated `PluginPrivilege privileges`, `disabled`, and repeated `env`; and `PluginPrivilege` with `name`, `description`, and repeated `value`. This mirrors `swarm.RuntimeSpec` and `swarm.RuntimePrivilege` enough for plugin service creation and controller execution.

There is no runtime state. Integration points are `gen.go`, generated `plugin.pb.go`, `convert.go`, service create/update validation for plugin runtime, and the plugin controller. Risks are backward-compatibility of field numbers and limited schema expressiveness if plugin runtime options expand. Test signal is indirect through generated-code compilation and plugin runtime behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/internal/runtime/plugin.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/listen_addr.go -->
## sources/cloud-native/moby/daemon/cluster/listen_addr.go

Purpose: resolves and validates swarm listen, advertise, data-path, default address pool, and data-path port settings. It also implements generic system address discovery used by platform-specific wrappers.

Important APIs: `resolveListenAddr`, `(*Cluster).resolveAdvertiseAddr`, `validateDefaultAddrPool`, `getDataPathPort`, `resolveDataPathAddr`, `resolveInterfaceAddr`, `resolveInputIPAddr`, `(*Cluster).resolveSystemAddrViaSubnetCheck`, `listSystemIPs`, and `errMultipleIPs`. Control flow favors interface-name resolution before literal IP parsing, allows unspecified listen addresses but rejects unspecified advertise/data-path addresses, fills missing advertise ports from listen ports, validates overlay default subnet sizes, and restricts VXLAN data-path ports to 1024-49151 with default 4789.

State is the host network interface table and Docker-managed subnets from `NetworkSubnetsProvider`. Integration points are `swarm.go` init/join request handling and daemon config `SwarmDefaultAdvertiseAddr`. Risks include ambiguous multi-address hosts, platform-specific interface behavior, Docker-managed subnet exclusion causing unexpected no-address results, and user-facing config errors from address parsing. Tests are not in this subset, so regressions are mostly caught by swarm integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/listen_addr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/listen_addr_linux.go -->
## sources/cloud-native/moby/daemon/cluster/listen_addr_linux.go

Purpose: Linux-specific implementation of `(*Cluster).resolveSystemAddr`. It uses netlink via daemon `nlwrap` to prefer real device interfaces and falls back to subnet-check discovery when running in environments where interfaces are not type `device`.

Control flow lists links, skips non-device or down interfaces, lists addresses, skips non-global-unicast addresses, favors IPv4 over IPv6 per interface, rejects multiple usable addresses on one or multiple interfaces, and returns `errNoIP` if active devices exist but none have usable addresses. If no suitable device is found, it calls `resolveSystemAddrViaSubnetCheck`, which helps containerized dockerd cases where NICs appear as veths.

State is host network interface state. Dependencies are `nlwrap`, `vishvananda/netlink`, and shared address error helpers. Risks include netlink failures, interface type assumptions, ambiguity on multi-homed hosts, and different behavior from non-Linux fallback. No direct tests are in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/listen_addr_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/listen_addr_others.go -->
## sources/cloud-native/moby/daemon/cluster/listen_addr_others.go

Purpose: non-Linux implementation of `(*Cluster).resolveSystemAddr`. It delegates directly to `resolveSystemAddrViaSubnetCheck`.

There are no additional APIs or local state beyond the method. The integration point is swarm init/join advertise address autodetection on non-Linux platforms. Risk is that non-Linux platforms do not get the Linux netlink device filtering behavior and rely on the generic `net.Interfaces` path. Test coverage is indirect.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/listen_addr_others.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/networks.go -->
## sources/cloud-native/moby/daemon/cluster/networks.go

Purpose: implements cluster-managed network inspection, listing, creation/removal, service network ID population, and attach/detach coordination for swarm network attachments.

Important APIs: `GetNetworks`, `GetNetworkSummaries`, `listNetworks`, `GetNetwork`, `GetNetworksByName`, `UpdateAttachment`, `WaitForDetachment`, `AttachNetwork`, `DetachNetwork`, `CreateNetwork`, `RemoveNetwork`, and `populateNetworkID`. Listing fetches from SwarmKit and applies daemon-side network filter semantics because SwarmKit filters are more limited. Optional status is requested through `netextra.GetNetworkExtraOptions` appdata. Attachment control uses the cluster `attachers` map with wait channels to bridge manager resource allocation and local network config delivery.

State includes remote SwarmKit networks and local `Cluster.attachers` entries keyed by target/container ID. Attach flow stores channels, requests allocation from the agent resource allocator, waits for `UpdateAttachment`, caches the returned `NetworkingConfig`, and releases allocation on timeout. Detach flow wakes waiters and calls `DetachNetwork`.

Dependencies include Engine network types, cluster convert/netextra packages, daemon network filters, SwarmKit control and agent resource allocator APIs, and daemon backend network lookup. Risks include channel deadlocks, timeout cleanup failures, duplicate attach notices, predefined network ID translation, and mismatch between Engine substring filter behavior and SwarmKit exact/prefix filters. Tests are indirect.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/networks.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/noderunner.go -->
## sources/cloud-native/moby/daemon/cluster/noderunner.go

Purpose: manages the lifecycle of a SwarmKit node inside dockerd, including startup, readiness, control-socket changes, store watches, reconnects, persistent config, and state reporting.

Important types and APIs: `nodeRunner`, `nodeStartConfig`, `Ready`, `Start`, `start`, `handleControlSocketChange`, `watchClusterEvents`, `handleReadyEvent`, `handleNodeExit`, `Stop`, `State`, `enableReconnectWatcher`, and `nodeState` helpers. Startup builds a `swarmnode.Config` with control socket, remote listen/advertise addresses, network allocator config, state dir, join token, container executor, raft ticks, unlock key, plugin getter, and network provider. It starts the SwarmKit node, saves persistent state, then launches goroutines for node exit, readiness, and control socket updates.

Persistent state is `nodeStartConfig` serialized by `savePersistentState` in the swarm state dir. Runtime state is guarded by `nodeRunner.mu`: current node, gRPC connection/clients, error, ready/done channels, reconnect delay, and reconnect cancel function. Cluster watch messages are forwarded into `cluster.watchStream`.

Dependencies include container executor, cluster convert, libnetwork cluster events, cnmallocator provider, SwarmKit node/control/watch APIs, gRPC status handling, and network allocator config. Risks include reconnect loops after promotion/demotion failures, stale join addresses, goroutine/channel lifetime complexity, persistent state consistency during join, and watch-stream backpressure. Tests are mostly integration-level outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/noderunner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/nodes.go -->
## sources/cloud-native/moby/daemon/cluster/nodes.go

Purpose: implements node list, inspect, update, and remove operations for the swarm backend API.

Important APIs: `GetNodes`, `GetNode`, `UpdateNode`, and `RemoveNode`. Control flow validates/list-builds filters with `newListNodesFilters`, calls SwarmKit control RPCs under `lockedManagerAction`, converts returned nodes with `convert.NodeFromGRPC`, resolves node names/IDs through `getNode`, converts API node specs to protobuf specs, applies versioned updates, and removes nodes with optional force.

State is remote SwarmKit node store state; there is no local persistence. Dependencies are daemon swarm backend option types, cluster convert helpers, errdefs, SwarmKit control client, and gRPC receive-size limits. Risks include manager-availability requirements from `lockedManagerAction`, ambiguous name/prefix resolution, and update conflicts through version mismatches. Test coverage is indirect.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/nodes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/provider/network.go -->
## sources/cloud-native/moby/daemon/cluster/provider/network.go

Purpose: defines lightweight provider data structures used by the container executor and daemon cluster backend for swarm-managed network creation and service binding.

Types: `NetworkCreateRequest` embeds Engine `network.CreateRequest` with a swarm network ID; `NetworkCreateResponse` returns an ID; `VirtualAddress` stores IPv4/IPv6 service VIPs; `PortConfig` stores service port metadata; `ServiceConfig` stores service ID/name, aliases, virtual addresses, and exposed ingress ports.

There is no control flow or persistence. Integration points include `container.go` network/service config generation and backend methods that create managed networks or activate service bindings. Risks are schema drift with libnetwork/backend expectations and sparse IPv6 use because current service config generation only fills IPv4 VIPs. Tests are indirect.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/provider/network.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/secrets.go -->
## sources/cloud-native/moby/daemon/cluster/secrets.go

Purpose: implements swarm secret CRUD operations for the daemon swarm backend.

Important APIs: `GetSecret`, `GetSecrets`, `CreateSecret`, `RemoveSecret`, and `UpdateSecret`. Control flow resolves secrets through `getSecret`, validates list filters through `newListSecretsFilters`, lists via SwarmKit with a large receive limit, converts secret specs and objects through `convert`, and sends versioned update/remove/create requests to the SwarmKit control client.

State is SwarmKit manager store state. Dependencies include Engine swarm API types, cluster convert package, daemon swarm backend option types, SwarmKit control client, and gRPC receive-size settings. Risks include manager lock/availability requirements, ambiguous name/prefix lookup, update version conflicts, and limited direct validation in this file. Tests in `filters_test.go` cover accepted filter keys; CRUD behavior is integration-tested elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/secrets.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/services.go -->
## sources/cloud-native/moby/daemon/cluster/services.go

Purpose: implements service list/inspect/create/update/remove/logs and image digest pinning for swarm services.

Important APIs: `GetServices`, `GetService`, `CreateService`, `UpdateService`, `RemoveService`, `ServiceLogs`, `convertSelector`, `imageWithDigestString`, and `digestWarning`. List filters accept name/id/label/mode/runtime and default to container runtime; service status is fetched through a separate `ListServiceStatuses` call. Create/update populate network IDs, convert specs, reject network-attachment runtime for services, validate plugin runtime requirements, carry registry auth, optionally pin image tags to digests by querying registries, and invoke SwarmKit create/update with version and rollback options.

Service logs translate Docker log options to SwarmKit log subscription options, including tail semantics, stream selection, since timestamp conversion, selector resolution by service/task, and conversion back to backend log messages with context attributes. State is remote SwarmKit service/task/log state; registry auth may be preserved from current or previous specs during update.

Dependencies include auth config decoding, registry repositories, swarm API types, convert package, backend log options, errdefs, SwarmKit control/log clients, gRPC size limits, and OpenContainers digest. Risks include slow registry lookup requiring context replacement, warning-only digest pin failures that can lead to nodes pulling different tag contents, registry-auth preservation complexity, log stream blocking/cancellation, and runtime-specific validation gaps. Tests are mostly indirect; this subset does not include direct service tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/services.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/swarm.go -->
## sources/cloud-native/moby/daemon/cluster/swarm.go

Purpose: implements top-level swarm lifecycle and status APIs: init, join, inspect, update, unlock, leave, info, status, request validation, initial spec merge, and cleanup of node-owned containers on leave.

Important APIs: `Init`, `Join`, `Inspect`, `inspect`, `Update`, `GetUnlockKey`, `UnlockSwarm`, `Leave`, `Info`, `Status`, `validateAndSanitizeInitRequest`, `validateAndSanitizeJoinRequest`, `validateAddr`, `initClusterSpec`, and `listContainerForNode`. Init validates and resolves listen/advertise/data-path addresses, default address pools, and data-path port, starts a `nodeRunner`, waits for readiness, clears persistent state on failed fresh init, and merges user spec into the initial cluster spec. Join validates remote addrs, starts a node runner with join token, waits with timeout, and clears state on failure.

State is `Cluster.nr`, guarded by `controlMutex` and `mu`, plus persistent swarm state managed through node runner utilities. Unlock restarts the node runner with a parsed unlock key. Leave enforces manager quorum safeguards unless forced, stops the node, removes containers labeled for this node, clears swarm state, and notifies the daemon backend.

Dependencies include address resolution helpers, convert package, swarmkit control/CA APIs, encryption key formatting, manager quorum helpers, daemon backend container removal, errdefs, and gRPC. Risks include quorum-loss decisions, state cleanup after partial failures, address autodetection ambiguity, locked-swarm edge cases, and synchronous waits on node readiness. Test coverage here is largely integration-level.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/swarm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/tasks.go -->
## sources/cloud-native/moby/daemon/cluster/tasks.go

Purpose: implements task list and inspect operations for the swarm backend.

Important APIs: `GetTasks` and `GetTask`. `GetTasks` builds a transform callback that resolves service filters and node filters to SwarmKit IDs, defaults runtime filtering to container plus empty runtime when no runtime filter is supplied, validates/builds task filters with `newListTasksFilters`, lists tasks through SwarmKit with a large receive limit, and converts each task with `convert.TaskFromGRPC`. `GetTask` resolves a single task with `getTask` and converts it.

State is remote SwarmKit task state. Dependencies include daemon internal filters, swarmbackend option types, cluster helper lookups, convert package, SwarmKit control client, and gRPC receive-size settings. Risks include mutation of filter args during transform, lookup failures for service/node names, runtime default behavior hiding non-container runtimes unless requested, and version/manager availability handled by `lockedManagerAction`. Tests are indirect.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/tasks.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/utils.go -->
## sources/cloud-native/moby/daemon/cluster/utils.go

Purpose: provides small shared utilities for filter conversion, swarm persistent-state I/O, state cleanup, and manager quorum calculations.

Important APIs: `convertKVStringsToMap`, `loadPersistentState`, `savePersistentState`, `clearPersistentState`, `removingManagerCausesLossOfQuorum`, and `isLastManager`. Persistent state loading reads the swarm state file, verifies the swarm node certificate exists, clears stale state if the certificate is missing, and unmarshals `nodeStartConfig`. Saving marshals config JSON and writes atomically with mode `0600`. Clearing removes all entries under the swarm state root while preserving the root directory inode.

Dependencies include JSON, filesystem operations, `atomicwriter`, and `nodeStartConfig`. Integration points are node runner start/restart, swarm init/join/leave/unlock, and filter-building code. Risks include destructive state cleanup, stale state when certificate checks fail, ignoring errors from some callers, labels without `=` becoming empty-value filters, and quorum helper off-by-one sensitivity. Tests are indirect.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/volumes.go -->
## sources/cloud-native/moby/daemon/cluster/volumes.go

Purpose: implements cluster volume CRUD operations against SwarmKit volume APIs.

Important APIs: `GetVolume`, `GetVolumes`, `CreateVolume`, `RemoveVolume`, and `UpdateVolume`. Control flow resolves volumes with `getVolume`, lists and converts all volumes, creates a volume from an Engine create request via `convert.VolumeCreateToGRPC`, then fetches the created volume for a complete response. Remove honors `force` by treating not-found as success. Update currently changes only availability, mapping Engine availability values to SwarmKit enums before a versioned update.

State is remote SwarmKit volume state; no local persistence in this file. Dependencies include containerd errdefs, Engine volume API types, daemon volume backend option types, convert package, errdefs, SwarmKit control client, and gRPC size limits. Risks include create succeeding but follow-up get failing, update using `nameOrID` as `VolumeID` after resolving `v`, limited update surface, and force-remove semantics hiding concurrent deletion. Tests are indirect.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/cluster/volumes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/cobra.go -->
## sources/cloud-native/moby/daemon/command/cobra.go

Purpose: configures root Cobra command presentation and flag error handling for dockerd.

Important APIs: `SetupRootCommand`, `FlagErrorFunc`, `wrappedFlagUsages`, plus `usageTemplate` and `helpTemplate`. Setup registers a template function, sets usage/help/version templates, installs a Docker CLI-like flag error function, adds persistent `--help/-h`, and marks the shorthand deprecated. `FlagErrorFunc` wraps parse errors in `StatusError` with status code 125 and a `See '<cmd> --help'` message, including usage for commands with subcommands.

State is Cobra command configuration. Dependencies are `github.com/spf13/cobra` and terminal width detection. Risks include terminal width errors falling back to 80 columns, template changes affecting UX and tests, and status-code compatibility with Docker CLI behavior. Tests are not in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/cobra.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/config.go -->
## sources/cloud-native/moby/daemon/command/config.go

Purpose: installs daemon-wide, cross-platform configuration flags on a pflag set and provides a generic string flag adapter.

Important APIs: `installCommonConfigFlags` and `stringVar[T]`. The flag installer wires registry mirrors, insecure registries, storage opts, authorization plugins, exec opts, pid/data/exec roots, containerd options, feature flags, network defaults, DNS, host-gateway IPs, labels, log driver/options, transfer concurrency, shutdown timeout, swarm default advertise address, experimental mode, metrics, generic resources, containerd namespaces, default runtime, proxy settings, CDI dirs, NRI options, and deprecated `--restart`.

State is mutation of the passed `config.Config` and `pflag.FlagSet`. Dependencies include daemon config, opts validators, registry validators, internal named option helpers, containerd log output format, and runtime GOOS for hiding Windows MTU. Risks include flag/config merge conflicts later in `loadDaemonCliConfig`, hidden/deprecated flag compatibility, map/list option aliasing, and permissive `stringVar` accepting any string until config validation. Tests in this subset cover Unix `--default-shm-size` through platform-specific flag installation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/config_unix.go -->
## sources/cloud-native/moby/daemon/command/config_unix.go

Purpose: installs Unix-specific dockerd configuration flags after common flags.

Important API: `installConfigFlags`. It adds runtime registration, socket group, storage driver, SELinux, default ulimits, bridge networking and firewall flags, default gateways, publishing host IP, userland proxy settings, cgroup parent, userns remap, live restore, init path, CPU real-time period/runtime, seccomp profile, default shm size, no-new-privileges, default IPC mode, default address pools, firewall backend, rootless mode, and default cgroup namespace.

State is mutation of the config object and flag set. Dependencies include daemon config, platform opts, `net`, and pflag. Risks include many flags feeding later validation and platform setup, especially userns remap, cgroup v2 CPU RT support, rootless behavior, and bridge/network defaults. `config_unix_test.go` confirms default shm size parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/config_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/config_unix_test.go -->
## sources/cloud-native/moby/daemon/command/config_unix_test.go

Purpose: Unix-only test for parsing the `--default-shm-size` daemon flag.

`TestDaemonParseShmSize` creates a pflag set and default config, installs Unix config flags, asserts the default shared memory size is 64 MiB, sets `default-shm-size` to `128M`, and asserts the config value updates to 128 MiB.

State is local config mutation. Dependencies are daemon config, pflag, and gotest assertions. The test protects a visible CLI compatibility default and parser behavior. Gaps include invalid size inputs and other Unix flags.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/config_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/config_windows.go -->
## sources/cloud-native/moby/daemon/command/config_windows.go

Purpose: installs Windows-specific dockerd configuration flags and defines Windows certificate-directory behavior.

Important APIs: `installConfigFlags` and `configureCertsDir`. It installs common flags, then Windows bridge fixed CIDR, virtual switch bridge name, and named-pipe access group. `configureCertsDir` is a no-op on Windows.

State is config and flag-set mutation only. Dependencies are daemon config and pflag. Risks include smaller Windows flag surface than Unix, compatibility of long-standing but platform-specific bridge/group flags, and no-op cert directory behavior differing from Unix implementations outside this subset. Tests are indirect.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/config_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/daemon.go -->
## sources/cloud-native/moby/daemon/command/daemon.go

Purpose: orchestrates dockerd startup, runtime configuration, API serving, reload, shutdown, BuildKit, cluster startup, listener/TLS setup, managed containerd, logging, tracing, proxy environment, middleware, routers, and CDI enablement.

Important types and APIs: `daemonCLI`, `newDaemonCLI`, `(*daemonCLI).start`, `setOTLPProtoDefault`, `initBuildkit`, `reloadConfig`, `stop`, `shutdownDaemon`, `loadDaemonCliConfig`, `defaultAPISocketPath`, `normalizeHosts`, `buildRouters`, `initMiddlewares`, `getContainerdDaemonOpts`, `newAPIServerTLSConfig`, `checkTLSAuthOK`, `loadListeners`, `createAndStartCluster`, `validateAuthzPlugins`, `systemContainerdRunning`, `configureDaemonLogs`, `configureProxyEnv`, `overrideProxyEnv`, `initializeContainerd`, and `cdiEnabled`.

Control flow is staged. Config is loaded/merged/validated, TLS config is built, system requirements are checked, proxy/logging/rootless settings are applied, daemon roots and pidfile are created, listeners are opened, containerd is detected or started, signal traps and HTTP shutdown are prepared, tracing/CDI/GPU/plugin store/middleware are initialized, `daemon.NewDaemon` starts the core daemon, metrics and cluster start, swarm containers restart, BuildKit starts, routers and gRPC are wired, API listeners serve, systemd readiness is sent, and shutdown stops cluster processing, daemon, BuildKit, context, API, containerd, and tracing.

State includes `daemonCLI` fields, daemon config, pidfile, daemon root/exec root, managed containerd address, plugin store, cluster object, API TLS config, authz middleware, BuildKit state, OTEL globals, proxy environment variables, and HTTP server goroutines. Persistent behavior includes config-file merge, pidfile lifecycle, CDI spec directory filtering, swarm state through `createAndStartCluster`, and daemon data root setup.

Dependencies are extensive across daemon packages, BuildKit, containerd, TLS, listeners, routers, authorization, OpenTelemetry/OpenCensus, CDI, rootless/homedir, pflag, and system runtime. Risks include startup ordering regressions, unauthenticated TCP listener warnings and future hard-fail behavior, context reuse after registry/containerd operations, config reload partial application, shutdown timeouts, userns/containerd-snapshotter incompatibility, CDI permission filtering, proxy env override side effects, and broad cross-platform differences. Tests in this subset cover Linux listener activation and userns snapshotter conflict; many other paths depend on integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/daemon.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/daemon_freebsd.go -->
## sources/cloud-native/moby/daemon/command/daemon_freebsd.go

Purpose: provides FreeBSD-specific no-op implementations for daemon readiness/reload/stopping notifications and CPU real-time validation.

APIs: `preNotifyReady`, `notifyReady`, `notifyReloading`, `notifyStopping`, and `validateCPURealtimeOptions`. Notification methods do nothing, `notifyReloading` returns an empty completion callback, and CPU real-time options are accepted as no-op by returning nil.

State is none. Integration point is the platform abstraction used by `daemon.go` startup and reload paths. Risk is platform behavior divergence: systemd notification and cgroup CPU real-time checks are intentionally absent on FreeBSD. Tests are indirect/compile-time.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/daemon_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/daemon_linux.go -->
## sources/cloud-native/moby/daemon/command/daemon_linux.go

Purpose: implements Linux-specific daemon platform setup, systemd notifications, and CPU real-time option validation.

Important APIs: `setPlatformOptions`, `preNotifyReady`, `notifyReady`, `notifyStopping`, `notifyReloading`, and `validateCPURealtimeOptions`. `setPlatformOptions` handles user namespace remapping by deriving remapped containerd namespaces, rejecting explicitly enabled containerd snapshotter, and otherwise disabling the snapshotter feature with a warning. Notifications use systemd `SdNotify` for ready, stopping, and reloading states. CPU real-time options are rejected on cgroup v2 and on kernels without CPU RT support.

State is mutation of daemon config features and containerd namespaces, plus systemd notification side effects. Dependencies include containerd cgroups, systemd daemon package, daemon remap helpers, sysinfo, and config. Risks include compatibility of userns remap with snapshotter, cgroup mode detection, and readiness/reload signaling correctness. `daemon_linux_test.go` covers snapshotter/userns behavior; listener tests also exercise Linux-specific socket activation through common `loadListeners`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/daemon_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/daemon_linux_test.go -->
## sources/cloud-native/moby/daemon/command/daemon_linux_test.go

Purpose: Linux-specific tests for listener socket activation and userns remap interaction with containerd snapshotter.

`TestLoadListenerNoAddr` uses a two-phase `reexec` setup to create a file descriptor, set `LISTEN_PID`/`LISTEN_FDS`, exec into a child, call `loadListeners` with `fd://`, and assert no error. This approximates systemd socket activation more accurately than running in one test process. `TestC8dSnapshotterWithUsernsRemap` is table-driven and checks that no-remap leaves config unchanged, userns remap without explicit snapshotter disables `containerd-snapshotter` and remaps containerd namespaces, explicit snapshotter plus userns returns the expected error, and explicit snapshotter without remap stays enabled.

State includes process environment, a temporary inherited Unix socket fd, reexec child process output, and mutated daemon config structs. Dependencies include unix syscalls, reexec, config, JSON, go-cmp, and gotest assertions. Risks covered are socket activation regressions and an important storage/userns incompatibility. Gaps include TCP/unix listeners without addresses and deeper rootless/containerd startup behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/daemon_linux_test.go -->
