# sources/cloud-native/moby/api/docs/v1.51.yaml lines 7727-13463

## Scope And Purpose

This chunk is the main `paths` section of the Docker Engine API v1.51 Swagger/OpenAPI 2.0 specification. It is not executable daemon code, but it is an authoritative HTTP contract used by generated API documentation, clients, tests, and server-routing expectations. The range starts inside `GET /containers/json` and continues through the final `POST /session` operation.

The covered API surface spans containers, images/builds, system/auth/events/disk usage, exec instances, volumes, networks, plugins, swarm nodes, swarm lifecycle, services, tasks, secrets, configs, registry distribution inspection, and interactive session setup. Shared schemas referenced here are defined earlier in the same YAML file; this chunk binds those types to concrete HTTP methods, paths, parameters, response codes, media types, and examples.

## API Contract Shape

Most operations use Docker Engine's standard object-oriented REST pattern: list, create, inspect, update or mutate, delete, and prune. Path variables such as `{id}`, `{name}`, and `{id}/update` are often documented as accepting either an ID or a human name. JSON responses commonly reference earlier `definitions` entries, and error responses use `ErrorResponse`.

Many query parameters are typed as simple OpenAPI strings even when the wire contract is structured. Filters are repeatedly encoded as JSON `map[string][]string` values for containers, images, builder cache, events, volumes, networks, plugins, nodes, services, tasks, secrets, configs, and prune endpoints. Registry auth headers are base64url-encoded JSON. Build and image export/import operations use tar streams and octet-stream bodies rather than ordinary JSON.

The chunk also defines protocol behavior that generic Swagger clients do not model well: connection hijacking for attach and session setup, websocket attach, raw and multiplexed stream media types, streamed JSON build/events/stats payloads, binary tar archives, and long-lived log streams.

## Important APIs And Types

Container operations dominate the beginning of the chunk. `ContainerList` returns `ContainerSummary` values and accepts `all`, `limit`, `size`, and rich filters such as ancestor, before/since, expose/publish, health, label, name, network, status, and volume. `ContainerCreate` accepts a request body composed from `ContainerConfig`, `HostConfig`, and `NetworkingConfig`, plus optional `name` and `platform` query parameters. `ContainerInspect`, `ContainerTop`, `ContainerLogs`, `ContainerChanges`, `ContainerExport`, `ContainerStats`, `ContainerResize`, `ContainerStart`, `ContainerStop`, `ContainerRestart`, `ContainerKill`, `ContainerUpdate`, `ContainerRename`, `ContainerPause`, `ContainerUnpause`, `ContainerAttach`, `ContainerAttachWebsocket`, `ContainerWait`, `ContainerDelete`, `ContainerArchiveInfo`, `ContainerArchive`, `PutContainerArchive`, and `ContainerPrune` define the full container lifecycle and filesystem/log/streaming surface.

Image and build operations include `ImageList`, `ImageBuild`, `BuildPrune`, `ImageCreate`, `ImageInspect`, `ImageHistory`, `ImagePush`, `ImageTag`, `ImageDelete`, `ImageSearch`, `ImagePrune`, `ImageCommit`, `ImageGet`, `ImageGetAll`, and `ImageLoad`. These operations reference `ImageSummary`, `ImageInspect`, `ImageHistoryResponseItem`, `ImageDeleteResponseItem`, `IDResponse`, `ContainerConfig`, and build/prune response objects. v1.51-specific image paths expose platform-aware behavior through query parameters such as `platform`, `platforms`, and `manifests` on inspect/list/delete/export/load-related operations.

System operations include `SystemAuth`, `SystemInfo`, `SystemVersion`, `SystemPing`, `SystemPingHead`, `SystemEvents`, and `SystemDataUsage`. Ping responses expose daemon headers such as API version, builder version, experimental mode, Swarm state, and no-cache controls. Events stream `EventMessage` objects and can be filtered by object type and scope across containers, images, volumes, networks, daemon, plugins, nodes, services, secrets, and configs. Disk usage returns images, containers, volumes, and build cache records with an optional `type` filter.

