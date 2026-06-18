# sources/cloud-native/moby/api/docs/v1.47.yaml lines 7687-12956

## Scope And Purpose

This chunk is a large path-section slice of the Docker Engine API v1.47 Swagger 2.0 document. It starts at the tail of a container endpoint and then covers the API contract from `ContainerExport` through the experimental session handshake. The source is documentation and schema contract, not executable daemon code, but its path names, `operationId` values, parameters, response codes, media types, examples, and `$ref` schemas drive generated API docs, client bindings, SDK behavior, and route conformance expectations.

The range covers most high-impact Engine surfaces after basic container inspect/log/change APIs: container export/stats/lifecycle/update/attach/archive/prune, image/build/registry/auth/system APIs, exec APIs, volume/network/plugin APIs, swarm/node/service/task/secret/config APIs, distribution inspection, and `/session`. It is source-tree-aligned with `sources/cloud-native/moby/api/docs/v1.47.yaml` and should later be merged with adjacent chunks for full-file conclusions.

## OpenAPI Shape

All operations are under the `paths` map and use Swagger 2.0 conventions: path parameters such as `id`, `name`, and `path`; query parameters for filters, booleans, version indexes, and transport controls; body schemas via inline objects, `allOf`, and `$ref`; and standard `#/definitions/ErrorResponse` error payloads. Tags group the operations into `Container`, `Image`, `System`, `Exec`, `Volume`, `Network`, `Plugin`, `Node`, `Swarm`, `Service`, `Task`, `Secret`, `Config`, `Distribution`, and `Session`.

Referenced definitions in this slice include `Resources`, `RestartPolicy`, `ContainerWaitResponse`, `ImageSummary`, `BuildCache`, `IdResponse`, `ImageInspect`, `ImageHistoryResponseItem`, `ImageDeleteResponseItem`, `AuthConfig`, `SystemInfo`, `SystemVersion`, `EventMessage`, `ContainerConfig`, `ProcessConfig`, `VolumeListResponse`, `Volume`, `VolumeCreateOptions`, `ClusterVolumeSpec`, `Network`, `NetworkCreateResponse`, `EndpointSettings`, `Plugin`, `PluginPrivilege`, `Node`, `NodeSpec`, `Swarm`, `SwarmSpec`, `Service`, `ServiceSpec`, `ServiceCreateResponse`, `ServiceUpdateResponse`, `Task`, `Secret`, `SecretSpec`, `Config`, `ConfigSpec`, and `DistributionInspect`.

## Container APIs

The container section exposes lifecycle, filesystem, streaming, and cleanup operations:

- `GET /containers/{id}/export` (`ContainerExport`) streams a container filesystem tarball as `application/octet-stream`.
- `GET /containers/{id}/stats` (`ContainerStats`) returns a live or one-shot JSON stats stream. The documentation gives CPU and memory usage formulas and calls out cgroup v2 gaps: many `blkio_stats` fields, `cpu_usage.percpu_usage`, `memory_stats.max_usage`, and `memory_stats.failcnt` are not populated, and cgroup v1/v2 memory stat keys differ.
- `POST /containers/{id}/resize` (`ContainerResize`) resizes a TTY with required `h` and `w` query integers.
- `ContainerStart`, `ContainerStop`, `ContainerRestart`, and `ContainerKill` mutate runtime state. They distinguish success (`204`), already-started/stopped idempotence (`304` for start/stop), missing containers (`404`), stopped-container kill conflict (`409`), and daemon errors (`500`). Stop/restart accept `signal` and timeout `t`; kill defaults `signal` to `SIGKILL`; start accepts `detachKeys`.
- `POST /containers/{id}/update` (`ContainerUpdate`) accepts `Resources` plus `RestartPolicy`, returning a `Warnings` array. This ties the update API to the same resource model used during container creation.
- `ContainerRename`, `ContainerPause`, and `ContainerUnpause` mutate naming and freezer-cgroup state. Pause explicitly uses cgroup freezer semantics rather than observable `SIGSTOP`.
- `POST /containers/{id}/attach` (`ContainerAttach`) hijacks the HTTP connection for stdin/stdout/stderr, optionally returning `101 UPGRADED` when clients request `Upgrade: tcp`, or `200` without upgrade headers. Non-TTY streams use Docker's multiplexed frame format with an 8-byte header; TTY streams are raw bytes.
- `GET /containers/{id}/attach/ws` (`ContainerAttachWebsocket`) provides websocket attach with equivalent stream selectors.
- `POST /containers/{id}/wait` (`ContainerWait`) blocks until a container reaches a requested condition (`not-running`, `next-exit`, or `removed`) and returns `ContainerWaitResponse`.
- `DELETE /containers/{id}` (`ContainerDelete`) removes a container with `v`, `force`, and `link` query booleans. Running or paused containers can produce a `409` conflict unless forced.
- `HEAD`, `GET`, and `PUT /containers/{id}/archive` cover path metadata, tar export, and tar extraction. `path` is required, `noOverwriteDirNonDir` protects file/directory replacement, and `copyUIDGID` asks extraction to copy ownership from the destination directory. Upload consumes `application/x-tar` or octet-stream and may be compressed as identity, gzip, bzip2, or xz.
- `POST /containers/prune` (`ContainerPrune`) deletes stopped containers using JSON-encoded `until` and label filters and returns deleted IDs plus reclaimed bytes.

