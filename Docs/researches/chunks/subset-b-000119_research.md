# sources/cloud-native/moby/api/docs/v1.35.yaml lines 1-7565

## Scope

This chunk is the opening and majority body of the Docker Engine API v1.35 Swagger 2.0 document. It covers file-level API metadata, ReDoc tag organization, all shared schema definitions from `ImageHistoryResponseItem` through `PeerNode`, and path operations from `GET /containers/json` through the start of `GET /volumes`.

The source is an API contract, not executable implementation. Its behavior is expressed through schemas, examples, status codes, media types, query/body/header parameters, and operation IDs consumed by generated clients, documentation renderers, daemon route tests, and compatibility tooling.

## Purpose

The file defines the versioned HTTP interface for Docker Engine API v1.35 under `basePath: /v1.35`. It documents how Docker clients talk to the daemon for container, image, exec, system, and early volume operations, and it provides shared object shapes for swarm, services, tasks, plugins, networks, volumes, images, and host/system state.

The initial prose establishes core API rules: standard HTTP status codes, JSON error bodies with a `message` field, API version prefixing, open-schema compatibility where clients must ignore extra response fields, and registry authentication supplied as `X-Registry-Auth` containing base64 JSON credentials or an identity token.

## Important APIs And Types

Top-level API metadata:

- Swagger 2.0 document with `http` and `https` schemes, JSON/text consumes and produces defaults, and Docker Engine API version `1.35`.
- Tags organize documentation and generated clients into `Container`, `Image`, `Network`, `Volume`, `Exec`, swarm object tags, `Plugin`, and `System`.
- The file uses `operationId` values such as `ContainerCreate`, `ImageBuild`, `SystemEvents`, and `ExecStart` as stable integration names.

Core container/image/network/storage definitions:

- `ContainerConfig` describes portable container settings: hostname, user, attach flags, TTY/stdin behavior, environment, command, image, entrypoint, working directory, labels, healthcheck, exposed ports, stop signal/timeout, and shell.
- `HostConfig` extends `Resources` with host-dependent runtime settings: binds, log driver, network mode, port bindings, restart policy, auto-remove, volume inheritance, mounts, Linux namespace/security options, sysctls, runtime, and Windows console/isolation options.
- `Resources` models cgroup and resource controls including CPU shares/quota/period/realtime, cpusets, memory/swap/reservation/swappiness, blkio limits, pids limit, ulimits, devices, and Windows CPU/IO controls.
- `MountType`, `Mount`, and `MountPoint` distinguish requested mount configuration from reported container mount state for `bind`, `npipe`, `tmpfs`, and `volume` mounts.
- `NetworkSettings`, `EndpointSettings`, `EndpointIPAMConfig`, `PortMap`, and `PortBinding` define container network state, endpoint driver options, IPAM addresses, aliases/links, and host-to-container port bindings.
- `Image`, `ImageSummary`, `ImageHistoryResponseItem`, `GraphDriverData`, `ImageDeleteResponseItem`, `BuildInfo`, `CreateImageInfo`, and `PushImageInfo` cover image inspection, listing, history, storage-driver data, delete results, and JSON progress-message streams.
- `Volume` defines persistent volume metadata and optional `UsageData` used by `GET /system/df`.
- `Network` and `IPAM` define Docker network metadata, driver options, attached containers, and address-management configuration.

Swarm, service, task, and security definitions:

- `ObjectVersion` documents optimistic concurrency for swarm objects; clients must submit the current version index on updates.
- `NodeSpec`, `Node`, `NodeDescription`, `NodeStatus`, `ManagerStatus`, `Reachability`, `Platform`, `EngineDescription`, and `TLSInfo` model swarm node desired state, observed state, engine plugins, resources, and certificate information.
- `SwarmSpec`, `ClusterInfo`, `JoinTokens`, `Swarm`, `SwarmInfo`, `LocalNodeState`, and `PeerNode` describe cluster configuration, raft/CA/dispatcher/encryption settings, task defaults, join tokens, local node role, and peer manager addresses.
- `TaskSpec`, `TaskState`, and `Task` model swarm task desired configuration, scheduling state, runtime status, networks, logs, secrets/config references, resources, placement, restart policy, and generic resources.
- `ServiceSpec`, `EndpointPortConfig`, `EndpointSpec`, `Service`, and `ServiceUpdateResponse` define swarm services, endpoint publishing, update/rollback policies, virtual IPs, and update warnings.
- `SecretSpec`, `Secret`, `ConfigSpec`, and `Config` define swarm secret/config metadata and payload fields; secret/config payloads are base64 strings with documented size constraints.
- `Plugin`, `PluginMount`, `PluginDevice`, `PluginEnv`, and `PluginInterfaceType` describe managed plugin configuration, mutable settings, rootfs layers, capabilities, sockets, mounts, devices, environment, network/pid/ipc permissions, and runtime entrypoints.

