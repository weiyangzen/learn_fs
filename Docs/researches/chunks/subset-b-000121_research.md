# sources/cloud-native/moby/api/docs/v1.36.yaml lines 1-7569

## Scope

This chunk covers the beginning of the Docker Engine API v1.36 Swagger 2.0 document through the end of the exec inspect endpoint. It includes the API metadata, tag taxonomy, all shared definitions present before `paths`, and path operations for containers, images, auth/system inspection, events/data usage, image import/export, and exec lifecycle. The range stops immediately before the volume endpoints.

The source is API contract documentation, not executable daemon code. It defines the request/response schemas, operation IDs, media types, status codes, query/body/header parameters, examples, and narrative protocol notes used by generated clients, API documentation, and daemon compatibility tests.

## Purpose

The file describes Docker Engine API v1.36 at `/v1.36`. It makes the Engine's container, image, exec, and basic system operations available through versioned HTTP endpoints, with an open-schema compatibility model where newer daemons may add response fields and ignore extra request fields.

This chunk is the core local-daemon API surface. It lets clients create and inspect containers, manipulate container process state, attach to streams, copy files into and out of containers, prune stopped containers, build/pull/tag/push/remove/search/load/save images, validate registry credentials, inspect daemon/system state, monitor events, and create/start/inspect exec instances inside running containers.

## Important APIs And Types

- API metadata: Swagger 2.0, `basePath: /v1.36`, default JSON/text media types, versioning notes, standard JSON error shape, and registry auth encoded in `X-Registry-Auth`.
- Tags: `Container`, `Image`, `Network`, `Volume`, `Exec`, swarm-related tags, `Plugin`, and `System`. Only `Container`, `Image`, `System`, and `Exec` path operations appear in this chunk.
- Core container/image definitions: `ContainerConfig`, `HostConfig`, `Resources`, `RestartPolicy`, `HealthConfig`, `Mount`, `MountPoint`, `MountType`, `Port`, `PortMap`, `PortBinding`, `NetworkSettings`, `EndpointSettings`, `Image`, `ImageSummary`, `ImageHistoryResponseItem`, `ContainerSummary`, `GraphDriverData`, and `ProcessConfig`.
- Storage/network support definitions: `Volume`, `Network`, `IPAM`, `NetworkContainer`, `Address`, `EndpointIPAMConfig`, and device/throttle mappings. Some are defined here for later endpoints and for container/image/system response fields.
- Plugin and swarm definitions: `Plugin`, `PluginMount`, `PluginDevice`, `PluginEnv`, `ObjectVersion`, `Node`, `SwarmSpec`, `Swarm`, `TaskSpec`, `Task`, `ServiceSpec`, `Service`, `Secret`, `Config`, and related enums. These are schema dependencies for `/info`, `/system/df`, and later path chunks even though most swarm paths are outside this range.
- System definitions: `SystemInfo`, `PluginsInfo`, `RegistryServiceConfig`, `IndexInfo`, `Runtime`, `Commit`, `SwarmInfo`, `LocalNodeState`, and `PeerNode`.
- Shared response definitions: `ErrorResponse`, `IdResponse`, `ImageDeleteResponseItem`, `ServiceUpdateResponse`, progress/status shapes for build/pull/push, and `BuildInfo`.
- Container path operations: `ContainerList`, `ContainerCreate`, `ContainerInspect`, `ContainerTop`, `ContainerLogs`, `ContainerChanges`, `ContainerExport`, `ContainerStats`, `ContainerResize`, `ContainerStart`, `ContainerStop`, `ContainerRestart`, `ContainerKill`, `ContainerUpdate`, `ContainerRename`, `ContainerPause`, `ContainerUnpause`, `ContainerAttach`, `ContainerAttachWebsocket`, `ContainerWait`, `ContainerDelete`, `ContainerArchiveInfo`, `ContainerArchive`, `PutContainerArchive`, and `ContainerPrune`.
- Image path operations: `ImageList`, `ImageBuild`, `BuildPrune`, `ImageCreate`, `ImageInspect`, `ImageHistory`, `ImagePush`, `ImageTag`, `ImageDelete`, `ImageSearch`, `ImagePrune`, `ImageCommit`, `ImageGet`, `ImageGetAll`, and `ImageLoad`.
- System path operations: `SystemAuth`, `SystemInfo`, `SystemVersion`, `SystemPing`, `SystemEvents`, and `SystemDataUsage`.
- Exec path operations: `ContainerExec`, `ExecStart`, `ExecResize`, and `ExecInspect`.

