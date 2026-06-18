# sources/cloud-native/moby/api/docs/v1.40.yaml lines 1-7825

## Scope And Purpose

This chunk is the opening and majority schema portion of Docker Engine API v1.40's Swagger 2.0 document. It defines global API metadata, versioning and authentication notes, ReDoc tag grouping, all shared `definitions` through `DistributionInspect`, and the first path operations from container listing through the beginning of image listing.

The file is not executable runtime logic, but it is an authoritative contract used to generate Engine API documentation and client/server types. Changes here affect public HTTP behavior, generated Go names, OpenAPI compatibility, documentation rendering, and client expectations for request bodies, response bodies, status codes, stream formats, nullable fields, and backward-compatible deprecated fields.

This chunk ends inside `GET /images/json` after the first `all` query parameter begins. Later image-list filters and the rest of the API paths continue outside this work item.

## API Model And Documentation Structure

The root document declares Swagger 2.0, `http` and `https` schemes, default JSON/text consumes and produces values, and `basePath: /v1.40`. The `info.description` establishes the Engine API as the HTTP surface used by Docker clients, explains JSON error responses with a `message` field, documents URL-prefix API versioning, and warns clients to tolerate unknown response properties and ignored extra request fields.

Registry authentication is documented as client-side and transported through `X-Registry-Auth` as a base64url JSON payload. The documented credential shapes include username/password/server address and identity-token-only forms. This is important for image endpoints outside this chunk, but the shared rule is declared here.

Tags group the ReDoc navigation into primary object APIs (`Container`, `Image`, `Network`, `Volume`, `Exec`), swarm APIs (`Swarm`, `Node`, `Service`, `Task`, `Secret`, `Config`), and system APIs (`Plugin`, `System`). These tag names are part of documentation organization rather than runtime dispatch, but endpoint `tags` later bind each operation to these groups.

## Core Shared Definitions

The definitions section starts with generic container/image support objects:

- `ImageHistoryResponseItem`, `ImageID`, `CreateImageInfo`, `PushImageInfo`, `BuildInfo`, `BuildCache`, `ErrorDetail`, `ProgressDetail`, `ErrorResponse`, and `IdResponse` describe common image, build, progress, and error payloads.
- `Port`, `PortMap`, `PortBinding`, `Address`, `GraphDriverData`, and network endpoint types capture container and image networking/storage metadata.
- `MountType`, `MountPoint`, `Mount`, `DeviceMapping`, `DeviceRequest`, and `ThrottleDevice` model mounts, bind/volume/tmpfs/npipe options, plugin/device requests, and blkio throttles.
- `RestartPolicy`, `Resources`, `ResourceObject`, and `GenericResources` define restart behavior, cgroup/resource knobs, device rules, PID limits, Windows CPU/IO options, and swarm-advertised generic resources.
- `HealthConfig`, `Health`, and `HealthcheckResult` specify healthcheck commands, timing values in nanoseconds, status enums, logs, and failure semantics.

`HostConfig` composes `Resources` and host-dependent container options. It is a large compatibility surface covering bind strings, structured mounts, logging driver config, networking mode, port bindings, restart policy, auto-remove, volumes-from, capabilities, DNS, extra hosts, IPC/PID/UTS/userns modes, privileged mode, read-only rootfs, SELinux/security options, storage options, tmpfs, ulimits, sysctls, runtime selection, Windows console/isolation fields, and masked/read-only paths.

`ContainerConfig` describes portable container configuration used at container creation and historically embedded in images. It includes hostname/domain/user, stream attachment flags, TTY/stdin behavior, environment variable semantics, command/entrypoint arrays, image reference, volumes, working directory, labels, stop signal/timeout, shell, and healthcheck. `ImageConfig` mirrors many of these fields as image defaults, but explicitly marks several runtime-only fields as always empty/false/omitted and not to be used by clients.

## Image, Volume, Network, Plugin, And Registry Definitions