System and registry definitions:

- `SystemInfo` is the large `/info` response schema covering daemon ID, container/image counts, storage driver state, Docker root dir, plugin availability, host kernel/OS/architecture, cgroup and networking capabilities, proxy settings, registries, runtimes, swarm state, live-restore, security options, and component commits.
- `PluginsInfo`, `RegistryServiceConfig`, `IndexInfo`, `Runtime`, and `Commit` support `SystemInfo`.
- `AuthConfig`, `ErrorDetail`, `ProgressDetail`, `ErrorResponse`, `IdResponse`, and `ProcessConfig` are reusable request/response primitives.

Path operations included in this chunk:

- Container lifecycle and inspection: `ContainerList`, `ContainerCreate`, `ContainerInspect`, `ContainerTop`, `ContainerLogs`, `ContainerChanges`, `ContainerExport`, `ContainerStats`, `ContainerResize`, `ContainerStart`, `ContainerStop`, `ContainerRestart`, `ContainerKill`, `ContainerUpdate`, `ContainerRename`, `ContainerPause`, `ContainerUnpause`, `ContainerAttach`, `ContainerAttachWebsocket`, `ContainerWait`, `ContainerDelete`, `ContainerArchiveInfo`, `ContainerArchive`, `PutContainerArchive`, and `ContainerPrune`.
- Image/build operations: `ImageList`, `ImageBuild`, `BuildPrune`, `ImageCreate`, `ImageInspect`, `ImageHistory`, `ImagePush`, `ImageTag`, `ImageDelete`, `ImageSearch`, `ImagePrune`, `ImageCommit`, `ImageGet`, `ImageGetAll`, and `ImageLoad`.
- System operations: `SystemAuth`, `SystemInfo`, `SystemVersion`, `SystemPing`, `SystemEvents`, and `SystemDataUsage`.
- Exec operations: `ContainerExec`, `ExecStart`, `ExecResize`, and `ExecInspect`.
- Volume operation start: `VolumeList` begins at the end of this chunk, including its response shape, examples, and the beginning of the filters description.

## Control Flow

The main control flow is lifecycle sequencing across REST operations.

For containers, clients typically list or create a container, inspect it, then move it through start/stop/restart/kill/pause/unpause/update/rename/delete operations. `ContainerCreate` composes `ContainerConfig`, `HostConfig`, and `NetworkingConfig.EndpointsConfig`; `ContainerStart` transitions a created/stopped container to running; `ContainerWait` blocks until stop and returns exit status; `ContainerDelete` removes state with optional volume/force/link parameters. Inspection exposes persisted configuration, current `State`, graph-driver data, mounts, size fields when requested, and network settings.

Container streaming operations use distinct response flows. `ContainerLogs` can return a normal body or, with `follow`, a `101` upgraded raw stream. `ContainerAttach` hijacks the HTTP connection for stdin/stdout/stderr multiplexing and documents the eight-byte stream header used when TTY is disabled. `ContainerAttachWebsocket` exposes similar attachment over a websocket. `ContainerStats` streams resource snapshots unless `stream=false`, while archive export/import operations use tar or octet-stream bodies rather than JSON.

Filesystem operations split metadata and content. `HEAD /containers/{id}/archive` returns a base64-encoded `X-Docker-Container-Path-Stat` header for a path. `GET /containers/{id}/archive` returns a tar archive of a filesystem resource. `PUT /containers/{id}/archive` extracts a tar archive into a target directory and can reject missing directories, invalid paths, or read-only filesystems.

