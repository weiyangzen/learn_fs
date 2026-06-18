# sources/cloud-native/moby/api/docs/v1.42.yaml research: subset-b-000134

Chunk: `sources/cloud-native/moby/api/docs/v1.42.yaml` lines 7761-12548.

## Purpose

This chunk is the central path-operation section of Docker Engine API v1.42. It documents HTTP endpoints for container control, image and build operations, system introspection, exec sessions, volumes, networks, plugins, swarm/node/service/task resources, secrets/configs, distribution metadata, and BuildKit sessions. The YAML is an OpenAPI/Swagger contract: it does not implement the daemon behavior directly, but it is the source of truth for generated API docs, clients, request validation expectations, media types, response models, and operation IDs.

The chunk starts after earlier container endpoints and continues to the end of the `paths` map. It relies heavily on shared `#/definitions/*` schemas that appear outside this chunk, so the final per-file report must reconcile this path surface with definitions for objects such as `ErrorResponse`, `ImageSummary`, `ContainerConfig`, `Network`, `Plugin`, `Node`, `Swarm`, `Service`, `Task`, `Secret`, `Config`, and registry/distribution models.

## Important API Surface

Container lifecycle and filesystem APIs in this range:

- `POST /containers/{id}/pause` (`ContainerPause`) and `POST /containers/{id}/unpause` (`ContainerUnpause`) change process scheduling state through freezer cgroups and return `204` on success.
- `POST /containers/{id}/attach` (`ContainerAttach`) and `GET /containers/{id}/attach/ws` (`ContainerAttachWebsocket`) expose stdin/stdout/stderr as raw, multiplexed, websocket, or hijacked HTTP streams. Query flags select `logs`, `stream`, `stdin`, `stdout`, `stderr`, and `detachKeys`.
- `POST /containers/{id}/wait` (`ContainerWait`) blocks until a condition, returning `ContainerWaitResponse`.
- `DELETE /containers/{id}` (`ContainerDelete`) removes containers, optionally deleting anonymous volumes, killing running containers, or deleting links.
- `HEAD/GET/PUT /containers/{id}/archive` (`ContainerArchiveInfo`, `ContainerArchive`, `PutContainerArchive`) reads file metadata, exports tar archives, and extracts uploaded tar streams into a container filesystem.
- `POST /containers/prune` (`ContainerPrune`) deletes stopped containers with `until` and `label` filters.
- `POST /containers/{id}/exec` (`ContainerExec`) creates exec instances with attach flags, TTY, environment, command, privilege, user, working directory, and console size.

Image, build, registry, and distribution APIs:

- `GET /images/json` (`ImageList`) lists images using `all`, JSON `filters`, `shared-size`, and `digests`.
- `POST /build` (`ImageBuild`) builds from a tar context or remote context. It accepts many daemon/build controls: dockerfile path, tags, extra hosts, quiet/no-cache/cachefrom/pull/rm/forcerm, memory and CPU limits, build args, shared memory, squash, labels, network mode, `Content-type`, base64 `X-Registry-Config`, platform, target, BuildKit `outputs`, and builder backend `version`.
- `POST /build/prune` (`BuildPrune`) deletes build cache with `keep-storage`, `all`, and cache filters.
- `POST /images/create` (`ImageCreate`) pulls or imports an image and supports registry auth, platform, import metadata, and Dockerfile-style image changes.
- `GET /images/{name}/json`, `/history`, `/get`, and `/images/get` inspect, show layer history, and export one or multiple image tarballs.
- `POST /images/{name}/push`, `/tag`, `DELETE /images/{name}`, `GET /images/search`, `POST /images/prune`, and `POST /images/load` push, tag, delete, search, prune, and import images.
- `POST /commit` (`ImageCommit`) creates an image from a container and can pause the container by default before committing.
- `GET /distribution/{name}/json` (`DistributionInspect`) contacts the registry for digest/platform information.

