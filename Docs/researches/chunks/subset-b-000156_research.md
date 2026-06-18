# sources/cloud-native/moby/api/docs/v1.53.yaml lines 7938-13879

## Scope And Purpose

This chunk covers the tail of the Docker Engine API v1.53 Swagger/OpenAPI 2.0 `definitions` section and nearly the entire `paths` table from `GET /containers/json` through `POST /session`. It is a public API contract and documentation source, not executable runtime code. Changes here affect generated API docs, generated client/server bindings, and compatibility expectations for Docker Engine API consumers.

The chunk begins inside the `ClusterVolume` definition, adds `ClusterVolumeSpec`, `Topology`, and `ImageManifestSummary`, then defines REST operations for containers, images/builds, system/auth/events, exec, volumes, networks, plugins, swarm nodes and cluster control, services, tasks, secrets, configs, registry distribution inspection, and the deprecated interactive session endpoint. It is source-tree-aligned to `sources/cloud-native/moby/api/docs/v1.53.yaml`; final per-file synthesis should reconcile this with other chunks for the same YAML file.

## API Contract Structure

The path section groups operations by Docker API tags: `Container`, `Image`, `System`, `Exec`, `Volume`, `Network`, `Plugin`, `Node`, `Swarm`, `Service`, `Task`, `Secret`, `Config`, `Distribution`, and `Session`. Most request bodies are JSON objects referencing schemas declared earlier in the same file, while streaming, tar, and plugin endpoints use binary media types such as `application/octet-stream`, `application/x-tar`, `application/vnd.docker.raw-stream`, and `application/vnd.docker.multiplexed-stream`.

The spec relies heavily on Docker conventions that Swagger 2.0 only partially expresses. Many filter parameters are typed as `string` but described as JSON-encoded `map[string][]string` values. Several platform selectors are JSON-encoded OCI platform objects carried in query strings or multi-value query arrays. Some responses are inline object schemas with `title` values instead of reusable named definitions. Vendor extensions such as `x-go-name`, `x-nullable`, and `x-omitempty` continue to shape generated Go/documentation semantics.

## Important Schemas And Types

`ClusterVolume` and `ClusterVolumeSpec` define Swarm cluster volume state and desired configuration. The state side includes plugin-returned context, CSI `VolumeID`, accessible topologies, and per-node `PublishStatus` entries with states `pending-publish`, `published`, `pending-node-unpublish`, and `pending-controller-unpublish`. The spec side controls grouping for scheduling, access mode scope and sharing, mount-vs-block volume intent, CSI plugin secrets sourced from Swarm secrets, topology requirements, capacity ranges, and availability states `active`, `pause`, and `drain`.

`Topology` is a CSI-style object containing `Segments`, a string-to-string map of topological domains and segments. `ClusterVolumeSpec.AccessibilityRequirements` uses lists of these objects for requisite and preferred placement constraints. These schemas bind the Engine API to CSI semantics even though the actual storage interactions happen through Docker/Swarm storage plugins.

`ImageManifestSummary` is introduced with Go name `ManifestSummary`. It summarizes content-addressable image manifests with required `ID`, `Descriptor`, `Available`, `Size`, and `Kind`. `Descriptor` references `OCIDescriptor`; `Kind` distinguishes `image`, BuildKit-generated `attestation`, and `unknown`; `ImageData` includes an `OCIPlatform`, container IDs using the image, and unpacked size; `AttestationData` records the image manifest digest the attestation is for. This schema is important for multi-platform image stores and for APIs that expose manifest-level availability and storage accounting.

The path definitions reuse major schemas declared earlier in the file: `ContainerConfig`, `HostConfig`, `NetworkingConfig`, `ContainerSummary`, `ContainerInspectResponse`, `ContainerStatsResponse`, `ContainerUpdateResponse`, `ContainerWaitResponse`, `ImageInspect`, `ImageSummary`, `ImageDeleteResponseItem`, `BuildCacheDiskUsage`, `AuthConfig`, `AuthResponse`, `SystemInfo`, `SystemVersion`, `EventMessage`, `IDResponse`, `Volume`, `VolumeCreateRequest`, `VolumeListResponse`, `NetworkSummary`, `NetworkInspect`, `NetworkCreateResponse`, `NetworkConnectRequest`, `NetworkDisconnectRequest`, `Plugin`, `PluginPrivilege`, `Node`, `NodeSpec`, `Swarm`, `SwarmSpec`, `Service`, `ServiceSpec`, `ServiceCreateResponse`, `ServiceUpdateResponse`, `Task`, `Secret`, `SecretSpec`, `Config`, `ConfigSpec`, `DistributionInspect`, and `ErrorResponse`.