Image flows cover local listing, remote registry interaction, build/import/export, and cleanup. `ImageBuild` accepts a tar build context and many build controls as query parameters, including Dockerfile path, tags, build args, labels, cache settings, target stage, network mode, platform-related options, and registry auth. `ImageCreate`, `ImagePush`, and `ImageSearch` integrate with registries and authentication. `ImageDelete` removes by name or ID with force and prune options. `ImageGet`, `ImageGetAll`, and `ImageLoad` exchange Docker image tarballs.

System flows are read-mostly. `/auth` validates registry credentials and can return an identity token. `/info`, `/version`, and `/_ping` expose daemon capabilities and health. `/events` streams or bounds event messages based on `since`, `until`, and JSON-encoded filters. `/system/df` aggregates disk usage across images, containers, and volumes.

Exec flow is two-phase. `POST /containers/{id}/exec` creates an exec instance with command, attach, TTY, env, user, privilege, and working-directory settings. `POST /exec/{id}/start` starts that instance and either detaches or establishes an interactive raw-stream session. `POST /exec/{id}/resize` changes TTY dimensions when a TTY-backed exec is active. `GET /exec/{id}/json` reports running state, exit code, process config, open streams, container ID, and host PID.

## State And Persistence Behavior

The YAML file itself persists no runtime state, but it specifies daemon operations that read and mutate Docker state:

- Container creation persists a container record and its configuration under daemon state, usually below the Docker root directory reported by `SystemInfo.DockerRootDir`.
- Start/stop/restart/kill/pause/unpause/update/rename/delete mutate container runtime or metadata state. `AutoRemove` and delete flags can remove persisted container state and optionally associated anonymous volumes.
- `RestartPolicy` affects future daemon behavior after container exit, with exponential backoff documented in the schema.
- `Mount`, `MountPoint`, `Volume`, and `PortMap` fields connect container state to persistent host storage, volume drivers, filesystem paths, and host port allocations.
- Logs, attach, and stats read runtime/logging state. Logs are explicitly constrained to containers using `json-file` or `journald` logging drivers.
- Image build/create/load/tag/push/delete/prune operations mutate local image metadata, layer storage, registry-side repositories, or builder cache; image export reads layer metadata and tar content.
- `/events` exposes daemon event history/new events but may hold a streaming connection open.
- `/system/df` reads aggregate storage accounting and includes volume `UsageData` only where available.
- Swarm definitions model persisted raft-backed cluster state and use `ObjectVersion` for optimistic concurrency, even though the actual swarm path operations mostly appear after this chunk.
- `SecretSpec.Data` and `ConfigSpec.Data` represent persisted swarm payloads, with the docs noting that secret data is create-only and not returned by other endpoints.

## Dependencies

This contract depends on Swagger 2.0 semantics, Docker-specific vendor extensions such as `x-go-name` and `x-nullable`, and ReDoc/GitHub-Flavored Markdown rendering for descriptions.

Internal dependencies are mostly `$ref` links among definitions. Examples include `HostConfig` composing `Resources`, `ContainerCreate` combining `ContainerConfig` with `HostConfig` and endpoint settings, `ContainerInspect` reusing `GraphDriverData`, `MountPoint`, `ContainerConfig`, and `NetworkSettings`, `/system/df` reusing `ImageSummary`, `ContainerSummary`, and `Volume`, and exec inspection reusing `ProcessConfig`.

Daemon/runtime dependencies include cgroups, blkio, cpuset, pids, ulimits, Linux namespace modes, Windows isolation/credential specs, OCI runtimes via containerd, graph/storage drivers, log drivers, registry service configuration, plugin systems, volume/network/IPAM drivers, HTTP connection hijacking, websocket attach, tar archive handling, and swarmkit concepts for nodes, services, tasks, secrets, configs, raft, and CA rotation.

Registry operations depend on `X-Registry-Auth` and `AuthConfig` conventions. Several list endpoints use JSON-encoded filter maps passed as query strings, which client tooling must encode exactly as strings rather than nested query parameters.

## Integration Points

Generated clients and SDKs integrate through the `operationId` names and schema definitions. Many operation IDs map directly to Docker CLI actions: `docker ps` to `ContainerList`, `docker create` to `ContainerCreate`, `docker inspect` to `ContainerInspect` or `ImageInspect`, `docker logs` to `ContainerLogs`, `docker attach` to `ContainerAttach`, `docker wait` to `ContainerWait`, `docker cp`-style archive operations to the container archive endpoints, `docker build` to `ImageBuild`, `docker pull`/import to `ImageCreate`, `docker push` to `ImagePush`, `docker system df` to `SystemDataUsage`, and `docker exec` to the exec create/start pair.

