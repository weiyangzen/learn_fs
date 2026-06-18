# sources/cloud-native/moby/api/docs/v1.38.yaml lines 1-7535

## Scope

This chunk covers the beginning of the Docker Engine API v1.38 Swagger/OpenAPI 2.0 contract. It includes the API metadata, tag ordering, all schema definitions from `ImageHistoryResponseItem` through `PeerNode`, and path operations from `GET /containers/json` through the start of `POST /exec/{id}/start`.

The source is a declarative API specification, not executable daemon code. Its behavior matters because this file is used for generated API documentation and generated client/server types. The line range ends mid-definition of the `ExecStart` request body, so this document only describes the `ExecStart` fields and behavior visible through line 7535.

## Purpose

The file defines Docker Engine API v1.38 under `basePath: /v1.38`, including supported media types, versioning rules, error format, registry authentication headers, menu/documentation tags, reusable schemas, and REST endpoints.

The covered path operations expose core daemon workflows: container listing, creation, inspection, lifecycle control, filesystem/archive transfer, attach/log/stat streaming, container pruning, image listing/build/pull/import/inspect/history/push/tag/delete/search/prune/export/load, registry auth validation, daemon info/version/ping, image commit, event streaming, system disk usage, exec creation, and the beginning of exec start. The definitions section also models broader Engine and Swarm resources used by endpoints later in the file, including networks, volumes, plugins, nodes, services, tasks, secrets, configs, registry configuration, runtimes, and swarm cluster metadata.

## Important APIs And Types

- API metadata declares Swagger 2.0, `http` and `https` schemes, JSON/text consumes and produces defaults, and an open schema model where clients must ignore extra response properties and servers ignore extra request/query properties.
- Error handling is standardized through `ErrorResponse`, a JSON object with required `message`.
- Registry auth is client-side and passed to registry-touching operations in `X-Registry-Auth` as base64-encoded JSON credentials or an identity token from `POST /auth`.
- `ContainerConfig`, `HostConfig`, `Resources`, `RestartPolicy`, `HealthConfig`, `Mount`, `MountPoint`, `PortMap`, `PortBinding`, `NetworkSettings`, `EndpointSettings`, and `EndpointIPAMConfig` form the container create/inspect/update contract.
- `Image`, `ImageSummary`, `ImageHistoryResponseItem`, `BuildInfo`, `CreateImageInfo`, `PushImageInfo`, `ImageDeleteResponseItem`, `GraphDriverData`, and `AuthConfig` model image state, image-transfer progress, registry auth, and image-layer metadata.
- `Volume`, `Network`, `IPAM`, `NetworkContainer`, and `PluginsInfo` model storage/network/plugin state used in daemon info and later endpoint groups.
- `Plugin`, `PluginMount`, `PluginDevice`, `PluginEnv`, and `PluginInterfaceType` describe managed plugin configuration, settings, rootfs, device, environment, mount, and interface requirements.
- Swarm schemas include `ObjectVersion`, `NodeSpec`, `Node`, `NodeDescription`, `NodeStatus`, `ManagerStatus`, `SwarmSpec`, `ClusterInfo`, `JoinTokens`, `Swarm`, `TaskSpec`, `Task`, `ServiceSpec`, `Service`, `EndpointSpec`, `SecretSpec`, `Secret`, `ConfigSpec`, and `Config`.
- `ObjectVersion.Index` is the optimistic concurrency token for mutable swarm objects such as nodes and services; clients must send the observed version when updating these resources.
- System schemas include `SystemInfo`, `RegistryServiceConfig`, `IndexInfo`, `Runtime`, `Commit`, `SwarmInfo`, `LocalNodeState`, and `PeerNode`.
- Container endpoints in this chunk include `ContainerList`, `ContainerCreate`, `ContainerInspect`, `ContainerTop`, `ContainerLogs`, `ContainerChanges`, `ContainerExport`, `ContainerStats`, `ContainerResize`, `ContainerStart`, `ContainerStop`, `ContainerRestart`, `ContainerKill`, `ContainerUpdate`, `ContainerRename`, `ContainerPause`, `ContainerUnpause`, `ContainerAttach`, `ContainerAttachWebsocket`, `ContainerWait`, `ContainerDelete`, `ContainerArchiveInfo`, `ContainerArchive`, `PutContainerArchive`, and `ContainerPrune`.
- Image/system endpoints include `ImageList`, `ImageBuild`, `BuildPrune`, `ImageCreate`, `ImageInspect`, `ImageHistory`, `ImagePush`, `ImageTag`, `ImageDelete`, `ImageSearch`, `ImagePrune`, `SystemAuth`, `SystemInfo`, `SystemVersion`, `SystemPing`, `ImageCommit`, `SystemEvents`, `SystemDataUsage`, `ImageGet`, `ImageGetAll`, and `ImageLoad`.
- Exec endpoints visible here include full `ContainerExec` creation and the opening of `ExecStart`, with `ExecStart` success/error responses and the first body property, `Detach`.

