# sources/cloud-native/moby/api/docs/v1.40.yaml lines 7826-11864

## Scope

This chunk covers Docker Engine API v1.40 Swagger path definitions from the tail of `GET /images/json` through `POST /session`. It includes image build/pull/import/inspect/history/push/tag/delete/search/prune/export/load/commit APIs, builder cache pruning, registry auth, system info/version/ping/events/disk-usage APIs, exec APIs, volume and network lifecycle APIs, plugin lifecycle APIs, swarm node and cluster control APIs, service/task log and lifecycle APIs, secret/config lifecycle APIs, registry distribution inspection, and the BuildKit session endpoint.

The source is an OpenAPI/Swagger YAML contract rather than executable daemon code. Its main consumers are Docker API documentation, compatibility tests, generated SDKs, and daemon route/handler conformance checks.

## Purpose

This chunk defines the bulk of the Docker Engine control surface after the container endpoints. It exposes daemon-local object management for images, build cache, exec sessions, volumes, networks, plugins, system data, and registry interactions, plus swarm-mode management for nodes, swarm membership, services, tasks, secrets, and configs.

The API surface is stateful and side-effect-heavy. Many operations mutate local daemon stores, image content stores, driver/plugin state, registry-backed resources, or swarm raft objects. Several endpoints are long-running or streaming, including image build, image create/pull/import, image push, events, logs, image save/load, exec start, and `/session` connection hijacking.

## Important APIs And Types

- `GET /images/json` (`ImageList`) returns `ImageSummary` rows with `all`, JSON `filters`, and optional digest material through `digests`.
- `POST /build` (`ImageBuild`) accepts a compressed tar build context and many query/header controls: `dockerfile`, repeated `t` tags, `remote`, `q`, `nocache`, `cachefrom`, `pull`, intermediate-container cleanup flags, CPU/memory controls, `buildargs`, `shmsize`, experimental `squash`, labels, build network mode, `Content-type`, `X-Registry-Config`, `platform`, target stage, BuildKit `outputs`, and builder `version` enum `1|2`.
- `POST /build/prune` (`BuildPrune`) deletes builder cache with `keep-storage`, `all`, and filters for age, id, parent, type, description, and in-use/shared/private cache state. It returns `CachesDeleted` and `SpaceReclaimed`.
- `POST /images/create` (`ImageCreate`) pulls from `fromImage` or imports from `fromSrc`, supports `repo`, `tag`, `message`, `inputImage`, `X-Registry-Auth`, Dockerfile-style `changes`, and `platform`.
- Image read and mutation endpoints include `GET /images/{name}/json` (`ImageInspect`), `GET /images/{name}/history` (`ImageHistory`), `POST /images/{name}/push` (`ImagePush`), `POST /images/{name}/tag` (`ImageTag`), `DELETE /images/{name}` (`ImageDelete`), `GET /images/search` (`ImageSearch`), and `POST /images/prune` (`ImagePrune`).
- Image tar endpoints are `GET /images/{name}/get` (`ImageGet`), `GET /images/get` (`ImageGetAll`), and `POST /images/load` (`ImageLoad`). They document the legacy image tarball layout with per-layer directories, `VERSION`, `json`, `layer.tar`, whiteout files, and optional `repositories`.
- System endpoints include `POST /auth` (`SystemAuth`), `GET /info` (`SystemInfo`), `GET /version` (`SystemVersion`), `GET`/`HEAD /_ping` (`SystemPing`, `SystemPingHead`), `GET /events` (`SystemEvents`), and `GET /system/df` (`SystemDataUsage`).
- Exec endpoints include `POST /containers/{id}/exec` (`ContainerExec`), `POST /exec/{id}/start` (`ExecStart`), `POST /exec/{id}/resize` (`ExecResize`), and `GET /exec/{id}/json` (`ExecInspect`). Inline schemas define `ExecConfig`, `ExecStartConfig`, and `ExecInspectResponse`.
- Volume endpoints include `GET /volumes` (`VolumeList`), `POST /volumes/create` (`VolumeCreate`), `GET /volumes/{name}` (`VolumeInspect`), `DELETE /volumes/{name}` (`VolumeDelete`), and `POST /volumes/prune` (`VolumePrune`).
- Network endpoints include `GET /networks` (`NetworkList`), `GET`/`DELETE /networks/{id}` (`NetworkInspect`, `NetworkDelete`), `POST /networks/create` (`NetworkCreate`), `POST /networks/{id}/connect` (`NetworkConnect`), `POST /networks/{id}/disconnect` (`NetworkDisconnect`), and `POST /networks/prune` (`NetworkPrune`).
- Plugin endpoints include list, privilege discovery, pull, inspect, delete, enable, disable, upgrade, create from tar, push, and set/configure: `PluginList`, `GetPluginPrivileges`, `PluginPull`, `PluginInspect`, `PluginDelete`, `PluginEnable`, `PluginDisable`, `PluginUpgrade`, `PluginCreate`, `PluginPush`, and `PluginSet`.
- Swarm/node endpoints include `NodeList`, `NodeInspect`, `NodeDelete`, `NodeUpdate`, `SwarmInspect`, `SwarmInit`, `SwarmJoin`, `SwarmLeave`, `SwarmUpdate`, `SwarmUnlockkey`, and `SwarmUnlock`.
- Service/task endpoints include `ServiceList`, `ServiceCreate`, `ServiceInspect`, `ServiceDelete`, `ServiceUpdate`, `ServiceLogs`, `TaskList`, `TaskInspect`, and `TaskLogs`.
- Secret/config endpoints include list/create/inspect/delete/update for both object kinds: `SecretList`, `SecretCreate`, `SecretInspect`, `SecretDelete`, `SecretUpdate`, `ConfigList`, `ConfigCreate`, `ConfigInspect`, `ConfigDelete`, and `ConfigUpdate`.
- `GET /distribution/{name}/json` (`DistributionInspect`) returns registry descriptor/platform metadata. `POST /session` (`Session`) upgrades to h2c raw-stream transport for BuildKit-style bidirectional client/server capabilities.