## Image, Build, Registry, And Auth APIs

`GET /images/json` (`ImageList`) lists image summaries with `all`, `digests`, `shared-size`, and JSON filters for dangling state, labels, references, and before/since image relationships.

`POST /build` (`ImageBuild`) is the broadest single operation in this chunk. It consumes a compressed tar build context or remote context, performs preliminary Dockerfile validation, emits JSON build progress, and cancels if the client disconnects. Query/header controls include Dockerfile path, one or more tags (`t`), extra hosts, `remote`, quiet/no-cache/cache-from/pull flags, intermediate container cleanup (`rm`, `forcerm`), resource limits, `buildargs` JSON, shared-memory size, experimental squash, labels, build network mode, content type, `X-Registry-Config`, target platform, target build stage, BuildKit `outputs`, and builder backend `version` (`1` classic daemon builder or `2` BuildKit).

`POST /build/prune` (`BuildPrune`) removes build cache. It accepts `all`, `keep-storage`, and JSON filters such as `until`, `id`, `parent`, `type`, `description`, `inuse`, `shared`, and `private`, returning deleted cache IDs and reclaimed bytes.

Image distribution and local store operations include:

- `POST /images/create` (`ImageCreate`) pulls or imports an image. It uses `fromImage`, `fromSrc`, `repo`, `tag`, optional `message`, `platform`, `changes`, and `X-Registry-Auth`.
- `GET /images/{name}/json` (`ImageInspect`) and `GET /images/{name}/history` (`ImageHistory`) expose image metadata and layer history.
- `POST /images/{name}/push` (`ImagePush`) pushes to a registry and can select a platform variant with JSON-encoded OCI platform data. It requires registry auth for private registries.
- `POST /images/{name}/tag` (`ImageTag`) creates a tag with `repo` and `tag`, returning `201`.
- `DELETE /images/{name}` (`ImageDelete`) removes image references/layers with `force` and `noprune`, returning `ImageDeleteResponseItem` records.
- `GET /images/search` (`ImageSearch`) searches registries with `term`, optional `limit`, and JSON filters.
- `POST /images/prune` (`ImagePrune`) deletes unused images, especially controlled by `dangling` and label filters.
- `GET /images/{name}/get` (`ImageGet`) and `GET /images/get` (`ImageGetAll`) export one or multiple images as tar streams; `ImageGetAll` takes repeated `names`.
- `POST /images/load` (`ImageLoad`) imports images from a tar stream, with `quiet` suppressing progress.
- `POST /auth` (`SystemAuth`) validates registry credentials from `AuthConfig` and may return an identity token.
- `GET /distribution/{name}/json` (`DistributionInspect`) contacts a registry to return image descriptor and platform information rather than local image state.

## System APIs

`GET /info` (`SystemInfo`) returns the daemon-wide `SystemInfo` snapshot. `GET /version` (`SystemVersion`) returns version/build/platform/API-bound metadata. `GET` and `HEAD /_ping` (`SystemPing`, `SystemPingHead`) provide health checks and response headers for API version, builder version, Swarm status, cache-control, and experimental mode.

