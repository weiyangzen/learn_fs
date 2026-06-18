# sources/cloud-native/moby/api/docs/v1.32.yaml lines 1-7574

## Scope And Purpose

This chunk is the first major portion of the Docker Engine API v1.32 Swagger 2.0 document. It defines global API metadata, tag grouping, shared schema definitions, and the beginning of the path catalog through the start of the volume delete endpoint. The file is both documentation input for ReDoc and a contract source for generated API documentation and client/server types, so schema names, response shapes, enum values, status codes, MIME types, and `operationId` values are part of the public Engine API compatibility surface.

The covered path range includes the complete container lifecycle API, image/build/registry-adjacent APIs, system information and event APIs, exec APIs, volume list/create/inspect, and the opening lines of `VolumeDelete`. The chunk stops at line 7574 before the rest of `VolumeDelete`, volume pruning, network, plugin, swarm, service, task, secret, config, distribution, and session paths.

## OpenAPI Structure

The document declares Swagger 2.0 over `http` and `https`, default JSON and plain-text content negotiation, `basePath: /v1.32`, API title/version metadata, and top-level guidance about errors, versioned URLs, open-schema compatibility, and registry authentication through the `X-Registry-Auth` header.

Tags define the documentation navigation and endpoint grouping: `Container`, `Image`, `Network`, `Volume`, `Exec`, swarm-mode tags (`Swarm`, `Node`, `Service`, `Task`, `Secret`), `Plugin`, and `System`. Only a subset of those tags has paths in this chunk, but all tag declarations are visible here.

The `definitions` block runs from line 134 to just before `paths` at line 4190. It models API payloads as reusable OpenAPI schemas with `$ref`, `allOf`, `required`, `x-nullable`, `x-go-name`, examples, enums, integer formats, and object maps. The `paths` block begins at line 4190 and maps each HTTP method to a stable `operationId`, typed parameters, success/error responses, media types, and tag membership.

## Shared Definitions

Container and execution schemas are centered on `ContainerConfig`, `HostConfig`, `Resources`, `RestartPolicy`, `HealthConfig`, `NetworkSettings`, `EndpointSettings`, `Mount`, `MountPoint`, `Port`, `PortMap`, `PortBinding`, `DeviceMapping`, `ThrottleDevice`, `ContainerSummary`, `ProcessConfig`, and `IdResponse`. `HostConfig` composes `Resources` with host-bound settings such as bind mounts, log configuration, networking mode, restart policy, capabilities, DNS, namespaces, privileged mode, read-only rootfs, storage options, tmpfs, sysctls, runtime, shm size, Windows console/isolation fields, and volume inheritance. `ContainerConfig` captures portable process/image configuration: hostname, user, attach flags, TTY/stdin behavior, env, command, healthcheck, image, volumes, working directory, entrypoint, labels, stop behavior, shell, and networking-disabled metadata.

Image schemas include `Image`, `ImageSummary`, `ImageHistoryResponseItem`, `ImageDeleteResponseItem`, `BuildInfo`, `CreateImageInfo`, `PushImageInfo`, `ErrorDetail`, and `ProgressDetail`. These definitions support image list/inspect/history/build/create/push/delete/search/prune/load/export flows, including stream-style progress records, graph-driver metadata, rootfs layer digests, repository tags/digests, image config, history, and size accounting.

Storage and networking schemas include `Volume`, `Network`, `IPAM`, `NetworkContainer`, `EndpointIPAMConfig`, `Address`, and `Driver`. `Volume` models local and global volume state, mountpoint, labels, driver options, optional driver status, and `UsageData` for `GET /system/df`. `Network` and endpoint schemas expose bridge/overlay/IPAM/container attachment details even though most network paths are later than this chunk.

Plugin and system schemas include `Plugin`, `PluginMount`, `PluginDevice`, `PluginEnv`, `PluginInterfaceType`, `SystemInfo`, `PluginsInfo`, `RegistryServiceConfig`, `IndexInfo`, `Runtime`, `Commit`, `AuthConfig`, and `ErrorResponse`. `SystemInfo` is a wide daemon state snapshot covering container/image counts, storage driver, docker root, plugin inventory, cgroup and kernel support flags, daemon proxy settings, registry configuration, runtimes, swarm status, security options, live restore, and build/runtime component commits.

