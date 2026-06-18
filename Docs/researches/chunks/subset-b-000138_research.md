# sources/cloud-native/moby/api/docs/v1.44.yaml lines 7749-12705

## Scope

This chunk is the latter half of the Docker Engine API v1.44 OpenAPI/Swagger path table. It defines HTTP resources, operation IDs, request parameters, response schemas, examples, content types, and error surfaces for container lifecycle operations, image/build flows, system inspection, exec sessions, volumes, networks, plugins, swarm nodes and cluster management, services, tasks, secrets, configs, registry distribution inspection, and BuildKit session setup.

The file is declarative YAML rather than executable code. Its practical purpose is to bind daemon behavior to a stable API contract used by generated clients, documentation renderers, compatibility tests, and API schema validation.

## Major API Areas

### Container Operations

The chunk opens in the container lifecycle API:

- `ContainerRestart` for `POST /containers/{id}/restart`, with optional `signal` and timeout `t`.
- `ContainerKill` for `POST /containers/{id}/kill`, defaulting the `signal` query parameter to `SIGKILL`.
- `ContainerUpdate` for runtime resource and restart policy changes using `Resources` plus `RestartPolicy`.
- `ContainerRename`, `ContainerPause`, and `ContainerUnpause`.
- `ContainerAttach` and `ContainerAttachWebsocket`, including connection hijacking semantics, raw stream vs multiplexed stream formats, TTY behavior, detach keys, and `logs`/`stream`/stdio selectors.
- `ContainerWait`, which blocks until `not-running`, `next-exit`, or `removed`.
- `ContainerDelete` with `v`, `force`, and `link` options.
- `ContainerArchiveInfo`, `ContainerArchive`, and `PutContainerArchive` for statting, exporting, and extracting tar archives from or into container filesystems.
- `ContainerPrune` with `until` and `label` filters.

Important schemas referenced here include `Resources`, `RestartPolicy`, `ContainerWaitResponse`, `ErrorResponse`, and archive bodies represented as binary strings. The attach endpoints are integration-sensitive because they intentionally step outside normal request/response JSON flow and use raw upgraded HTTP connections.

### Image and Build Operations

The image section defines image inventory, build, pull/import, inspect, history, push, tag, delete, search, prune, save, and load operations:

- `ImageList` lists `ImageSummary` objects and supports `all`, `filters`, `shared-size`, and `digests`.
- `ImageBuild` accepts an archive build context and many build controls: `dockerfile`, `t`, `remote`, cache flags, resource limits, `buildargs`, `shmsize`, `squash`, labels, build network mode, registry config header, `platform`, `target`, BuildKit `outputs`, and builder backend `version`.
- `BuildPrune` exposes builder cache cleanup with `keep-storage`, `all`, and cache filters including age, id, parent, type, description, and sharing state.
- `ImageCreate` handles pull or import via `fromImage` or `fromSrc`, optional repository/tag/message, raw import body, registry auth, Dockerfile-style `changes`, and platform selection.
- `ImageInspect`, `ImageHistory`, `ImagePush`, `ImageTag`, `ImageDelete`, `ImageSearch`, and `ImagePrune` cover standard image lifecycle.
- `ImageCommit` creates an image from a container and can pause the container, set repo/tag/comment/author, apply Dockerfile instructions, and override container config.
- `ImageGet`, `ImageGetAll`, and `ImageLoad` define tarball save/load flows and document OCI image layout plus backward-compatible Docker save metadata.

Stateful behavior is explicit: image deletion must respect descendants, running containers, and builds; build cancellation follows client connection closure; push/pull are registry-authenticated and can be canceled on connection close; `ImageBuild` toggles between classic builder and BuildKit. The risk surface is large because many parameters are JSON-encoded query strings, binary tar streams, or base64 registry auth headers.

### System APIs

System endpoints include:

- `SystemAuth` for validating registry credentials and optionally returning an identity token.
- `SystemInfo` and `SystemVersion` for daemon/system metadata.
- `SystemPing` and `SystemPingHead` for health/version probing, exposing headers such as `Api-Version`, `Builder-Version`, `Docker-Experimental`, and `Swarm`.
- `SystemEvents` for streaming event records from containers, images, volumes, networks, daemon, services, nodes, secrets, configs, and builder.
- `SystemDataUsage` for `GET /system/df`, returning layer size plus image, container, volume, and build cache usage, optionally filtered by object type.

The event stream is a long-lived integration point. Its filter syntax is JSON encoded and spans many object domains, so generated clients and tests need to cover both historical bounded reads (`since`/`until`) and live stream behavior.

### Exec APIs