`POST /commit` (`ImageCommit`) creates an image from a container with repository/tag/comment/author/pause/changes query controls and optional `ContainerConfig`. `GET /events` (`SystemEvents`) streams daemon events with `since`, `until`, and JSON filters across container, image, volume, network, daemon, plugin, node, service, secret, config, scope, label, and event type. `GET /system/df` (`SystemDataUsage`) aggregates disk usage for images, containers, volumes, and build cache.

## Exec APIs

`POST /containers/{id}/exec` (`ContainerExec`) creates an exec instance with stream attachment booleans, detach keys, TTY, env, command, privileged flag, user, working directory, and console dimensions. It returns an `IdResponse`, with explicit missing-container and paused-container errors.

`POST /exec/{id}/start` (`ExecStart`) starts the exec instance and can detach or attach over `application/vnd.docker.raw-stream` / `application/vnd.docker.multiplexed-stream`. `POST /exec/{id}/resize` (`ExecResize`) resizes an exec TTY with required `h` and `w`. `GET /exec/{id}/json` (`ExecInspect`) returns runtime state including `Running`, `ExitCode`, `ProcessConfig`, stream-open booleans, `CanRemove`, `ContainerID`, `DetachKeys`, and host `Pid`.

## Volume, Network, And Plugin APIs

Volume operations cover list/create/inspect/update/delete/prune. `VolumeList` supports JSON filters for dangling, driver, label, name, and id. `VolumeCreate` takes `VolumeCreateOptions`. `VolumeUpdate` applies `ClusterVolumeSpec` and requires a `version` query to avoid conflicting writes. `VolumeDelete` has `force`, and `VolumePrune` returns deleted volume names and reclaimed bytes.

Network operations cover list, inspect, delete, create, connect, disconnect, and prune. `NetworkList` accepts filters including dangling, driver, id, label, name, scope, and type. `NetworkInspect` can include `verbose` and `scope`. `NetworkCreate` accepts name, `CheckDuplicate`, driver, scope, IPAM, internal/attachable/ingress/config-only flags, config-from, options, labels, IPv4/IPv6 enablement, and responds with `NetworkCreateResponse`. Connect/disconnect accept container IDs and endpoint config or force disconnect, and swarm-scoped networks can reject unsupported operations with `403`. `NetworkPrune` uses `until` and label filters.

Plugin operations expose list, privilege discovery, pull/install, inspect, remove, enable, disable, upgrade, create, push, and set/configure. Pull and upgrade consume privilege acceptance data and use `X-Registry-Auth`; create points at a tar rootfs/manifest path; enable has a timeout; disable/delete can be forced; set takes an array of settings. This part of the contract integrates daemon plugin management with registry and privilege workflows.

## Swarm, Node, Service, Task, Secret, And Config APIs

Node APIs list, inspect, delete, and update swarm nodes. List filters include id, label, membership, name, node.label, role, and name prefixes. `NodeUpdate` requires a `NodeSpec` body and `version` query for optimistic concurrency. Most node endpoints return `503` when the local daemon is not part of a swarm.

Swarm APIs include inspect, init, join, leave, update, unlock-key retrieval, and unlock. `SwarmInit` returns the new node ID and configures listen/advertise/data-path addresses, data-path port, default address pools, subnet size, force-new-cluster, and `SwarmSpec`. `SwarmJoin` requires `ListenAddr`, `RemoteAddrs`, and `JoinToken`. `SwarmLeave` has a dangerous `force` option that can break the cluster or remove the last manager. `SwarmUpdate` requires a `version` and can rotate worker token, manager token, or manager unlock key. `SwarmUnlockkey` returns sensitive unlock material; `SwarmUnlock` submits it.

Service APIs list, create, inspect, delete, update, and stream logs. `ServiceCreate` and `ServiceUpdate` consume `ServiceSpec`; the examples cover container image/args, mounts, hosts, DNS, secrets, log drivers, resources, restart policy, replicated mode, update and rollback configs, endpoint ports, and labels. Create accepts `X-Registry-Auth`; update requires a `version`, can select `registryAuthFrom=spec|previous-spec`, and can perform server-side rollback with `rollback=previous`.