Exec APIs are grouped under `Exec`: `ContainerExec` creates an exec instance with attach flags, TTY, console size, environment, command, privilege, user, and working-directory settings; `ExecStart` starts it with detach/TTY/console-size controls and raw/multiplexed stream output; `ExecResize` resizes a TTY exec session; `ExecInspect` returns running state, exit code, process config, PID, and container ID.

Volume APIs include `VolumeList`, `VolumeCreate`, `VolumeInspect`, `VolumeUpdate`, `VolumeDelete`, and `VolumePrune`. `VolumeUpdate` is only valid for swarm cluster volumes and uses `ClusterVolumeSpec` plus a required `version` query parameter for optimistic concurrency. Volume deletion has a `force` flag and can return conflict when a volume is in use.

Network APIs include `NetworkList`, `NetworkInspect`, `NetworkDelete`, `NetworkCreate`, `NetworkConnect`, `NetworkDisconnect`, and `NetworkPrune`. Network creation accepts name, driver, scope, internal/attachable/ingress/config-only flags, config source, IPAM, IPv4/IPv6 toggles, options, and labels. Network connect embeds an `EndpointSettings` object, while disconnect can force removal. Swarm-scoped network restrictions are explicitly represented in `403` responses.

Plugin APIs include `PluginList`, `GetPluginPrivileges`, `PluginPull`, `PluginInspect`, `PluginDelete`, `PluginEnable`, `PluginDisable`, `PluginUpgrade`, `PluginCreate`, `PluginPush`, and `PluginSet`. They use `Plugin`, `PluginPrivilege`, registry auth headers, privilege arrays, tar plugin contexts, force/timeout controls, and string arrays of settings.

Swarm and orchestration operations cover `NodeList`, `NodeInspect`, `NodeDelete`, `NodeUpdate`, `SwarmInspect`, `SwarmInit`, `SwarmJoin`, `SwarmLeave`, `SwarmUpdate`, `SwarmUnlockkey`, `SwarmUnlock`, `ServiceList`, `ServiceCreate`, `ServiceInspect`, `ServiceDelete`, `ServiceUpdate`, `ServiceLogs`, `TaskList`, `TaskInspect`, and `TaskLogs`. These bind `Node`, `NodeSpec`, `Swarm`, `SwarmSpec`, `Service`, `ServiceSpec`, `ServiceCreateResponse`, `ServiceUpdateResponse`, and `Task` definitions to HTTP behavior.

Secret and config operations are parallel: `SecretList`, `SecretCreate`, `SecretInspect`, `SecretDelete`, `SecretUpdate`, `ConfigList`, `ConfigCreate`, `ConfigInspect`, `ConfigDelete`, and `ConfigUpdate`. Updates require a `version` query parameter and document that only labels can be changed; all other fields must remain equal to inspect output. `DistributionInspect` queries registry metadata for an image name and returns `DistributionInspect`. `Session` initializes an upgraded/hijacked HTTP2 cleartext session for client callback services.

## Control Flow And Protocol Behavior

The container workflow is encoded as separate calls: list or create, inspect, start, attach/log/stats/resize, update resources, pause/unpause, wait, stop/restart/kill, archive/copy filesystem data, delete, and prune stopped containers. Status codes convey state transitions: start and stop return `204` on state change and `304` when already started or stopped; kill returns `409` when the target is not running; delete can return `409` for running containers unless forced.

Attach and exec-start are the most complex wire protocols. Container attach can return `200` or `101 UPGRADED`, hijacks the HTTP connection, and can stream stdin/stdout/stderr. Without TTY, stdout and stderr use Docker's multiplexed binary frame format; with TTY enabled, the stream is raw PTY data. `ContainerAttachWebsocket` exposes a websocket variant. `ExecStart` mirrors raw/multiplexed behavior for exec processes. `Session` also upgrades/hijacks the connection, but to h2c so the daemon can call back to client-provided gRPC services.

