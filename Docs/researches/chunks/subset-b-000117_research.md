# sources/cloud-native/moby/api/docs/v1.34.yaml lines 1-7562

## Scope And Purpose

This chunk is the opening and largest foundational slice of the Docker Engine API v1.34 Swagger 2.0 document. It defines global API metadata, versioning/authentication behavior, ReDoc tag ordering, reusable schemas under `definitions`, and the first path block from container APIs through the beginning of volume creation. The file is both user-facing API documentation and a schema source for generated client/server types, so field names, `operationId` values, response codes, examples, and vendor extensions such as `x-go-name` and `x-nullable` are part of the contract.

The documented base path is `/v1.34`, with HTTP/HTTPS schemes and default JSON/text consume/produce declarations. The introductory contract states that clients should prefix URLs with an API version, that unversioned access is deprecated, unsupported versions return HTTP 400, and the schema is open: daemons may add response fields and ignore unknown request fields. Registry authentication is deliberately client-side and passed to registry-facing endpoints through base64-encoded JSON in `X-Registry-Auth`; identity tokens from `/auth` can replace username/password credentials.

## Source Layout In This Chunk

- Lines 1-138: Swagger metadata, API versioning, open-schema compatibility rules, registry auth header format, and top-level tags for Container, Image, Network, Volume, Exec, Swarm, Node, Service, Task, Secret, Config, Plugin, and System.
- Lines 139-4221: reusable response and model definitions for containers, images, volumes, networks, plugins, swarm objects, services, tasks, secrets, configs, system info, registry config, runtime commits, and local swarm status.
- Lines 4222-7562: path definitions beginning with `/containers/json` and continuing through `/volumes/create`; the chunk ends in the middle of the `VolumeCreate` request body schema immediately after the `Name` field description.

## Important APIs, Types, And Schemas

Container and filesystem model:

- `ContainerConfig` describes portable image/container configuration: identity and process fields, attach/stdin/TTY flags, environment, command/entrypoint, image reference, exposed ports, volumes, working directory, labels, healthcheck, stop signal/timeout, shell, and Windows `ArgsEscaped`.
- `HostConfig` composes `Resources` and host-specific settings: bind strings, log driver, network mode, port bindings, restart policy, auto-removal, volume inheritance, mounts, Linux capabilities/namespaces/DNS/security/sysctl/tmpfs/runtime knobs, and Windows console/isolation fields.
- `Resources` is the shared cgroup/resource schema used for create and update: CPU shares/quota/period/realtime/nano CPU, memory limits/reservation/swap/swappiness, blkio throttle devices, cgroup parent, devices and cgroup rules, pids, ulimits, OOM behavior, and Windows CPU/IO controls.
- `MountType`, `Mount`, and `MountPoint` separate request-time mount intent from inspect/list reporting. Mount requests support `bind`, `npipe`, `tmpfs`, and `volume`, with nested bind propagation, volume driver/options/no-copy, and tmpfs size/mode. Mount reports include source, destination, driver, mode, RW, and propagation.
- `NetworkSettings`, `EndpointSettings`, `EndpointIPAMConfig`, `PortMap`, `PortBinding`, and `Address` define container networking and per-network endpoint data. The older default-bridge fields in `NetworkSettings` are documented as deprecated in favor of the `Networks` map.
- `HealthConfig` documents healthcheck command forms, exit-code meaning, retry count, interval/timeout/start-period units, and minimum timing behavior.
- `ContainerSummary` is the smaller list representation used by `/containers/json` and `/system/df`, distinct from full inspect output.

Image, registry, and build model:

- `Image`, `ImageSummary`, `ImageHistoryResponseItem`, `ImageDeleteResponseItem`, `GraphDriverData`, `BuildInfo`, `CreateImageInfo`, `PushImageInfo`, `ProgressDetail`, and `ErrorDetail` cover image inspection, listing, history, delete results, graph-driver metadata, and progress/error streams.
- `AuthConfig` is the JSON shape accepted by `/auth` and encoded in registry auth headers. It keeps deprecated `email` for compatibility.
- `RegistryServiceConfig` and `IndexInfo` expose daemon registry policy: insecure registry CIDRs and host configs, index mirrors, official registry state, and deprecated nondistributable-artifact lists.
- `Runtime` and `Commit` connect daemon info to OCI runtimes and build-time expected commits for `containerd`, `runc`, and `docker-init`.

Volume and network model:

- `Volume` describes persistent storage state with required name, driver, mountpoint, labels, scope, options, optional driver status, creation time, and `UsageData` used by `/system/df`. `UsageData.Size` and `RefCount` use `-1` for unavailable values.
- `Network`, `IPAM`, and `NetworkContainer` describe user-defined network metadata, IPAM config, attached containers, driver/options/labels, scope, IPv6, internal, attachable, and ingress flags.

