# sources/cloud-native/moby/api/docs/v1.52.yaml lines 7900-13627

## Chunk Scope

This chunk covers the end of the `definitions` block and the complete `paths:` block for Docker Engine API v1.52. It starts with volume topology/capacity fields and `ImageManifestSummary`, then defines HTTP operations for containers, images/build, system/auth/events, exec, volumes, networks, plugins, swarm, nodes, services, tasks, secrets, configs, distribution inspection, and interactive sessions.

The file is an OpenAPI/Swagger contract, so the important "functions" in this chunk are the `operationId` values, schemas referenced through `$ref`, media types, parameters, status codes, and streaming protocol descriptions that downstream clients, generated SDKs, and daemon route tests depend on.

## Purpose

This section is the public REST contract for the daemon control plane. It maps Docker Engine concepts to HTTP routes and documents:

- CRUD and lifecycle control for local resources: containers, images, volumes, networks, plugins, and exec instances.
- Cluster/swarm resources and state transitions: nodes, swarm membership, services, tasks, secrets, and configs.
- Streaming and connection-upgrade APIs used by logs, attach, stats, build, image create/push, service/task logs, and sessions.
- Error and conflict semantics through consistent `ErrorResponse` references and status codes.
- Optimistic concurrency for swarm, node, service, secret, and config updates through required `version` query parameters.

Because this is the `v1.52.yaml` contract, consumers can use it as the precise compatibility surface for API clients, CLI tests, generated documentation, and daemon handler conformance.

## Important Types And Schemas

- `Topology` is a CSI-style topology map with `Segments` as string key/value pairs. It is used by volume placement/accessibility-related schema from the preceding definition block.
- Volume capacity and scheduling fields just before `Topology` define `CapacityRange.RequiredBytes`, `CapacityRange.LimitBytes`, and `Availability` values `active`, `pause`, and `drain`. These fields describe state that affects swarm task scheduling and storage plugin provisioning.
- `ImageManifestSummary` (`x-go-name: ManifestSummary`) summarizes one image manifest by digest-like `ID`, OCI `Descriptor`, local content availability, `Size`, `Kind`, optional `ImageData`, and optional `AttestationData`.
- `ImageManifestSummary.Size` distinguishes `Content` bytes in the content store from `Total` bytes including kind-specific local data, such as unpacked snapshots for runnable image manifests.
- `ImageManifestSummary.Kind` is constrained to `image`, `attestation`, or `unknown`. `ImageData` is populated only for runnable image manifests; `AttestationData.For` links an attestation manifest back to the target image manifest digest.
- This chunk heavily reuses shared definitions declared earlier in the file: `ContainerSummary`, `ContainerConfig`, `HostConfig`, `NetworkingConfig`, `ContainerInspectResponse`, `ContainerTopResponse`, `ContainerStatsResponse`, `ContainerUpdateResponse`, `ContainerWaitResponse`, `ContainerCreateResponse`, `FilesystemChange`, `ImageSummary`, `ImageInspect`, `HistoryResponseItem`, `BuildCachePruneResponse`, `BuildInfo`, `AuthConfig`, `AuthResponse`, `SystemInfo`, `SystemVersion`, `EventMessage`, `DiskUsage`, `ExecConfig`, `ExecStartConfig`, `ExecInspectResponse`, `Volume`, `VolumeCreateOptions`, `VolumeListResponse`, `VolumePruneResponse`, `Network`, `NetworkCreateResponse`, `NetworkConnectRequest`, `NetworkDisconnectRequest`, `Plugin`, `PluginPrivilege`, `Node`, `NodeSpec`, `Swarm`, `SwarmSpec`, `Service`, `ServiceSpec`, `ServiceCreateResponse`, `ServiceUpdateResponse`, `Task`, `Secret`, `SecretSpec`, `Config`, `ConfigSpec`, `DistributionInspect`, `IDResponse`, and `ErrorResponse`.

## API Surface By Area

### Containers

Container operations form the largest local lifecycle surface:

- `ContainerList`: `GET /containers/json`, filters by status, image ancestor, labels, name/id, network, exposed/published ports, volume, health, and time-relative container ids. Optional `all`, `limit`, and `size` change result scope and add filesystem size fields.
- `ContainerCreate`: `POST /containers/create`, accepts `ContainerConfig` plus `HostConfig` and `NetworkingConfig`. It supports query `name` validation, platform-specific image lookup, registry/platform warnings, and returns `ContainerCreateResponse`.
- `ContainerInspect`, `ContainerTop`, `ContainerLogs`, `ContainerChanges`, `ContainerExport`, and `ContainerStats`: read detailed state, process lists, logs, filesystem diff, rootfs tar export, and resource usage. Logs and stats are streaming/binary-oriented surfaces, with stats supporting `stream` and `one-shot`.
- `ContainerResize`, `ContainerStart`, `ContainerStop`, `ContainerRestart`, `ContainerKill`, `ContainerUpdate`, `ContainerRename`, `ContainerPause`, and `ContainerUnpause`: mutate runtime/container state. Timeout handling appears on stop/restart; kill accepts a signal; update accepts resource settings and returns warnings.
- `ContainerAttach` and `ContainerAttachWebsocket`: bidirectional attach protocols with raw stream or multiplexed stream output. `logs`, `stream`, `stdin`, `stdout`, and `stderr` decide the data flow.
- `ContainerWait`: waits for container termination or removal-like conditions and returns a `ContainerWaitResponse`.
- `ContainerDelete`: removes containers with `v`, `force`, and `link` flags.
- `ContainerArchiveInfo`, `ContainerArchive`, and `PutContainerArchive`: inspect, download, or upload tar archives at paths inside a container. The `HEAD` variant returns metadata through `X-Docker-Container-Path-Stat`.
- `ContainerPrune`: deletes stopped containers with filter support and returns reclaimed-space information.

Important integration behavior: attach, logs, stats, archive export, and container export are not simple JSON request/response APIs. Clients and tests must validate binary streams, raw streams, websocket behavior, hijacked connections, headers, and cancellation.

### Images And Build

Image/build operations expose local image inventory, build, registry transfer, and image import/export:

- `ImageList`: `GET /images/json`, filtered by `dangling`, labels, refs, and other image-list predicates; supports `all`, `filters`, `digests`, `shared-size`, `manifests`, and `container-count`.
- `ImageBuild`: `POST /build`, consumes a tar build context and can use the classic builder or BuildKit through `version=1|2`. Query/header controls include Dockerfile path, tags, remote context, cache settings, resource limits, network mode, build args, target, platform, BuildKit outputs, and `X-Registry-Config`.
- `BuildPrune`: `POST /build/prune`, deletes build cache with `keep-storage`, `all`, and filter parameters.
- `ImageCreate`: `POST /images/create`, creates or pulls images, returning a streaming JSON progress body. It accepts `fromImage`, `fromSrc`, `repo`, `tag`, message, platform, registry auth, and content-type handling for imports.
- `ImageInspect`, `ImageHistory`, `ImagePush`, `ImageTag`, `ImageDelete`, `ImageSearch`, `ImagePrune`, `ImageCommit`, `ImageGet`, `ImageGetAll`, and `ImageLoad`: cover inspection, layer history, registry push, tagging, deletion, search, pruning, committing a container, tar export of one or many images, and loading tarred images.

State and persistence signals: image operations mutate or query content store, image metadata, build cache, layer snapshots, tags, registry state, and local manifest availability. Build and pull/push endpoints depend on connection lifetime because the build is canceled when the client disconnects, and several endpoints stream progress rather than returning a final JSON object only.

### System, Auth, Events, And Data Usage

- `SystemAuth`: validates registry authentication config and returns `AuthResponse`.
- `SystemInfo` and `SystemVersion`: expose daemon-wide runtime and version state.
- `SystemPing` and `SystemPingHead`: health/protocol probes, with the `GET` route returning daemon headers such as API version and swarm/experimental/buildkit indicators.
- `SystemEvents`: streams daemon events, filtered by JSON filters, with `since` and `until` timestamp bounds.
- `SystemDataUsage`: returns system disk usage through `DiskUsage`.

These routes are integration points for CLI startup checks, API negotiation, monitoring, and disk usage reporting. Event streaming and ping headers are especially important compatibility signals for clients.

### Exec

- `ContainerExec`: creates an exec instance inside a container from `ExecConfig`.
- `ExecStart`: starts an exec instance, can detach or hijack a stream using `ExecStartConfig`.
- `ExecResize`: resizes an exec TTY with `h` and `w`.
- `ExecInspect`: returns `ExecInspectResponse`, including process/container state.

Exec state is transient and tied to a container. The start route shares attach-like stream handling risks: clients need to handle upgraded/hijacked connections and TTY vs non-TTY stream framing.

### Volumes And Networks

Volume operations:

- `VolumeList`, `VolumeCreate`, `VolumeInspect`, `VolumeUpdate`, `VolumeDelete`, and `VolumePrune`.
- `VolumeUpdate` is a notable swarm-aware mutating route: it requires a `version` query parameter and updates fields such as availability/spec through the volume object contract.
- Prune operations return deleted names and reclaimed bytes.