## Control Flow

The container create/start workflow is intentionally split. `POST /containers/create` accepts portable `ContainerConfig`, host-specific `HostConfig`, and `NetworkingConfig.EndpointsConfig`, then returns a new container ID plus warnings. `POST /containers/{id}/start` later starts that container, optionally overriding detach keys. Inspection through `GET /containers/{id}/json` returns the persisted and runtime state: process path/args, state booleans and status enum, restart count, host paths, graph driver, mounts, config, host config, exec IDs, and network settings.

Container lifecycle operations mutate existing state and mostly return empty success bodies. Start, stop, restart, kill, update, rename, pause, unpause, wait, and delete all resolve a container by path `id` and map daemon state conflicts into HTTP status codes such as `304` already started/stopped, `404` missing, and `409` conflict or not running. `ContainerWait` blocks until a condition (`not-running`, `next-exit`, or `removed`) and returns an exit `StatusCode` with an optional wait error object.

Several container operations are streaming or binary protocols rather than ordinary JSON. `ContainerLogs` can return a body string or, when `follow` is true, a `101` upgraded raw stream. `ContainerAttach` hijacks the HTTP connection and carries stdin/stdout/stderr over the socket; with TTY disabled it uses 8-byte multiplex headers and big-endian payload sizes, while TTY mode sends raw PTY bytes without multiplexing. `ContainerAttachWebsocket` exposes a websocket attach variant. `ContainerStats` returns live resource-usage JSON unless `stream=false`. Export and archive operations use tar streams and path-stat headers rather than JSON bodies.

Container filesystem operations are split by intent. `GET /containers/{id}/changes` reports overlay changes as `Kind` values `0` modified, `1` added, and `2` deleted. `GET /containers/{id}/export` exports the full container filesystem as a tarball. `HEAD /containers/{id}/archive` returns `X-Docker-Container-Path-Stat` with base64-encoded JSON metadata for a path, `GET /containers/{id}/archive` downloads a tar archive of a path, and `PUT /containers/{id}/archive` extracts a tar archive into a container directory, with read-only and directory/non-directory overwrite protections.

Image flow covers both local image-store operations and remote registry operations. `ImageBuild` sends a compressed tar build context, validates the Dockerfile before running steps, streams build output, and cancels if the client connection closes. It accepts classic builder or BuildKit selection through `version`, registry auth through `X-Registry-Config`, resource controls for build containers, target/platform, build args, cache settings, labels, and network mode. `ImageCreate` pulls or imports depending on `fromImage` versus `fromSrc`; pulls are also canceled when the HTTP connection closes. `ImagePush` requires `X-Registry-Auth` and is canceled on connection close. Image export/load operations use tar formats with layer directories, `VERSION`, `json`, `layer.tar`, and optional `repositories` metadata.

System endpoints expose daemon-wide introspection and event streams. `SystemAuth` validates registry credentials and may return an identity token. `SystemInfo` returns large daemon state including storage driver, root dir, runtime, registry, proxy, swarm, security, cgroup, kernel, architecture, plugin, and resource-support data. `SystemVersion` returns daemon and component version metadata. `SystemPing` returns a text `OK` plus headers for max API version and experimental mode. `SystemEvents` streams object events and supports JSON-encoded filters by type, object ID/name, label, scope, and event action. `SystemDataUsage` returns disk usage grouped by images, containers, and volumes.

Exec flow starts with `POST /containers/{id}/exec`, which creates an exec instance inside a running container and returns an ID. The request config controls attached streams, detach keys, TTY allocation, environment, command, privilege elevation, user/group, and working directory. The visible part of `POST /exec/{id}/start` documents the second phase: starting a prepared exec instance, returning immediately in detached mode or establishing an interactive raw-stream session otherwise.

## State And Persistence Behavior

This spec does not persist data itself, but it describes stateful daemon objects and the externally visible persistence model. Containers have stable IDs/names, persisted create-time config, host config, labels, mounts, graph-driver data, logs, writable-layer size, restart counts, network endpoint state, exec IDs, and lifecycle state. Some fields are explicitly runtime-derived, such as process PID, paused/running booleans, health/log output, stats, and path state in archives.