Plugin and swarm model:

- `Plugin`, `PluginMount`, `PluginDevice`, `PluginEnv`, and `PluginInterfaceType` define managed plugin metadata, mutable settings, rootfs layers, interface socket/type, Linux device/capability needs, propagated mounts, env, args, and host namespace flags.
- `ObjectVersion` is the central optimistic-concurrency token for swarm-managed objects. The comments state clients must submit the version when updating so concurrent writes cannot silently overwrite each other.
- `NodeSpec`, `Node`, `NodeDescription`, `Platform`, `EngineDescription`, `TLSInfo`, `NodeStatus`, `NodeState`, `ManagerStatus`, and `Reachability` model swarm nodes and managers.
- `SwarmSpec`, `ClusterInfo`, `JoinTokens`, `Swarm`, `SwarmInfo`, `LocalNodeState`, and `PeerNode` model cluster settings, raft and CA configuration, autolock/encryption, task defaults, local swarm state, remote managers, and join tokens.
- `TaskSpec`, `TaskState`, `Task`, `ServiceSpec`, `EndpointPortConfig`, `EndpointSpec`, `Service`, and `ServiceUpdateResponse` model swarm scheduling, container/plugin task templates, secrets/config references, placement, resources, restart policies, service modes, update/rollback policies, endpoint publishing, task status, and service update warnings.
- `SecretSpec`/`Secret` and `ConfigSpec`/`Config` define swarm secret/config objects. Secret data is base64 and create-only; external secret drivers are supported. Config data has a documented max-size link.

System model:

- `SystemInfo` is a broad daemon snapshot: container/image counts, storage driver and root directory, cgroup/resource support flags, debug counters, host OS/kernel/architecture, registry config, proxy env-derived settings, daemon labels, experimental flag, runtimes/default runtime, swarm info, live-restore, isolation, init binary, component commits, and security options.
- `PluginsInfo` only includes unmanaged V1 plugins and may omit lazily loaded plugins.
- `ErrorResponse` and `IdResponse` are reused across most endpoints.

## Endpoint Flow And Behavior

Container lifecycle and inspection:

- `GET /containers/json` (`ContainerList`) lists containers using `ContainerSummary`, with `all`, `limit`, `size`, and JSON `filters`. Filters include ancestry, creation ordering, ports, exit code, health, id/name, isolation, task marker, labels, network, status, and volume. Errors are 400 for bad parameters and 500 for daemon failures.
- `POST /containers/create` (`ContainerCreate`) combines `ContainerConfig`, `HostConfig`, and `NetworkingConfig.EndpointsConfig`, returns 201 with created container ID and warnings, and distinguishes bad parameters, missing image, conflicts, and server errors.
- `GET /containers/{id}/json` (`ContainerInspect`) returns full state/config/host config/graph driver/mount/network information. The state block documents an important semantic trap: a paused container can have both `Running` and `Paused` true, so clients should prefer `Status`.
- `GET /containers/{id}/top`, `/logs`, `/changes`, `/export`, `/stats`, and `/resize` expose process listing, log retrieval, filesystem-diff reporting, rootfs tar export, resource usage streaming, and TTY sizing. `top` is Unix-only. Logs require `json-file` or `journald`; `follow` can hijack/upgrade the connection. Stats use `precpu_stats` for CPU percentage calculations and include compatibility guidance for missing `online_cpus`.
- `POST /containers/{id}/start`, `/stop`, `/restart`, `/kill`, `/update`, `/rename`, `/pause`, `/unpause`, and `/wait` mutate lifecycle or configuration. Idempotency and state conflicts are visible in response codes: start/stop may return 304 when already in that state; remove and rename can return 409; wait supports `not-running`, `next-exit`, and `removed`.
- `DELETE /containers/{id}` removes containers with options for anonymous volumes, forced kill-before-remove, and link removal. Running-container deletion without `force` is a documented conflict.
- `HEAD`, `GET`, and `PUT /containers/{id}/archive` implement Docker copy-style filesystem access. The HEAD response returns `X-Docker-Container-Path-Stat`, a base64 JSON stat header. GET returns tar. PUT extracts tar into a required directory path, can reject directory/non-directory overwrite with `noOverwriteDirNonDir`, and returns 403 when the target volume or rootfs is read-only.
- `POST /containers/prune` deletes stopped containers by JSON filters (`until`, `label`, `label!=`) and reports deleted IDs and reclaimed bytes.

Attach, stream, and exec protocol:

- `POST /containers/{id}/attach` (`ContainerAttach`) is a connection-hijacking endpoint. It requires `stream` or `logs` to be useful, may return 101 with upgrade headers or 200 without an upgrade header, and produces `application/vnd.docker.raw-stream`.
- Non-TTY attach output is multiplexed into 8-byte-header frames: stream type byte, three zero bytes, and a big-endian uint32 payload size; stream types are stdin/stdout/stderr. With TTY enabled, there is no multiplexing and raw PTY bytes are exchanged.
- `GET /containers/{id}/attach/ws` provides a websocket attach variant.
- `POST /containers/{id}/exec` creates an exec instance in a running container and can fail with 409 if the container is paused. `POST /exec/{id}/start` starts it and either detaches immediately or opens an interactive raw-stream session. `POST /exec/{id}/resize` only works for TTY execs. `GET /exec/{id}/json` exposes running state, exit code, process config, open streams, container ID, and process PID.

Image, build, and registry endpoints:

- `GET /images/json` lists images with `all`, `digests`, and JSON filters (`before`, `dangling`, `label`, `reference`, `since`), returning compact `ImageSummary` objects.
- `POST /build` builds an image from a tar stream or remote context. Build cancellation is tied to client connection close. Query/header options cover Dockerfile path, tags, extra hosts, remote Git/HTTP context, quiet/no-cache/cache-from/pull, intermediate-container cleanup, resource limits, build args, shm size, experimental squash, labels, build network mode, `Content-type`, `X-Registry-Config`, and target platform.
- `POST /build/prune` deletes builder cache and reports reclaimed space.
- `POST /images/create` pulls or imports images based on `fromImage` vs `fromSrc`, optional repo/tag/body import content, platform, and `X-Registry-Auth`; pull is canceled if the HTTP connection closes.
- `GET /images/{name}/json` and `/history` inspect image metadata and layer history.
- `POST /images/{name}/push` requires `X-Registry-Auth`; the path name is treated without tag and the `tag` query selects one tag or all tags.
- `POST /images/{name}/tag` creates or overwrites a repository/tag reference.
- `DELETE /images/{name}` removes an image and possibly untagged parents; `force` permits deletion when stopped containers or other tags refer to it, while `noprune` preserves untagged parents.
- `GET /images/search` searches Docker Hub with term/limit/filter support.
- `POST /images/prune` deletes unused images using `dangling`, `until`, and label filters, reporting deleted image entries and reclaimed bytes.
- `POST /commit` creates a new image from a container, optionally pausing the container, applying Dockerfile-style changes, and setting repo/tag/comment/author plus a container config body.
- `GET /images/{name}/get`, `GET /images/get`, and `POST /images/load` export/import image tarballs. The tarball format is documented as per-layer directories with `VERSION`, `json`, `layer.tar`, and optional root `repositories`; layer tar uses AUFS-style whiteout entries.

System and volume endpoints in range:

- `POST /auth` validates registry credentials and may return an identity token.
- `GET /info`, `/version`, and `/_ping` expose daemon info, version/build/runtime data, and a lightweight liveness/version probe. Ping returns headers for max API version and experimental mode.
- `GET /events` streams real-time events for containers, images, volumes, networks, daemon reloads, plugins, swarm services/nodes/tasks/secrets/configs. Filters are JSON `map[string][]string` by object names/IDs, event, label, scope, and type; `since` and `until` bound replay/streaming.
- `GET /system/df` returns disk usage across layers, images, containers, and volumes, reusing `ImageSummary`, `ContainerSummary`, and `Volume` with volume `UsageData`.
- `GET /volumes` lists volumes with filters for dangling status, driver, label, and name; response includes `Volumes` plus `Warnings`.
- `POST /volumes/create` begins at the end of this chunk and is only partially present: the operation ID, content types, 201/500 responses, required `volumeConfig` body, and the `Name` field description are visible. The rest of the volume-create request schema falls outside this chunk.

## State And Persistence Behavior

The API surface is explicitly stateful around daemon-managed objects. Containers persist created config, host config, runtime state, mounts, logs, filesystem changes, exec instances, network endpoints, and size accounting under Docker state paths such as `/var/lib/docker/containers/...`. Images persist content-addressed layers, graph-driver metadata, rootfs diff IDs, tags/digests, build/cache intermediates, and tarball import/export metadata. Volumes persist independently of containers unless explicitly removing anonymous volumes on container deletion; named volumes keep driver metadata, mountpoints, labels, options, and optional usage counters. Networks persist IPAM, driver options, endpoints, and container attachment state.

Swarm-managed objects use versioned state. `ObjectVersion.Index` is the documented concurrency guard for node/service/secret/config updates, and swarm configuration includes raft snapshot/election/heartbeat settings, CA rotation/autolock state, join tokens, and task history retention. System state surfaces daemon root directory, storage driver details, registry policy, default runtimes, live-restore status, proxy settings, security options, and plugin availability.

