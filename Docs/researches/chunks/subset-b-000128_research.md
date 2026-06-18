# sources/cloud-native/moby/api/docs/v1.39.yaml lines 7775-11611

## Scope

This chunk covers Docker Engine API v1.39 Swagger path definitions from `POST /images/create` through the experimental `POST /session` endpoint. It is an API contract, not executable daemon code, and therefore documents the request/response shapes consumed by generated clients, compatibility tests, the rendered API reference, and daemon handler conformance checks.

The covered surface spans image pull/import/inspect/history/push/tag/delete/search/prune/export/load/commit operations; registry auth and distribution inspection; system auth/info/version/ping/events/data-usage APIs; container exec creation/start/resize/inspect; volume, network, and plugin lifecycle APIs; swarm node and cluster control; service and task APIs; secret/config management; and the BuildKit session upgrade endpoint.

## Purpose

The chunk exposes the mid-to-late Docker Engine API v1.39 resource model. It lets clients move images between registries, tar archives, containers, and the local image store; inspect daemon status and stream daemon events; create interactive exec sessions inside running containers; manage local storage and networking resources; install and configure plugins; manage swarm nodes, services, tasks, secrets, and configs; query registry manifest metadata; and establish an experimental bidirectional session channel for advanced build/client callbacks.

Most operations are stateful daemon mutations or state reads. Image, volume, network, plugin, swarm, service, secret, and config endpoints mutate persistent local or swarm state. System endpoints expose daemon-level status and event streams. Exec and log/session endpoints are connection-oriented APIs where response handling can require raw streams, HTTP upgrade, or hijacking behavior rather than ordinary JSON decoding.

## Important APIs And Types

- `POST /images/create` (`ImageCreate`) pulls from a registry with `fromImage` or imports with `fromSrc`; it accepts `repo`, `tag`, `message`, optional body content for `fromSrc=-`, `platform`, and `X-Registry-Auth`.
- Image inspection and metadata endpoints include `GET /images/{name}/json` (`ImageInspect`) returning `ImageInspect`, `GET /images/{name}/history` (`ImageHistory`) returning `ImageHistoryResponseItem[]`, and `GET /distribution/{name}/json` (`DistributionInspect`) returning descriptor and platform metadata from a registry.
- Image mutation/export endpoints include `POST /images/{name}/push`, `POST /images/{name}/tag`, `DELETE /images/{name}`, `GET /images/{name}/get`, `GET /images/get`, `POST /images/load`, `POST /commit`, and `POST /images/prune`.
- Image discovery endpoints include `GET /images/search`, with `term`, `limit`, and JSON-encoded filters, plus `ImagePrune` filters for `dangling`, `until`, and labels.
- System endpoints include `POST /auth` (`SystemAuth`) with `AuthConfig`; `GET /info` (`SystemInfo`); `GET /version` (`SystemVersion`); `GET /_ping` (`SystemPing`) with `Api-Version`, `Builder-Version`, and `Docker-Experimental` headers; `GET /events` (`SystemEvents`); and `GET /system/df` (`SystemDataUsage`) returning layer size, `ImageSummary[]`, `ContainerSummary[]`, `Volume[]`, and `BuildCache[]`.
- Exec endpoints include `POST /containers/{id}/exec` (`ContainerExec`) with inline exec config fields such as attach flags, detach keys, TTY, env, command, privilege, user, and working directory; `POST /exec/{id}/start` (`ExecStart`); `POST /exec/{id}/resize`; and `GET /exec/{id}/json` returning `ExecInspectResponse` with `ProcessConfig`, stream flags, running state, exit code, container ID, and PID.
- Volume endpoints include list/create/inspect/delete/prune and reference `VolumeListResponse`, `Volume`, `VolumeCreateOptions`, and `VolumePruneResponse`.
- Network endpoints include list/inspect/delete/create/connect/disconnect/prune and use `Network`, `IPAM`, `EndpointSettings`, and inline request/response objects. Create supports bridge defaults, duplicate checking, internal/attachable/ingress flags, IPv6, driver options, labels, and IPAM config.
- Plugin endpoints include list, privileges, pull, inspect, delete, enable, disable, upgrade, create, push, and set. They use `Plugin`, plugin privilege arrays, registry auth headers, tar rootfs/manifest upload, force/timeout flags, and string setting lists.
- Node and swarm endpoints include node list/inspect/delete/update, swarm inspect/init/join/leave/update/unlockkey/unlock. They reference `Node`, `NodeSpec`, `Swarm`, and `SwarmSpec`, and use required object `version` query parameters for updates.
- Service and task endpoints include service list/create/inspect/delete/update/logs and task list/inspect/logs. They reference `Service`, `ServiceSpec`, `ServiceUpdateResponse`, and `Task`, with versioned service update, registry auth, rollback, raw log streaming, and JSON filters.
- Secret and config endpoints provide list/create/inspect/delete/update for `Secret`, `SecretSpec`, `Config`, and `ConfigSpec`; update operations require `version` and are documented as label-only updates.
- `POST /session` (`Session`) is experimental and produces `application/vnd.docker.raw-stream`; it upgrades/hijacks the HTTP connection to h2c so the daemon can call back to client-provided gRPC services.