## Control Flow

Container lifecycle flow starts with `POST /containers/create`, which combines portable `ContainerConfig`, host-specific `HostConfig`, and optional `NetworkingConfig.EndpointsConfig`. The created ID can then be used for `start`, `stop`, `restart`, `kill`, `pause`, `unpause`, `rename`, `update`, `wait`, `inspect`, archive/file operations, attach/logs/stats, and delete. `ContainerUpdate` is narrower than create and accepts resource controls plus restart policy without recreating the container.

Container listing and inspection are separate response shapes. `GET /containers/json` returns compact `ContainerSummary` objects with filter support, optional stopped containers, and optional size fields. `GET /containers/{id}/json` returns a detailed inspect response with state booleans, timestamps, host config, graph driver data, mounts, config, and network settings.

Streaming control flow is explicit. `ContainerAttach` can return `101` with an upgraded/hijacked connection or `200` without upgrade headers. When TTY is disabled, stdout/stderr are multiplexed with 8-byte frame headers where the first byte selects the stream and the last four bytes encode payload size; when TTY is enabled, the stream is raw PTY data. `ContainerLogs` can also return a stream for follow mode, and `ContainerStats` defaults to a live stream unless `stream=false`.

Filesystem transfer flow uses tar archives. `ContainerExport` exports a whole container filesystem. `HEAD /containers/{id}/archive` returns file metadata in the `X-Docker-Container-Path-Stat` header. `GET /containers/{id}/archive` downloads a path as tar, and `PUT /containers/{id}/archive` uploads and extracts a tar stream into an existing directory, optionally rejecting directory/non-directory overwrite mismatches.

Image flow covers local and registry-backed operations. `ImageBuild` consumes a build context tar or remote context and streams JSON build status. `ImageCreate` either pulls from a registry or imports from a source/body. `ImagePush` uses required registry auth and is canceled when the connection closes. `ImageTag`, `ImageDelete`, `ImagePrune`, `ImageGet`, `ImageGetAll`, and `ImageLoad` mutate or transfer local image store contents. `ImageCommit` snapshots a container into a new image and can pause the container before committing.

System flow is mostly read-only. `SystemAuth` validates registry credentials and may return an identity token. `/info`, `/version`, and `/_ping` report daemon and API capability state. `/events` streams past and live events with JSON string filters. `/system/df` summarizes image, container, volume, and layer disk usage.

Exec flow is two-step. `POST /containers/{id}/exec` creates an exec instance tied to a running container and returns an ID. `POST /exec/{id}/start` starts it, either detached or attached to a raw-stream session. `POST /exec/{id}/resize` changes the TTY size only for TTY exec sessions. `GET /exec/{id}/json` reports running state, exit code, process config, open stream flags, container ID, and PID.

## State And Persistence Behavior

The YAML has no runtime state, but it documents durable and transient daemon state:

- Container create persists container metadata/configuration and prepares filesystem/network/mount state. Start/stop/restart/kill/pause/unpause/wait change or observe process state, exit status, timestamps, restart counts, and cgroup freezer state.
- Container `HostConfig` and `Resources` map directly to host-level cgroup, device, logging, namespace, security, mount, DNS, and Windows isolation settings. Some updateable resource fields can be changed without recreation through `ContainerUpdate`.
- Mount and volume state is split between requested mount specs (`Mount`, `HostConfig.Binds`, `VolumesFrom`) and observed mount points (`MountPoint`). Anonymous volumes may be removed during container deletion with `v=true`.
- Image operations persist or remove content-addressed image/layer data, repository tags, digests, history, metadata, and build cache. Image deletion can untag or delete layers, and prune endpoints report reclaimed bytes.
- Build state is streamed as status/progress JSON and may create intermediate containers. The `rm` and `forcerm` parameters govern cleanup after success or failure.
- Registry interactions use per-request auth headers or body credentials. Pull/push/build operations can be canceled by dropped connections and may contact remote registries.
- System info exposes daemon state such as storage driver, runtime configuration, plugins, registry configuration, proxy settings, swarm status, live-restore, security options, commit IDs, and resource totals. Some values are startup snapshots, such as available CPU count.
- Events are an append/stream view of daemon object changes. Filtering by object type, ID/name, label, scope, and event narrows the stream.
- Exec instances are transient state attached to a container. They have separate IDs, process configs, stream flags, running/exited status, exit code, and PID.

Swarm definitions in this chunk describe versioned raft-backed objects (`ObjectVersion`, `SwarmSpec`, `ServiceSpec`, `Task`, `Secret`, `Config`) even where their mutating paths are outside the line range. The version index is documented as an optimistic concurrency guard for updates.

## Dependencies

This contract depends on Swagger 2.0 semantics, ReDoc rendering conventions, Docker's generated client/server type pipeline, and `$ref` resolution within the same YAML file. `x-go-name` and `x-nullable` annotations influence generated Go bindings and documentation.

Runtime dependencies described by the API include Linux and Windows container runtime primitives, cgroups, namespaces, filesystem/archive handling, graph drivers, volume drivers, network drivers/IPAM, logging drivers, OCI runtimes through containerd, registry services, build context processing, and swarmkit object models.

Several endpoints depend on Docker-specific transport behavior beyond ordinary JSON HTTP. Attach, logs, stats, build, create/pull/push, events, image load/save, and exec start may stream bytes or JSON messages over long-lived responses; attach and follow-style logs can rely on connection upgrade/hijacking and raw-stream framing.

Authentication is intentionally registry-side rather than daemon-session auth in this spec. The auth material is supplied in `X-Registry-Auth`, `X-Registry-Config`, or the `/auth` body and is base64-encoded JSON using Docker registry credential fields.

## Integration Points

The `operationId` values are the main SDK generation and documentation anchors. They map directly to Docker CLI workflows such as `docker ps`, `docker create`, `docker inspect`, `docker logs`, `docker attach`, `docker cp`, `docker prune`, `docker build`, `docker pull`, `docker push`, `docker tag`, `docker rmi`, `docker save/load`, `docker login`, `docker info`, `docker events`, `docker system df`, and `docker exec`.

Container definitions integrate with image definitions through `ContainerConfig`: images preserve creation-time config, while new containers use image defaults plus create-time overrides. Container network fields integrate with endpoint and network definitions through `EndpointSettings`, `NetworkSettings`, and per-network maps.

Image endpoints integrate with registries through names/tags/digests, auth headers, platform selectors, registry mirrors/insecure registry config, push/pull progress records, and image tarball formats. Build integrates with Dockerfile parsing, remote Git/HTTP contexts, build cache selection, resource limits, labels, platform targeting, and optional registry credentials for base images.

System endpoints integrate otherwise separate subsystems into one daemon view: plugins, graph/storage drivers, cgroup/runtimes, registry config, swarm state, security features, commit metadata, proxies, and host resource totals. `/system/df` reuses image, container, and volume schemas to provide a cross-resource disk usage report.

Exec APIs integrate with container attach streaming. A client that supports `ContainerAttach` raw-stream handling can generally reuse the same stream decoder for `ExecStart` when TTY is disabled.

## Risks And Edge Cases