System and streaming APIs:

- `POST /auth` (`SystemAuth`) validates registry credentials and may return an identity token or `204`.
- `GET /info`, `GET /version`, and `GET/HEAD /_ping` expose daemon information, version metadata, health, API version, builder version, experimental mode, swarm state, and no-cache headers.
- `GET /events` (`SystemEvents`) streams daemon events across object types using timestamp and JSON filter query parameters.
- `GET /system/df` (`SystemDataUsage`) reports layer, image, container, volume, and build-cache disk usage. The `type` query parameter is a multi-value enum.
- `POST /session` (`Session`) hijacks an HTTP connection to h2c for BuildKit-style interactive sessions that let the daemon call back to client-side gRPC services.

Exec APIs:

- `POST /exec/{id}/start` starts an existing exec instance, either detached or as an interactive raw/multiplexed stream.
- `POST /exec/{id}/resize` resizes an exec TTY and requires `h` and `w`.
- `GET /exec/{id}/json` inspects exec state, including running flag, exit code, process config, open stdio flags, container ID, and host PID.

Volume and network APIs:

- `GET /volumes`, `POST /volumes/create`, `GET/PUT/DELETE /volumes/{name}`, and `POST /volumes/prune` list, create, inspect, update swarm cluster volumes, delete, and prune volumes.
- `GET /networks`, `GET/DELETE /networks/{id}`, `POST /networks/create`, `POST /networks/{id}/connect`, `POST /networks/{id}/disconnect`, and `POST /networks/prune` manage local, global, swarm, builtin, and custom networks.
- Network creation includes duplicate-name best-effort semantics, driver and scope selection, internal/attachable/ingress/config-only flags, config-source references, IPAM, IPv6, driver options, and labels.

Plugin APIs:

- `GET /plugins`, `GET /plugins/privileges`, `POST /plugins/pull`, `GET /plugins/{name}/json`, `DELETE /plugins/{name}`, `POST /plugins/{name}/enable`, `/disable`, `/upgrade`, `POST /plugins/create`, `POST /plugins/{name}/push`, and `POST /plugins/{name}/set` cover plugin lifecycle, registry auth, privilege negotiation, tar-based creation, enable/disable force flags, upgrade privileges, and string-based configuration.

Swarm, node, service, and task APIs:

- `GET /nodes`, `GET/DELETE /nodes/{id}`, and `POST /nodes/{id}/update` manage swarm nodes and use object `version` for optimistic concurrency.
- `GET /swarm`, `POST /swarm/init`, `/join`, `/leave`, `/update`, `GET /swarm/unlockkey`, and `POST /swarm/unlock` handle swarm membership, advertised/listen/data-path addresses, default address pools, forced new clusters, token rotation, manager unlock keys, and spec updates.
- `GET /services`, `POST /services/create`, `GET/DELETE /services/{id}`, `POST /services/{id}/update`, and `GET /services/{id}/logs` manage service specs, image registry auth, update/rollback controls, default insertion on inspect, and service log streaming.
- `GET /tasks`, `GET /tasks/{id}`, and `GET /tasks/{id}/logs` list/inspect tasks and stream task logs.

Secret and config APIs:

- `GET /secrets`, `POST /secrets/create`, `GET/DELETE /secrets/{id}`, and `POST /secrets/{id}/update` manage swarm secrets. Updates require a version and currently only allow label changes while preserving the remaining spec fields.
- `GET /configs`, `POST /configs/create`, `GET/DELETE /configs/{id}`, and `POST /configs/{id}/update` mirror the secret API for swarm configs, with versioned label-only updates.

## Control Flow and Protocol Behavior

Most operations follow a declarative REST shape: identify a resource by path, pass optional query filters or a JSON/tar body, and return an object reference, full object, stream, or empty success code. State-changing endpoints use `POST`, `PUT`, or `DELETE`, while read-only inspection endpoints use `GET` or `HEAD`.

