# sources/cloud-native/moby/api/docs/v1.41.yaml lines 7813-12168

## Scope

This chunk covers the Docker Engine API v1.41 Swagger path definitions from `POST /containers/{id}/wait` through `POST /session`. It starts near the end of the container API, then defines the image/build, auth/system, exec, volume, network, plugin, swarm, node, service, task, secret, config, distribution, and BuildKit session endpoints.

The source is an OpenAPI/Swagger YAML contract, not executable daemon code. The behavior researched here is the public HTTP API surface consumed by Docker CLI code, SDKs, generated clients, API documentation, and daemon compatibility/conformance tests.

## Purpose

The chunk defines the stateful control plane for most Docker Engine resources after the early container endpoints. It lets clients wait for and remove containers, transfer archive data into and out of container filesystems, prune stopped containers, manage images and build cache, authenticate to registries, inspect daemon state, monitor events, run exec sessions, manage persistent volumes and networks, administer plugins, control swarm membership and Raft-backed swarm resources, read service/task logs, manage secrets/configs, query registry distribution metadata, and initialize an interactive BuildKit session.

The YAML models a mix of ordinary JSON APIs, destructive mutation endpoints, binary tar streams, raw Docker stream endpoints, connection-upgrade endpoints, and optimistic-concurrency updates. That mixture is the main implementation burden for generated clients and compatibility tests: many paths share the same `ErrorResponse` shape, but request/response media types and success status codes differ significantly across resource families.

## Important APIs And Types

Container endpoints in this chunk:

- `POST /containers/{id}/wait` (`ContainerWait`) blocks until a container reaches `condition=not-running|next-exit|removed` and returns `ContainerWaitResponse`.
- `DELETE /containers/{id}` (`ContainerDelete`) removes a container by ID/name, with `v`, `force`, and `link` query booleans for anonymous volume removal, killing a running container first, and removing a link.
- `HEAD /containers/{id}/archive` (`ContainerArchiveInfo`) returns `X-Docker-Container-Path-Stat`, a base64-encoded JSON path stat header.
- `GET /containers/{id}/archive` (`ContainerArchive`) returns a tar archive for a container filesystem path as `application/x-tar`.
- `PUT /containers/{id}/archive` (`PutContainerArchive`) uploads a tar stream, extracts it into a directory path, and supports `noOverwriteDirNonDir` plus `copyUIDGID`.
- `POST /containers/prune` (`ContainerPrune`) deletes stopped containers with `until` and `label` filters and returns deleted container IDs plus reclaimed bytes.

Image, build, and registry-related endpoints:

- `GET /images/json` (`ImageList`) returns `ImageSummary` arrays and supports `all`, JSON `filters`, and `digests`.
- `POST /build` (`ImageBuild`) consumes a tar build context or remote context, produces JSON progress, and accepts Dockerfile path, tags, remote context, cache controls, resource limits, build args, labels, build network mode, registry config, platform, target, BuildKit `outputs`, and builder `version=1|2`.
- `POST /build/prune` (`BuildPrune`) removes build cache with `keep-storage`, `all`, and cache filters such as `until`, `id`, `parent`, `type`, `description`, `inuse`, `shared`, and `private`.
- `POST /images/create` (`ImageCreate`) pulls or imports images, with `fromImage` for pull, `fromSrc` and body content for import, `repo`, `tag`, `message`, `changes`, `platform`, and `X-Registry-Auth`.
- `GET /images/{name}/json`, `GET /images/{name}/history`, `POST /images/{name}/push`, `POST /images/{name}/tag`, `DELETE /images/{name}`, `GET /images/search`, and `POST /images/prune` cover image inspect, history, push, tag, delete, Docker Hub search, and prune.
- `POST /commit` (`ImageCommit`) snapshots a container into a new image using optional `ContainerConfig`, repo/tag/comment/author metadata, `pause`, and Dockerfile-style `changes`.
- `GET /images/{name}/get`, `GET /images/get`, and `POST /images/load` implement image save/load tarball flows.
- `GET /distribution/{name}/json` (`DistributionInspect`) contacts a registry and returns `DistributionInspect` descriptor/platform metadata.

