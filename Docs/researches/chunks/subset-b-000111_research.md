# sources/cloud-native/moby/api/docs/v1.31.yaml lines 1-7634

## Scope And Purpose

This chunk is the main body of the Docker Engine API v1.31 Swagger 2.0 contract. It covers the top-level API metadata, tag layout, all shared schema definitions, and most path operations from containers through the beginning of `SwarmInit`. The source is not executable daemon code; it is an authoritative HTTP API description used for generated documentation and for client/server type generation, as stated in the file header.

The API is versioned under `basePath: "/v1.31"` and describes the HTTP surface used by Docker clients to control the Engine. It models container, image, auth, system, exec, volume, network, plugin, node, and initial swarm operations. The chunk ends at line 7634 inside the `/swarm/init` request body after the `ListenAddr` property, so the rest of `SwarmInit` and later swarm, service, task, secret, config, distribution, and session paths are outside this chunk.

## API Metadata And Organization

The top-level document declares Swagger 2.0, HTTP and HTTPS schemes, JSON and plain-text request/response defaults, and API information for Docker Engine API v1.31. The long `info.description` documents standard JSON error bodies, version prefix behavior, deprecated unversioned access, the open schema model, and registry authentication via Base64-encoded `X-Registry-Auth` JSON or identity tokens from `/auth`.

The tag list is part documentation layout and part client-generation signal. Primary object tags are `Container`, `Image`, `Network`, `Volume`, and `Exec`; swarm-related tags are `Swarm`, `Node`, `Service`, `Task`, and `Secret`; system-level tags are `Plugin` and `System`. Operation IDs follow the file comment convention of singular noun plus verb, such as `ContainerCreate`, `ImageBuild`, `SystemInfo`, `ExecStart`, `PluginUpgrade`, `NodeUpdate`, and `SwarmInit`.

## Shared Definitions

The definitions section provides reusable models for the path contracts. Major groups are:

- Container and filesystem models: `Port`, `MountType`, `MountPoint`, `Mount`, `DeviceMapping`, `ThrottleDevice`, `RestartPolicy`, `Resources`, `HealthConfig`, `HostConfig`, `ContainerConfig`, `NetworkConfig`, and `ContainerSummary`.
- Image and registry models: `ImageHistoryResponseItem`, `GraphDriverData`, `Image`, `ImageSummary`, `AuthConfig`, `BuildInfo`, `CreateImageInfo`, `PushImageInfo`, `ImageDeleteResponseItem`, `ErrorDetail`, `ProgressDetail`, `ErrorResponse`, and `IdResponse`.
- Storage and networking models: `Volume`, `Network`, `IPAM`, `NetworkContainer`, `EndpointSettings`, `EndpointPortConfig`, and `EndpointSpec`.
- Plugin models: `PluginMount`, `PluginDevice`, `PluginEnv`, `PluginInterfaceType`, and `Plugin`.
- Swarm orchestration models: `ObjectVersion`, `NodeSpec`, `Node`, `TLSInfo`, `SwarmSpec`, `ClusterInfo`, `TaskSpec`, `TaskState`, `Task`, `ServiceSpec`, `Service`, and `ServiceUpdateResponse`.
- Swarm data object models introduced in this API area: `Driver`, `SecretSpec`, `Secret`, `ConfigSpec`, and `Config`.

`HostConfig` composes `Resources` with host-dependent options such as binds, logging, network mode, port bindings, restart policy, mounts, Linux capabilities, namespace modes, tmpfs, sysctls, runtime, Windows console size, and Windows isolation. `ContainerConfig` describes portable image/container runtime settings such as command, entrypoint, environment, labels, healthcheck, exposed ports, stop signal, stop timeout, shell, and image name.

`TaskSpec` is the core swarm execution template. It can describe either `PluginSpec` or `ContainerSpec`, includes Windows credential specs, SELinux context, mounts, health checks, hosts, DNS config, secret/config references, resources, restart policy, placement constraints and preferences, target platforms, force-update counter, runtime, networks, and log driver. `ServiceSpec` wraps that template with replicated/global scheduling, update and rollback policies, service networks, and endpoint/load-balancing configuration.

`ObjectVersion` is a key concurrency type. Its description requires clients to send the current version when updating versioned swarm objects so simultaneous updates do not overwrite each other.

## Container Operations