Shared response schemas are dominated by `ErrorResponse`, `IdResponse`, and resource-specific response objects. Many list/prune endpoints use JSON-encoded query filters represented as plain strings rather than structured Swagger objects.

## Control Flow

Image flows branch by operation. `ImageCreate` is either a registry pull or an import depending on `fromImage` versus `fromSrc`; import can read the body when `fromSrc=-`, while pull and push are cancellable when the HTTP connection closes. Push and plugin pull/upgrade rely on base64url `X-Registry-Auth`. Commit snapshots a container into a new image, optionally pausing the container and applying Dockerfile-style changes. Save/load operations exchange tar archives, and image deletion can force removal or skip parent pruning.

System flows are mostly read-only, except `SystemAuth` validates registry credentials and can return an identity token. `_ping` is the lightweight liveness/capability probe. `SystemEvents` is a long-lived stream: callers can replay events since a timestamp, stop at `until`, then stream new events while applying filters across containers, images, volumes, networks, daemon, plugins, nodes, services, secrets, and configs. `SystemDataUsage` gathers a cross-resource disk-usage snapshot including BuildKit cache data.

Exec flow is two-stage. A client creates an exec instance against a running container, then starts it. Non-detached start establishes an interactive raw-stream session, while detached start returns after launch. Resize only applies to TTY exec sessions. Inspect reports whether the exec is running, its exit code, process config, open streams, container ID, and PID. Conflict responses cover paused, stopped, or paused containers.

Volume, network, and plugin flows are local daemon resource lifecycles. Volumes can be filtered, created through drivers, inspected, force-deleted, and pruned. Networks can be filtered, created with IPAM/driver options, inspected with optional verbose/scope controls, deleted, connected to containers with endpoint settings, disconnected with optional force, and pruned. Plugins have a privilege-acceptance flow: privileges can be queried before pull/upgrade, accepted permissions are submitted in the request body, and the installed plugin can then be inspected, enabled, disabled, configured, pushed, upgraded, or removed.

Swarm control flow starts with node listing/inspection/update/removal and cluster inspect/init/join/leave/update/unlock operations. Init and join accept listen/advertise/data-path addresses; init can set default address pools and force a new cluster, while join requires remote manager addresses and a join token. Updates on nodes and swarms require an object version to avoid conflicting writes. Swarm update can rotate worker tokens, manager tokens, and manager unlock keys.

Service control follows an inspect-modify-update model. Create persists a `ServiceSpec` and can return a warning if image digest pinning fails. Inspect can fill defaults. Update requires the current service version, accepts registry credentials from the request or existing specs, and can trigger server-side rollback with `rollback=previous`, in which case the supplied spec is ignored. Service and task logs share the container log model: ordinary `200` string responses are possible, while `follow=true` can return `101` and hijack the connection for raw stream output.