Shared definitions referenced across the chunk include `ImageSummary`, `ImageInspect`, `ImageHistoryResponseItem`, `BuildCache`, `CreateImageInfo`, `PushImageInfo`, `ImageDeleteResponseItem`, `AuthConfig`, `SystemInfo`, `SystemVersion`, `EventMessage`, `ContainerSummary`, `Volume`, `VolumeCreateOptions`, `VolumeListResponse`, `Network`, `IPAM`, `EndpointSettings`, `Plugin`, `PluginPrivilege`, `Node`, `NodeSpec`, `Swarm`, `SwarmSpec`, `ServiceSpec`, `Service`, `ServiceUpdateResponse`, `Task`, `SecretSpec`, `Secret`, `ConfigSpec`, `Config`, `DistributionInspect`, `IdResponse`, and `ErrorResponse`.

## Control Flow

Image/build flows are mostly daemon-local but can delegate to registries and build backends. `ImageBuild` validates Dockerfile syntax before running instructions, streams JSON build progress, can cancel when the client connection closes, and chooses classic builder or BuildKit through the `version` query parameter. Build cache pruning walks builder cache objects and applies JSON filters and storage retention before returning deleted cache IDs and reclaimed space. `ImageCreate` branches between pull and import depending on `fromImage` versus `fromSrc`; pulls can retrieve all tags when `tag` is empty and imports can read an upload body when `fromSrc=-`.

Image reference mutation follows a tag/delete/reference-store model. `ImageTag` adds or overwrites a repository/tag reference for an existing source image. `ImageDelete` can untag and remove unreferenced parent layers, subject to descendant-image, running-container, and build-use conflicts, with `force` and `noprune` controlling conflict and parent pruning behavior. `ImagePrune` applies dangling, timestamp, and label filters before deleting unused images and reporting reclaimed bytes.

Registry and archive flows use a mix of auth headers, streaming bodies, and tar formats. `ImagePush`, `ImageCreate`, plugin pull/upgrade, service create/update, and system auth all depend on encoded registry credentials. Image save/load endpoints move tar streams over HTTP and must preserve Docker's documented layer metadata layout. `DistributionInspect` contacts the registry for manifest descriptor/platform information without being a local image inspect.

