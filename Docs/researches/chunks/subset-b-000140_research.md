# sources/cloud-native/moby/api/docs/v1.45.yaml lines 7752-12685

## Scope

This chunk is a large Swagger/OpenAPI 2.0 path-table slice of the Docker Engine API v1.45 contract. It starts inside the tail of `POST /containers/{id}/restart` parameters, then covers container lifecycle/streaming/archive operations, image/build/registry/system APIs, exec sessions, volumes, networks, plugins, swarm/node/service/task APIs, secrets, configs, registry distribution inspection, and the interactive session endpoint.

The source is API documentation and schema contract data, not executable implementation. It defines request parameters, media types, response bodies, operation IDs, examples, status-code behavior, and `$ref` links used by generated API docs, client bindings, SDK conformance checks, and daemon route tests.

## Purpose

The endpoints in this chunk expose the daemon's main object-control surface after container start/stop:

- container endpoints kill, update, rename, pause/unpause, attach, wait, delete, copy archives into/out of filesystems, and prune stopped containers;
- image and build endpoints list, build, prune cache, pull/import, inspect, show history, push, tag, delete, search, prune, commit, save, and load images;
- system endpoints authenticate registry credentials, report daemon info/version/ping/data usage, and stream daemon events;
- exec endpoints create, start, resize, and inspect commands running inside containers;
- volume, network, and plugin endpoints manage host/driver resources and their prune/install/configuration flows;
- node, swarm, service, task, secret, and config endpoints manage swarm-mode cluster state and workload objects;
- distribution inspection queries remote registry metadata, while `/session` upgrades a connection for advanced client/server interaction.

The chunk is especially important for generated clients because it mixes ordinary JSON responses with tar streams, raw Docker multiplexed streams, websocket-like attach, HTTP connection hijacking, h2c upgrade, optimistic-concurrency `version` parameters, base64 registry authentication headers, and destructive prune/delete operations.

## Important APIs And Types