Swarm-mode schemas are fully defined even though most related paths are outside this chunk: `ObjectVersion`, `NodeSpec`, `Node`, `NodeDescription`, `Platform`, `EngineDescription`, `TLSInfo`, `NodeStatus`, `NodeState`, `ManagerStatus`, `Reachability`, `SwarmSpec`, `ClusterInfo`, `JoinTokens`, `Swarm`, `TaskSpec`, `TaskState`, `Task`, `ServiceSpec`, `EndpointPortConfig`, `EndpointSpec`, `Service`, `ServiceUpdateResponse`, `SecretSpec`, `Secret`, `ConfigSpec`, `Config`, `ResourceObject`, and `GenericResources`. The important contract detail is optimistic concurrency through `ObjectVersion.Index`, which update endpoints must use to avoid conflicting writes.

## Container APIs

The container path set is complete in this chunk.

`ContainerList` (`GET /containers/json`) lists containers using the smaller `ContainerSummary` representation. Query parameters include `all`, `limit`, `size`, and JSON-encoded filters for ancestry, creation ordering, exposed/published ports, exit code, health, id, isolation, task membership, labels, name, network, status, and volume. It returns 200 with container summaries or standard 400/500 error responses.

`ContainerCreate` (`POST /containers/create`) accepts an optional `name` query and a body composed from `ContainerConfig` plus `HostConfig` and `NetworkingConfig.EndpointsConfig`. Its example is a dense executable specification for create-time behavior across env, command, labels, exposed ports, stop policy, host binds, links, memory/CPU/blkio controls, port bindings, DNS, capabilities, restart policy, auto-remove, network mode, ulimits, logging, security/storage options, shm size, and explicit endpoint IPAM/aliases. Responses distinguish created (201), bad parameter, missing image, conflict, and server error.

`ContainerInspect` (`GET /containers/{id}/json`) returns low-level state: creation timestamp, process path/args, detailed `State` booleans and status enum, image ID, resolver/hosts/log paths, name, restart count, driver, security labels, exec IDs, `HostConfig`, graph driver, optional size fields, mounts, config, and network settings. The schema preserves the historic nuance that a paused container can still have `Running: true`, and clients should use `State.Status` for user-facing status.

Process and lifecycle endpoints include `ContainerTop`, `ContainerLogs`, `ContainerChanges`, `ContainerExport`, `ContainerStats`, `ContainerResize`, `ContainerStart`, `ContainerStop`, `ContainerRestart`, `ContainerKill`, `ContainerUpdate`, `ContainerRename`, `ContainerPause`, `ContainerUnpause`, `ContainerWait`, and `ContainerDelete`. They expose status-code level state transitions such as 204 success, 304 already started/stopped, 404 missing container, 409 conflict for running-container deletion, and 500 daemon failures. `ContainerUpdate` accepts the reusable `Resources` shape plus `RestartPolicy`, which makes resource update compatibility tightly coupled to create-time resource fields.

Streaming and archive endpoints have special transport semantics. `ContainerAttach` (`POST /containers/{id}/attach`) can hijack the HTTP connection, optionally upgrade with `101 UPGRADED`, and multiplex non-TTY stdout/stderr frames with an 8-byte header. TTY mode switches to raw PTY bytes. `ContainerAttachWebsocket` exposes an alternate websocket attach path. `ContainerStats` can stream JSON resource snapshots or return a single sample when `stream=false`. `ContainerArchiveInfo`, `ContainerArchive`, and `PutContainerArchive` use `HEAD`, `GET`, and `PUT` on `/containers/{id}/archive`, returning path metadata in `X-Docker-Container-Path-Stat`, tar archives, or tar extraction results with path, overwrite, read-only, and permission error handling.

`ContainerPrune` deletes stopped containers with JSON-encoded `until` and label filters and returns deleted container IDs plus reclaimed bytes.

## Image, Build, Registry, And Auth APIs

`ImageList` (`GET /images/json`) returns `ImageSummary` items with filters for dangling state, labels, references, and before/since relationships. Optional `digests` controls whether repo digests are included.

`ImageBuild` (`POST /build`) builds an image from a tar stream or remote context. It consumes `application/octet-stream` and returns JSON progress records. Parameters cover Dockerfile path, tags, extra hosts, remote context, quiet mode, no-cache, cache-from, pull behavior, remove/intermediate-container cleanup, force remove, memory, memory swap, CPU shares, cpuset CPUs, build args, shm size, squash, labels, network mode, platform, target, outputs, and Dockerfile parser/build options visible in this API revision. The endpoint documents that Dockerfile validation happens before build execution and that the build is canceled if the client connection drops.

`BuildPrune` (`POST /build/prune`) removes build cache and returns cache records deleted plus reclaimed bytes. It accepts filters, `keep-storage`, and `all`.