Network operations:

- `NetworkList`, `NetworkInspect`, `NetworkDelete`, `NetworkCreate`, `NetworkConnect`, `NetworkDisconnect`, and `NetworkPrune`.
- Network creation supports driver, scope, attachability, ingress, internal/external behavior, IPv4/IPv6 flags, IPAM, labels, and driver options.
- Connect/disconnect use body schemas with container identity and endpoint configuration/force flags.

State and persistence behavior: volumes and networks are daemon-managed durable resources. Network connect/disconnect mutate container endpoint attachments. Swarm-scoped networks and local-scoped networks have eligibility restrictions, reflected in 403/500/503 responses and descriptions.

### Plugins

Plugin operations include:

- `PluginList`, `GetPluginPrivileges`, `PluginPull`, `PluginInspect`, `PluginDelete`, `PluginEnable`, `PluginDisable`, `PluginUpgrade`, `PluginCreate`, `PluginPush`, and `PluginSet`.
- Pull and upgrade endpoints return JSON stream progress and accept privilege grants. Delete supports `force`; enable/disable support timeout/force-like controls. Create consumes a plugin rootfs/manifest tar from a local path parameter.

Plugins are an extension boundary for volume, network, logging, and authorization behaviors. The API exposes both installation and runtime enablement, so tests must cover privilege negotiation, enabled-vs-disabled state, and error handling when a plugin is not installed.

### Swarm, Nodes, Services, And Tasks

Swarm and node operations:

- `NodeList`, `NodeInspect`, `NodeDelete`, and `NodeUpdate`.
- `SwarmInspect`, `SwarmInit`, `SwarmJoin`, `SwarmLeave`, `SwarmUpdate`, `SwarmUnlockkey`, and `SwarmUnlock`.
- Swarm init/join bodies define listen, advertise, and data-path addresses, data-path port, default address pools, subnet size, join token, remote manager addresses, and `SwarmSpec`.
- Swarm and node update routes require `version` query parameters for optimistic concurrency. Swarm update can rotate worker token, manager token, and manager unlock key.

Service and task operations:

- `ServiceList`, `ServiceCreate`, `ServiceInspect`, `ServiceDelete`, `ServiceUpdate`, and `ServiceLogs`.
- `TaskList`, `TaskInspect`, and `TaskLogs`.
- Service create/update bodies use `ServiceSpec` with task templates, container specs, mounts, hosts, DNS, secrets, log drivers, placement, resources, restart policy, replicated/global mode, update/rollback config, endpoint spec, and labels.
- Service update requires current `version`, supports `registryAuthFrom`, `rollback=previous`, and `X-Registry-Auth`.
- Task and service log endpoints mirror container logs with raw/multiplexed streams, `details`, `follow`, stdout/stderr, timestamp, since, and tail parameters.

Swarm routes consistently return 503 when the daemon is not in the required swarm state, or when already part of a swarm for init/join. This is a major test signal: the same endpoint can be valid structurally but unavailable depending on cluster membership and manager/worker role.

### Secrets And Configs

Secrets:

- `SecretList`, `SecretCreate`, `SecretInspect`, `SecretDelete`, and `SecretUpdate`.
- List filters include id, label, name, and names. Create returns `IDResponse`. Update requires `version` and currently allows only label updates while all other inspected fields must remain unchanged.

Configs:

- `ConfigList`, `ConfigCreate`, `ConfigInspect`, `ConfigDelete`, and `ConfigUpdate`.
- Config update mirrors secret update: required `version`, labels-only mutability, and conflict/error responses.

Secrets and configs are swarm-scoped durable objects. They should be tested for manager-only/swarm availability, name conflicts, version conflicts, label-only updates, base64 data handling, and error status differentiation.

### Distribution And Session

- `DistributionInspect`: `GET /distribution/{name}/json` contacts a registry and returns digest/platform information through `DistributionInspect`. It can return 401 for failed authentication or no image found.
- `Session`: `POST /session` initializes an interactive h2c-upgraded session. It hijacks the HTTP connection to HTTP/2 transport so the daemon can call back to client-exposed gRPC services.

`Session` is a special integration point for advanced BuildKit/build-client capabilities. It is not a normal JSON endpoint; callers must handle upgrade headers and raw stream transport.

## Control Flow And Protocol Patterns