## Container API Surface

`GET /containers/json` (`ContainerList`) returns `ContainerSummary` arrays, normally only running containers unless `all=true`. It supports `limit`, `size`, and a JSON filter string covering image ancestry, before/since, exposed or published ports, exit code, health, id, Windows isolation, task marker, labels, names, networks, status, and volumes.

`POST /containers/create` (`ContainerCreate`) creates a container from a body combining `ContainerConfig`, `HostConfig`, and `NetworkingConfig`. Query parameters include validated `name` and `platform` in `os[/arch[/variant]]` form. The platform description encodes important behavior: with an explicit platform the daemon checks local image cache compatibility and can return `404`; without one it uses the host platform but may create from an available mismatched image and return a warning.

Inspection, process, log, filesystem, and resource endpoints include `ContainerInspect`, `ContainerTop`, `ContainerLogs`, `ContainerChanges`, `ContainerExport`, and `ContainerStats`. `ContainerTop` is Unix-only because it runs `ps`. `ContainerLogs` only works with `json-file` or `journald` logging drivers and can return raw or multiplexed binary stream data without upgrading the connection. `ContainerChanges` reports writable-layer changes with numeric `Kind` values. `ContainerStats` supports streaming and one-shot modes, documents cgroup v1/v2 differences, and gives CPU and memory calculation formulas.

Lifecycle and mutation endpoints include `ContainerResize`, `ContainerStart`, `ContainerStop`, `ContainerRestart`, `ContainerKill`, `ContainerUpdate`, `ContainerRename`, `ContainerPause`, `ContainerUnpause`, `ContainerWait`, `ContainerDelete`, and `/containers/prune`. The spec uses status codes to encode state: `start`/`stop` return `304` for already-started/already-stopped states, `kill` returns `409` when not running, `delete` can return `409` for running containers unless forced, and prune returns deleted IDs plus reclaimed space.

Interactive and filesystem archive operations are protocol-sensitive. `ContainerAttach` can hijack the HTTP connection, optionally return `101 UPGRADED`, and multiplex stdout/stderr with 8-byte headers when TTY is disabled. `ContainerAttachWebsocket` exposes the same attach model through websocket-style upgrade behavior. `HEAD`, `GET`, and `PUT /containers/{id}/archive` provide path stat metadata through `X-Docker-Container-Path-Stat`, tar export of a container path, and tar extraction into a path, with errors for bad path, missing container/path, read-only filesystems, and non-directory targets.

## Image, Build, Registry, And System API Surface

Image and build operations start with `GET /images/json` (`ImageList`), `POST /build` (`ImageBuild`), `POST /build/prune` (`BuildPrune`), and `POST /images/create` (`ImageCreate`). Build accepts many query controls for Dockerfile path, tags, remote sources, cache settings, labels, squash, network mode, build args, memory/CPU controls, registry auth, platform, target, BuildKit outputs, and builder backend `version` where `1` is classic builder and `2` is BuildKit. Build prune exposes reserved-space, max-used-space, min-free-space, `all`, and filter controls.

Image object operations include `ImageInspect`, `ImageHistory`, `ImagePush`, `ImageTag`, `ImageDelete`, `ImageSearch`, and `ImagePrune`. v1.53 adds multi-platform considerations throughout: image inspect has mutually exclusive `manifests` and `platform`; history and push accept JSON-encoded `OCIPlatform` selection; delete accepts multiple platform strings; save/load endpoints accept multi-value platform query entries. Push and create/pull use `X-Registry-Auth`, while search still models Docker Hub search results including deprecated `is_automated`.