The container API covers listing, creation, inspection, process listing, logs, filesystem diffs, export, stats, TTY resize, lifecycle changes, attach, wait, delete, archive transfer, and pruning.

Important operations in this chunk include:

- `GET /containers/json` (`ContainerList`) returns `ContainerSummary` data with `all`, `limit`, `size`, and JSON-encoded filters for ancestry, status, health, labels, ID/name, network, exposed/published ports, volume, isolation, and swarm task membership.
- `POST /containers/create` (`ContainerCreate`) accepts `ContainerConfig` plus `HostConfig` and `NetworkingConfig`, optionally names the container, and returns a created ID with warnings.
- `GET /containers/{id}/json` (`ContainerInspect`) returns low-level state, host paths, labels, restart count, driver data, mounts, host config, portable config, graph driver data, and network settings.
- `ContainerTop`, `ContainerLogs`, `ContainerChanges`, `ContainerExport`, `ContainerStats`, and `ContainerResize` expose process, log, filesystem, tar export, live metrics, and TTY control views.
- Lifecycle mutation endpoints include `ContainerStart`, `ContainerStop`, `ContainerRestart`, `ContainerKill`, `ContainerUpdate`, `ContainerRename`, `ContainerPause`, and `ContainerUnpause`.
- Stream and blocking endpoints include `ContainerAttach`, `ContainerAttachWebsocket`, and `ContainerWait`.
- `/containers/{id}/archive` has `HEAD` (`ContainerArchiveInfo`), `GET` (`ContainerArchive`), and `PUT` (`PutContainerArchive`) forms for container filesystem metadata, tar export, and archive extraction.
- `POST /containers/prune` deletes stopped containers with optional `until` and label filters.

The attach and logs APIs are special. `ContainerAttach` can hijack or upgrade the HTTP connection and uses `application/vnd.docker.raw-stream`. When the container has no TTY, stdout and stderr are multiplexed with an eight-byte header and big-endian frame length. With TTY enabled, the stream is raw PTY data. Generated clients that only support ordinary JSON request/response handling will not be sufficient for these endpoints.

Container state changes are modeled through HTTP transitions and status codes. Creation can fail for bad parameters, missing images, impossible attach configuration, conflicts, or daemon errors. Start/stop use `204` for success and `304` for already-started or already-stopped states. Delete can remove anonymous volumes, force-kill running containers, or remove links, and reports conflict when a running container cannot be removed without force.

## Image, Build, Auth, And System Operations

Image operations include list, build, builder cache prune, pull/import, inspect, history, push, tag, remove, search, image prune, commit, save, and load:

- `GET /images/json` (`ImageList`) returns `ImageSummary` data and supports `all`, `digests`, and JSON-encoded filters for before/since, dangling state, labels, and references.
- `POST /build` (`ImageBuild`) consumes a compressed tar build context, validates the Dockerfile before executing instructions, supports remote contexts, tags, cache options, resource controls, build args, labels, network mode, squash, and registry config headers, and cancels when the client connection drops.
- `POST /build/prune` (`BuildPrune`) deletes builder cache and reports reclaimed bytes.
- `POST /images/create` (`ImageCreate`) pulls from a registry or imports from a URL/body and can use `X-Registry-Auth`.
- `ImageInspect`, `ImageHistory`, `ImagePush`, `ImageTag`, `ImageDelete`, `ImageSearch`, and `ImagePrune` expose standard image lifecycle and registry flows.
- `ImageGet`, `ImageGetAll`, and `ImageLoad` exchange image tarballs and document the legacy image tarball layout with layer directories, `VERSION`, `json`, `layer.tar`, and optional `repositories`.

System endpoints in this chunk are `SystemAuth`, `SystemInfo`, `SystemVersion`, `SystemPing`, `SystemEvents`, and `SystemDataUsage`. They expose registry credential validation, daemon and host configuration, API/version metadata, liveness headers, event streams, and disk usage across layers, images, containers, and volumes. `ImageCommit` snapshots a container into a new image, optionally pausing the container and applying Dockerfile-style changes.

State and persistence risks are high in this area. Builds create images and intermediate containers; pulls, pushes, plugin pulls, and builds depend on registry authentication; image deletion and prune endpoints mutate local image and cache stores; commits snapshot container filesystems; and tar save/load endpoints can import or export large persistent state.

## Exec, Volume, Network, And Plugin Operations