The exec API is split into create, start, resize, and inspect:

- `ContainerExec` creates an exec instance inside a running container from `ExecConfig`, with stdio attachment flags, console size, detach keys, TTY, environment, command, privileged flag, user, and working directory.
- `ExecStart` starts the created exec instance and can detach or hijack the connection for raw or multiplexed streaming.
- `ExecResize` resizes a TTY exec session using required `h` and `w`.
- `ExecInspect` exposes `ExecInspectResponse`, including `Running`, `ExitCode`, `ProcessConfig`, open stream flags, `ContainerID`, and host `Pid`.

Control flow is intentionally two-phase: create returns an ID, then start binds that ID to process execution and possible streaming. Resize is valid only for TTY exec sessions. Tests should assert 409 behavior for stopped or paused containers and 404 behavior for missing exec IDs.

### Volumes

Volume endpoints include `VolumeList`, `VolumeCreate`, `VolumeInspect`, `VolumeUpdate`, `VolumeDelete`, and `VolumePrune`. List/prune use JSON-encoded filters. Create and inspect use `VolumeCreateOptions` and `Volume` schemas.

`VolumeUpdate` is specifically constrained to Swarm cluster volumes and wraps `ClusterVolumeSpec` in a body object with `Spec`. It requires a `version` query parameter to avoid conflicting writes and currently allows only `Availability` to change. This optimistic concurrency pattern also appears later in node, swarm, service, secret, and config updates.

Persistent state is direct: volume create/delete/prune changes daemon volume metadata and storage managed by volume drivers. Delete has a `force` flag but still advertises 409 when a volume is in use.

### Networks

Network endpoints include list, inspect, delete, create, connect, disconnect, and prune:

- `NetworkList` returns reduced `Network` objects and supports filters for dangling state, driver, id, label, name, scope, and built-in/custom type.
- `NetworkInspect` supports `verbose` and `scope`.
- `NetworkCreate` defines `NetworkCreateRequest` with name, driver, scope, internal/attachable/ingress/config-only flags, `ConfigFrom`, `IPAM`, IPv6, driver options, and labels.
- `NetworkConnect` binds a container to a local network or attachable swarm network, with optional endpoint settings including IPAM and MAC address.
- `NetworkDisconnect` removes the container endpoint and supports `Force`.
- `NetworkPrune` removes unused networks by `until` and label filters.

Integration points include libnetwork drivers, swarm overlay constraints, IPAM plugins, and endpoint settings shared with container network configuration. The spec documents forbidden cases such as deleting predefined networks or creating overlay networks on a non-swarm daemon.

### Plugins

Plugin operations include `PluginList`, `GetPluginPrivileges`, `PluginPull`, `PluginInspect`, `PluginDelete`, `PluginEnable`, `PluginDisable`, `PluginUpgrade`, `PluginCreate`, `PluginPush`, and `PluginSet`.

These endpoints manage installed plugin state and registry interactions. Pull and upgrade accept `X-Registry-Auth` and a body of accepted `PluginPrivilege` values. Delete/disable have force options that may disrupt containers using the plugin. `PluginCreate` consumes a plugin rootfs/manifest tar archive, while `PluginSet` applies key/value settings such as `DEBUG=1`.

The security risk is high relative to ordinary metadata APIs: plugin privileges can request host network, mount, or device access, and registry auth is sent as a base64url-encoded header.

### Swarm Nodes and Cluster

Swarm cluster management starts with node APIs:

- `NodeList`, `NodeInspect`, `NodeDelete`, and `NodeUpdate`.
- Node filters include id, engine labels, membership, name, node labels, and role.
- `NodeUpdate` requires the current object `version` and a `NodeSpec`.

Cluster endpoints include:

- `SwarmInspect`.
- `SwarmInit`, with listen/advertise/data-path addresses, data path port, default address pool, subnet size, force-new-cluster, and `SwarmSpec`.
- `SwarmJoin`, requiring `ListenAddr`, `RemoteAddrs`, and `JoinToken`.
- `SwarmLeave` with `force`.
- `SwarmUpdate`, requiring `SwarmSpec` plus object `version` and optional worker token, manager token, and manager unlock key rotation.
- `SwarmUnlockkey` and `SwarmUnlock`.

Most swarm endpoints return 503 when the daemon is not in the required swarm state. Mutating operations are persistent and cluster-wide, affecting Raft state, join tokens, manager unlock state, networking defaults, and node membership. Tests need to cover non-swarm daemons, already-in-swarm init/join behavior, forced leave, and version conflict handling.

### Services and Tasks