Image archive operations include `ImageGet`, `ImageGetAll`, and `ImageLoad`. The export docs describe the tarball as containing OCI image layout content plus Docker-compatible `manifest.json` and optional `repositories` mapping. These endpoints produce or consume `application/x-tar` and need binary-safe clients.

System endpoints include `SystemAuth`, `SystemInfo`, `SystemVersion`, `SystemPing`, `SystemPingHead`, `ImageCommit`, `SystemEvents`, and `SystemDataUsage`. Ping returns daemon capability headers such as `Api-Version`, `Builder-Version`, `Docker-Experimental`, `Swarm`, `Cache-Control`, and `Pragma`. Events streams Docker object events as JSONL/NDJSON/JSON sequence and supports filters by object, event, scope, labels, and object IDs. Data usage aggregates image, container, volume, and build cache disk usage, with `type` as a multi-value query and `verbose` for detail.

`GET /distribution/{name}/json` (`DistributionInspect`) contacts the registry and returns descriptor and platform information via `DistributionInspect`. It can return `401` for failed authentication or no image found, so consumers should not treat the status as pure authentication failure.

## Exec, Volume, Network, And Plugin API Surface

Exec operations model a two-step command flow inside a running container. `ContainerExec` creates an exec instance with attach flags, console size, detach keys, TTY, environment, command, privilege, user, and working directory. `ExecStart` starts it and either detaches or returns an interactive raw/multiplexed stream. `ExecResize` only applies when TTY was configured, and `ExecInspect` exposes running state, exit code, process config, open streams, container ID, and host PID.

Volume operations include `VolumeList`, `VolumeCreate`, `VolumeInspect`, `VolumeUpdate`, `VolumeDelete`, and `VolumePrune`. Standard local volumes use `Volume` and `VolumeCreateRequest`; `VolumeUpdate` is valid only for Swarm cluster volumes and wraps `ClusterVolumeSpec` under `Spec`. The update contract currently only allows `Availability` to change and requires a `version` query value from the volume's `ClusterVolume` field to avoid conflicting writes.

Network operations include `NetworkList`, `NetworkInspect`, `NetworkDelete`, `NetworkCreate`, `NetworkConnect`, `NetworkDisconnect`, and `NetworkPrune`. Network creation models bridge/local and swarm/global networks, attachable networks, ingress networks, config-only/config-from behavior, IPAM, IPv4/IPv6 enablement, driver options, and labels. Connect requires a local-scoped network or attachable swarm-scoped network and refuses re-attach to a running container; disconnect explicitly disallows swarm-scoped networks.

Plugin operations cover lifecycle and distribution: `PluginList`, `GetPluginPrivileges`, `PluginPull`, `PluginInspect`, `PluginDelete`, `PluginEnable`, `PluginDisable`, `PluginUpgrade`, `PluginCreate`, `PluginPush`, and `PluginSet`. Pull and upgrade accept registry auth and a requested privilege list. Create consumes an `application/x-tar` context containing plugin rootfs and manifest. Delete and disable have force options with operational risk when the plugin is in use.

## Swarm, Service, Task, Secret, And Config API Surface

Swarm node operations include `NodeList`, `NodeInspect`, `NodeDelete`, and `NodeUpdate`. List filters cover ID, engine label, membership, name, node label, and role. `NodeUpdate` uses `NodeSpec` plus a required object version to prevent conflicting writes. These endpoints return `503` when the daemon is not part of a swarm.

Cluster control operations include `SwarmInspect`, `SwarmInit`, `SwarmJoin`, `SwarmLeave`, `SwarmUpdate`, `SwarmUnlockkey`, and `SwarmUnlock`. Init accepts listen/advertise/data-path addresses, data path port, default address pools, subnet size, force-new-cluster, and `SwarmSpec`; join requires `ListenAddr`, `RemoteAddrs`, and `JoinToken`. Update uses optimistic concurrency through required `version` and can rotate worker token, manager token, and manager unlock key. Unlock key retrieval and unlock are tied to manager autolock behavior.