System endpoints:

- `POST /auth` (`SystemAuth`) validates `AuthConfig` and may return `SystemAuthResponse` with `Status` and `IdentityToken`.
- `GET /info` (`SystemInfo`) returns daemon system information.
- `GET /version` (`SystemVersion`) returns Engine version and host/runtime information.
- `GET /_ping` (`SystemPing`) and `HEAD /_ping` (`SystemPingHead`) provide liveness plus headers such as `Api-Version`, `Builder-Version`, and `Docker-Experimental`.
- `GET /events` (`SystemEvents`) streams `EventMessage` objects with `since`, `until`, and JSON filters across containers, images, volumes, networks, daemon, plugins, nodes, services, secrets, configs, and builder events.
- `GET /system/df` (`SystemDataUsage`) returns layer size, images, containers, volumes, and build cache usage.

Exec endpoints:

- `POST /containers/{id}/exec` (`ContainerExec`) creates an exec instance in a running container using an inline `ExecConfig` object with attach flags, detach keys, TTY, environment, command, privileged flag, user, and working directory.
- `POST /exec/{id}/start` (`ExecStart`) starts the exec instance and returns Docker raw-stream data unless detached.
- `POST /exec/{id}/resize` (`ExecResize`) changes TTY height/width.
- `GET /exec/{id}/json` (`ExecInspect`) returns inline `ExecInspectResponse` data including running state, exit code, `ProcessConfig`, open streams, container ID, and process PID.

Volume, network, and plugin endpoints:

- `GET /volumes`, `POST /volumes/create`, `GET /volumes/{name}`, `DELETE /volumes/{name}`, and `POST /volumes/prune` use `VolumeListResponse`, `Volume`, `VolumeCreateOptions`, and prune responses. Filters include dangling, driver, label, and name.
- `GET /networks`, `GET/DELETE /networks/{id}`, `POST /networks/create`, `POST /networks/{id}/connect`, `POST /networks/{id}/disconnect`, and `POST /networks/prune` use `Network`, `EndpointSettings`, `ConfigReference`, and `IPAM`. Network create supports duplicate checking, driver/scope, internal/attachable/ingress/config-only flags, config source, IPv6, options, and labels.
- `GET /plugins`, `GET /plugins/privileges`, `POST /plugins/pull`, `GET /plugins/{name}/json`, `DELETE /plugins/{name}`, enable/disable/upgrade/create/push/set endpoints, `Plugin`, and `PluginPrivilege` cover the plugin lifecycle. Pull and upgrade carry privilege grants and optional registry auth.

Swarm and orchestration endpoints:

- `GET /nodes`, `GET/DELETE /nodes/{id}`, and `POST /nodes/{id}/update` expose `Node` and `NodeSpec`. Node update requires a `version` query parameter.
- `GET /swarm`, `POST /swarm/init`, `POST /swarm/join`, `POST /swarm/leave`, `POST /swarm/update`, `GET /swarm/unlockkey`, and `POST /swarm/unlock` expose `Swarm`, `SwarmSpec`, inline init/join/unlock request shapes, join tokens, manager unlock keys, data-path addresses/ports, default address pools, and token/key rotation flags.
- `GET /services`, `POST /services/create`, `GET/DELETE /services/{id}`, `POST /services/{id}/update`, and `GET /services/{id}/logs` use `Service`, `ServiceSpec`, `ServiceCreateResponse`, and `ServiceUpdateResponse`. Create/update support private registry auth through `X-Registry-Auth`; update additionally supports required object `version`, `registryAuthFrom=spec|previous-spec`, and `rollback=previous`.
- `GET /tasks`, `GET /tasks/{id}`, and `GET /tasks/{id}/logs` expose read-only `Task` state and log streams.
- `GET/POST/DELETE/UPDATE` groups for `/secrets` and `/configs` use `Secret`, `SecretSpec`, `Config`, and `ConfigSpec`. Updates require object versions and are documented as label-only.
- `POST /session` (`Session`) initializes an interactive session by hijacking/upgrading the HTTP connection to h2c so the daemon can call back to client-exposed gRPC services.