Task APIs list and inspect scheduler tasks and stream task logs. Task list filters include desired state, id, label, name, node, and service. The examples show task versions, status timestamps, shutdown/running state, container status, desired state, service/node/slot identifiers, and network attachments.

Secret and config APIs are parallel swarm object lifecycles: list with JSON filters, create returning `IdResponse`, inspect returning versioned object metadata, delete returning `204`, and update requiring `version`. Secret create uses `SecretSpec` and may include base64 `Data` or an external driver; config create uses `ConfigSpec` and base64 `Data`. Both update descriptions state that only `Labels` are mutable and all other fields must match the inspect response.

## Distribution And Session

`DistributionInspect` queries remote registry metadata for a named image and returns `DistributionInspect`, with `401` used for failed authentication or missing image. This is registry-backed and should not be confused with local `ImageInspect`.

`POST /session` (`Session`) initializes an interactive session by hijacking the HTTP connection to an h2c HTTP/2 transport. The daemon can then call back to client-exposed gRPC services. Success is `101`, and bad parameters or server failures use `ErrorResponse`.

## Control Flow

The chunk documents externally observable flows rather than implementation code. Container lifecycle flows move through create/start/attach/stats/stop/wait/delete, with streaming and blocking calls dependent on container state. Archive flows first inspect or stream a container path, then optionally write a tar stream back into the container filesystem. Prune flows are filter-driven cleanup operations that return object IDs/names and reclaimed bytes.

Build and image flows bridge local daemon state, remote registries, tar streams, and BuildKit/classic builder backends. Build accepts either a client-uploaded context or daemon-fetched remote context, uses registry config for base images, emits progress, and is canceled on disconnect. Pull/push/create/distribution inspect depend on registry auth headers and remote availability; load/save/export use binary tar streams.

Swarm and service flows use read-modify-write concurrency. Clients inspect versioned objects, submit full specs with `version`, and handle stale version rejection. Service update can either apply the supplied spec or ignore it for `rollback=previous`. Logs, stats, events, attach, exec start, image build, image push/pull, and session use long-lived or hijacked transports that ordinary JSON clients must special-case.

## State And Persistence Behavior

Container lifecycle endpoints mutate runtime state and sometimes persistent metadata such as names, restart policy, and resource settings. Container archives and export expose filesystem state; stats, attach, wait, and logs observe live runtime state. Container prune and delete reclaim persisted container metadata, root filesystems, and optionally volumes/links.

Image and build endpoints mutate the local image store, layer store, tags, build cache, and registry references. `ImageCommit` snapshots a container into a new image. `BuildPrune` and `ImagePrune` delete stored build/image data, while `ImageLoad` and `ImageGet` move persistent image state through tar archives.

Volumes and networks are persistent daemon objects backed by drivers. Volume update is versioned for cluster volumes; network connect/disconnect changes endpoint attachment state. Plugin endpoints mutate installed plugin state, enabled/disabled state, settings, and registry-pulled plugin artifacts.

Swarm, node, service, task, secret, and config endpoints read and mutate Raft-backed cluster state. Version indexes guard node, swarm, service, secret, config, and cluster volume updates. Secret/config data is create-time sensitive material; updates are label-only in this API. Task objects are scheduler state derived from service desired state and node execution.

Session state is a live upgraded connection, not a persisted object. Distribution inspection reads remote registry state and returns descriptor/platform metadata without changing local image state.

## Dependencies And Integration Points

This YAML depends on Moby's Swagger/ReDoc documentation pipeline and any generated clients that consume `operationId`, `$ref`, `allOf`, examples, response codes, and media types. Any change to schema names, parameter names, response status codes, enum values, or nullability/format hints can affect generated SDKs and user code.

Runtime subsystems implied by this contract include the Docker daemon HTTP router, container runtime and TTY handling, cgroups v1/v2 stats collection, logging drivers, filesystem archive copy logic, graph/image stores, registry resolver and auth handling, BuildKit/classic builder, build cache, system event broadcaster, volume and network drivers/IPAM, plugin manager, swarmkit managers/agents/Raft state, scheduler, secret/config stores, and h2c session transport.