Secrets and configs follow parallel swarm object flows. List filters by id, label, name, or names; create persists a named object and returns an ID; inspect returns metadata/spec; delete returns `204`; update requires a version and allows only label changes, despite accepting the full spec schema. Distribution inspect is registry-facing rather than local-state-facing: it resolves an image name through registry access and returns descriptor and platform records or `401` for authentication failure/no image.

The session endpoint is a special control flow: clients request HTTP/1.1 upgrade to `h2c`, the daemon replies `101 UPGRADED`, and the resulting connection carries HTTP2/gRPC callback traffic. Generated clients and proxies must treat it differently from JSON endpoints.

## State And Persistence Behavior

The YAML document itself persists no runtime state, but it defines contracts for persistent Docker Engine resources. Images, tags, pulled/imported layers, committed images, loaded tarballs, volumes, networks, plugins, swarm nodes, services, secrets, and configs are all durable daemon or swarm state. Prune/delete endpoints reclaim storage or remove object references; force flags can bypass normal safety checks for images, volumes, plugins, nodes, swarm leave, and network disconnects.

Image operations change local content-addressed image/layer storage and repository tag references. Import and commit create new image records; tag creates another reference and may overwrite an existing repo/tag; delete may untag and remove untagged parents; prune removes unused images and reports reclaimed bytes. Save/load preserve image layer metadata in tar format.

System data usage reports aggregated local state but does not mutate it. Events expose state transitions across object types with timestamps and actor attributes. Because events are stream/replay oriented, callers must handle both historical replay bounded by `since`/`until` and ongoing event delivery.

Exec state is transient but daemon-tracked. Exec instances are created under a container, can be started once, may hold open stream state, and expose lifecycle fields such as running and exit code. The process itself is not persisted like a container; it is runtime state tied to the parent container.

Volumes and networks are persistent local resources, often backed by drivers/plugins. Volume prune/delete affects storage and can fail if references remain. Network create stores driver/IPAM/options/labels and can be scoped local, global, or swarm; connect/disconnect mutates container endpoint attachments.

Plugins are installed daemon extensions with accepted privileges, enabled/disabled state, settings, rootfs/manifest data, and registry references. Upgrade and pull depend on remote registry state and accepted privileges. Forced disable/delete can affect containers that rely on plugin capabilities.

Swarm, node, service, secret, and config objects are versioned swarm-store resources. Required `version` parameters on node, swarm, service, secret, and config updates are optimistic concurrency controls. Services additionally cause scheduler-produced task state, endpoint allocation, log availability, image credential storage, and rollback/update status. Secrets and configs are mounted into service tasks but are only partially mutable after creation.

Distribution inspection does not document local persistence; it reports external registry descriptor/platform metadata. Session state is connection-scoped and experimental, enabling daemon/client cooperation for build-related capabilities without creating an ordinary persisted resource.

## Dependencies

The Swagger path block depends on definitions elsewhere in `v1.39.yaml`, including `ErrorResponse`, `AuthConfig`, `SystemInfo`, `SystemVersion`, `IdResponse`, `ContainerConfig`, `ImageInspect`, `ImageHistoryResponseItem`, `ImageDeleteResponseItem`, `ImageSummary`, `ContainerSummary`, `Volume`, `VolumeListResponse`, `VolumeCreateOptions`, `BuildCache`, `ProcessConfig`, `Network`, `IPAM`, `EndpointSettings`, `Plugin`, `Node`, `NodeSpec`, `Swarm`, `SwarmSpec`, `Service`, `ServiceSpec`, `ServiceUpdateResponse`, `Task`, `Secret`, `SecretSpec`, `Config`, and `ConfigSpec`.

Runtime dependencies include the Docker daemon image store, content/layer storage, registry client and credential handling, container runtime process execution, log drivers, HTTP raw-stream/hijack support, volume and network drivers, plugin manager, swarmkit raft store and scheduler, overlay networking/VXLAN configuration, BuildKit cache accounting, and external registries. Swarm endpoints depend on the daemon being in the correct swarm state and, for most management operations, manager/state-store availability.