Image distribution endpoints in this chunk include `ImageCreate`, `ImageInspect`, `ImageHistory`, `ImagePush`, `ImageTag`, `ImageDelete`, `ImageSearch`, `ImagePrune`, `ImageGet`, `ImageGetAll`, and `ImageLoad`. These cover pull/import from registry or source, image inspection, history, pushing with `X-Registry-Auth`, tag creation, deletion with `force`/`noprune`, registry search, unused image prune with filters, single/multiple image export as tar, and tar import. `ImageGet` documents the legacy image tarball layout with one directory per layer, `VERSION`, `json`, `layer.tar`, whiteout representation, and root `repositories` mapping.

`SystemAuth` (`POST /auth`) validates registry credentials and returns auth status/identity token details. It uses the `AuthConfig` body and shares the same registry credential model described in the top-level API description.

`ImageCommit` (`POST /commit`) creates an image from a container, combining query fields such as container ID, repository, tag, comment, author, pause flag, and config changes with an optional `ContainerConfig` body. It mutates image state while reading container filesystem/config state.

## System APIs

`SystemInfo` (`GET /info`) returns the `SystemInfo` daemon inventory. This endpoint is an integration point for storage drivers, registry configuration, runtime configuration, security features, cgroup/kernel capability detection, swarm status, daemon labels, proxy environment, and component commit metadata.

`SystemVersion` (`GET /version`) returns version/build information including platform, components, API version bounds, git commit, Go version, OS/architecture, kernel, and experimental flag. `SystemPing` (`GET /_ping`) is a lightweight health check that returns plain text and headers indicating API version and daemon experimental mode.

`SystemEvents` (`GET /events`) streams daemon events. It accepts `since`, `until`, and JSON filters for config, container, daemon, event, image, label, network, node, plugin, scope, secret, service, type, and volume. This endpoint is state-observation oriented rather than state-mutating, and it can stay open for live event delivery.

`SystemDataUsage` (`GET /system/df`) aggregates disk usage for images, containers, and volumes, returning `LayersSize`, `Images`, `Containers`, and `Volumes`. It depends on the image/container/volume schemas and the optional `Volume.UsageData` fields.

## Exec APIs

`ContainerExec` (`POST /containers/{id}/exec`) creates an exec instance inside an existing running container. The body configures attached streams, detach keys, TTY, env, command, privileged flag, and user. It returns an `IdResponse` on 201, with explicit missing-container, paused-container, and server-error cases.

`ExecStart` (`POST /exec/{id}/start`) starts a previously created exec instance and can either detach immediately or attach an interactive raw stream using the same `application/vnd.docker.raw-stream` transport family as container attach. `ExecResize` resizes the exec TTY through required `h` and `w` query parameters. `ExecInspect` returns exec runtime state including running flag, exit code, `ProcessConfig`, open stream booleans, container ID, and host PID.

Exec state is transient daemon state tied to a container. The API requires a create/start/inspect lifecycle and must handle race conditions where the container is stopped, paused, missing, or the exec instance no longer exists.

## Volume APIs In This Chunk

`VolumeList` (`GET /volumes`) returns an object with non-null `Volumes` and `Warnings` arrays. It accepts JSON filters for dangling state, driver, label, and name. `VolumeCreate` (`POST /volumes/create`) accepts name, driver, driver options, and labels, returning the created `Volume`. `VolumeInspect` (`GET /volumes/{name}`) returns a volume by name or ID with 404 and 500 error paths.

`VolumeDelete` begins at line 7566 with `DELETE /volumes/{name}`, summary, description, operation ID, and the first two response cases: 204 removed and 404 no such volume or driver. The remaining response details and parameters are outside this chunk, so this research should not be treated as complete coverage of the delete-volume contract.

## Control Flow And State Behavior

This YAML does not implement runtime control flow, but it specifies the externally observable flow clients must follow. Container creation composes image/config/host/network state, start/stop/restart/kill/pause/unpause mutate runtime state, wait blocks on state transitions, attach/logs/stats/events stream runtime output, archive operations move filesystem data across the daemon boundary, and delete/prune endpoints reclaim objects and storage.

Image and build flows mutate image stores, registry references, and build cache. Build accepts a context stream or remote context, emits progress, may create tagged images, and is canceled on client disconnect. Pull/create, push, tag, delete, prune, save, and load integrate the local image store with remote registries and tar streams. Registry authentication is explicitly client-supplied through request bodies or `X-Registry-Auth` rather than server-side login sessions.

System endpoints expose daemon state without generally mutating it, except auth and commit-related image creation. Events and stats are live streams, making transport lifetime and client disconnect behavior part of the contract.