Exec is a two-step workflow. `POST /containers/{id}/exec` (`ContainerExec`) creates an exec instance with attach flags, env, command, TTY, privileged flag, user, and detach keys. `POST /exec/{id}/start` (`ExecStart`) starts the instance and can attach an interactive raw stream unless detached. `ExecResize` changes TTY size for TTY exec sessions, and `ExecInspect` reports running state, exit code, process config, stdio flags, container ID, and process ID. Paused or stopped containers surface as `409` conflicts for exec creation/start.

Volume operations include `VolumeList`, `VolumeCreate`, `VolumeInspect`, `VolumeDelete`, and `VolumePrune`. The volume schema includes driver, mountpoint, labels, local/global scope, options, optional driver status, creation timestamp, and usage data. Deletion and prune mutate persistent host or driver-backed storage and must handle in-use volumes via `409`.

Network operations include `NetworkList`, `NetworkInspect`, `NetworkDelete`, `NetworkCreate`, `NetworkConnect`, `NetworkDisconnect`, and `NetworkPrune`. Network creation accepts duplicate-name best-effort checking, driver, internal/attachable/ingress flags, IPv6, IPAM, options, and labels. Connect/disconnect operate on container endpoints through `EndpointSettings`; the spec explicitly returns `403` for swarm-scoped networks where direct container connect/disconnect is unsupported.

Plugin operations include `PluginList`, `GetPluginPrivileges`, `PluginPull`, `PluginInspect`, `PluginDelete`, `PluginEnable`, `PluginDisable`, `PluginUpgrade`, `PluginCreate`, `PluginPush`, and `PluginSet`. The `Plugin` schema describes enabled state, mutable settings, remote reference, interface socket/capabilities, rootfs, Linux capabilities/devices, mounts, env, args, propagated mounts, and host namespace flags. Install and upgrade accept user-approved privilege arrays and optional registry auth. `PluginSet` configures plugin environment-like settings with a string array body.

Plugins are especially sensitive integration points because they can extend daemon volume, network, and other host-facing capabilities. Force delete/disable and privilege acceptance should be covered by daemon validation and integration tests, not trusted to client schemas alone.

## Node And Swarm Operations In This Chunk

Node operations include:

- `GET /nodes` (`NodeList`) with JSON filters for ID, labels, membership, name, and role.
- `GET /nodes/{id}` (`NodeInspect`) returning `Node` metadata, spec, description, engine plugins, status, manager status, and TLS information.
- `DELETE /nodes/{id}` (`NodeDelete`) with optional force removal.
- `POST /nodes/{id}/update` (`NodeUpdate`) with a `NodeSpec` body and required `version` query parameter for optimistic concurrency.

Swarm coverage starts with `GET /swarm` (`SwarmInspect`) and `POST /swarm/init` (`SwarmInit`). `SwarmInspect` returns `ClusterInfo` plus join tokens, root rotation state, TLS information, and `SwarmSpec`. The chunk includes the start of `SwarmInit`, including response status codes and the beginning of the request body with `ListenAddr`; later fields such as advertise address, data-path address, force-new-cluster, and the spec body continue beyond the requested line range.

The swarm definitions visible in this chunk model Raft settings, dispatcher heartbeats, CA/external CA settings, manager autolock encryption-at-rest, task default log driver, node certificate/TLS issuer information, task states, service update/rollback policies, and secret/config references from service task templates.

## Dependencies And Integration Points

This file depends on Swagger/OpenAPI 2.0 semantics, JSON Schema-like object definitions, `$ref` resolution, `allOf` composition, path/query/header/body parameter encoding, and vendor extensions such as `x-go-name` and `x-nullable`. It is intended for ReDoc rendering and generated Docker client/server types, so operation IDs, tags, examples, and schema names are part of the public developer surface.

Runtime integration points described by the contract include:

- Docker Engine HTTP routing and daemon handlers for every path/method/status/body combination.
- Docker CLI and SDK clients that map commands onto these versioned endpoints.
- Container runtime, cgroups, namespaces, Windows isolation, credential specs, SELinux, AppArmor, seccomp, logging drivers, storage drivers, graph drivers, and filesystem archive handling.
- Registry interactions through `X-Registry-Auth`, `X-Registry-Config`, image pull/push, build, plugin pull, and plugin upgrade.
- Network and IPAM drivers, swarm overlay/ingress behavior, and volume/plugin drivers.
- Swarmkit/Raft state for nodes, services, tasks, object versions, CA rotation, join tokens, secrets, configs, task defaults, and manager autolock.
- Documentation generation through markdown descriptions, examples, tag grouping, and link anchors.