- Normal JSON CRUD flow: path/query/body validation, daemon lookup or mutation, status code, JSON schema response or `ErrorResponse`.
- Optimistic update flow: client first inspects/list-fetches a resource, reads `Version.Index`, submits full/partial spec with `version` query parameter, and daemon rejects stale writes with bad-parameter/conflict-style errors depending on handler implementation.
- Streaming progress flow: build, image create/push/load, plugin pull/upgrade/push, logs, events, stats, service logs, and task logs keep the response open and emit multiple frames/messages. Tests need to validate both content type and stream termination/cancellation.
- Hijacked raw-stream flow: attach, exec start, and session can switch the HTTP connection from normal request/response to bidirectional transport. Non-TTY container streams are multiplexed with 8-byte headers; TTY streams are raw PTY bytes.
- Prune flow: prune endpoints take JSON-encoded filters, delete unused resources, and return deleted identifiers plus reclaimed bytes where applicable.
- Swarm membership flow: init creates a manager and returns node id; join consumes remote manager addresses and join token; leave changes daemon cluster membership; update mutates swarm spec/tokens/unlock key; unlock handles autolocked manager recovery.

## State And Persistence Behavior

- Persistent local daemon state includes containers, images/tags/manifests/content, build cache, volumes, networks, plugins, and exec metadata while active.
- Cluster-persistent swarm state includes nodes, swarm spec/tokens/unlock key, services, tasks, secrets, configs, and swarm-scoped volumes/networks.
- Runtime state includes container running/paused/restarting/dead states, process lists, stats streams, attach/log streams, exec process state, network endpoint attachments, and task/service log streams.
- Registry-dependent state is external to the daemon but triggered through image pull/push/search and distribution inspect; these require auth headers and can fail independently of local daemon health.
- Archive and export endpoints expose filesystem snapshots and image tar streams, so persistence tests should verify durable on-disk content rather than only response status.
- Versioned update endpoints encode concurrency control in the API contract; clients should not blindly update specs without a fresh inspect/list source.

## Dependencies And Integration Points

- OpenAPI consumers: documentation generation, SDK generation, endpoint validation tests, and CLI behavior mapping depend on stable operation ids, parameter names, media types, and schema refs.
- Docker daemon router/handlers: every `operationId` corresponds to server-side route behavior that must match the documented status codes and response shapes.
- Registry integration: image create/push/search, distribution inspect, build registry config, and service create/update registry auth depend on registry authentication and network availability.
- BuildKit/classic builder: `/build`, `/build/prune`, `/session`, and `ImageManifestSummary` fields integrate with builder backends, content stores, snapshots, and attestation data.
- Container runtime and OS facilities: top uses `ps` on Unix and is unsupported on Windows; stats/logs/attach/exec depend on runtime streams, cgroups, TTY settings, and logging drivers.
- SwarmKit/cluster store: node, swarm, service, task, secret, config, and swarm-scoped volume/network operations depend on swarm manager state and Raft object versions.
- Plugin subsystem: plugin operations integrate with privilege negotiation, rootfs/manifest packaging, enable/disable lifecycle, and plugin-specific backends for volumes/networks/logging.

## Risks And Edge Cases

- Large JSON-in-query filters (`filters`, `buildargs`, `outputs`, `cachefrom`, labels) are easy to encode incorrectly. Generated clients must preserve JSON string parameters and URI encoding.
- Stream endpoints often have `200` success with binary/raw bodies rather than schema-rich JSON. Tests that only check status codes will miss framing, cancellation, and content-type regressions.
- Attach and exec stream framing changes based on container TTY setting. Non-TTY streams require Docker's 8-byte multiplexed header; TTY streams do not.
- Some endpoints use `101` upgrade and `200` no-upgrade success variants. Proxies and generated HTTP clients may mishandle these routes.
- Swarm APIs have role/state-dependent 503 responses. Local-only daemon test fixtures should not assume service/task/secret/config endpoints are available.
- Versioned update routes can race. Test fixtures should intentionally verify stale `version` rejection for nodes, swarm, services, secrets, configs, and volume update.
- Destructive operations (`ContainerDelete force`, image delete, prune endpoints, network/volume prune, swarm leave force) can remove significant local state. Integration tests need isolated daemons or cleanup guards.
- Registry auth headers are base64/base64url-encoded JSON and differ by endpoint (`X-Registry-Auth` vs `X-Registry-Config`). Misencoding leads to authentication failures that can be mistaken for daemon bugs.
- Platform selection appears in container create, build, image create/load, and image list/manifest behavior. Multi-arch tests need explicit platform assertions.
- The schema includes examples and descriptions that imply behavior not always fully represented by JSON schema validation, such as labels-only secret/config updates and service rollback semantics.

## Test Signals