`ImageInspect` and `ImageSummary` distinguish full image inspection from image list output. They document content-addressable image IDs, repo tags, repo digests, parent/comment/container metadata, Docker version, author, config, platform fields, image/rootfs sizes, graph-driver metadata, rootfs layer IDs, local metadata such as last tag time, shared size, and container reference counts. Compatibility risks are high here because legacy fields such as `VirtualSize` are retained even though they are equivalent to `Size` in modern image storage.

`Volume`, `VolumeCreateOptions`, and `VolumeListResponse` model named volumes, driver options, labels, scope, mountpoint, optional driver status, and `UsageData` for `/system/df`. `Network`, `IPAM`, `NetworkContainer`, `EndpointSettings`, `EndpointIPAMConfig`, and `NetworkingConfig` model network creation/inspection data and the network settings accepted during container creation.

Plugin definitions (`PluginMount`, `PluginDevice`, `PluginEnv`, `PluginInterfaceType`, `PluginPrivilege`, and `Plugin`) describe managed plugin configuration, runtime settings, accepted privileges, mount/device/env declarations, plugin rootfs layers, entrypoint/workdir/user/network/Linux fields, propagated mounts, and plugin interface socket/protocol data.

`RegistryServiceConfig`, `IndexInfo`, `Runtime`, `Commit`, `OCIDescriptor`, `OCIPlatform`, and `DistributionInspect` integrate the daemon with registries, OCI runtimes, external component versions, and registry-distribution metadata. The registry definitions explicitly document insecure registry behavior, mirrors, official registry state, and deprecated nondistributable artifact allowlists.

## Swarm, Service, Secret, Config, And Event Definitions

Swarm object definitions center on optimistic concurrency and clustered state:

- `ObjectVersion` documents the version index required for safe concurrent updates of nodes, services, and related swarm objects.
- `NodeSpec`, `Node`, `NodeDescription`, `Platform`, `EngineDescription`, `TLSInfo`, `NodeStatus`, `NodeState`, `ManagerStatus`, and `Reachability` model node identity, role, availability, engine plugins, advertised resources, TLS CA metadata, and manager reachability.
- `SwarmSpec`, `ClusterInfo`, `JoinTokens`, `Swarm`, `SwarmInfo`, `LocalNodeState`, and `PeerNode` define raft/dispatcher/CA/encryption/task-default settings, cluster metadata, manager auto-lock state, data path port, default address pools, join tokens, and local swarm status.
- `TaskSpec`, `TaskState`, `Task`, `ServiceSpec`, `EndpointPortConfig`, `EndpointSpec`, `Service`, and `ServiceUpdateResponse` describe the service scheduler contract: container/plugin/attachment task modes, mounts, secrets/configs, DNS, placement constraints/preferences, resources, restart policy, networks, logging, replicated/global mode, update/rollback behavior, service endpoints, virtual IPs, and update status.
- `SecretSpec`, `Secret`, `ConfigSpec`, and `Config` define swarm-managed secret/config storage. Secret data is create-only and base64 encoded with a 500KB maximum; config data is base64 encoded with a 1000KB maximum.
- `EventActor` and `EventMessage` describe daemon and swarm event envelopes, actor attributes, event scope, and second/nanosecond timestamps.

## System Definitions

`SystemVersion` documents `/version` output, including daemon and API versions, minimum API version, component versions, build metadata, platform, OS/architecture, kernel version, and experimental status. `SystemInfo` is the broad `/info` payload and captures host/daemon state: container and image counts, storage driver details, Docker root directory, standalone swarm status, plugins, kernel/cgroup feature flags, debug counts, daemon time, logging/cgroup drivers, event listeners, host OS/architecture/CPU/memory, registry config, daemon proxy environment with masked credentials, daemon labels, experimental build flag, runtimes, default runtime, swarm info, live restore, default isolation, init binary, component commits, security options, product license, and warnings.

`PluginsInfo` is a daemon info helper for unmanaged v1 plugin names grouped by volume, network, authorization, and log plugin types.