System flows are read-mostly except registry auth. `/info`, `/version`, and `/_ping` are health/capability probes. `/_ping` exposes headers such as `Api-Version`, `Builder-Version`, and `Docker-Experimental`; `HEAD /_ping` is a lighter equivalent. `/events` streams real-time daemon events and supports `since`, `until`, and broad object filters. `/system/df` aggregates local storage accounting for layers, images, containers, volumes, and build cache.

Exec flow is two-phase. A client creates an exec instance against a running container through `ContainerExec`, then starts it through `ExecStart`. Non-detached start establishes an interactive raw-stream response; TTY sessions can be resized through `ExecResize`; `ExecInspect` exposes whether the process is running, its exit code, open streams, process config, container ID, and daemon-side PID. A paused container yields `409` at creation or start.

Volume and network flows map API requests onto daemon drivers. Volumes can be listed with filters, created with `VolumeCreateOptions`, inspected, force-deleted, and pruned when unused. Networks can be listed or inspected in compact/detailed forms, created with driver/IPAM/options/labels, removed unless predefined, connected to or disconnected from containers with endpoint/IPAM config, and pruned by age/label filters.

Plugin flow manages installed plugin packages and their runtime enablement. Clients discover requested privileges for a remote plugin, pull or upgrade with accepted privilege grants and registry auth, create a plugin from a tar rootfs/manifest, inspect installed plugin metadata, enable/disable with timeout or force semantics, push installed plugins, set string configuration entries, and remove plugins with an optional force disable.

Swarm/node/service/task flows are versioned manager-control-plane operations. Node, swarm, service, secret, and config updates require a `version` query parameter to avoid conflicting writes. Swarm init/join configure manager listen/advertise addresses, data-path address/port, default address pools, subnet size, force-new-cluster, and `SwarmSpec`. Service create/update accepts full `ServiceSpec` bodies, registry auth, update/rollback strategies, endpoint specs, secrets, mounts, log drivers, placement, and restart policies. Tasks are read-only scheduler artifacts with list filters and inspect/log access.

Secrets and configs have parallel lifecycles: list by JSON filters, create from specs containing name/labels/data and optional secret driver, inspect metadata/spec, delete by ID, and versioned update. The update descriptions explicitly limit mutation to labels; all other fields must remain unchanged from inspect responses.

The session flow is an HTTP upgrade. `POST /session` returns `101` on success and hijacks the connection to h2c raw-stream transport, allowing the daemon/server side to call back into client-provided gRPC services used by advanced build features.

## State And Persistence Behavior

The YAML has no persistence itself, but it describes persistent daemon and swarm state. Images, tags, build cache, volumes, networks, plugins, exec instances, swarm objects, services, tasks, secrets, and configs all have lifecycle semantics visible through these routes.

Images persist content-addressed layers plus mutable references such as repo tags and digests. Build output can create new images and intermediate containers/cache; build prune and image prune reclaim persisted cache/layer data. Image export/import operates on durable image metadata and layer tarballs. Commit creates a new image from a container, optionally pausing the container first and applying Dockerfile-style changes.

Volumes persist through volume drivers and can outlive containers. Network state includes built-in networks, user-defined networks, overlay/global scopes, IPAM allocations, endpoint connections, and driver options. Prune endpoints mutate persistent state and report reclaimed bytes or deleted object names/IDs.

Plugins persist installed rootfs/manifest/configuration and have separate enabled/disabled runtime state. Pull/upgrade/create/push integrate with registries or tar contexts, while enable/disable changes whether plugin capabilities are active for daemon subsystems.

Swarm-mode resources are raft-backed and versioned. `NodeUpdate`, `SwarmUpdate`, `ServiceUpdate`, `SecretUpdate`, and `ConfigUpdate` require object versions, making read-modify-write the intended client flow. Tasks are persisted or retained scheduler records produced by service reconciliation rather than directly mutable through this chunk.

Secrets and configs persist object metadata and base64 data in swarm state. Secret inspect/list examples expose name, labels, driver, ID, version, and timestamps but not secret payload material. Configs are less sensitive but follow the same versioned lifecycle and label-only update rule.

Streaming endpoints may have transient connection state that affects daemon work. Builds and image pulls/pushes can be canceled by client disconnect. Events, logs, exec start, and session upgrade hold open HTTP connections and require client support for Docker raw streams or h2c upgrade.