- Contract tests should assert every `operationId` in this chunk is present in generated docs/clients and maps to the expected HTTP method/path.
- Schema validation should cover success and error responses for `ErrorResponse`, required path parameters, required body parameters, enum values, nullable/omitempty fields, and `required` arrays.
- Streaming tests should cover build cancellation on disconnect, image pull/push progress, container/service/task logs with `follow`, event streams with filters and time bounds, stats `stream=false` and `one-shot`, and raw tar export/import.
- Attach/exec/session tests should verify hijack/upgrade behavior, raw-vs-multiplexed stream framing, websocket attach, detach key parsing, stdin/stdout/stderr selection, and TTY resize.
- Lifecycle tests should cover container create/start/stop/restart/kill/pause/unpause/rename/update/delete, archive upload/download/stat, and prune filters.
- Image tests should cover build v1/v2 selection, BuildKit outputs, registry auth headers, platform lookup mismatch warnings, manifest availability/content size fields, pruning, tagging, removal conflicts, save/load, and commit from container.
- Swarm tests should run against both non-swarm and swarm-enabled daemons to assert 503 states, init/join/leave flows, token rotation, unlock key behavior, node updates, service create/update/rollback/logs, and task list filters.
- Secret/config tests should check create/list/inspect/delete/update, name conflicts, label filters, required `version`, and labels-only mutation restrictions.
- Network/volume tests should cover local and swarm-scoped resources, connect/disconnect eligibility, IPAM options, IPv4/IPv6 toggles, prune filters, volume update versioning, capacity/topology fields, and availability transitions.
- Plugin tests should verify privilege discovery, pull/upgrade progress, enable/disable state, delete force, create from tar path, push, and setting plugin variables.

## Operation Inventory

Container: `ContainerList`, `ContainerCreate`, `ContainerInspect`, `ContainerTop`, `ContainerLogs`, `ContainerChanges`, `ContainerExport`, `ContainerStats`, `ContainerResize`, `ContainerStart`, `ContainerStop`, `ContainerRestart`, `ContainerKill`, `ContainerUpdate`, `ContainerRename`, `ContainerPause`, `ContainerUnpause`, `ContainerAttach`, `ContainerAttachWebsocket`, `ContainerWait`, `ContainerDelete`, `ContainerArchiveInfo`, `ContainerArchive`, `PutContainerArchive`, `ContainerPrune`.

Image/build/system/exec: `ImageList`, `ImageBuild`, `BuildPrune`, `ImageCreate`, `ImageInspect`, `ImageHistory`, `ImagePush`, `ImageTag`, `ImageDelete`, `ImageSearch`, `ImagePrune`, `SystemAuth`, `SystemInfo`, `SystemVersion`, `SystemPing`, `SystemPingHead`, `ImageCommit`, `SystemEvents`, `SystemDataUsage`, `ImageGet`, `ImageGetAll`, `ImageLoad`, `ContainerExec`, `ExecStart`, `ExecResize`, `ExecInspect`.

Volume/network/plugin: `VolumeList`, `VolumeCreate`, `VolumeInspect`, `VolumeUpdate`, `VolumeDelete`, `VolumePrune`, `NetworkList`, `NetworkInspect`, `NetworkDelete`, `NetworkCreate`, `NetworkConnect`, `NetworkDisconnect`, `NetworkPrune`, `PluginList`, `GetPluginPrivileges`, `PluginPull`, `PluginInspect`, `PluginDelete`, `PluginEnable`, `PluginDisable`, `PluginUpgrade`, `PluginCreate`, `PluginPush`, `PluginSet`.

Swarm/cluster resources: `NodeList`, `NodeInspect`, `NodeDelete`, `NodeUpdate`, `SwarmInspect`, `SwarmInit`, `SwarmJoin`, `SwarmLeave`, `SwarmUpdate`, `SwarmUnlockkey`, `SwarmUnlock`, `ServiceList`, `ServiceCreate`, `ServiceInspect`, `ServiceDelete`, `ServiceUpdate`, `ServiceLogs`, `TaskList`, `TaskInspect`, `TaskLogs`.

Secrets/configs/distribution/session: `SecretList`, `SecretCreate`, `SecretInspect`, `SecretDelete`, `SecretUpdate`, `ConfigList`, `ConfigCreate`, `ConfigInspect`, `ConfigDelete`, `ConfigUpdate`, `DistributionInspect`, `Session`.

## Unresolved Cross-Chunk References

Most schemas referenced in this chunk are defined before line 7900, outside this chunk. The final merged per-file report should reconcile those earlier type definitions with this route surface, especially container/host config, image/build responses, swarm/service/task specs, plugin schemas, and shared error/ID responses. This chunk also starts in the middle of the volume-related definition block, so the preceding lines are needed to name the owning schema for `CapacityRange`, accessibility requirements, and `Availability`.