Service operations include `ServiceList`, `ServiceCreate`, `ServiceInspect`, `ServiceDelete`, `ServiceUpdate`, and `ServiceLogs`. Create and update use `ServiceSpec`, support registry auth for pulling private images, and return typed response schemas. Update requires the current service version, can choose registry auth from `spec` or `previous-spec`, and supports server-side rollback by setting `rollback=previous`. Service logs stream stdout/stderr and only work for services using `local`, `json-file`, or `journald` logging drivers.

Task operations include `TaskList`, `TaskInspect`, and `TaskLogs`. Tasks expose swarm scheduler state and container execution status through `Task` objects. List filters include desired state, id, label, name, node, and service. Task logs mirror service log behavior with details, follow, stdout/stderr, since, timestamps, and tail controls.

Secret and config operations are parallel CRUD surfaces for swarm-scoped data. `SecretList`, `SecretCreate`, `SecretInspect`, `SecretDelete`, and `SecretUpdate` use `SecretSpec`; `ConfigList`, `ConfigCreate`, `ConfigInspect`, `ConfigDelete`, and `ConfigUpdate` use `ConfigSpec`. Updates require the current object version and currently only allow `Labels` to change; other fields must remain identical to inspect response values. Create can return `409` on name conflict and all swarm object operations can return `503` outside swarm mode.

## Session API Surface

`POST /session` (`Session`) initializes an interactive session and hijacks the HTTP connection to an HTTP/2 cleartext transport so the daemon can call back to client-exposed gRPC services. The endpoint is explicitly deprecated and the note says servers should support gRPC directly on the listening socket. It returns `101` on successful hijack and uses raw-stream media type.

## Control Flow And State Behavior

The container workflow is split into explicit state transitions: create, start, attach/log/stats/exec, update, pause/unpause, stop/restart/kill, wait, archive/export, delete, and prune. Container configuration persists in daemon state while runtime state, logs, filesystem changes, network endpoints, and stats are exposed through separate endpoints. Mutating endpoints often return empty success bodies but signal important outcomes through status codes.

Image workflows integrate local content store state, registry state, and build state. Pull/import/create, build, tag, push, save, load, delete, and prune mutate image references, manifest/content availability, unpacked snapshots, and build cache. Multi-platform controls are a central state dimension in v1.53: platform selectors can narrow inspect, history, push, delete, save, and load behavior, and `ImageManifestSummary` tracks per-manifest availability and storage size.

Swarm workflows rely on Raft-managed object versions for safe updates. Node, swarm, service, cluster-volume, secret, and config updates require a `version` query value so clients must inspect/list first, then submit an update against the current version. Availability and desired-state fields do not directly perform work in-process; they alter desired cluster state and Swarm reconciles tasks, nodes, services, volumes, secrets, configs, and networks asynchronously.

Streaming endpoints are long-lived control flows rather than ordinary request/response calls. Attach, exec start, logs, service logs, task logs, stats, events, and session can hold connections open, send binary or newline-delimited data, use HTTP upgrade/hijack, and change payload framing based on TTY and media type. Generic OpenAPI clients are likely to need custom transport code for these operations.

## Dependencies And Integration Points

The spec depends on Docker Engine subsystems: container runtime/containerd/OCI runtime execution, image store and content store, BuildKit/classic builder, registry authentication and distribution, log drivers, graph/storage drivers, cgroups, network drivers/IPAM, volume drivers and CSI-like cluster volume plugins, plugin management, SwarmKit, Raft object versioning, task scheduler, secrets/configs storage, and daemon event broadcasting.

External protocol dependencies include HTTP clients capable of binary-safe tar transfer, raw stream handling, connection hijacking, websocket or upgrade semantics, long-lived JSON stream consumption, and base64/base64url registry auth headers. OpenAPI tooling must tolerate Swagger 2.0 limitations around JSON-in-query, arrays in query, inline object schemas, binary streams, and vendor extensions.

Integration with OCI is visible through descriptors, platforms, image layout tarball docs, and platform-selection query strings. Integration with CSI appears in cluster volume topology, capacity, secrets, publish status, and plugin-returned IDs/contexts. Swarm integration appears across nodes, services, tasks, networks, secrets, configs, cluster volumes, join tokens, unlock keys, and `503` swarm-not-available failure modes.