Host-level persistence is visible through storage paths such as Docker root dir, container hostname/hosts/resolv/log paths, graph-driver data, image layers, volume mountpoints, and local registry/cache/image stores. Prune operations mutate persistent state by deleting stopped containers, unused images, or builder cache and return reclaimed byte counts.

Image state includes content-addressed IDs, tags, digests, parent/layer history, graph-driver data, rootfs layers, labels, creation metadata, and last tag time. Tagging creates or overwrites references to existing image content. Image delete may untag references and remove untagged parents unless blocked by descendants, running containers, or active builds.

Volumes are persistent resources with driver, mountpoint, labels, scope, driver options, and optional usage data for `GET /system/df`. Mount definitions distinguish bind mounts, named pipes, tmpfs, and volumes; the spec explicitly states that Docker volumes created or used through `Mount.Type=volume` are not removed when the container is removed unless separate volume-delete behavior is requested for anonymous volumes.

Swarm definitions describe a versioned, replicated state model. `ObjectVersion` exists to prevent conflicting writes. `SwarmSpec` includes Raft snapshot/heartbeat/election settings, CA configuration, manager autolock encryption at rest, task defaults, and dispatcher heartbeat. `ClusterInfo` intentionally omits join tokens when returned through `/info`, while `Swarm` includes them. Secrets and configs carry base64 data at creation time and metadata thereafter.

SystemInfo exposes daemon process and host state that may be sampled at different times. Some values are explicitly unstable or environment-derived, including storage-driver status formatting, daemon ID format, proxy environment variables, kernel/OS/architecture, debug-only file descriptor and goroutine counts, cgroup support, configured runtimes, and live-restore status.

## Dependencies

The file depends on Swagger/OpenAPI 2.0 semantics: `$ref`, `allOf`, response schemas, path/query/header/body parameters, MIME types, examples, required lists, enum validation, nullable extensions, and vendor extensions such as `x-go-name`.

Generated clients and server stubs depend on operation IDs, schema names, parameter names, required flags, status codes, and media types staying compatible. The opening comment states that this file is used for API documentation and generated client/server types, so schema mistakes can directly affect SDK model shapes and daemon API compatibility.

At runtime, the documented endpoints depend on Docker daemon subsystems: container lifecycle and state store, graph/storage drivers, cgroups and namespaces, logging drivers, volume drivers, networking/IPAM, registry auth and distribution, image builder/BuildKit, archive/tar handling, event broadcaster, swarmkit state and Raft, plugin management, OCI runtimes through containerd, and platform-specific Linux/Windows isolation/resource features.

Registry-related endpoints depend on client-supplied auth headers and daemon registry configuration. Build operations may depend on remote Git/HTTP contexts, registry auth maps, cache images, platform resolution, Dockerfile validation, and the selected builder backend.

Streaming endpoints depend on HTTP connection hijacking, websocket support, proxy behavior, raw stream framing, and client-side connection lifecycle. Archive/image import/export endpoints depend on tar format handling and compressed input support for identity, gzip, bzip2, and xz.

## Integration Points

The tag list defines the ReDoc menu order and groups endpoints into user-visible domains: containers, images, networks, volumes, exec, swarm resources, plugins, and system. The operation IDs are the likely stable hooks for generated SDK method names.

The spec integrates with Docker CLI workflows. Examples in the metadata map CLI commands to endpoints, such as `docker ps` to `GET /containers/json`; running a container requires several API calls; `docker exec` maps to exec create plus exec start; image build/push/pull/tag/save/load/commit/search map to the image endpoint group.

Common conventions recur across endpoint groups: `id` or `name` path parameters resolve names or IDs, `filters` query parameters are JSON-encoded `map[string][]string`, error bodies use `ErrorResponse`, and successful mutating operations commonly return `204`, `201`, or an ID/warnings object.

Container, image, and system sections share model definitions. For example, `SystemDataUsage` returns `ImageSummary`, `ContainerSummary`, and `Volume`; `ImageCommit` reuses `ContainerConfig`; `ContainerCreate` combines `ContainerConfig`, `HostConfig`, and `EndpointSettings`; `ContainerUpdate` reuses `Resources` and `RestartPolicy`.

The system event stream is a cross-domain integration point. It documents events for containers, images, volumes, networks, daemon reloads, services, nodes, secrets, and configs, and filters can select object types or specific resources.

Swarm object definitions in this chunk are integration scaffolding for later endpoint groups. Service specs reference task specs, mounts, secrets/configs, placement, resource reservations, networks, endpoint ports, and log drivers. Node and swarm definitions connect daemon info to cluster state, TLS material, manager reachability, and Raft/CA settings.