Service endpoints include `ServiceList`, `ServiceCreate`, `ServiceInspect`, `ServiceDelete`, `ServiceUpdate`, and `ServiceLogs`.

`ServiceCreate` and `ServiceUpdate` use `ServiceSpec`, with examples covering container image, mounts, hosts, user, DNS, secrets, log driver, resource limits/reservations, restart policy, replicated mode, update/rollback config, endpoint ports, and labels. `ServiceUpdate` requires the current service `version`, supports `registryAuthFrom`, can trigger server-side rollback with `rollback=previous`, and accepts `X-Registry-Auth`.

`ServiceLogs` streams stdout/stderr and mirrors container logs flags: `details`, `follow`, `stdout`, `stderr`, `since`, `timestamps`, and `tail`. The spec notes support only for `local`, `json-file`, or `journald` logging drivers.

Task endpoints include `TaskList`, `TaskInspect`, and `TaskLogs`. List filters include desired state, id, labels, name, node, and service. Task examples expose scheduler state: service ID, slot, node ID, task status, desired state, container status, and network attachments.

Services are desired-state resources; tasks are scheduler-produced runtime records. The API contract should be tested for propagation from service specs to task state, rollback/update failure behavior, log driver limitations, and 503 behavior outside swarm mode.

### Secrets and Configs

Secret endpoints include `SecretList`, `SecretCreate`, `SecretInspect`, `SecretDelete`, and `SecretUpdate`. Config endpoints mirror this with `ConfigList`, `ConfigCreate`, `ConfigInspect`, `ConfigDelete`, and `ConfigUpdate`.

Both resource families are swarm-scoped and return 503 when the node is not part of a swarm. Create operations return `IdResponse` and can fail with 409 on name conflicts. Update operations require a `version` query parameter and are explicitly limited to label updates; other fields must remain unchanged from inspect output. Secret examples include base64 `Data` and optional secret driver configuration, while config examples include base64 `Data`.

Persistence is cluster-state backed. Risks include accidental mutation of immutable fields, leaking secret data in examples/logs/generated clients, and failing to enforce version concurrency.

### Distribution and Session

`DistributionInspect` contacts a registry for image digest and platform information and returns `DistributionInspect`; it can return 401 for auth failure or missing image.

`Session` initializes an interactive BuildKit-style session by hijacking an HTTP connection to h2c. The daemon can then call back to client-exposed gRPC services over that connection. This is a nonstandard transport contract: response 101 indicates successful upgrade, while 400 and 500 use `ErrorResponse`.

## Shared Types and Schema Dependencies

This chunk references many definitions rather than defining them locally. Key dependencies include:

- Error and identity wrappers: `ErrorResponse`, `IdResponse`.
- Container/runtime types: `Resources`, `RestartPolicy`, `ContainerConfig`, `ContainerSummary`, `ContainerWaitResponse`, `ProcessConfig`, `EndpointSettings`.
- Image/build types: `ImageSummary`, `ImageInspect`, `ImageHistoryResponseItem`, `ImageDeleteResponseItem`, `BuildCache`, `DistributionInspect`.
- Storage/network types: `Volume`, `VolumeCreateOptions`, `ClusterVolumeSpec`, `Network`, `IPAM`, `ConfigReference`.
- Plugin types: `Plugin`, `PluginPrivilege`.
- Swarm types: `Node`, `NodeSpec`, `Swarm`, `SwarmSpec`, `Service`, `ServiceSpec`, `ServiceCreateResponse`, `ServiceUpdateResponse`, `Task`, `Secret`, `SecretSpec`, `Config`, `ConfigSpec`.

Because the path table relies heavily on `$ref`, schema integrity depends on matching definitions elsewhere in the same YAML file. A broken definition name or incompatible schema change would affect generated SDKs even if endpoint text still renders.

## Control Flow Patterns

Several recurring API patterns are visible:

- Simple synchronous lifecycle operations return 200, 201, 204, or an `ErrorResponse`.
- Streaming and hijacked operations return raw streams, multiplexed streams, websockets, or HTTP upgrade responses instead of normal JSON.
- Long-lived reads include attach, exec start, events, service logs, task logs, and session.
- Mutating swarm resources use optimistic concurrency through a required `version` query parameter.
- Many list/prune operations accept JSON-encoded `filters` query parameters expressed as `map[string][]string`.
- Import/export operations use tar or binary bodies rather than JSON.
- Registry-affecting operations use `X-Registry-Auth` or `X-Registry-Config` headers.
- Non-swarm daemons return 503 for swarm-only resource families.

These patterns are important for client generation because query serialization, body streaming, connection hijacking, response status handling, and header construction differ materially across operations.