## Dependencies

This chunk depends on earlier schema definitions in `v1.40.yaml` for almost every response and body type. It also depends on shared error modeling through `ErrorResponse` and common object IDs through `IdResponse`.

Runtime dependencies include Docker's image store, layer/content storage, builder implementations, BuildKit, registry client/auth handling, container runtime and exec support, logging drivers, volume drivers, libnetwork/IPAM/network plugins, plugin manager, swarmkit manager/raft store/scheduler, overlay networking, secrets/config distribution, and HTTP connection hijacking.

Generated clients depend on correct interpretation of JSON-encoded `filters` query parameters, repeated array-style query parameters such as tags or image names, binary request/response bodies, required path/query parameters, base64/base64url auth headers, mixed success status codes, inline object schemas, `allOf` examples, enum values, and raw-stream or upgrade responses.

## Integration Points

The operation IDs in this chunk are the stable integration names for SDKs and tests. They cover image operations (`ImageList`, `ImageBuild`, `BuildPrune`, `ImageCreate`, `ImageInspect`, `ImageHistory`, `ImagePush`, `ImageTag`, `ImageDelete`, `ImageSearch`, `ImagePrune`, `ImageCommit`, `ImageGet`, `ImageGetAll`, `ImageLoad`), system operations (`SystemAuth`, `SystemInfo`, `SystemVersion`, `SystemPing`, `SystemPingHead`, `SystemEvents`, `SystemDataUsage`), exec operations, storage/network operations, plugins, swarm, services, tasks, secrets, configs, distribution, and session.

Image/build APIs integrate Docker Engine with Dockerfile parsing, classic builder, BuildKit, registry credentials, platform selection, remote Git/HTTP/tar contexts, BuildKit exporters, local image reference stores, and archive import/export tooling.

System APIs integrate with CLI and health-check tooling. `/info`, `/version`, and `/_ping` are used for client capability detection, daemon readiness, API negotiation, builder selection, and experimental-mode discovery. `/events` is the common integration point for watchers, orchestrators, audit tools, and UI refresh loops.

Exec/log/session APIs integrate with terminal clients and stream-capable HTTP stacks. `ExecStart`, service/task logs, image build progress, image pull/push/load progress, and `/session` require clients to handle streaming semantics beyond ordinary JSON request/response flows.

Volume, network, and plugin APIs integrate with external drivers and plugin capabilities. Network create/connect/disconnect bridges container runtime state with libnetwork and IPAM. Plugin pull/privilege/enable operations gate access to host mounts, devices, and network capabilities.

Swarm APIs integrate with swarmkit orchestration, raft object versions, node membership, service scheduling, task history, overlay networking, registry auth for service images, update/rollback controllers, secret/config distribution, and service/task log aggregation.

## Risks And Edge Cases