Client-generation dependencies include correct handling of path parameters, query booleans and integers, required update versions, JSON-encoded filter strings, binary request/response bodies, mixed content types, base64url registry auth headers, inline schemas, `allOf` examples, enum values, and response status codes that differ across similar resource classes.

## Integration Points

Operation IDs are the main SDK hooks: `ImageCreate`, `ImageInspect`, `ImageHistory`, `ImagePush`, `ImageTag`, `ImageDelete`, `ImageSearch`, `ImagePrune`, `SystemAuth`, `SystemInfo`, `SystemVersion`, `SystemPing`, `ImageCommit`, `SystemEvents`, `SystemDataUsage`, `ImageGet`, `ImageGetAll`, `ImageLoad`, `ContainerExec`, `ExecStart`, `ExecResize`, `ExecInspect`, `VolumeList`, `VolumeCreate`, `VolumeInspect`, `VolumeDelete`, `VolumePrune`, `NetworkList`, `NetworkInspect`, `NetworkDelete`, `NetworkCreate`, `NetworkConnect`, `NetworkDisconnect`, `NetworkPrune`, `PluginList`, `GetPluginPrivileges`, `PluginPull`, `PluginInspect`, `PluginDelete`, `PluginEnable`, `PluginDisable`, `PluginUpgrade`, `PluginCreate`, `PluginPush`, `PluginSet`, `NodeList`, `NodeInspect`, `NodeDelete`, `NodeUpdate`, `SwarmInspect`, `SwarmInit`, `SwarmJoin`, `SwarmLeave`, `SwarmUpdate`, `SwarmUnlockkey`, `SwarmUnlock`, `ServiceList`, `ServiceCreate`, `ServiceInspect`, `ServiceDelete`, `ServiceUpdate`, `ServiceLogs`, `TaskList`, `TaskInspect`, `TaskLogs`, `SecretList`, `SecretCreate`, `SecretInspect`, `SecretDelete`, `SecretUpdate`, `ConfigList`, `ConfigCreate`, `ConfigInspect`, `ConfigDelete`, `ConfigUpdate`, `DistributionInspect`, and `Session`.

Registry integration appears in image create/push, plugin pull/upgrade, service create/update image resolution, auth validation, and distribution inspection. Storage integration appears through image save/load/prune, system df, volumes, and build cache. Runtime integration appears through exec, commit, logs, events, and container network attachment. Swarm integration ties nodes, services, tasks, secrets, configs, overlay networks, join tokens, unlock keys, and service credentials into one state model.

The raw-stream and upgrade endpoints integrate with lower-level HTTP behavior. `ExecStart`, `ServiceLogs`, `TaskLogs`, and `Session` require clients, proxies, and test harnesses to support stream framing or connection upgrades instead of assuming JSON-only REST semantics.

## Risks And Edge Cases