Logs and events are long-lived streams controlled by query parameters. Container, service, and task logs support `details`, `follow`, `stdout`, `stderr`, `since`, `timestamps`, and `tail` variants depending on object type, and only work for documented logging drivers. Events stream after optional historical `since` output until an optional `until` cutoff. Stats can stream repeated resource samples or return a one-shot snapshot with `stream=false` and `one-shot=true`.

Build, image load/export, container export, and archive operations use tar or binary streams. `ImageBuild` accepts a compressed tar build context and has many query/header controls for Dockerfile path, tags, remote context, cache, resource limits, build args, labels, network mode, content type, registry config, platform, target, BuildKit outputs, and builder version. Container archive `HEAD` returns metadata through `X-Docker-Container-Path-Stat`; `GET` returns tar content; `PUT` extracts tar content with options for overwrite and UID/GID handling.

Swarm control flow uses optimistic concurrency and cluster membership checks. Node, swarm, service, secret, config, and cluster-volume updates require a `version` query parameter to prevent conflicting writes. Swarm operations return `503` when a daemon is not part of a swarm, while init/join use `503` for already-in-swarm conditions. Service update has additional controls for registry-auth source and rollback behavior.

## State And Persistence Behavior

Container calls expose and mutate daemon-persisted container metadata, runtime state, resource settings, filesystem changes, logs, network endpoints, mounts, and names. `ContainerCreate` persists image/config/host/network settings. `ContainerUpdate` mutates selected live resource controls and restart policy. `ContainerRename` changes metadata. `ContainerArchive` and `PutContainerArchive` read and write filesystem content, while `ContainerChanges` reports writable-layer deltas. `ContainerPrune` removes stopped container objects and returns reclaimed space.

Image/build calls read and mutate local image store and build cache state. Pull/import/build/load create images or image records; tag and delete adjust references; prune removes unused images; build prune removes cache records subject to retention and filter settings. Platform and manifest parameters influence whether operations target a single platform-specific image, multiple variants, or manifest metadata.

Volumes and networks represent persistent daemon resources shared by containers and services. Volume create/update/delete/prune mutates volume driver-managed state, with cluster volume updates requiring swarm concurrency control. Network create/connect/disconnect/delete/prune mutates network driver/IPAM state and container endpoint membership; swarm-scoped and predefined networks have additional restrictions.

Plugins are installed, configured, enabled, disabled, upgraded, pushed, or removed through this API. The persistent state includes plugin rootfs/manifest, privileges, mutable settings, enablement, remote references, and registry credentials used during pull/upgrade/push flows.

Swarm objects are persisted through swarmkit/raft state rather than only local daemon state. Nodes, services, tasks, secrets, and configs are cluster objects with versions, specs, labels, and immutable or partially mutable fields. Secrets and configs can be created and deleted; updates are label-only according to this contract. Service creation/update stores scheduler-visible specs, endpoint/network settings, task templates, and registry-auth handling.

System endpoints expose daemon-local state rather than mutating it, except auth checks and streaming sessions. `/info`, `/version`, `/system/df`, `/events`, and `/_ping` reflect daemon configuration, runtime status, storage usage, swarm mode, and event history/current stream. `/session` establishes a live bidirectional integration channel rather than a persisted object.

## Dependencies And Integration Points

This chunk depends on the earlier `definitions` section of `v1.51.yaml` for all referenced schema models. It also depends on Swagger 2.0 tooling, ReDoc rendering, Docker's API generation pipeline, and vendor extension handling elsewhere in the file. Operation IDs, tags, response schemas, examples, and media types are part of the generated client/documentation contract.

Runtime integration points represented by these paths include the Docker daemon HTTP router, container runtime/containerd/OCI runtimes, Linux and Windows kernel resource controls, cgroups v1/v2, graph/storage drivers, log drivers, network drivers and IPAM, volume drivers, managed plugins, registries and auth configuration, BuildKit/classic builder, swarmkit raft/control plane, secret/config storage, and HTTP clients/proxies that support streaming or connection hijacking.