- This large path chunk mixes ordinary JSON APIs, binary tar streams, indefinite streams, and HTTP upgrade/hijack flows. Generated clients that assume JSON-only responses will mishandle build, logs, exec, archive, image save/load, and session operations.
- `POST /build` has many loosely typed string query parameters that contain JSON (`buildargs`, `cachefrom`, labels, `outputs`) or special values. URI encoding and backend-version differences are compatibility risks.
- Build args are explicitly not intended for secrets, but the schema cannot enforce that. Tooling should avoid passing credentials through `buildargs`.
- `ImageCreate` overloads pull and import in one endpoint. Invalid combinations of `fromImage`, `fromSrc`, `repo`, `tag`, body upload, and `changes` need daemon-side validation and client tests.
- Client disconnect cancellation is part of build, pull, and push behavior. Reverse proxies and SDK transports can accidentally cancel daemon work or leak long-running operations.
- Image delete/prune and build/volume/network prune are destructive and filter-sensitive. Time filters are computed relative to daemon time, not client time.
- Several endpoints use JSON-encoded `map[string][]string` filters in query strings. Bad encoding, wrong filter names, and negative label filters are easy sources of client/daemon mismatch.
- Image push ignores a tag embedded in the path `name` and requires `tag` query selection. This can surprise clients that pass `registry/repo:tag` as the path.
- `SystemAuth` can return either `200` with an identity token or `204` with no body. Clients must handle both as success.
- `/_ping` exposes important capability headers on both success and some errors. Compatibility tests should ensure proxies and clients do not discard them.
- `SystemEvents` is unbounded without `until`; consumers must support streaming and reconnect/resume from timestamps.
- Exec creation and start can fail with `409` for paused/stopped containers; resize only works when TTY was configured during both creation and start.
- Volume removal can return `409` when in use, and `force` semantics depend on the driver. Network removal rejects predefined networks with `403`.
- `NetworkConnect` and `NetworkDisconnect` inline schema titles appear swapped in the source (`NetworkDisconnectRequest` under connect and `NetworkConnectRequest` under disconnect), which can confuse generated model names.
- Swarm resource endpoints consistently document `503` when the node is not part of a swarm, while duplicate names and invalid networks produce more specific `409`/`403` statuses on service/secret/config creation.
- Versioned update APIs require full-object read-modify-write discipline. Omitting unchanged fields, using stale versions, or treating update bodies as patches can corrupt intent or fail validation.
- `ServiceUpdate` has special rollback control through `rollback=previous`, where the submitted spec is ignored. SDK validation requiring a meaningful full spec could block valid rollback requests.
- Secret/config update bodies use full specs but only labels may change. Clients must preserve all non-label fields from inspect responses.
- Logs for services/tasks only work for `local`, `json-file`, or `journald` logging drivers. Driver configuration in service specs can therefore determine later API availability.
- Delete success statuses vary by resource: images return `200` with deletion details, volumes/networks/secrets/configs often return `204`, service/node/plugin delete can return `200`. Generic clients need per-endpoint status handling.
- `/session` documentation says gRPC callback services over h2c after HTTP upgrade. This is a narrow transport contract that ordinary OpenAPI tooling will not model well.

## Test Signals

Useful validation signals for this chunk include:

- OpenAPI validation that all operation IDs are unique, path parameters are defined, required query/body parameters are marked correctly, response schemas resolve, and inline schemas remain generator-safe.
- Generated-client tests for JSON filter encoding across images, build cache, events, volumes, networks, plugins, nodes, services, tasks, secrets, and configs.
- Image/build tests covering classic versus BuildKit builder version, remote contexts, alternate Dockerfile paths, multiple tags, registry config headers, platform/target/options handling, malformed Dockerfile `400`, disconnect cancellation, and BuildKit output JSON encoding.
- Image lifecycle tests for pull/import mode selection, tag overwrite, push auth and tag query behavior, image delete conflict/force/noprune behavior, search filters, prune filters, and image save/load tar compatibility.
- System endpoint tests for `SystemAuth` `200` and `204` success variants, ping headers for GET and HEAD, event stream filtering and resume semantics, and `/system/df` inclusion of images, containers, volumes, and build cache.
- Exec tests covering create/start/inspect/resize, TTY versus non-TTY raw-stream framing, detach mode, env/user/working-dir propagation, exit-code reporting, missing container/exec `404`, and paused/stopped `409`.
- Volume/network tests covering driver filters, create/inspect/delete/prune, in-use volume `409`, predefined network `403`, IPv4/IPv6 IPAM config, endpoint connect/disconnect, swarm-scoped network restrictions, and prune age/label filters.
- Plugin tests covering privilege discovery, pull/upgrade auth and privilege grants, create from tar, enable timeout, forced disable/delete, set configuration arrays, inspect missing plugin `404`, and push behavior.
- Swarm/node tests covering init/join address and token validation, data-path port/default address pool handling, leave force behavior, unlock key retrieval/use, node filters, node force delete, and versioned node/swarm updates.
- Service/task tests covering service create warnings, duplicate-name `409`, network-not-eligible `403`, inspect defaults, update with version/registry auth/registryAuthFrom/rollback, log parameters and driver restrictions, task filters, task inspect, and non-swarm `503`.
- Secret/config tests covering create/list/inspect/delete/update, duplicate-name conflicts, required update versions, label-only mutation enforcement, attempted data/name changes, non-swarm `503`, and secret inspect not leaking payload data.
- Distribution/session tests covering private-registry auth failures, missing image documented as `401`, multi-platform descriptor decoding, server errors, and successful `/session` `101` upgrade to h2c raw stream.