Several endpoints are long-lived or connection-sensitive:

- Attach, exec start, service logs, and task logs return Docker raw or multiplexed stream media types. For non-TTY streams, clients must decode 8-byte multiplex headers whose first byte identifies stdout/stderr and whose final four bytes encode payload size in big-endian order.
- Attach and session endpoints can hijack or upgrade the HTTP connection (`tcp` for attach, `h2c` for session). Proxies and generated clients must preserve upgrade headers and avoid buffering assumptions.
- Build, image pull/import/push, events, logs, wait, and session APIs depend on client connection lifetime. The spec explicitly says build, pull, and push are cancelled when the client connection is closed.
- Wait uses a blocking POST with `condition` values `not-running`, `next-exit`, and `removed`.

Versioned swarm resources use optimistic concurrency: node, swarm, service, volume, secret, and config updates require a `version` query parameter that must match the current object version from inspect/list responses. Service update also supports `registryAuthFrom` and a `rollback=previous` mode in which the supplied spec is ignored.

## State and Persistence Behavior

This chunk is dominated by daemon state mutation. Persistent or durable state touched by these endpoints includes container runtime state, container filesystems, image store content, build cache, plugin installation/configuration, volume metadata/backing storage, network definitions and endpoint attachments, swarm Raft objects, secrets/configs, and registry-derived image metadata.

High-impact mutations include:

- Container pause/unpause, removal, archive extraction, exec creation/start, and commit.
- Image build, create/pull/import, tag, push, delete, prune, load, and export.
- Build-cache prune, container/image/volume/network prune operations that reclaim disk and delete objects selected by filters.
- Network creation/deletion plus connect/disconnect, which changes container connectivity and may interact with swarm overlay constraints.
- Plugin pull/create/enable/disable/upgrade/delete/set/push, which can install executable extension code and request host privileges such as network, mount, and device access.
- Swarm init/join/leave/update/unlock and token rotation, which can reconfigure cluster membership, control-plane security, and manager lock state.
- Service create/update/delete and task/service logs, which drive swarm orchestration and may pull private images using supplied registry credentials.
- Secret and config create/delete/update, which persist cluster-scoped sensitive or configuration data.

The YAML models persistence through response codes, required versions, filters, and schema references rather than by implementation code. For code generation and tests, the important state cues are required request bodies, required query parameters, conflict status codes (`409`), swarm availability status (`503`), and documented limitations such as label-only secret/config updates and local-driver-only service/task logs.

## Dependencies and Integration Points

Schema dependencies are primarily `$ref` links into the file's definitions section. Key references from this chunk include `ErrorResponse`, `ContainerWaitResponse`, `ImageSummary`, `ImageInspect`, `ImageHistoryResponseItem`, `ImageDeleteResponseItem`, `AuthConfig`, `SystemInfo`, `SystemVersion`, `IdResponse`, `ContainerConfig`, `EventMessage`, `ContainerSummary`, `Volume`, `BuildCache`, `ProcessConfig`, `VolumeListResponse`, `VolumeCreateOptions`, `ClusterVolumeSpec`, `Network`, `ConfigReference`, `IPAM`, `EndpointSettings`, `Plugin`, `PluginPrivilege`, `Node`, `NodeSpec`, `Swarm`, `SwarmSpec`, `Service`, `ServiceSpec`, `ServiceUpdateResponse`, `Task`, `Secret`, `SecretSpec`, `Config`, `ConfigSpec`, and `DistributionInspect`.

External and daemon subsystem integrations include:

- Linux freezer cgroup behavior for pause/unpause.
- Container PTY and stdio plumbing for attach/exec/logs.
- Tar archive readers/writers and compression support for container archive, image save/load, image import, plugin create, and build context upload.
- Dockerfile parser/classic builder and BuildKit backend selection.
- Registry authentication headers (`X-Registry-Auth`, `X-Registry-Config`) and Docker Hub legacy registry URL handling.
- Docker Hub search and registry distribution inspect.
- Logging drivers (`local`, `json-file`, `journald`) for service/task logs.
- Swarm control plane, Raft object versions, manager unlock keys, overlay networking, and join tokens.
- Plugin registry and host-privilege model.