The API also integrates with Docker CLI behavior. CLI commands such as `docker ps`, `create`, `inspect`, `logs`, `stats`, `attach`, `exec`, `cp`, `build`, `pull`, `push`, `images`, `system df`, `network`, `volume`, `plugin`, `swarm`, `node`, `service`, `secret`, and `config` rely on these wire contracts.

## Risks And Edge Cases

The largest risk is API contract drift. Small changes to operation IDs, status codes, parameter names, defaults, required flags, schema references, media types, or examples can break generated clients, CLI compatibility, documentation, or tests. The spec's JSON-in-query pattern is especially easy for generated clients to mishandle because the OpenAPI type is usually only `string`.

Streaming and hijacking endpoints require special client support. Attach, websocket attach, exec start, logs, stats, events, build output, image create/push progress, archive/export, and session setup cannot be treated as normal JSON request/response calls. TTY mode changes stream framing, and logs/service/task endpoints depend on logging drivers.

Platform and daemon capability differences are pervasive. `ContainerTop` is Unix-only. Stats fields vary by cgroup version. Windows isolation/resource fields differ from Linux. BuildKit versus classic builder behavior is selected by `version`. Swarm-only operations return `503` outside swarm mode. Overlay or swarm-scoped network operations have eligibility restrictions.

State-changing calls can be destructive or race-prone. Force delete/remove/disable flags can remove containers, nodes, volumes, images, plugins, or swarm membership despite active references. Image delete has multi-platform behavior through `platforms`. Archive extraction can overwrite filesystem data and fail on read-only rootfs or volumes. Service/node/swarm/secret/config/volume updates require correct version numbers to avoid stale writes.

Security-sensitive surfaces include registry auth headers, build args and registry config, privileged exec, container capabilities/devices/security options inherited through referenced schemas, plugin privileges, swarm join tokens and unlock keys, secret data, config data, raw stdin attach, image import from URLs or request bodies, and network exposure settings.

## Test Signals

Validation should parse the complete `sources/cloud-native/moby/api/docs/v1.51.yaml` as Swagger/OpenAPI 2.0 and ensure every `$ref` used in lines 7727-13463 resolves against the full file. Generated client/server model diffs should be reviewed for operation IDs, parameter locations, required flags, enum/default handling, array query parameters, binary body handling, and vendor-extension effects.

Contract tests should cover container create/list/inspect/start/stop/restart/kill/update/rename/pause/unpause/wait/delete/prune, including documented `204`, `304`, `400`, `404`, `409`, and `500` distinctions. Archive tests should cover `HEAD`, `GET`, and `PUT`, metadata headers, compression formats, overwrite controls, UID/GID behavior, and read-only failure paths.

Wire-protocol tests should use real HTTP clients capable of raw streams, hijacked connections, websockets, and h2c upgrade. They should verify attach and exec-start framing with TTY and non-TTY containers, service/task/container logs, build progress, image pull/push progress, events streaming, stats streaming and one-shot stats, tar export/import/load, and `/session` upgrade behavior.

Image/build tests should exercise filter JSON encoding, build context compression, remote contexts, BuildKit output strings, cache prune filters and storage limits, platform and manifest query behavior, registry-auth headers, image tag/delete conflicts, and prune reclaimed-space reporting.

Swarm and cluster tests should run against both standalone and swarm-enabled daemons. They should verify `503` membership errors, init/join/leave flows, token rotation and unlock-key behavior, node/service update version checks, service rollback/registry-auth controls, service/task log streams, task filters, secret/config create/list/inspect/delete/update behavior, and label-only update constraints.

Volume, network, and plugin tests should cover filter encoding, in-use conflict responses, force flags, cluster volume update versions, predefined and swarm-scoped network restrictions, attachable network connection behavior, plugin privilege discovery, pull/upgrade auth, enable/disable timeout or force behavior, plugin settings, and tar-based plugin creation.