## Container Path Operations In This Chunk

The path section begins at line 5914 and this chunk covers the container API surface plus the start of image listing:

- `GET /containers/json` (`ContainerList`) lists containers as `ContainerSummary` objects. Query parameters include `all`, `limit`, `size`, and JSON-encoded filters for ancestor, before/since, exposed/published ports, exited code, health, ID, isolation, task state, label, name, network, status, and volume.
- `POST /containers/create` (`ContainerCreate`) accepts a body combining `ContainerConfig`, `HostConfig`, and `NetworkingConfig`, plus an optional `name` query parameter with a strict name pattern. It returns an ID and warnings on `201`, with documented `400`, `404`, `409`, and `500` errors.
- `GET /containers/{id}/json` (`ContainerInspect`) returns detailed container state, paths, driver/platform/security labels, exec IDs, host config, graph driver, sizes, mounts, config, and network settings. The optional `size` query parameter controls size fields.
- `GET /containers/{id}/top` (`ContainerTop`) returns process table titles and process rows, using `ps` arguments on Unix and not supported on Windows.
- `GET /containers/{id}/logs` (`ContainerLogs`) streams stdout/stderr logs for json-file and journald drivers, with `follow`, `stdout`, `stderr`, `since`, `until`, `timestamps`, and `tail` controls.
- `GET /containers/{id}/changes` (`ContainerChanges`) reports filesystem changed paths with kind `0` modified, `1` added, or `2` deleted.
- `GET /containers/{id}/export` (`ContainerExport`) exports the container filesystem as an octet-stream tarball.
- `GET /containers/{id}/stats` (`ContainerStats`) returns live or one-shot JSON stats. The description documents CPU and memory usage formulas, cgroups v1/v2 cache differences, `precpu_stats` meaning, and online CPU fallback behavior.
- Lifecycle mutation endpoints cover resize, start, stop, restart, kill, update, rename, pause, unpause, wait, delete, and prune operations with their operation IDs, query parameters, status codes, and conflict/error semantics.
- Archive endpoints under `/containers/{id}/archive` support `HEAD` metadata through `X-Docker-Container-Path-Stat`, `GET` tar archive download, and `PUT` tar extraction with `noOverwriteDirNonDir`, `copyUIDGID`, read-only-rootfs/volume permission errors, and accepted compression formats.
- `GET /images/json` (`ImageList`) begins at the end of the chunk. The visible portion shows it returns an array of `ImageSummary` and starts the `all` query parameter; remaining image-list parameters are outside this chunk.

## Control Flow And Protocol Behavior

The Swagger document encodes API control flow as HTTP method, path, status-code, parameter, and schema contracts rather than executable branches. Typical object operations follow create/list/inspect/mutate/delete patterns with path IDs accepting container ID or name, JSON request/response bodies for structured operations, and `ErrorResponse` for many failure cases.

Several endpoints have non-trivial protocol behavior:

- Attach (`POST /containers/{id}/attach`) hijacks the HTTP connection and can return either `200 OK` or `101 UPGRADED`. Without TTY, stdout/stderr are multiplexed in 8-byte-header frames where byte 0 is stream type and the last four bytes are a big-endian payload size. With TTY enabled, the stream is raw PTY data with no multiplexing.
- Websocket attach (`GET /containers/{id}/attach/ws`) provides a websocket-oriented attach route with similar stream/log controls.
- Logs and stats are streaming-style endpoints, but logs explicitly do not upgrade the connection and stats can be disabled from streaming with `stream=false`.
- Wait blocks until a requested condition is reached (`not-running`, `next-exit`, or `removed`) and then returns an exit status object.
- Archive upload/download and export use tar/binary media types rather than JSON payloads.

## State And Persistence Behavior

The definitions and paths describe multiple persistent state domains:

- Container state includes created/running/paused/restarting/removing/exited/dead states, start/finish timestamps, exit code, restart count, health state, mutable resource limits, and filesystem changes.
- Container creation persists container config, host config, network endpoint configuration, mounts, logging config, resource settings, labels, stop behavior, and optional generated or user-supplied names.
- Container lifecycle endpoints mutate process state (`start`, `stop`, `restart`, `kill`, `pause`, `unpause`), metadata (`rename`, `update`), filesystem contents (`archive` PUT), or daemon storage (`delete`, `prune`).
- Images persist content-addressable config IDs, manifest repo digests, tags, rootfs layer IDs, local graph-driver metadata, sizes, and local tag metadata.
- Volumes, networks, plugins, secrets, configs, services, nodes, tasks, swarm raft data, registry settings, daemon root directory, and runtime configuration are all represented as durable daemon or swarm state.
- Swarm object updates rely on `ObjectVersion.Index` for optimistic concurrency so stale updates do not overwrite newer state.

## Dependencies And Integration Points

This OpenAPI file integrates with several downstream consumers: generated API documentation, generated client/server types, Docker CLI behavior, daemon HTTP routing, and tests that validate schema compatibility. Vendor extensions such as `x-go-name`, `x-nullable`, titles, examples, and tag metadata are important because they influence generated Go model names, nullable pointer handling, and ReDoc output.

Runtime integration points represented in the schemas include the Docker daemon, containerd, OCI runtimes, Linux and Windows kernel resource controls, cgroups, storage drivers, log drivers, network/IPAM drivers, volume drivers, managed and unmanaged plugins, registries and mirrors, swarmkit raft/control APIs, external CAs, secret/config drivers, TLS certificate material, and OCI image/distribution specifications.

## Risks And Edge Cases

The biggest risk is accidental API contract drift. Field names, enum values, nullable markers, required lists, response codes, operation IDs, media types, and examples are consumed by generated clients and documentation; even small edits can break client compatibility or produce incorrect generated Go structs.

Compatibility-sensitive fields include deprecated-but-retained image/network fields (`VirtualSize`, default bridge network fields), image config fields documented as unused, registry nondistributable artifact fields documented as always null, standalone swarm-only system fields, platform-specific Windows/Linux resource and isolation fields, and fields where daemon output is explicitly unstable (`DriverStatus`, `SystemStatus`, component details).

Security-sensitive areas include registry auth transport, insecure registry configuration, privileged/capability/device/cgroup options, sysctls, user namespace and security labels, read-only paths, secrets/configs data handling, swarm TLS CA material, plugin privileges, and raw attach/stdin behavior.

Protocol risks include attach hijack framing, TTY versus non-TTY stream differences, log streaming without connection upgrade, stats formula changes across cgroups v1/v2, archive extraction path handling, read-only filesystem errors, and wait/delete lifecycle races. Container state booleans also have a documented edge case: paused containers can be both `Running` and `Paused`, so clients should prefer `Status`.

This chunk also contains several examples with apparent documentation typos or schema quirks, such as quoted `DeviceIDs"` in examples and `format: dateTime` versus `date-time` differences. These may be existing compatibility artifacts and should be changed only with generator/test awareness.

## Test Signals

Useful validation signals for changes to this chunk include:

- Swagger/OpenAPI parsing and documentation generation for `api/docs/v1.40.yaml`.
- Generated client/server model diffs, especially around `x-go-name`, `x-nullable`, `required`, enum, and `allOf` behavior.
- Docker API integration tests for container create/list/inspect/lifecycle/logs/stats/attach/archive/prune and image list behavior.
- CLI compatibility checks for `docker ps`, `docker create`, `docker inspect`, `docker logs`, `docker stats`, `docker attach`, `docker cp`, `docker rm`, `docker container prune`, and `docker images`.
- Platform matrix tests for Linux versus Windows fields, rootless/cgroup support flags, log driver limitations, and swarm-enabled versus standalone daemon state.
- Wire-protocol tests for attach multiplex framing, websocket attach, tar archive media handling, binary export, streaming logs/stats, and JSON error bodies.