- The API uses an open schema model. Strict clients that reject additional response properties or unknown request fields will be brittle against newer daemons.
- Many filter parameters are JSON-encoded `map[string][]string` values carried as query strings, not structured query objects. Incorrect URL escaping or client-side typing can silently broaden queries or cause `400`.
- `ContainerList` and `ImageList` intentionally use smaller summary shapes than inspect endpoints. Code that assumes inspect-only fields are present in list responses will break.
- Several parameters are string-typed because they accept non-numeric sentinels or complex values, such as `tail=all`, JSON filter strings, `pull`, build args, labels, cache-from lists, and detach key sequences.
- Attach/log/exec streaming can return `101` and hijack the connection. Generic OpenAPI clients that only handle JSON bodies or ordinary `200` responses will mishandle interactive sessions and follow logs.
- TTY changes raw-stream framing: non-TTY streams are multiplexed with frame headers, while TTY streams are unframed PTY data. Clients must branch on the container/exec TTY setting.
- `ContainerLogs` only works for containers using `json-file` or `journald` logging drivers; other logging drivers are a compatibility and test edge.
- `ContainerInspect` documents that `Running` and `Paused` can both be true; callers should use `State.Status` rather than boolean combinations to classify state.
- `ContainerResize` says the container must be restarted for resize to take effect, while exec resize only works for TTY exec sessions. Tests need to reflect those different semantics.
- Archive upload requires the target path to be a directory and may fail on read-only volume/rootfs state. The `noOverwriteDirNonDir` query parameter is string-typed and accepts multiple truth spellings.
- Image deletion has dependency constraints: descendant images, running containers, stopped-container references, multiple tags, and active builds can prevent removal unless supported flags are chosen.
- Build parameters mix booleans, integers, strings, headers, and a binary body. `buildargs` is documented as a JSON map but typed as `integer` in this YAML, a notable schema risk for generated clients.
- Registry auth is base64-encoded JSON with legacy Docker Hub URL requirements in `X-Registry-Config`. Missing or malformed auth can surface as pull/push/build failures rather than local validation errors.
- `SystemInfo` includes platform-specific fields and deprecated standalone Swarm/registry fields. Cross-platform clients need nullable/empty handling.
- The chunk defines many swarm/plugin/volume/network schemas before their path operations. Schema-level conclusions are valid here, but endpoint behavior for those resources is in later chunks.

## Test Signals

Useful validation signals for this chunk include:

- Swagger/OpenAPI linting for unique `operationId` values, resolvable `$ref`s, valid path parameter declarations, valid response schemas, and intentional custom fields such as `x-nullable` and `x-go-name`.
- Generated-client tests that preserve Docker-specific string-encoded JSON filters, string `tail`, string `noOverwriteDirNonDir`, binary bodies, tar media types, raw-stream media types, and multiple success statuses including `101`, `200`, `201`, `204`, and `304`.
- Container lifecycle integration tests for create/list/inspect/start/stop/restart/kill/pause/unpause/update/rename/wait/delete, including missing-container `404`, already-started/stopped `304`, conflict `409`, and delete `force`/volume behavior.
- Attach/log/exec stream tests covering upgraded and non-upgraded responses, multiplexed non-TTY framing, raw TTY framing, `stdin`/`stdout`/`stderr` selection, detach keys, follow mode, and unsupported logging drivers.
- Container filesystem tests for changes, export, archive stat header decoding, archive download, archive upload, not-a-directory errors, read-only `403`, missing path `404`, compression formats, and overwrite protection.
- Stats tests for `stream=true` continuous responses, `stream=false` single response, CPU percentage calculation using `precpu_stats`, and fallback when `online_cpus` is absent.
- Image tests for list filters/digests, build context upload and remote contexts, build cancellation on dropped connection, cache/no-cache options, intermediate container cleanup, pull/import/create, inspect/history, push auth, tag overwrite, delete conflict/force/noprune, search filters, prune filters, commit pause behavior, save/load tar format, and platform query handling.
- System tests for `/auth` token/no-token responses, `/info` schema breadth, `/version` component details, `/_ping` headers, `/events` filtering and streaming cutoff with `since`/`until`, and `/system/df` cross-resource usage data.
- Contract tests should specifically flag schema/documentation mismatches such as `ImageBuild` `buildargs` being typed as an integer despite a JSON-map description, and any examples that include fields not declared in their surrounding schema.