Volumes are persistent storage objects. Create/list/inspect/delete operate through volume drivers, with driver-specific options and status maps intentionally left open-ended. `UsageData` may be present for data-usage reporting and may use sentinel values such as `-1` when a driver cannot report size/refcount.

Swarm definitions specify state and persistence rules even before their paths appear: object updates are guarded by version indexes, secrets/configs have size constraints and create-only data fields, node/service/task state is timestamped, and service updates/rollbacks encode scheduling strategy, restart policy, placement, resources, endpoint exposure, secrets, configs, and log driver settings.

## Dependencies And Integration Points

The document depends on Swagger/OpenAPI 2.0 tooling, ReDoc rendering, and Moby's API generation/documentation pipeline. Fields such as `x-go-name` and `x-nullable` are generator hints, so changes can affect generated Go types and JSON marshal/unmarshal behavior.

The API contract integrates with Docker daemon subsystems: container runtime and OCI runtimes, containerd/runC/init version reporting, graph/storage drivers, cgroups and kernel feature detection, logging drivers, volume drivers, network drivers/IPAM, registry resolver/auth/push/pull, builder/build cache, swarmkit managers/agents, plugin management, and event broadcasting.

Transport integration is non-trivial. Several endpoints use ordinary JSON, while attach/exec use raw hijacked streams, websocket attach uses upgrade semantics, archive/save/load use tar or binary bodies, build/create/push emit streaming JSON progress records, and events/stats can be long-lived streams. Clients and proxies need to preserve these protocol differences.

## Risks And Edge Cases

Because the file is open-schema API documentation and generator input, small edits can create compatibility regressions: changing a field name, enum value, `required` list, nullability hint, integer format, response status, MIME type, or `operationId` can break generated clients or users relying on documented behavior.

Container API risk is concentrated around transport and state races: attach stream framing differs between TTY and non-TTY, stats/events/build can stream indefinitely, wait blocks until configurable state conditions, archive upload must protect directory/file replacement and read-only roots, and lifecycle endpoints must distinguish idempotent states from conflicts using the documented status codes.

Resource schemas are platform-sensitive. Linux-only fields, Windows-only fields, cgroup support flags, namespace modes, isolation modes, device throttling, realtime CPU settings, and memory/swap semantics require clients to tolerate unsupported values and daemon warnings.

Registry and image APIs carry security risks around base64 registry auth headers, insecure registry configuration, nondistributable artifact settings, tar import/export trust boundaries, and push/pull credentials. The top-level open-schema note means clients must ignore unknown response properties and avoid assuming that undocumented fields will be rejected.

Swarm definitions include concurrency-sensitive `ObjectVersion.Index` and sensitive data handling for secrets/configs. `SecretSpec.Data` is create-only and base64 encoded, with documented size limits; exposing or returning it accidentally would be a security bug.

The chunk boundary itself is a reconciliation risk: `VolumeDelete` is incomplete here. Any final per-file research must merge this with the next chunk before making claims about the full volume delete, prune, network, plugin, swarm, service, task, secret, config, distribution, or session endpoint sets.

## Test Signals

Strong validation signals for this file include Swagger/OpenAPI parsing, documentation generation, generated Go type compilation, and operation ID uniqueness checks. The file should continue to parse as YAML and Swagger 2.0 after edits.

API compatibility tests should compare generated clients/types and rendered docs for stable schema names, `x-go-name`, nullability, required fields, enums, parameter names, status codes, and media types. Golden tests around known endpoints such as `ContainerCreate`, `ContainerAttach`, `ImageBuild`, `SystemInfo`, `ExecStart`, and `VolumeList` would catch high-impact schema drift.

Runtime integration tests should exercise representative endpoint classes: JSON request/response (`ContainerInspect`, `ImageInspect`, `SystemInfo`), lifecycle mutations (`ContainerStart/Stop/Delete`, `ImageTag/Delete`, `VolumeCreate/Inspect`), streaming (`ContainerAttach`, `ContainerStats`, `SystemEvents`, `ImageBuild`), binary/tar transfer (`ContainerArchive`, `PutContainerArchive`, `ImageGet`, `ImageLoad`), registry-auth flows (`SystemAuth`, `ImagePush`, `ImageCreate`), and prune/data-usage accounting (`ContainerPrune`, `ImagePrune`, `BuildPrune`, `SystemDataUsage`).

Negative tests should assert documented error statuses for missing containers/images/volumes, invalid parameters, paused/stopped conflicts, running-container deletion conflicts, read-only filesystem archive writes, bad registry credentials, and malformed JSON filter strings.