## Risks And Edge Cases

The largest generated-client risk is transport mismatch. Attach, exec start, logs, service logs, task logs, stats, events, image/container archive transfer, plugin tar contexts, and session cannot be treated as simple JSON calls. Clients must parse multiplexed stream frames when TTY is disabled, pass raw PTY bytes when TTY is enabled, stream NDJSON-like events, and avoid buffering unbounded responses.

JSON-in-query and JSON-encoded platform parameters are easy to mis-generate. Filters are often declared as `string` despite representing `map[string][]string`; system data usage and several image archive/platform endpoints use array query forms; image inspect marks `manifests` and `platform` as mutually exclusive in prose rather than schema validation. Tests should verify exact wire encoding, not just type generation.

Optimistic concurrency is contractually important for Swarm objects. Node, swarm, service, cluster volume, secret, and config updates require current version numbers. Secret/config updates only allow label mutation despite accepting full specs. Service update rollback ignores the supplied spec when `rollback=previous`, which is a non-obvious control-flow branch.

Status code semantics encode many state edge cases: `304` for already-started/stopped containers, `409` for conflicts and stopped container kill, `403` for unsupported network/plugin/filesystem operations, `503` for swarm-only endpoints when not in swarm mode, `401` for distribution inspect authentication or missing image, and `204` empty successes on many deletes/creates/pulls/upgrades. Generated SDKs should not collapse these into generic success/failure without preserving meaning.

Platform and daemon feature variance is explicit. `ContainerTop` is unsupported on Windows, stats differ across cgroup v1 and v2, BuildKit support differs by platform and daemon recommendation, overlay/network operations depend on swarm membership, native Windows images use classic builder by default, and driver-specific maps must remain opaque.

There are documentation/contract footguns in this range. The `ClusterVolumeSpec.AccessMode.MountVolume` indentation in the YAML prose is unusual and should be validated against the full parser. Some comments acknowledge Swagger 2.0 limits, such as inability to `$ref` `OCIPlatform` inside array query parameters. Deprecated surfaces remain present (`/session`, search `is_automated`, classic builder) and should be maintained for compatibility until intentionally removed.

## Test Signals

Parse the full `sources/cloud-native/moby/api/docs/v1.53.yaml` as Swagger/OpenAPI 2.0 and verify every `$ref` target referenced in lines 7938-13879 resolves, including new `ClusterVolumeSpec`, `Topology`, and `ImageManifestSummary` references. Validate that vendor extensions and inline titled schemas survive the documentation/client generation pipeline.

Contract tests should cover representative filter encoding for containers, images, build prune, events, volumes, networks, plugins, nodes, services, tasks, secrets, configs, and prunes. They should also cover JSON-encoded OCI platform query values, multi-value platform arrays, mutually exclusive `manifests`/`platform`, registry auth headers, and required object `version` parameters for update endpoints.

Stateful integration tests should exercise container create/start/inspect/logs/stats/update/pause/unpause/stop/wait/archive/delete/prune; image build/pull/tag/push/inspect/history/save/load/delete/prune; exec create/start/resize/inspect; volume create/update/delete/prune; network create/connect/disconnect/delete/prune; plugin pull/enable/disable/set/delete; and swarm init/join/update/service/task/secret/config flows where test infrastructure supports swarm mode.

Transport tests need real HTTP clients rather than pure schema mocks. Cover attach with and without upgrade, websocket attach, TTY and non-TTY stream framing, exec start streaming and detached modes, service/task/container logs with `follow`, stats streaming versus one-shot, events until/since streaming, tar upload/download for images/containers/plugins, and deprecated `/session` h2c hijack behavior if still supported by the daemon under test.

Negative tests should assert documented status codes and error schema bodies: missing objects return `404`, invalid inputs return `400`, conflicts return `409`, forbidden operations return `403`, swarm-only endpoints return `503` outside swarm mode, stopped container kill returns `409`, and distribution inspect can return `401` for either auth failure or no image found. Compatibility tests should ensure clients ignore unknown response fields and preserve opaque driver/plugin/status maps.