- `POST /containers/{id}/restart` (`ContainerRestart`) is partially visible at the start of the chunk. The visible parameters are container `id`, optional POSIX `signal`, and optional timeout `t`.
- `POST /containers/{id}/kill` (`ContainerKill`) sends a POSIX signal, defaulting to `SIGKILL`, and reports `409` if the container is not running.
- `POST /containers/{id}/update` (`ContainerUpdate`) consumes `Resources` plus `RestartPolicy` and returns `ContainerUpdateResponse` with `Warnings`.
- `POST /containers/{id}/rename`, `/pause`, and `/unpause` (`ContainerRename`, `ContainerPause`, `ContainerUnpause`) mutate container metadata or freezer-cgroup state.
- `POST /containers/{id}/attach` (`ContainerAttach`) and `GET /containers/{id}/attach/ws` (`ContainerAttachWebsocket`) attach stdin/stdout/stderr with query flags for `logs`, `stream`, `stdin`, `stdout`, `stderr`, and `detachKeys`.
- `POST /containers/{id}/wait` (`ContainerWait`) returns `ContainerWaitResponse` after `not-running`, `next-exit`, or `removed`.
- `DELETE /containers/{id}` (`ContainerDelete`) removes a container with `v`, `force`, and `link` query controls.
- `HEAD/GET/PUT /containers/{id}/archive` (`ContainerArchiveInfo`, `ContainerArchive`, `PutContainerArchive`) inspect, export, or extract tar archives against a path in the container filesystem. `HEAD` returns `X-Docker-Container-Path-Stat`.
- `POST /containers/prune` (`ContainerPrune`) deletes stopped containers and returns deleted IDs plus `SpaceReclaimed`.
- `GET /images/json` (`ImageList`) returns `ImageSummary` arrays with filters for ancestry/reference/dangling/labels/until and options for `all`, `shared-size`, and `digests`.
- `POST /build` (`ImageBuild`) consumes a compressed tar build context and accepts Dockerfile path, tags, remote context, cache controls, resource limits, build args, labels, network mode, registry config, platform, target, BuildKit `outputs`, and builder backend `version` (`1` classic, `2` BuildKit).
- `POST /build/prune` (`BuildPrune`) deletes builder cache with `keep-storage`, `all`, and filters for age, id, parent, type, description, and sharing/in-use state.
- `POST /images/create` (`ImageCreate`) pulls or imports images using `fromImage` or `fromSrc`, optional import `repo`, `tag`, `message`, `changes`, `platform`, body content, and `X-Registry-Auth`.
- `ImageInspect`, `ImageHistory`, `ImagePush`, `ImageTag`, `ImageDelete`, `ImageSearch`, and `ImagePrune` cover image read/write, registry push, reference mutation, hub search, and garbage collection.
- `POST /auth` (`SystemAuth`) validates `AuthConfig` and may return `Status` plus `IdentityToken`.
- `GET /info`, `/version`, and `/_ping` (`SystemInfo`, `SystemVersion`, `SystemPing`, `SystemPingHead`) expose daemon metadata, supported API version, builder recommendation, experimental mode, swarm state, and liveness.
- `POST /commit` (`ImageCommit`) snapshots a container into a new image using `ContainerConfig` and query metadata.
- `GET /events` (`SystemEvents`) streams `EventMessage` records with JSON-encoded filters across containers, images, volumes, networks, daemon, plugins, nodes, services, secrets, configs, and builder prune.
- `GET /system/df` (`SystemDataUsage`) returns layer size, `ImageSummary`, `ContainerSummary`, `Volume`, and `BuildCache` usage, optionally filtered by object `type`.
- `GET /images/{name}/get`, `GET /images/get`, and `POST /images/load` (`ImageGet`, `ImageGetAll`, `ImageLoad`) implement Docker save/load tarball flows.
- `POST /containers/{id}/exec`, `POST /exec/{id}/start`, `POST /exec/{id}/resize`, and `GET /exec/{id}/json` (`ContainerExec`, `ExecStart`, `ExecResize`, `ExecInspect`) model the two-step exec lifecycle plus TTY resize and inspection.
- `VolumeList`, `VolumeCreate`, `VolumeInspect`, `VolumeUpdate`, `VolumeDelete`, and `VolumePrune` use `VolumeListResponse`, `VolumeCreateOptions`, `Volume`, and `ClusterVolumeSpec`.
- `NetworkList`, `NetworkInspect`, `NetworkDelete`, `NetworkCreate`, `NetworkConnect`, `NetworkDisconnect`, and `NetworkPrune` use `Network`, `IPAM`, `ConfigReference`, `EndpointSettings`, and inline connect/disconnect request objects.
- Plugin operations (`PluginList`, `GetPluginPrivileges`, `PluginPull`, `PluginInspect`, `PluginDelete`, `PluginEnable`, `PluginDisable`, `PluginUpgrade`, `PluginCreate`, `PluginPush`, `PluginSet`) use `Plugin`, `PluginPrivilege`, tar contexts, privilege approval arrays, registry auth, and key/value configuration strings.
- Node operations (`NodeList`, `NodeInspect`, `NodeDelete`, `NodeUpdate`) use `Node`, `NodeSpec`, filters, `force`, and required update `version`.
- Swarm operations (`SwarmInspect`, `SwarmInit`, `SwarmJoin`, `SwarmLeave`, `SwarmUpdate`, `SwarmUnlockkey`, `SwarmUnlock`) use `Swarm`, `SwarmSpec`, join tokens, advertised/listen/data-path addresses, token rotation, manager unlock keys, and required update `version`.
- Service operations (`ServiceList`, `ServiceCreate`, `ServiceInspect`, `ServiceDelete`, `ServiceUpdate`, `ServiceLogs`) use `Service`, `ServiceSpec`, `ServiceCreateResponse`, `ServiceUpdateResponse`, `X-Registry-Auth`, `registryAuthFrom`, `rollback`, `insertDefaults`, and log query controls.
- Task operations (`TaskList`, `TaskInspect`, `TaskLogs`) return `Task` records and Docker raw/multiplexed logs.
- Secret and config operations (`SecretList/Create/Inspect/Delete/Update`, `ConfigList/Create/Inspect/Delete/Update`) use `Secret`, `SecretSpec`, `Config`, `ConfigSpec`, `IdResponse`, label-only versioned updates, and duplicate-name errors.
- `GET /distribution/{name}/json` (`DistributionInspect`) returns `DistributionInspect` metadata from a registry.
- `POST /session` (`Session`) upgrades to h2c and produces `application/vnd.docker.raw-stream`.

## Control Flow

Container mutation endpoints are direct daemon state transitions keyed by container ID or name. Kill and restart send signals; update applies resource and restart-policy changes; rename changes the object name; pause/unpause toggles freezer-cgroup state; delete removes containers and can first kill running containers when `force=true`. Archive endpoints route through the container filesystem: `HEAD` reads path metadata into a base64-encoded header, `GET` streams a tar archive, and `PUT` uploads a tar archive to extract into an existing directory with overwrite and UID/GID mapping flags.