## Risks And Edge Cases

- The file uses an open schema model. Clients that fail on unknown response fields will be brittle against newer daemons, and servers intentionally ignore unknown request fields or query parameters.
- `ExecStart` is truncated in this chunk. Any generated or manual research based only on this range must not assume the full exec start request schema is visible here.
- Several operations use non-JSON transports. Client libraries that assume JSON-only responses will mishandle attach/log hijacking, websocket attach, stats streams, event streams, tar archive transfer, image export/load, and build/push/pull progress streams.
- The attach raw-stream protocol differs when TTY is enabled. Consumers must not try to demultiplex TTY streams with the 8-byte frame header.
- `ContainerInspect.State.Running` and `Paused` are not mutually exclusive; callers should use `State.Status` to determine the user-visible state.
- `ContainerLogs` only works for `json-file` or `journald` logging drivers, so logs may be unavailable for containers using other drivers even when the container exists.
- `PublishAllPorts` allocates ephemeral host ports on start and deallocates them on stop; port numbers may change after restart.
- Build args are explicitly not intended for secret values, but the schema accepts arbitrary string pairs. Tooling should avoid logging or persisting sensitive build args.
- Pull, push, and build cancellation is tied to client connection closure. Proxies, retries, and generated clients need to preserve or deliberately close streams.
- `ImageDelete` has state conflicts when images have descendants, are used by running containers, or are used by builds. `force` and `noprune` change deletion semantics but do not remove all conflicts.
- Prune filters accept timestamps, formatted timestamps, or Go duration strings relative to daemon machine time. Clock differences between client and daemon can change deletion scope.
- Registry insecure configuration is documented as security-sensitive. Clients and tests should not treat insecure registries as normal production configuration.
- Multiple schemas include deprecated fields or unstable formatting notes, such as legacy default bridge network fields, standalone Swarm system status, nondistributable artifact registry fields, and storage-driver status text.
- `ObjectVersion` optimistic concurrency is essential for swarm updates; ignoring it can cause lost updates or rejected writes.
- Platform-specific fields are mixed into shared schemas. Windows-only fields such as isolation, credential specs, CPU count/percent, and registry credential spec paths must not be assumed to work on Linux, and Linux-specific namespace/cgroup/security fields must be guarded on Windows.
- Several definitions use broad `object` maps with `additionalProperties`, driver-specific options, or nullable values. Generated clients must preserve unknown driver/plugin/runtime options instead of dropping them.

## Test Signals

Useful validation for this chunk includes:

- Swagger validation for path uniqueness, `$ref` resolution, `allOf` composition, required fields, enum values, parameter locations, and operation ID uniqueness.
- Generated-client contract tests for Docker's open schema rule: unknown response fields should be ignored, and unknown request/query properties should not break callers.
- Container list/create/inspect tests covering JSON filter encoding, create warnings, missing image `404`, name conflict `409`, size flags, network endpoint config, host config, and inspect state fields.
- Container lifecycle tests for start/stop/restart/kill/update/rename/pause/unpause/delete/wait status codes, including already-started/stopped `304`, missing container `404`, not-running or removal conflicts `409`, and wait conditions.
- Stream protocol tests for logs with and without `follow`, attach with and without upgrade headers, multiplexed non-TTY frames, raw TTY attach, websocket attach, live stats with `stream=true`, and one-shot stats with `stream=false`.
- Archive tests for `HEAD` path stat header decoding, tar download/upload, missing paths, read-only rootfs or volume `403`, `not a directory` errors, and `noOverwriteDirNonDir`.
- Image build tests for tar input, Dockerfile path validation, remote contexts, multiple tags, cache settings, build args encoding, registry config header, platform/target, BuildKit selection, cancellation on disconnect, and streamed progress parsing.
- Image registry tests for pull/import selection (`fromImage` versus `fromSrc`), auth headers, platform query, push tag behavior, connection-close cancellation, missing repository/image errors, and private registry names.
- Image state tests for list filters, digest inclusion, inspect schema, history items, tag overwrite behavior, delete with `force` and `noprune`, search filters, prune filters, export tar structure, multi-image export, and load progress.
- System tests for `/auth` token/no-token responses, `/info` feature fields, `/version` component metadata, `/_ping` headers, `/events` filters and streaming termination with `until`, `/system/df` volume usage data, and daemon error handling.
- Exec tests for create in running, missing, and paused containers; create config fields for streams, env, user, working directory, privilege, and TTY; and `ExecStart` detached versus interactive behavior once the following chunk supplies the full request schema.