The path definitions integrate with daemon route handlers and compatibility tests through status-code contracts. Common responses include `400` for bad parameters, `404` for missing containers/images/exec instances, `409` for state conflicts such as paused containers or name conflicts, `500` for daemon errors, and `101` for upgraded streaming connections.

The schema definitions are cross-cutting integration surfaces for Docker internals and external tools. Container schemas bridge client configuration to host runtime, network, storage, logging, security, and resource subsystems. Image schemas bridge local graphdriver metadata, registries, build progress streams, and tar import/export. Swarm schemas bridge the Engine API to swarmkit manager state, raft concurrency, CA material, and service/task scheduling.

## Risks And Edge Cases

- This is an open-schema API: clients that reject unknown response fields can break when talking to newer daemons.
- Several query parameters are JSON-encoded strings (`filters`, build args, labels, auth configs), so client libraries must avoid treating them as ordinary repeated query fields.
- `PortMap` values can be arrays of bindings or `null`, and `PortBinding.HostPort` is a string, not an integer.
- `ContainerInspect.State.Running` and `Paused` are not mutually exclusive; the docs explicitly recommend using `Status` for state decisions.
- `ContainerLogs`, `ContainerAttach`, `ExecStart`, and related streaming operations require special handling for HTTP hijack, raw multiplexed stream framing, or websocket transport.
- `stdout` and `stderr` log/attach options default to false in several endpoints; callers that forget stream-selection parameters may receive no useful stream.
- Logs work only with `json-file` or `journald`; other logging drivers can produce unsupported behavior.
- `ContainerTop` is Unix-only and not supported on Windows.
- `ContainerResize` says the container must be restarted for resize to take effect, while `ExecResize` only works for TTY exec sessions.
- Resource fields are platform-sensitive. Linux cgroup controls, Windows CPU/isolation options, and credential specs have different validation and behavior.
- `RestartPolicy` has interactions with `AutoRemove`; the schema notes auto-remove has no effect if restart policy is set.
- Mount behavior differs by type: bind and npipe sources must exist, tmpfs must not specify `Source`, and named volumes persist after container removal.
- Registry insecure configuration is documented as testing-only due to security risk.
- `ObjectVersion` makes swarm updates concurrency-sensitive; stale versions are expected to fail.
- The chunk ends inside the `VolumeList` filters documentation, so complete volume endpoint behavior is intentionally deferred to the next chunk.

## Test Signals

Useful validation for this API contract includes:

- OpenAPI linting for valid Swagger 2.0 structure, unique `operationId` values, valid `$ref` targets, declared path parameters, valid response schemas, and media-type consistency.
- Generated-client tests that preserve Docker-specific typing edge cases: string host ports, string-or-`all` tail parameters, JSON-encoded filter/build maps, nullable arrays/maps, binary tar bodies, and raw-stream responses.
- Container lifecycle integration tests covering create, inspect, start, stop, restart, kill with signal, pause/unpause, update resources/restart policy, rename conflicts, wait exit code, delete with force/volume flags, and prune filters.
- Streaming tests for logs, attach, websocket attach, stats, and exec start, including `101` upgrade handling and raw-stream frame demultiplexing.
- Container filesystem tests for changes, export, archive stat headers, archive download, archive extraction, invalid paths, no-such-container, and read-only filesystem errors.
- Image tests covering list filters, build context upload and progress stream, cache prune, pull/import, inspect, history, push with registry auth, tag validation, delete force/prune semantics, search filters/limits, prune filters, commit from container, save/load tar compatibility, and multi-image export.
- System endpoint tests for auth success/failure, `/info` schema stability, `/version`, `/_ping`, event filters and bounded/streaming behavior, and `/system/df` inclusion of image/container/volume usage.
- Exec tests for paused/stopped container conflicts, create/start/inspect lifecycle, detached versus attached starts, TTY resize validation, env/user/working directory propagation, and exit-code reporting.
- Cross-platform tests for Linux-only, Windows-only, and swarm-only fields so clients do not assume every documented field is present or meaningful on every daemon.