## Risks and Edge Cases

- Streaming and hijacked endpoints are easy to break in generated clients because normal JSON response handling does not apply. Tests need to cover raw stream, multiplexed stream, websocket attach, HTTP 101 upgrade, and h2c session behavior.
- Several request parameters are JSON encoded strings in query parameters (`filters`, `buildargs`, `labels`, `outputs`, `cachefrom`, registry config headers). Clients must URL/base64 encode them correctly and should not treat them as ordinary object bodies.
- The build API mixes classic-builder and BuildKit options. The `version` parameter defaults to `"1"` while ping advertises daemon builder recommendation; clients should handle daemon recommendation and explicit user override separately.
- Dangerous cleanup endpoints (`container/image/volume/network/build prune`) depend on filter semantics. Poor filter encoding can delete more data than intended.
- Archive extraction can overwrite filesystem objects and has special `noOverwriteDirNonDir` and `copyUIDGID` flags. Tests should cover directory/file conflicts, read-only rootfs or volume `403`, and malformed tar input.
- Registry auth data appears in headers and base64-encoded objects. Logs, generated examples, and client debug traces should avoid leaking credentials or tokens.
- Swarm update/delete operations often return `503` when the node is not part of a swarm. Tests must distinguish authorization/authentication failures, not-found errors, conflicts, and not-in-swarm states.
- Versioned swarm object updates must reject stale versions. Secret/config update descriptions require all non-label fields to remain unchanged, which is a subtle contract not fully enforced by schema shape alone.
- Plugin operations can request host privileges and may remain in use by containers. `force` flags on plugin disable/delete and network disconnect can have disruptive effects.
- Some documented types are loose or legacy: `pull` on build is a string, `noOverwriteDirNonDir` and `copyUIDGID` are strings that accept boolean-like values, and image search is tied to Docker Hub. Generated clients should preserve these shapes for API compatibility.
- Path parameters such as image/plugin names can include tags, digests, registry prefixes, or slashes. Routers, docs links, and client URL escaping need tests for encoded path segments.
- Media type declarations vary: some success responses have no schema, some stream binary strings, and `/auth` can return either `200` with body or `204`. Code generators may need custom handling for such alternatives.

## Test Signals

Useful validation signals for this chunk:

- OpenAPI parsing succeeds and every operation ID in this range is unique.
- All `$ref` targets used in this range resolve in the definitions section during full-file validation.
- Generated clients preserve required fields and query parameters, especially `version`, path IDs/names, body requirements, auth headers, and array query collection behavior.
- Golden tests cover representative success and error responses: `204` no-content mutations, `201` create responses, `409` conflicts, `503` not-in-swarm, `101` upgrades, binary/tar responses, and streaming log/attach responses.
- Filter encoding tests cover each object family: container, image, build-cache, volume, network, plugin, node, service, task, secret, and config filters.
- Stream decoder tests cover Docker's 8-byte multiplex header, TTY raw stream mode, websocket attach flags, service/task log query flags, and client disconnect cancellation behavior.
- State mutation integration tests should exercise version conflict handling for node/swarm/service/volume/secret/config updates and should verify prune endpoints return deleted IDs and reclaimed space where applicable.
- Security-focused tests should ensure registry auth headers and secret/config payloads are accepted in the documented locations but not echoed unexpectedly in logs or error messages.

## Cross-Chunk Notes

This chunk references definitions and earlier container endpoints outside lines 7761-12548. The final merged research for `v1.42.yaml` should connect these path operations to the top-level OpenAPI metadata, shared parameters/security definitions, earlier container CRUD/logs/stats operations, and the schema definitions that close the `$ref` graph.