Several endpoints have stream lifecycle tied to client connections: build, pull/import, push, logs with follow, stats, attach, exec start, and events. Closing the client connection cancels build and image pull/import operations according to the documentation. Prune and delete endpoints mutate persisted stores and return reclaimed-space/deleted-object signals for auditability.

## Dependencies And Integration Points

- OpenAPI/Swagger tooling and ReDoc consume the schema, markdown descriptions, tags, examples, vendor extensions, and `operationId` naming convention.
- Docker client commands map directly to paths for list/create/inspect/start/stop/logs/attach/build/pull/push/exec/volume/system workflows.
- Registry integration is externalized through `X-Registry-Auth`, `X-Registry-Config`, `/auth`, registry mirrors, insecure-registry policy, and Docker Hub search.
- Runtime integration is through OCI runtimes invoked via `containerd`, with runtime names/paths/args exposed through `/info`.
- Host OS integrations include Linux cgroups, cpusets, blkio, OOM killer, namespaces, SELinux/AppArmor/seccomp/userns, kernel forwarding/iptables sysctls, Unix `ps`, AUFS-style whiteouts, and Windows isolation, credential specs, registry lookup, named pipes, and CPU/IO controls.
- Networking integrates Docker bridge/host/none/container modes, user-defined networks, IPAM, endpoint aliases/links, published ports, swarm ingress/host publish modes, and legacy standalone Swarm external key-value stores.
- Swarm integration depends on swarmkit-style objects, raft, manager reachability, TLS CA material, external CAs, node certificates, secrets/configs, placement, resources, and task orchestration.
- Plugin integration covers managed plugins and unmanaged V1 plugins, including volume/network/log/authz plugin exposure through system info.

## Risks And Edge Cases

- This schema intentionally permits open responses and ignored unknown request fields. Client generators and validators that assume closed schemas can break against newer daemons.
- Versioning is a compatibility boundary. Unsupported API versions return 400, while unversioned access is deprecated.
- Registry auth is base64-encoded JSON, not a server-side session. Clients must avoid logging `X-Registry-Auth`, `X-Registry-Config`, credentials, and identity tokens.
- Several fields are deprecated or unstable: `AuthConfig.email`, default-bridge fields in `NetworkSettings`, standalone Swarm `SystemStatus`, nondistributable-artifact registry fields, and storage-driver `DriverStatus` formatting.
- Attach/log/exec stream framing changes with TTY. Consumers must branch between multiplexed raw-stream frames and unframed PTY bytes.
- Paused containers can report `Running=true`; `State.Status` is the reliable lifecycle discriminator.
- API examples include platform-specific behavior. Some fields/endpoints are Linux-only or Windows-only, and tests need OS-specific expectations.
- Build args are documented as not suitable for secrets, but the API cannot enforce client-side misuse by itself.
- Prune/delete/remove endpoints are destructive and filter parsing is broad. Bad JSON filters should be tested, and label negation/until duration semantics depend on daemon time.
- Image delete, container remove, exec start, and archive PUT have meaningful 409/403/400 states that can be easy to collapse incorrectly in client code.
- The chunk ends mid-schema for `VolumeCreate`, so any final per-file analysis must merge the following chunk before treating volume-create request fields as complete.

## Test Signals

Useful conformance and regression signals from this chunk:

- Validate the Swagger document parses as Swagger 2.0 and preserves all referenced definitions through `/volumes/create` without unresolved `$ref` in this range.
- Generate client/server types and verify `x-go-name`, `x-nullable`, required fields, enums, int formats, `allOf`, array/object `additionalProperties`, and binary stream schema handling.
- Exercise container create/list/inspect/start/stop/restart/kill/update/rename/pause/unpause/wait/remove flows and assert documented 2xx/3xx/4xx/5xx outcomes, including already-started/already-stopped 304 and conflict cases.
- Test attach/log/exec raw-stream framing with TTY disabled and raw PTY behavior with TTY enabled; include websocket attach and detach-key parsing.
- Test archive HEAD/GET/PUT with valid path, missing path, file-vs-directory overwrite, read-only rootfs/volume, and compressed tar input.
- Verify image build cancellation on connection close, remote context handling, registry auth config decoding, platform parameter propagation, and cache/prune behavior.
- Verify pull/import/push/tag/delete/search/prune/commit/export/load behavior, especially auth requirements, tag-vs-name semantics, parent pruning, and tarball repositories metadata.
- Validate `/events` streaming with `since`, `until`, type/object filters, label filters, and event names generated by the documented state-changing endpoints.
- Check `/info`, `/version`, `/_ping`, and `/system/df` against daemon feature flags, root directory, runtime/commit metadata, security options, swarm state, and volume usage data.
- For volume APIs in this chunk, test `GET /volumes` filters and warnings; defer full `POST /volumes/create` schema coverage until the subsequent chunk is merged.