Shared schema dependencies in this chunk include `ErrorResponse`, `IdResponse`, `ContainerWaitResponse`, `ImageSummary`, `ImageInspect`, `ImageHistoryResponseItem`, `ImageDeleteResponseItem`, `AuthConfig`, `SystemInfo`, `SystemVersion`, `EventMessage`, `ContainerSummary`, `BuildCache`, `ProcessConfig`, `Volume`, `VolumeListResponse`, `VolumeCreateOptions`, `Network`, `EndpointSettings`, `Plugin`, `PluginPrivilege`, `Node`, `NodeSpec`, `Swarm`, `SwarmSpec`, `Service`, `ServiceSpec`, `ServiceUpdateResponse`, `Task`, `Secret`, `SecretSpec`, `Config`, `ConfigSpec`, and `DistributionInspect`.

## Control Flow

Container flow in this range is mostly terminal lifecycle and filesystem transfer. A client can wait on an existing container state transition, then remove it, optionally killing a running container or deleting anonymous volumes. Archive flow is three separate contracts on the same path: `HEAD` probes metadata through a response header, `GET` streams a tar archive out, and `PUT` streams a tar archive in and performs server-side extraction. The archive `PUT` flow has validation branches for missing containers/paths, non-directory destinations, read-only filesystems, and overwrite policy.

Image/build flow combines long-running streaming operations with local image-store mutations. Builds accept an uploaded context or a daemon-fetched remote context, validate the Dockerfile before executing instructions, and are canceled when the client connection closes. Pull/import (`ImageCreate`) and push are also cancellation-sensitive. Tag/delete/prune mutate local image references and layers. Export/load endpoints use tar streams rather than JSON object bodies.

System flow is observational except for registry auth validation. `/_ping`, `/info`, `/version`, and `/system/df` are point-in-time daemon reads. `/events` is a streaming watch: it can replay from `since`, stop at `until`, then stream new events if no stopping bound is reached. The event filter vocabulary links this endpoint to every resource family in the chunk.

Exec flow is explicitly two-phase. `ContainerExec` creates an exec object inside a running, non-paused container; `ExecStart` starts it and either detaches immediately or returns an interactive raw stream. `ExecResize` is valid only when the exec was created/started with a TTY. `ExecInspect` then exposes process state and exit status.

Volume and network flows are standard CRUD plus prune, but network connect/disconnect introduces cross-resource control flow between networks and containers. Network creation can also reference config-only networks through `ConfigFrom`; direct connect/disconnect is blocked for swarm-scoped networks.

Plugin flow includes privilege discovery, user-approved installation, runtime enable/disable, upgrade with a new remote reference, creation from a tar rootfs/manifest, push, deletion, and setting environment/config values. Pull and upgrade require the client to handle a privilege array body and optional registry credentials.

Swarm flow is versioned and membership-aware. Init creates a new swarm and returns the node ID; join requires listen address, manager addresses, and join token; leave can be forced; update requires the current swarm object version and can rotate credentials. Unlock-key retrieval and unlock submission only apply when manager autolock is relevant. Most swarm, node, service, task, secret, and config endpoints document `503` when the node is not part of a swarm.

Service flow follows the Docker inspect-modify-update pattern. Create persists a `ServiceSpec`, may resolve/pin images with registry credentials, and can return warnings. Inspect can optionally fill default fields. Update requires the current service version and accepts a full `ServiceSpec`; the special `rollback=previous` mode makes the submitted spec ignored. Logs are raw stream/binary responses constrained by logging driver support.

Secret and config flows are parallel. List uses JSON filters, create persists named data with labels, inspect returns metadata/spec, delete removes the object, and update is optimistic-concurrency controlled. Although update bodies are full spec schemas, the descriptions restrict mutation to labels and require all other fields to remain unchanged from inspect output.

Distribution inspection and session are integration flows rather than local resource CRUD. Distribution inspection resolves image metadata by contacting a registry. Session upgrades the HTTP connection and then uses it as a bidirectional transport for advanced BuildKit/client capabilities.