- Several long-running operations are cancelled when the HTTP connection closes, notably image pull and push. Clients need retry and cancellation semantics that do not corrupt local expectations.
- Many filters are typed as plain strings containing JSON maps. Invalid JSON, unsupported keys, and generator assumptions about structured query parameters are common compatibility risks.
- Status codes are not uniform across resources: image delete returns `200` with deletion records, volume/config/secret delete returns `204`, plugin delete returns `200` with a plugin body, and network delete returns `204`.
- Force flags can bypass important safety checks: image removal, volume removal, plugin disable/delete, node removal, swarm leave, and network disconnect can affect running workloads or cluster availability.
- `ImageTag` can overwrite an existing repository/tag, and `ImageDelete noprune=false` can remove untagged parents. Automation should not assume these are metadata-only operations.
- `SystemEvents` is a stream with broad filters and object-specific attributes. Consumers must handle event ordering, reconnect gaps, unknown future event actions, and partial historical replay.
- Exec APIs mix JSON creation with raw-stream start behavior. TTY mode changes stream multiplexing expectations, resize only applies to TTY sessions, and conflict responses cover paused/stopped parent containers.
- Network create's `CheckDuplicate` is explicitly best-effort. Duplicate names can still exist because networks are keyed by ID, so clients should not rely on name uniqueness.
- Network connect/disconnect rejects swarm-scoped networks with `403`; service networking must use service specs rather than these container-level endpoints.
- Plugin privilege acceptance is security-sensitive. Pull/upgrade body contents must match accepted privileges, and forced disable/delete can break dependent containers.
- Swarm, node, service, secret, and config update endpoints require current versions. Stale or omitted versions must be tested because the spec often reports only `400`/`500` rather than a dedicated conflict status.
- Service update's `rollback=previous` ignores the supplied spec, a special path that generated clients or validation wrappers can accidentally block.
- Service and task logs can return either `101` hijacked streams or `200` strings and only work for `json-file` or `journald` logging drivers.
- Secret/config update accepts full specs but permits only label changes. Clients must preserve immutable fields from inspect responses and should not expect to rotate secret/config data through update.
- Secret and config create examples show `Data` as a base64 string; generated models must align with the shared definitions and real daemon behavior.
- `DistributionInspect` uses `401` for both failed authentication and no image found, which can blur auth and not-found handling.
- `Session` is experimental, h2c-based, and misspells gRPC as `gPRC` in the description. Proxies and clients that do not support HTTP upgrade/h2c will fail even though the endpoint is valid.

## Test Signals

Useful validation signals for this chunk include:

- Swagger validation for all `$ref` targets, operation ID uniqueness, path/query/header/body parameter requirements, enum values, response schemas, and binary content types.
- Generated-client tests for JSON-encoded filters on images, events, volumes, networks, plugins, nodes, services, tasks, secrets, and configs.
- Image lifecycle tests for pull/import modes, `fromSrc=-` body import, platform selection, auth failures, push cancellation, tag overwrite, delete force/noprune behavior, prune filters, save/load tar archive compatibility, and commit pause/changes handling.
- System endpoint tests for auth identity-token responses, ping headers, version/info schema compatibility, data-usage `BuildCache` presence, and event streaming with `since`, `until`, and filters for every documented object type.
- Exec tests for create/start/inspect/resize, attach stream combinations, TTY versus non-TTY stream behavior, detach keys, environment/user/working directory propagation, paused/stopped container conflicts, missing exec/container IDs, and exit code reporting.
- Volume tests for list filters, driver-backed create, inspect, force delete, in-use `409`, prune label filters, and reclaimed-space accounting.
- Network tests for list/inspect filters, verbose/scope inspect, create with IPAM/IPv6/options/labels/ingress/attachable flags, duplicate-name behavior, builtin-network delete `403`, plugin-not-found `404`, connect/disconnect endpoint settings, swarm-scope rejection, and prune `until`/label filters.
- Plugin tests for privilege query, pull/upgrade with accepted privileges and registry auth, create from tar, inspect, enable timeout, disable force, delete force, push missing-plugin errors, and setting updates.
- Swarm/node tests for init/join address parsing and required fields, force-new-cluster, default address pools, leave force semantics, unlock key retrieval/submission, token/key rotation, non-swarm/already-in-swarm `503`, and versioned node/swarm updates.
- Service/task tests for create warnings, network eligibility `403`, duplicate-name `409`, inspect defaults, delete status, versioned update, `registryAuthFrom` enum values, `rollback=previous`, task filters, task history, and service/task log `101` raw stream versus `200` body behavior.
- Secret/config tests for list filters, create duplicate names, inspect responses that avoid exposing secret payload data, delete `204`, label-only updates, stale versions, attempted name/data mutation, and non-swarm `503`.
- Distribution/session tests for registry descriptor/platform decoding, private registry auth, missing image as `401`, multi-platform manifests, h2c upgrade success, bad upgrade parameters, experimental feature gating, and proxy/client behavior around hijacked connections.