## State And Persistence Behavior

The YAML itself is static contract data. The API it describes controls substantial daemon state:

- Containers are created, configured, started, stopped, killed, paused, unpaused, renamed, updated, waited on, attached to, removed, archived, exported, and pruned.
- Images are built, pulled, imported, tagged, pushed, inspected, committed, saved, loaded, deleted, searched, and pruned; builder cache can also be pruned.
- Volumes and networks can be created, attached to containers, disconnected, removed, and pruned.
- Exec instances are created, started, resized, inspected, and associated with container lifecycle state.
- Plugins are installed, configured, enabled, disabled, upgraded, pushed, created from tar, and removed.
- Swarm node and cluster objects are versioned and persisted, with update requests protected by explicit object-version query parameters.

The API uses status codes as lifecycle and state guards: `404` for missing objects, `409` for conflicts or in-use/paused/stopped states, `403` for unsupported or permission-denied operations, `304` for no-op lifecycle transitions, `406` for impossible attach semantics, and `503` for swarm precondition failures such as not being in a swarm or already being in one.

## Risks And Edge Cases

- The contract uses an open schema model. Clients should ignore unknown response fields and should not assume generated models are closed over future daemon responses.
- Stream-oriented endpoints (`logs`, `attach`, `attach/ws`, `stats`, `events`, build/pull/push/load/save paths, and exec start) require special handling for hijacked sockets, raw streams, tar archives, JSON progress streams, and long-lived responses.
- Registry auth headers and build registry config contain sensitive Base64-encoded JSON. Debug logging and tracing must redact them.
- Build arguments are explicitly not intended for secrets, but this cannot be enforced by the schema and can lead to sensitive data in image layers or history.
- Prune/delete endpoints can remove broad persistent state. Filters, force flags, in-use checks, and reclaimed-space accounting need careful conformance testing.
- Several schema details are weakly typed or inconsistent with examples. `NetworkConfig` is marked with `TODO: check is correct`; some examples include fields not represented in nearby schemas, such as `KernelMemory`/`MaximumIOps` style fields; `ProgressDetail.message` is typed as integer; `buildargs` is documented as a JSON map but typed as integer; and `ServiceUpdateResponse` defines `Warnings` while its example uses `Warning`.
- Platform-specific options are mixed into shared models. Linux-only cgroup/namespace/security settings and Windows-only credential spec, isolation, console, and CPU controls require platform-aware validation.
- `Node.Description.TLSInfo` references `SwarmSpec` in the schema even though a separate `TLSInfo` definition exists and examples show TLS fields. That looks like a schema reference risk for generated clients.
- The chunk boundary interrupts `SwarmInit`; consumers of this chunk report should not treat the visible request body as a complete operation schema.

## Test Signals

Useful validation signals for this chunk include:

- Swagger/OpenAPI linting for `$ref` resolution, operation ID uniqueness, valid parameter placement, required fields, response schemas, examples, and vendor extension handling.
- Generated type compilation from v1.31, with attention to `x-nullable`, `x-go-name`, `allOf`, maps, string-or-array fields, binary bodies, array query parameters, and object examples.
- API conformance tests for documented status codes, error body shape, path/query/header/body encoding, and filters encoded as JSON `map[string][]string`.
- Stream-specific tests for attach multiplexing and TTY mode, websocket attach, logs follow mode, stats stream versus single-shot mode, events since/until behavior, exec start streams, build progress, pull/push progress, image save/load tar streams, and archive upload/download.
- Persistence tests for container lifecycle, container archive writes, image build/import/export/delete/prune, builder cache prune, volume lifecycle/prune, network create/connect/disconnect/prune, plugin install/configure/enable/disable/upgrade/delete, and node update/delete.
- Swarm concurrency tests for `ObjectVersion`-protected updates, especially `NodeUpdate` in this chunk and later swarm/service/secret/config updates in following chunks.
- Security tests for redaction of registry auth headers, plugin privilege approval, host namespace/capability settings, credential spec loading, secret/config references in service task templates, and read-only filesystem/archive permission checks.