## State and Persistence Behavior

The chunk describes APIs that mutate several durable daemon stores:

- Container runtime and metadata state: restart, kill, update, rename, pause/unpause, delete, archive extraction, exec instance creation.
- Image graph and build cache: build, prune, pull/import, commit, tag, delete, save/load.
- Volume storage: create, update, delete, prune.
- Network state: create, connect, disconnect, delete, prune.
- Plugin installation and configuration: pull/create/enable/disable/upgrade/push/set/delete.
- Swarm Raft/cluster state: nodes, swarm init/join/leave/update/unlock, services, tasks, secrets, configs, cluster volumes.
- Registry-derived metadata: distribution inspect.

The API spec also captures transient state: event streams, logs, exec running status, wait conditions, and session callbacks. Tests should distinguish durable mutations from streaming/transient reads.

## Integration Points

External or cross-component integrations include:

- Docker daemon HTTP API routing and API versioning.
- Generated clients and documentation consuming `operationId`, schemas, examples, produces/consumes, and response codes.
- Container runtime and cgroups for kill, restart, pause/unpause, exec, and resource updates.
- Tar archive handling for container filesystem copy and image/plugin import/export.
- Build backends, including classic builder and BuildKit, plus BuildKit session h2c upgrade.
- Registries for image pull/push, plugin pull/upgrade, distribution inspect, and registry auth.
- SwarmKit/Raft for swarm, node, service, task, secret, config, and cluster volume state.
- Network, IPAM, volume, logging, and plugin drivers.
- Docker Hub search for `ImageSearch`.
- System event bus and log backends for event/log streaming endpoints.

## Risks and Edge Cases

- Connection hijacking and stream multiplexing are easy to model incorrectly in generated clients. TTY and non-TTY attach/exec/log behavior must not be conflated.
- JSON-encoded query parameters such as `filters`, `buildargs`, `labels`, cache settings, and BuildKit `outputs` can fail through double-encoding, wrong map shape, or incorrect array serialization.
- Many destructive operations have force flags (`ContainerDelete`, `VolumeDelete`, `PluginDelete`, `PluginDisable`, `NodeDelete`, `SwarmLeave`) that need clear client behavior and tests.
- Swarm update operations rely on version numbers from inspect responses; stale versions should produce conflicts rather than silent overwrites.
- Secret/config updates are intentionally restricted to labels; clients must not imply that secret/config payload data can be changed in place.
- Registry auth headers contain credentials and should not be logged by clients or test harnesses.
- Prune APIs delete resources and depend on daemon-local time for `until` filters; tests should avoid relying on wall-clock ambiguity.
- Platform selection appears in pull/import/build paths and can produce warnings or host-native fallbacks.
- Plugin privilege negotiation can grant host resources; API docs and generated code should preserve privilege structure exactly.
- `ServiceLogs` and `TaskLogs` only work with specific logging drivers, which creates environment-sensitive behavior.
- 503 responses are semantic for swarm-only APIs and should not be collapsed into generic server failures.

## Test Signals

High-value tests for this chunk should validate:

- Every `operationId` in this range remains unique and mapped to the expected path/method.
- Referenced schemas resolve: especially `ServiceSpec`, `SwarmSpec`, `SecretSpec`, `ConfigSpec`, `ClusterVolumeSpec`, `PluginPrivilege`, `ImageSummary`, and stream response schemas.
- Generated clients serialize JSON query filters consistently for container/image/build/volume/network/event/task/service/secret/config APIs.
- Archive, image save/load, plugin create, and build endpoints preserve binary request/response bodies and correct content types.
- Attach, exec start, logs, events, and session endpoints preserve streaming/hijack metadata and status-code expectations.
- Mutating swarm APIs require `version` where specified.
- Non-swarm daemon tests assert 503 for nodes, swarm, services, tasks, secrets, configs, and cluster volume update paths.
- Error responses use `ErrorResponse` consistently for 400/401/403/404/409/500/503 cases.
- Examples remain parseable YAML/JSON-like structures for documentation generation.
- Dangerous operations expose documented safeguards and conflict responses: image delete conflicts, volume-in-use conflicts, predefined network removal, plugin in-use disable/delete, and container delete conflict without force.

## Chunk Boundary Notes

This chunk begins inside the container restart endpoint, so the path key for `/containers/{id}/restart` starts before line 7749. It ends at the `Session` endpoint before the global `definitions` section. The final merged research for `sources/cloud-native/moby/api/docs/v1.44.yaml` should combine this with earlier chunks so endpoint groups and schema definitions can be reconciled across the whole file.