The transport surface is a major integration point. Standard JSON endpoints coexist with binary tar endpoints, octet-stream import/export, streaming JSON progress, raw stream/multiplexed stream attach and exec protocols, websocket attach, live event/stats streams, registry-auth headers, and HTTP connection upgrades for attach and session.

## Risks And Edge Cases

- The chunk begins at the tail of a previous container endpoint, so final per-file research should merge adjacent chunks before claiming complete coverage of the preceding operation.
- `ContainerStats` has cgroup v1/v2 behavioral differences; clients must tolerate missing fields and different memory accounting keys.
- Attach, exec start, service logs, task logs, and session require special transport handling. Generic JSON clients or proxies can break hijacking, websocket, h2c, and multiplexed frame semantics.
- TTY mode changes attach stream framing from multiplexed stdout/stderr to raw PTY bytes.
- `stream`, `one-shot`, `follow`, stdout/stderr selectors, and `tail` defaults can produce empty or long-lived responses if clients set them incorrectly.
- Archive upload can overwrite container paths unless `noOverwriteDirNonDir` is used correctly; read-only roots and missing paths map to different error codes.
- Build args are explicitly not for secret values, while registry auth headers/configs contain credentials and must not be logged.
- `ImageBuild` backend `version` defaults to classic builder in this API contract even though daemons may recommend BuildKit through `_ping`; tests must keep both concepts distinct.
- Platform selection on build, create, push, and registry inspection can fail when requested variants are unavailable.
- Delete/prune endpoints are destructive and filter-driven; malformed JSON filters or broad filters can delete more state than intended.
- Swarm `force` operations can intentionally break clusters; token and unlock-key rotation/retrieval expose sensitive operational material.
- Version query parameters are required concurrency guards for updates. Stale client-side specs can be rejected or accidentally overwrite desired state if clients skip an inspect-before-update flow.
- Service update rollback ignores the supplied body when `rollback=previous`; clients must not assume submitted fields were applied.
- Secret/config update bodies are specs but only labels are mutable. Changing data, names, or driver fields should be treated as invalid.
- Service/task logs only work for supported logging drivers such as `local`, `json-file`, or `journald`.
- `DistributionInspect` returns `401` for both authentication failure and no image found, so callers need careful error messaging.
- Plugin pull/upgrade privilege acceptance and registry auth combine security-sensitive user consent with credential handling.

## Test Signals

Strong contract-level tests include YAML parsing, Swagger 2.0 validation, `$ref` resolution, unique `operationId` checks, path parameter declaration checks, and generated client/type compilation for API v1.47.

Compatibility tests should snapshot parameter names/types/defaults, body schemas, response codes, tags, media types, and examples for high-impact operations such as `ContainerAttach`, `ContainerStats`, `ImageBuild`, `ImagePush`, `SystemPing`, `ExecStart`, `NetworkCreate`, `PluginPull`, `SwarmUpdate`, `ServiceUpdate`, `TaskLogs`, `SecretUpdate`, `ConfigUpdate`, `DistributionInspect`, and `Session`.

Runtime integration tests should cover representative endpoint classes: container lifecycle state transitions and conflicts; stats on cgroup v1 and v2; attach/exec raw and multiplexed streams with and without TTY; archive HEAD/GET/PUT including overwrite and permission cases; build with local context, remote context, BuildKit output, registry config, and disconnect cancellation; image pull/push/load/save/delete/prune; auth success/failure; events streaming and filters; volume/network/plugin lifecycle; swarm init/join/leave/update/unlock; service create/update/rollback/logs; task list/inspect/logs; secret/config create/inspect/update/delete; distribution inspect against public, private, and missing registry references; and session h2c upgrade.

Negative tests should assert documented `400`, `401`, `403`, `404`, `409`, `500`, and `503` mappings for bad parameters, bad auth, unsupported swarm/network operations, missing objects, name conflicts, paused/stopped/running conflicts, stale versions, unavailable swarm state, unsupported logging drivers, malformed filter JSON, and failed connection upgrade parameters.