Attach and exec flows are transport-sensitive. Container attach can return `200` and hijack the existing socket, or `101 UPGRADED` when the client sends upgrade headers. Non-TTY streams are multiplexed with 8-byte headers whose first byte identifies stdin/stdout/stderr and whose final four bytes encode big-endian frame size; TTY streams are raw PTY bytes. Exec first creates an exec instance on a running, unpaused container, then starts it either detached or attached. Exec resize is only valid for TTY exec sessions, and exec inspect reports process config, running state, exit code, open stream flags, container ID, and host PID.

Image/build control flow spans local image store, build context upload, and registry operations. `ImageBuild` streams a build context to the daemon; daemon-side validation happens before step execution; build cancellation is tied to client connection closure. `ImageCreate` either pulls an image by reference or imports from a URL/body stream. `ImagePush` requires local tagging and registry auth, and push/pull/build progress is modeled as streaming JSON. Save/load endpoints move OCI-compatible Docker image tarballs, with repository metadata described through `manifest.json` and `repositories`.

System endpoints are mixed read and stream flows. `/auth` validates credentials and may issue an identity token. `/events` begins with historical events from `since`, streams live events until `until` or disconnect, and filters by object type and selectors. `/system/df` computes storage usage across selected object classes.

Volume and network flows manage driver-backed state. Volume update is restricted to swarm cluster volumes and currently only changes availability through `ClusterVolumeSpec`, guarded by a version from the volume's `ClusterVolume` field. Network create takes driver/IPAM/options/labels, connect attaches an endpoint configuration to a container, disconnect detaches it, and prune deletes unused networks according to filters.

Plugin flows require privilege negotiation. Clients can query requested privileges for a remote plugin, pull/install with an approved privilege array, enable/disable with timeout or force, upgrade with a new remote reference and privileges, create from a plugin tar rootfs/manifest, push to a registry, and set configuration variables.

Swarm and orchestrator flows are versioned desired-state updates. Nodes, swarm objects, services, secrets, configs, and cluster volumes require a current version on update to avoid conflicting writes. Swarm init creates a new cluster and returns the node ID; join requires `ListenAddr`, `RemoteAddrs`, and `JoinToken`; leave can be forced even when it breaks the cluster; update can rotate worker/manager tokens or manager unlock key. Services create/update full specs and drive task reconciliation. `rollback=previous` tells the daemon to ignore the supplied service spec and roll back server-side.

Service and task logs follow the same log-stream model as container logs. Query flags select details, follow, stdout, stderr, timestamps, `since`, and string-typed `tail` (`all` or an integer). The contract notes these endpoints work only with the `local`, `json-file`, or `journald` logging drivers.

Secrets and configs follow parallel CRUD flows: list with JSON filters, create with a spec and return an ID, inspect by ID/name, delete, and update labels through a full spec plus required version. Distribution inspection is a registry-backed metadata read, not a local image inspect. Session setup is a connection-upgrade flow where HTTP/1.1 is upgraded to h2c so the daemon can call client-exposed gRPC services over the connection.

## State And Persistence Behavior

The YAML file itself is static contract data, but it documents many persistent or live daemon states:

- container runtime state changes through kill, restart, pause, unpause, wait, exec, delete, archive extraction, and prune;
- container filesystem state changes through archive `PUT`, and image state changes through build, import, pull, tag, delete, prune, commit, save, and load;
- build cache state changes through `BuildPrune`, with reclaimed space accounting;
- registry credential validation, identity tokens, pull/push auth, and registry distribution metadata lookups;
- event streams observe object changes but do not persist new objects;
- volumes persist host or driver-managed data and can be listed, created, updated for cluster availability, deleted, and pruned;
- networks persist driver/IPAM/options/labels and endpoint attachments to containers; builtin networks are protected from unsupported deletion;
- plugins persist installed rootfs/manifest/configuration and can be enabled, disabled, upgraded, pushed, or removed;
- swarm state persists manager membership, Raft-backed swarm spec, join tokens, unlock key, nodes, services, tasks, secrets, configs, and cluster volumes;
- services persist desired state and trigger orchestrator reconciliation into tasks; tasks expose scheduler/runtime state and logs;
- secrets/configs persist metadata and base64 data or external-driver references, but update operations only permit label changes in this API version;
- `/session` creates a live upgraded transport channel, not a persisted resource.

Status codes encode important state boundaries: `304` for already-stopped containers in the preceding stop/restart area, `403` for forbidden network/plugin/read-only archive operations, `404` for missing objects, `409` for conflicts such as running containers, paused containers, name conflicts, in-use volumes/images, or stopped/paused exec containers, and `503` for swarm-incompatible daemon state.

## Dependencies