## State And Persistence Behavior

The YAML itself persists no state, but it documents persistent Docker daemon and swarm state.

Container remove and prune delete container metadata and writable layer state, with optional anonymous volume deletion. Archive `PUT` mutates the container filesystem or mounted volumes and can be rejected when the destination is read-only. Container wait observes lifecycle state and returns exit information without mutating state.

Image and build endpoints mutate the local image store, content/layer store, build cache, and image reference graph. Build cache prune and image prune report `SpaceReclaimed` as `int64`, which makes reclaimed-byte accounting a visible contract. Image delete may untag references, delete image records, and optionally avoid pruning parents. Save/load endpoints serialize and restore image layers and repository metadata.

Registry-related operations depend on external mutable state as well as local state. Pull, push, build registry config, plugin pull/upgrade, service image resolution, auth validation, and distribution inspection all depend on registry availability and credentials. Auth headers and identity tokens are transient API inputs/outputs but are security-sensitive.

Exec objects are daemon-managed runtime state associated with a container. They expose running/completed status, exit code, open stream state, and PID. The exec process itself is not durable beyond container/runtime lifetime, but its inspectable object state is part of the daemon API.

Volumes are persistent host or driver-backed resources. Delete/prune can permanently remove data if no container references prevent it. Network objects persist driver/IPAM configuration and endpoint attachments; connect/disconnect mutate container network state and may affect service reachability.

Plugins are installed host extensions with privileges over networking, storage, devices, mounts, and environment/config values. Enabling, disabling, upgrading, deleting, or configuring them mutates daemon capabilities and can affect containers using those plugin-provided resources.

Swarm resources are versioned state, typically Raft-backed for managers. `version` query parameters on node, swarm, service, secret, and config updates are optimistic concurrency controls. Service state drives task reconciliation; tasks are scheduler-produced records showing desired state, execution state, container status, node placement, and network attachments. Secrets and configs persist metadata and creation data, with label-only updates preserving immutable payload/name semantics.

The session endpoint creates a live transport state rather than a named persistent object. Its success status is `101`, and after upgrade the HTTP connection is no longer a normal request/response channel.

## Dependencies

The document depends on Swagger/OpenAPI 2.0 constructs: path/method objects, `operationId`, `$ref`, `allOf`, inline object schemas, response headers, binary string formats, examples, enums, and vendor extensions elsewhere in the file. It also depends on ReDoc/SDK generation conventions around operation IDs and tag grouping.

Runtime dependencies implied by the contract include:

- Docker daemon routing, error handling, and versioned API dispatch for v1.41.
- Container runtime state, filesystem/archive handling, user/group ID mapping, mounted volumes, read-only rootfs/volume enforcement, and process lifecycle events.
- Image store, layer/content store, build backends, BuildKit, classic builder compatibility, build cache accounting, image tarball save/load format, and Dockerfile instruction parsing.
- Registry clients and credential handling for image pull/push, build registry config, plugin pull/upgrade, service image resolution, auth validation, and distribution inspect.
- Logging drivers and Docker raw-stream framing for exec, service logs, task logs, build/push/pull progress, and event streaming.
- Volume drivers, network drivers, IPAM, overlay/swarm networking, and plugin driver capabilities.
- SwarmKit/Raft state for swarm, node, service, task, secret, and config endpoints.
- HTTP connection hijack/upgrade support for raw streams and `/session` h2c transport.

Generated clients depend on correct handling of JSON-encoded filter query strings, repeated query parameters (`t`, `names`, `changes`), boolean and integer query parsing, base64url auth headers, required body fields, required version parameters, tar/binary request bodies, response headers, status-only success responses, and `101` upgraded streams.

## Integration Points