This chunk depends on the surrounding Docker Engine Swagger conventions: versioned base path, `operationId` naming, shared `ErrorResponse`, `$ref` links into `definitions`, inline schemas, `allOf` composition, JSON-string filter encoding, binary body schemas, ReDoc markdown descriptions, and vendor extensions such as `x-nullable`.

Runtime dependencies implied by the contract include:

- Linux/Windows container runtime behavior, POSIX signals, freezer cgroups, TTY/PTTY handling, exec process lifecycle, and container filesystem archive helpers;
- HTTP connection hijacking, websocket attach, raw Docker stream framing, h2c upgrade, and long-lived streaming response support;
- image store, content/layer store, graph drivers, build backends, BuildKit/classic builder selection, build cache, Dockerfile parsing, and OCI/Docker save tarball formats;
- registry clients and authentication for image pull/push, build registry config, plugin pull/upgrade/push, service image credentials, and distribution inspection;
- logging drivers (`local`, `json-file`, `journald`) for service/task logs and log stream multiplexing;
- volume drivers, cluster volume metadata, network drivers, IPAM, overlay ingress/routing mesh, attachable swarm networks, and endpoint settings;
- plugin manager, plugin privilege model, plugin tar manifests, and host-integrated plugin capabilities such as network, mount, and device access;
- swarmkit/Raft state, node membership, join tokens, unlock keys, CA/encryption settings, scheduler tasks, service rollout/rollback machinery, secrets, configs, and object-version concurrency checks.

## Integration Points

Operation IDs are the stable integration names used by generated clients and documentation. This chunk includes `ContainerRestart`, `ContainerKill`, `ContainerUpdate`, `ContainerRename`, `ContainerPause`, `ContainerUnpause`, `ContainerAttach`, `ContainerAttachWebsocket`, `ContainerWait`, `ContainerDelete`, `ContainerArchiveInfo`, `ContainerArchive`, `PutContainerArchive`, `ContainerPrune`, all image/build operations from `ImageList` through `ImageLoad`, system operations from `SystemAuth` through `SystemDataUsage`, exec operations, volume/network/plugin operations, node/swarm/service/task operations, secret/config operations, `DistributionInspect`, and `Session`.

CLI and SDK integration is direct: Docker CLI commands such as `docker kill`, `docker update`, `docker attach`, `docker cp`, `docker image build/pull/push/tag/rm/save/load/prune`, `docker system df/events/info/version`, `docker exec`, `docker volume`, `docker network`, `docker plugin`, and swarm/service/secret/config commands map to these routes.

The chunk also integrates with documentation generation and test fixtures through examples. The examples cover response objects, archive stat headers, image history and deletion items, system data-usage payloads, network create/connect payloads, plugin privileges, swarm init/join/unlock, service specs, task records, and secret/config specs.

Generated clients need custom transport integration for binary and streaming routes. JSON-only code generation is insufficient for attach, exec start, image/build push/pull progress, events, save/load tarballs, service/task logs, and session upgrade.

## Risks And Edge Cases