Operation IDs are the primary SDK/documentation integration points: `ContainerWait`, `ContainerDelete`, `ContainerArchiveInfo`, `ContainerArchive`, `PutContainerArchive`, `ContainerPrune`, `ImageList`, `ImageBuild`, `BuildPrune`, `ImageCreate`, `ImageInspect`, `ImageHistory`, `ImagePush`, `ImageTag`, `ImageDelete`, `ImageSearch`, `ImagePrune`, `SystemAuth`, `SystemInfo`, `SystemVersion`, `SystemPing`, `SystemPingHead`, `ImageCommit`, `SystemEvents`, `SystemDataUsage`, `ImageGet`, `ImageGetAll`, `ImageLoad`, `ContainerExec`, `ExecStart`, `ExecResize`, `ExecInspect`, `VolumeList`, `VolumeCreate`, `VolumeInspect`, `VolumeDelete`, `VolumePrune`, `NetworkList`, `NetworkInspect`, `NetworkDelete`, `NetworkCreate`, `NetworkConnect`, `NetworkDisconnect`, `NetworkPrune`, all plugin lifecycle operations, node/swarm/service/task operations, secret/config operations, `DistributionInspect`, and `Session`.

The CLI maps directly to many of these contracts: `docker wait`, `rm`, `cp`, `container prune`, `image ls/build/pull/import/inspect/history/push/tag/rm/search/prune/save/load`, `login`, `info`, `version`, `events`, `system df`, `commit`, `exec`, `volume`, `network`, `plugin`, `swarm`, `node`, `service`, `task`, `secret`, and `config`.

Registry integration appears through `X-Registry-Auth`, `X-Registry-Config`, image pull/push, plugin pull/upgrade, service create/update credentials, and distribution inspect. These endpoints must coordinate with credential stores and avoid leaking auth material in logs or generated debug output.

Swarm integration ties together services, tasks, networks, secrets, configs, nodes, and logs. Service specs can mount volumes, secrets, and configs; attach networks; publish ports; define update/rollback behavior; and trigger task creation. Task list/inspect/log APIs are the read side of the service scheduler.

BuildKit integration appears in `ImageBuild` through `version=2`, `outputs`, builder-version ping headers, `/build/prune`, `/system/df` build-cache reporting, and `/session` for callback-capable client sessions.

## Risks And Edge Cases

- This chunk mixes normal JSON APIs, tar upload/download, raw Docker streams, long-running JSON progress streams, status-only responses, response-header metadata, and `101` upgraded connections. JSON-only generated clients will be incomplete.
- Build, pull, and push are canceled when clients close the connection. Tests and clients need to handle partial work and cleanup semantics.
- `ImageBuild` exposes both classic builder and BuildKit through `version=1|2`; client tooling must not assume BuildKit-only options are valid for every backend.
- Build args are explicitly not meant for secrets, but the schema cannot enforce that. Build history/cache can leak values supplied through `buildargs`.
- Auth headers (`X-Registry-Auth`, `X-Registry-Config`) and swarm unlock/join tokens are sensitive. Logging/tracing around these endpoints is high risk.
- Many filters are JSON-encoded `map[string][]string` query parameters, not structured JSON bodies. Encoding errors can surface as `400` or silently alter selection semantics.
- Delete/prune endpoints are destructive and have different success status codes across resources: containers/images often return bodies or `204`, volumes/networks/plugins/services/secrets/configs vary.
- `ContainerArchiveInfo` relies on a base64-encoded JSON response header. Proxies, SDKs, and tests must preserve and decode that header correctly.
- Archive extraction can overwrite container paths unless `noOverwriteDirNonDir` is set; `copyUIDGID` and read-only mounts/rootfs introduce platform and storage-driver edge cases.
- `ImagePush` path `name` ignores an included tag and requires the `tag` query parameter to select one tag. Clients that put tags only in the path can push the wrong set of tags.
- Image search is Docker Hub-specific while many other image endpoints are registry-generic.
- `/_ping` has both GET and HEAD variants with similar headers but different bodies; clients should not expect a body on HEAD.
- Service and task logs only work with the `local`, `json-file`, or `journald` logging drivers. Follow mode/raw-stream handling must be tested separately from non-follow reads.
- Network create `CheckDuplicate` is best-effort because networks are ID-keyed. Duplicate names can still occur.
- The schema titles for network connect/disconnect request bodies appear swapped: `/connect` uses title `NetworkDisconnectRequest`, while `/disconnect` uses title `NetworkConnectRequest`. Generated model names may be misleading.
- Direct network connect/disconnect is unsupported for swarm-scoped networks and returns `403`; higher-level orchestration should use service specs instead.
- Plugin operations can grant broad host privileges. `force` delete/disable can disrupt containers that depend on the plugin.
- Swarm, node, service, task, secret, and config endpoints consistently need `503` handling when the node is not part of a swarm.
- Versioned update endpoints require current object versions. Stale or missing versions should be treated as concurrency failures even when the documented status set does not always name `409`.
- `ServiceUpdate rollback=previous` ignores the supplied spec. Client validators that insist on a meaningful full spec can block a valid rollback flow.
- Secret/config update bodies are broad specs, but only labels may change. Implementations need validation to reject name/data/driver changes.
- Distribution inspection documents `401` for both auth failure and no image found, which can blur not-found versus unauthorized behavior.
- `/session` says it hijacks to HTTP2 transport for client gRPC callbacks; clients and proxies that cannot do h2c upgrade cannot use the advanced session path.