- The chunk starts mid-operation: the first visible lines are the tail of `ContainerRestart` parameters, so full operation summary/status context begins just before line 7752.
- `ContainerKill` defaults to `SIGKILL`; clients that omit `signal` may terminate workloads abruptly.
- `ContainerUpdate` composes resource fields and restart policy. Platform-specific resource fields may be accepted, ignored, or rejected depending on daemon OS and cgroup support.
- `ContainerPause` uses freezer cgroups rather than `SIGSTOP`; process-observable behavior differs from ordinary signal suspension.
- Attach and exec-start responses are not ordinary JSON. Clients must handle `101` upgrade, `200` hijack, raw PTY streams, and Docker multiplexed stream framing.
- Attach does nothing unless either `stream` or `logs` is true. `stdout` and `stderr` selectors default false on many log-like endpoints.
- `detachKeys` has a narrow syntax; invalid values should be treated as bad parameters.
- Archive extraction can fail when the target path is a file, missing, read-only, or would overwrite directory/non-directory types when `noOverwriteDirNonDir` is set.
- Prune endpoints are destructive and filter syntax is JSON encoded in a query string. Bad escaping can cause broad deletion or no deletion.
- Build args are documented as not intended for secrets, but the API cannot prevent secret values from entering image history or build cache.
- Build is canceled when the client disconnects; proxies or client timeouts can abort long builds.
- `ImageCreate` overloads pull and import behavior through mutually contextual query parameters (`fromImage` versus `fromSrc`).
- `ImagePush` requires `X-Registry-Auth` and ignores tags embedded in the path `name`; callers must use the `tag` query parameter.
- Image delete is blocked by descendants, running containers, and builds unless force semantics permit it.
- `/auth`, image registry headers, plugin registry headers, and service `X-Registry-Auth` carry credentials and should not be logged.
- `/_ping` exposes capability headers whose values are advisory; clients still choose builder backend.
- `/events` is a long-lived stream and filter keys span many object types; clients need reconnect and backfill behavior around `since`.
- `VolumeUpdate` is valid only for swarm cluster volumes and only mutates availability. The body wrapper around `ClusterVolumeSpec` is intentional for future extensibility.
- Network connect is forbidden for non-attachable swarm networks and cannot reattach a running container to the same network.
- Plugin delete/disable `force=true` can disrupt containers or daemon capabilities that rely on the plugin.
- Node/swarm/service/secret/config/cluster-volume updates require current version parameters; stale reads must be handled explicitly.
- `SwarmLeave force=true` can break a cluster or remove the last manager.
- Swarm unlock keys and join tokens are sensitive operational secrets; responses and query flags around rotation need careful audit logging.
- Service update `rollback=previous` ignores the supplied spec, so clients must not assume request-body fields were applied.
- Service and task logs only work with supported logging drivers (`local`, `json-file`, `journald`).
- Secret/config update bodies are full specs even though only labels are mutable; changed immutable fields can be rejected.
- `SecretSpec.Data` and `ConfigSpec.Data` are base64 payloads. Secret data should not be returned by inspect/list, and clients should not rely on inspect for secret recovery.
- `DistributionInspect` returns `401` both for authentication failure and no image found, so error interpretation needs context.
- `/session` relies on h2c upgrade and gRPC-over-connection behavior, which generic HTTP clients and proxies may not support.

## Test Signals

Useful validation for this API contract includes:

- Swagger/OpenAPI linting over `api/docs/v1.45.yaml` for `$ref` resolution, valid path parameters, unique `operationId` values, response schemas, binary body declarations, and `allOf` composition.
- Generated client/server compilation tests focused on mixed response types, inline request/response schemas, `x-nullable`, array query parameters, JSON-string filters, string-or-enum fields, and binary streams.
- Container lifecycle tests for kill signal defaults, not-running `409`, update warnings, rename name-conflict `409`, pause/unpause state, wait conditions, delete `force/v/link`, and archive `HEAD/GET/PUT` behavior.
- Attach and exec transport tests for TTY versus non-TTY framing, upgrade versus non-upgrade responses, detach keys, logs-to-stream transition, stdin/stdout/stderr selectors, exec create/start/resize/inspect, paused/stopped container errors, and exit-code reporting.
- Image/build tests for build context compression, remote context, Dockerfile selection, BuildKit/classic `version`, build cache pruning, platform selection, registry auth, import versus pull, history shape, tag overwrite, push tag query behavior, image delete conflicts, search filters, image prune filters, commit pause behavior, save/load tar compatibility, and OCI layout metadata.
- System tests for `/auth` success/token and failure, `/info`, `/version`, `/_ping` headers, `/events` filters and streaming boundaries, and `/system/df` type filtering and reclaimed/storage accounting.
- Volume tests for list filters, create/inspect/delete in-use conflict, cluster-volume update with current and stale versions, prune `all` and label filters, and driver error mapping.
- Network tests for list/inspect filters, create duplicate/builtin/overlay-not-in-swarm errors, IPAM/options/labels, connect endpoint config, forbidden swarm-scoped operations, disconnect force, builtin delete `403`, and prune filters.
- Plugin tests for privilege discovery, pull with approved privileges and registry auth, inspect missing plugin, enable timeout, force disable/delete while in use, upgrade remote/auth/privileges, create from tar, push, and set config strings.
- Swarm/node tests for not-in-swarm `503`, already-in-swarm `503`, init/join required fields, advertise/data-path address handling, forced leave risk, versioned swarm/node update, token rotation, unlock-key retrieval, and unlock success/failure.
- Service/task tests for service list filters/status, create with private registry auth and ineligible network `403`, duplicate service `409`, inspect `insertDefaults`, versioned update, registry auth source selection, rollback, delete, task list filters, task inspect, and service/task log stream options.
- Secret/config tests for duplicate-name `409`, list filters, inspect omission of secret payload, create with base64 data and optional external driver, label-only versioned update, immutable-field rejection, stale-version rejection, delete, and documented size limits.
- Distribution/session tests for registry descriptor/platform response, auth/missing-image `401`, server error mapping, h2c upgrade response, bad session parameters, proxy compatibility, and client-side gRPC service exposure over the upgraded connection.