## Test Signals

Useful validation signals for this chunk include:

- Swagger/OpenAPI validation for path syntax, method uniqueness, operation ID uniqueness, `$ref` resolution, inline schema validity, response header definitions, binary `format` usage, and required parameter placement.
- Generated-client compilation against v1.41, especially for inline schemas such as `ExecConfig`, `ExecStartConfig`, `NetworkCreateRequest`, swarm init/join/unlock requests, prune responses, and system auth/data-usage responses.
- Contract tests for every operation ID verifying documented success status codes, shared `ErrorResponse` bodies, required path/query/body/header parameters, and media types.
- Container tests for wait conditions, forced remove versus running-container conflict, anonymous volume removal, archive `HEAD` header decoding, archive `GET` tar contents, archive `PUT` read-only failures, non-directory failures, overwrite policy, UID/GID copy behavior, and prune filters.
- Image/build tests for build context upload, remote contexts, Dockerfile validation errors, client disconnect cancellation, classic versus BuildKit builder selection, `outputs`, `X-Registry-Config`, `platform`, cache prune filters/accounting, pull/import modes, tag behavior, push tag selection, delete force/noprune behavior, image search filters, image prune filters, image save/load tar compatibility, and commit with pause/changes.
- System tests for auth success with identity token versus `204`, auth failure `401`, ping headers on GET and HEAD, event stream replay/filters/until termination, and `/system/df` accounting for images, containers, volumes, and build cache.
- Exec tests for create/start/inspect lifecycle, paused or stopped container errors, attached stdout/stderr/stdin behavior, detach behavior, TTY resize validation, exit-code reporting, and raw-stream framing.
- Volume/network tests for list filters, create/inspect/delete/prune, in-use volume deletion, network duplicate-name best effort, config-only networks, IPAM/IPv6/options/labels, connect/disconnect endpoint settings, swarm-scoped network `403`, and prune label/until filters.
- Plugin tests for privilege discovery, pull/install with approved privileges and registry auth, inspect missing plugin `404`, enable timeout, force disable/delete, upgrade body privileges, create from tar, push, and set configuration values.
- Swarm/node tests for init/join address and token validation, force leave, inspect outside swarm `503`, update version requirements, token/unlock-key rotation, manager unlock flows, node filters, node force delete, and stale version handling.
- Service/task tests for service filters/status, create warnings and duplicate-name conflict, private registry auth, inspect defaults, update version and `registryAuthFrom`, rollback behavior, service delete status, service/task log parameters and driver restrictions, task filters, task inspect missing/not-in-swarm errors, and task examples with running/shutdown history.
- Secret/config tests for filters, create duplicate-name conflicts, inspect/list data exposure expectations, delete `204`, label-only update validation, required versions, stale versions, and non-swarm `503`.
- Distribution/session tests for successful descriptor/platform decoding, private registry auth/missing-image `401`, registry server errors, h2c upgrade success on `/session`, and failure through clients/proxies that do not support connection hijacking.
