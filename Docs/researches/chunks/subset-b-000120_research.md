# sources/cloud-native/moby/api/docs/v1.35.yaml lines 7566-10093

## Scope

This chunk covers Docker Engine API v1.35 Swagger path definitions from the tail of the volume list filter documentation through the experimental `POST /session` endpoint. It includes volume create/inspect/delete/prune operations; full network lifecycle and connect/disconnect operations; plugin list/install/configure/lifecycle operations; node list/inspect/delete/update; swarm inspect/init/join/leave/update/unlock operations; service list/create/inspect/delete/update/log operations; task list/inspect/log operations; secret and config lifecycle operations; registry distribution inspection; and the experimental session hijack endpoint.

The source is an OpenAPI/Swagger YAML contract, not executable daemon implementation code. The researched behavior is the API surface consumed by Docker clients, generated SDKs, CLI integration, daemon API compatibility tests, and documentation tooling.

## Purpose

This chunk defines the storage, networking, plugin, swarm orchestration, registry metadata, and advanced session portions of the Engine API v1.35 path table. The early endpoints expose local daemon resources such as volumes, networks, and plugins. The middle and later endpoints expose swarm-mode control-plane resources: nodes, swarm cluster settings, services, tasks, secrets, and configs. The last endpoints bridge to external registry metadata and to an experimental h2c session transport.

Most operations are stateful mutations or state reads against daemon-managed resources. Volume and network APIs affect local engine state and driver/plugin integrations. Node, swarm, service, task, secret, and config APIs depend on swarm mode and consistently document `503` when the daemon is not in a compatible swarm state. Plugin and distribution APIs integrate with registries and may require auth headers or accepted privileges. Log and session endpoints require clients to support raw stream or hijacked HTTP connections.

## Important APIs And Types

- `POST /volumes/create` (`VolumeCreate`) consumes a volume configuration object with `Name`, `Driver`, `DriverOpts`, and `Labels`, returning a `Volume` on `201`.
- `GET /volumes/{name}` (`VolumeInspect`) and `DELETE /volumes/{name}` (`VolumeDelete`) resolve a volume by name or ID. Delete supports `force=false` by default and can fail with `409` when the volume is in use.
- `POST /volumes/prune` (`VolumePrune`) removes unused volumes, filters by positive or negative labels, and returns `VolumesDeleted` plus `SpaceReclaimed`.
- `GET /networks` (`NetworkList`) returns a reduced array of `Network` objects and filters by driver, id, label, name, scope, and builtin/custom type.
- `GET /networks/{id}` (`NetworkInspect`) resolves a network by ID or name and supports `verbose` troubleshooting output and a `scope` filter. `DELETE /networks/{id}` (`NetworkDelete`) removes a network but rejects predefined networks with `403`.
- `POST /networks/create` (`NetworkCreate`) consumes a network config requiring `Name` and optionally carrying `CheckDuplicate`, `Driver`, `Internal`, `Attachable`, `Ingress`, `IPAM`, `EnableIPv6`, `Options`, and `Labels`. It returns a created network `Id` and optional `Warning`.
- `POST /networks/{id}/connect` (`NetworkConnect`) attaches a container to a network with optional `EndpointSettings`, including per-endpoint IPAM configuration. `POST /networks/{id}/disconnect` (`NetworkDisconnect`) detaches a container and supports `Force`.
- `POST /networks/prune` (`NetworkPrune`) deletes unused networks and filters by `until` timestamp/duration and label inclusion/exclusion.
- `GET /plugins` (`PluginList`) lists installed `Plugin` objects filtered by capability or enabled state.
- `GET /plugins/privileges` (`GetPluginPrivileges`) returns the permission set required to install a remote plugin, with entries such as `network`, `mount`, and `device`.
- `POST /plugins/pull` (`PluginPull`) installs a plugin from a registry using a required `remote`, optional local `name`, optional `X-Registry-Auth`, and a body containing accepted privilege entries.
- `GET /plugins/{name}/json` (`PluginInspect`), `DELETE /plugins/{name}` (`PluginDelete`), `POST /plugins/{name}/enable` (`PluginEnable`), `POST /plugins/{name}/disable` (`PluginDisable`), `POST /plugins/{name}/upgrade` (`PluginUpgrade`), `POST /plugins/create` (`PluginCreate`), `POST /plugins/{name}/push` (`PluginPush`), and `POST /plugins/{name}/set` (`PluginSet`) define the plugin lifecycle. Plugin create consumes `application/x-tar`; plugin set consumes a JSON string array such as `["DEBUG=1"]`.
- `GET /nodes` (`NodeList`) returns `Node` objects filtered by id, engine label, membership, name, and role. `GET /nodes/{id}` (`NodeInspect`) and `DELETE /nodes/{id}` (`NodeDelete`) resolve by ID or name; delete supports `force=false`.
- `POST /nodes/{id}/update` (`NodeUpdate`) consumes `NodeSpec` and requires an integer `version` query parameter for optimistic concurrency.
- `GET /swarm` (`SwarmInspect`) returns a `Swarm`. `POST /swarm/init` (`SwarmInit`) creates a swarm and returns the node ID string. `POST /swarm/join` (`SwarmJoin`) joins an existing swarm with required `ListenAddr`, `RemoteAddrs`, and `JoinToken`.
- `POST /swarm/leave` (`SwarmLeave`) accepts `force=false`; `POST /swarm/update` (`SwarmUpdate`) consumes `SwarmSpec`, requires `version`, and supports rotation flags for worker token, manager token, and manager unlock key.
- `GET /swarm/unlockkey` (`SwarmUnlockkey`) returns `UnlockKey`; `POST /swarm/unlock` (`SwarmUnlock`) accepts the unlock key object to unlock a locked manager.
- `GET /services` (`ServiceList`) returns `Service` objects filtered by id, label, mode, and name. `POST /services/create` (`ServiceCreate`) consumes `ServiceSpec`, accepts `X-Registry-Auth`, and returns created service `ID` plus optional `Warning`.
- `GET /services/{id}` (`ServiceInspect`) resolves by ID or name and supports `insertDefaults`; `DELETE /services/{id}` (`ServiceDelete`) removes a service.
- `POST /services/{id}/update` (`ServiceUpdate`) consumes `ServiceSpec`, requires `version`, accepts `X-Registry-Auth`, supports `registryAuthFrom=spec|previous-spec`, and supports `rollback=previous` where the supplied spec is ignored.
- `GET /services/{id}/logs` (`ServiceLogs`) and `GET /tasks/{id}/logs` (`TaskLogs`) return service/task stdout and stderr logs as either a `200` string body or a `101` hijacked raw stream. Parameters include `details`, `follow`, `stdout`, `stderr`, `since`, `timestamps`, and `tail`.
- `GET /tasks` (`TaskList`) returns `Task` objects filtered by desired state, id, label, name, node, and service. `GET /tasks/{id}` (`TaskInspect`) returns one task by ID.
- `GET /secrets`, `POST /secrets/create`, `GET /secrets/{id}`, `DELETE /secrets/{id}`, and `POST /secrets/{id}/update` define secret list/create/inspect/delete/update. `SecretUpdate` requires `version` and only permits label changes even though the body schema is `SecretSpec`.
- `GET /configs`, `POST /configs/create`, `GET /configs/{id}`, `DELETE /configs/{id}`, and `POST /configs/{id}/update` mirror secret lifecycle behavior for config objects using `Config` and `ConfigSpec`.
- `GET /distribution/{name}/json` (`DistributionInspect`) contacts the registry and returns a required `Descriptor` object plus `Platforms` array.
- `POST /session` (`Session`) is experimental, requires daemon experimental features, upgrades to h2c, hijacks the HTTP connection, and allows the daemon to call back to client-exposed gRPC services.

Shared definitions referenced by this chunk include `Volume`, `Network`, `IPAM`, `EndpointSettings`, `Plugin`, `Node`, `NodeSpec`, `Swarm`, `SwarmSpec`, `Service`, `ServiceSpec`, `ServiceUpdateResponse`, `Task`, `Secret`, `SecretSpec`, `Config`, `ConfigSpec`, and `ErrorResponse`.

## Control Flow

Volume control flow is the standard daemon resource lifecycle. Clients may list volumes before this chunk, create a named or daemon-generated volume, inspect it, delete it when unused, and prune all unused volumes matching label filters. Delete delegates removal to the volume driver and must handle driver-not-found and in-use states separately.

Network control flow is richer because networks are both local daemon resources and service/task integration points. Clients list or inspect networks, create a network with a driver and IPAM plan, connect containers with endpoint settings, disconnect containers with optional force, delete removable networks, and prune unused networks. Builtin networks such as bridge/host/none are represented in list examples, but predefined networks are protected from unsupported delete/create behavior by `403` responses.

Plugin operations form an install/accept/enable/configure lifecycle. Clients can ask for required privileges for a remote plugin, pull it with accepted privileges and registry auth, inspect the installed plugin, enable or disable it, update settings with a string array, push or upgrade it, create one from a tar stream, and delete it. Upgrade reuses the accepted-privilege body and registry auth pattern from pull.

Node and swarm operations implement swarm membership and cluster administration. A daemon can inspect swarm state, initialize a new swarm with listen/advertise/data-path addresses, join an existing swarm using manager addresses and a join token, leave the swarm, update the swarm spec with version protection and token/key rotation flags, retrieve the manager unlock key, and unlock a locked manager. Node update and swarm update both use explicit object versions to avoid lost writes.

Service lifecycle flow follows Docker's inspect-modify-update pattern. A client lists services, creates a `ServiceSpec`, inspects the returned object by ID or name, deletes it, or submits a full updated `ServiceSpec` with the current version. Service update has important alternate paths: if `rollback=previous`, the daemon performs a server-side rollback and ignores the submitted spec; if `X-Registry-Auth` is omitted, `registryAuthFrom` tells the daemon whether to source credentials from the submitted spec or the previous spec.

Task APIs are read-only observation endpoints for scheduler output. `TaskList` can return current and historical task records for the same service slot, with examples showing one running task and one shutdown task. `TaskInspect` is a point lookup. Task/service log endpoints follow the same transport model as container attach: `follow=false` can be a normal body, while `follow=true` can return `101` and hijack the connection for Docker raw-stream output.

Secret and config flows are parallel. Clients list with filters, create named objects with labels and base64 data, inspect metadata/spec, delete by ID, and update labels using a required version. The update descriptions explicitly require every non-label field to remain unchanged from inspect responses, so the expected client flow is inspect, preserve fields, modify labels, and update with the inspected version.

Distribution inspection is a read-through registry query rather than a local resource mutation. It resolves the path `name`, contacts the registry, and returns descriptor/platform metadata. The experimental session flow is also transport-oriented rather than object-oriented: the client sends `POST /session` with HTTP upgrade headers, the daemon returns `101`, and both sides communicate over a hijacked h2c transport for advanced callback capabilities.

## State And Persistence Behavior

The YAML file itself has no persistence, but it documents persistent and semi-persistent daemon state. Volumes persist on disk through volume drivers and expose name, driver, labels, and driver options. Prune endpoints are destructive garbage-collection operations and report reclaimed storage only for volumes.

Networks persist daemon and libnetwork state, including driver, IPAM, options, labels, scope, IPv6 enablement, attachability, ingress status, endpoint membership, and container connections. `CheckDuplicate` is explicitly best-effort because networks are keyed by random ID rather than name, so duplicate-name state can exist and clients must not rely on name uniqueness.

Plugins persist installed plugin metadata, enabled state, privileges, settings, and rootfs/manifest data. Pull and upgrade depend on remote registry content and accepted privilege state; delete may disable first when `force=true`, which can disturb containers using the plugin.

Swarm, node, service, task, secret, and config objects are swarm-state resources backed by the manager control plane. Node, swarm, service, secret, and config updates require version query parameters, documenting optimistic concurrency over versioned raft objects. Tasks are scheduler-produced state; they are observed here but not directly mutated by path operations in this chunk.

Services persist desired state in `ServiceSpec`, including task template, image, mounts, hosts, DNS, secrets, log driver, placement, resources, restart policy, replicated mode, update/rollback config, endpoint ports, and labels. Create/update may return image digest pinning warnings, so successful persistence can still carry advisory failure information.

Secrets and configs persist IDs, versions, timestamps, names, labels, optional drivers for secrets, and creation payloads. Inspect/list examples do not echo secret payload data, which is a confidentiality signal. Config examples similarly show metadata/spec rather than emphasizing data read-back.

Distribution inspection should not create local persistent state according to this contract. It reports registry descriptor and platform data. Session state is a live connection-level capability, not a durable object; it exists only while the upgraded/hijacked HTTP2 transport is active.

## Dependencies

At the schema level, the paths depend heavily on definitions elsewhere in `v1.35.yaml`: `Volume`, `Network`, `IPAM`, `EndpointSettings`, `Plugin`, `Node`, `NodeSpec`, `Swarm`, `SwarmSpec`, `Service`, `ServiceSpec`, `ServiceUpdateResponse`, `Task`, `Secret`, `SecretSpec`, `Config`, `ConfigSpec`, and the common `ErrorResponse`.

At runtime, volume endpoints depend on volume drivers and filesystem/storage accounting. Network endpoints depend on network drivers, IPAM plugins, libnetwork state, overlay/VXLAN behavior for swarm networks, and container endpoint attachment. Plugin endpoints depend on plugin registry access, local plugin storage, accepted privilege validation, tar unpacking for plugin creation, and plugin enable/disable semantics.

Swarm APIs depend on swarmkit manager availability, node membership, join tokens, manager unlock-key/autolock state, raft object versions, and cluster networking addresses such as listen, advertise, and data-path addresses. Service and task APIs depend on swarm scheduling/reconciliation, registry auth and image digest resolution, task runtime status, logging drivers, network attachments, secrets/configs, and endpoint publication.

Log and session endpoints depend on Docker's HTTP hijacking/raw-stream support. The service and task log endpoints only work for services using `json-file` or `journald` logging drivers. The session endpoint additionally depends on experimental daemon mode, HTTP h2c upgrade support, and client-side gRPC services exposed over the upgraded connection.

Distribution inspection depends on registry authentication, name parsing, manifest retrieval, descriptor handling, and platform metadata decoding. Generated clients depend on correct Swagger interpretation for path parameters, required query parameters, mixed content types, body schemas using `allOf`, binary tar/raw-stream bodies, and special `101` response handling.

## Integration Points

The operation IDs are the primary generated-client integration hooks: `VolumeCreate`, `VolumeInspect`, `VolumeDelete`, `VolumePrune`, `NetworkList`, `NetworkInspect`, `NetworkDelete`, `NetworkCreate`, `NetworkConnect`, `NetworkDisconnect`, `NetworkPrune`, `PluginList`, `GetPluginPrivileges`, `PluginPull`, `PluginInspect`, `PluginDelete`, `PluginEnable`, `PluginDisable`, `PluginUpgrade`, `PluginCreate`, `PluginPush`, `PluginSet`, `NodeList`, `NodeInspect`, `NodeDelete`, `NodeUpdate`, `SwarmInspect`, `SwarmInit`, `SwarmJoin`, `SwarmLeave`, `SwarmUpdate`, `SwarmUnlockkey`, `SwarmUnlock`, `ServiceList`, `ServiceCreate`, `ServiceInspect`, `ServiceDelete`, `ServiceUpdate`, `ServiceLogs`, `TaskList`, `TaskInspect`, `TaskLogs`, `SecretList`, `SecretCreate`, `SecretInspect`, `SecretDelete`, `SecretUpdate`, `ConfigList`, `ConfigCreate`, `ConfigInspect`, `ConfigDelete`, `ConfigUpdate`, `DistributionInspect`, and `Session`.

The CLI maps directly onto many of these paths: `docker volume create/inspect/rm/prune`, `docker network ls/inspect/create/connect/disconnect/rm/prune`, `docker plugin ls/install/inspect/rm/enable/disable/upgrade/create/push/set`, `docker node ls/inspect/rm/update`, `docker swarm init/join/leave/update/unlock-key/unlock`, `docker service ls/create/inspect/rm/update/logs`, `docker task`-style inspection through service/task commands, `docker secret` and `docker config` commands, registry manifest inspection paths, and BuildKit/session-style advanced client-daemon features.

Service APIs integrate with registry authentication through `X-Registry-Auth`, with image digest pinning via warning fields, with swarm networking through `EndpointSpec` and network attachments, and with secrets/configs through task template references. Task APIs integrate with service reconciliation, node placement, container runtime status, overlay network attachments, and logs.

Secret and config APIs integrate into service/task execution because service specs can mount them. Their update endpoints integrate with inspect results by requiring unchanged non-label fields. Distribution integrates the Engine API with Docker registry/manifest data. The experimental session endpoint integrates the daemon with client-provided callback services over h2c rather than a regular request/response JSON flow.

## Risks And Edge Cases

- The chunk begins mid-block at the tail of volume list filter documentation. Merge/reconciliation must combine this with the preceding chunk to reconstruct the full `/volumes` list path.
- Volume delete has both `404` for missing volume or driver and `409` for in-use volumes. Automation should treat these differently from idempotent missing-resource cases.
- Volume and network prune endpoints are destructive and accept JSON-encoded filter strings. Bad filter encoding or negative label semantics can delete more resources than intended.
- Network `CheckDuplicate` is best-effort and cannot guarantee name uniqueness. Clients that key networks by name can connect or delete the wrong resource if duplicate names exist.
- Builtin/predefined networks can appear in list output but reject unsupported operations with `403`; tests should cover `bridge`, `host`, `none`, ingress, and user-defined network differences.
- Network list intentionally returns a smaller representation than inspect and omits attached container details for API versions 1.28 and newer. Clients must not assume list and inspect shapes are equivalent.
- Plugin install and upgrade require explicit privilege acceptance. A client that skips `GET /plugins/privileges` or sends an incomplete privilege body should fail safely.
- `PluginDelete force=true` can disable a plugin in use by containers. This is operationally risky and should not be defaulted by higher-level tooling.
- Plugin names treat `:latest` as optional/default in many endpoints. Name normalization bugs can cause inspect/delete/enable/upgrade mismatches.
- `PluginCreate` consumes a tar stream, while most adjacent endpoints consume JSON. Generated clients need correct binary body support.
- Node, swarm, service, secret, and config updates require version parameters. Stale versions, missing versions, and concurrent writes are central compatibility cases.
- `SwarmInit` and `SwarmJoin` both return `503` for "already part of a swarm", while many other swarm endpoints use `503` for "not part of a swarm". Clients need endpoint-specific handling for the same status code.
- `SwarmLeave force=true` can break the cluster or remove the last manager. Tooling should make this an explicit user choice.
- `DataPathAddr` lets management and container data traffic use different addresses. Invalid interface/address handling and advertised address auto-detection are important deployment edge cases.
- `SwarmUpdate` rotation flags are independent of the required `SwarmSpec` body. Clients must preserve the full spec while rotating only credentials or unlock keys.
- `ServiceCreate` returns a singular `Warning`, while `ServiceUpdate` returns `ServiceUpdateResponse`. Client code should not assume warning shapes are identical across create and update.
- `ServiceUpdate rollback=previous` ignores the supplied spec. Client libraries that require a semantically valid spec for every update may accidentally block rollback.
- `registryAuthFrom` is documented as accepting `spec` and `previous-spec`, but the schema is a plain string rather than an enum. Invalid values depend on daemon validation.
- Service and task log endpoints can return `101` or `200`, and follow mode hijacks the connection. Generic JSON clients will not handle these endpoints correctly without raw-stream support.
- Service/task logs are limited to `json-file` and `journald` logging drivers. Other log drivers need explicit test coverage for unsupported behavior.
- Secret and config updates accept broad spec bodies but only labels may change. Implementations and clients must reject accidental changes to name/data/driver fields.
- Secret and config create examples provide `Data` as a base64 string through the spec, while generated models must be checked against actual `SecretSpec` and `ConfigSpec` definitions for type compatibility.
- Distribution inspect returns `401` for both authentication failure and no image found, which can blur auth and not-found handling.
- `/session` is experimental and only enabled with daemon experimental features. It uses h2c upgrade and gRPC callback behavior, so compatibility depends on low-level HTTP support beyond ordinary Swagger JSON handling.

## Test Signals

Useful validation signals for this chunk include:

- Swagger/OpenAPI validation for all operation IDs, `$ref` targets, path parameters, required body/query parameters, response schemas, binary body formats, and mixed `101`/`200` response declarations.
- Generated-client tests for JSON filter encoding on volume, network, node, service, task, secret, and config list/prune endpoints.
- Volume tests covering create with default and custom driver, inspect by name/ID, delete with `force`, in-use `409`, driver missing `404`, prune by positive and negative label filters, and `SpaceReclaimed` accounting.
- Network tests covering list-vs-inspect shape differences, builtin network handling, create with IPAM/IPv6/options/labels, duplicate-name best-effort behavior, connect with `EndpointSettings` and static IPv4/IPv6 addresses, disconnect with `Force`, delete `403` for predefined networks, and prune `until` and label filters.
- Plugin tests covering privilege discovery, pull with accepted privileges and `X-Registry-Auth`, inspect missing plugin `404`, enable timeout, disable force, upgrade with remote/auth/privileges, create from tar, push, set with string array settings, and delete force behavior.
- Node and swarm tests covering non-swarm and already-in-swarm `503` meanings, node list filters, inspect by ID/name, force remove, node update with current and stale versions, swarm init/join address parsing, data-path address behavior, leave force, swarm spec update, token rotation, unlock-key rotation, unlock-key retrieval, and unlock failure modes.
- Service lifecycle tests covering create warnings, duplicate service `409`, non-eligible network `403`, inspect with `insertDefaults`, delete success status, update with required version, stale update versions, `registryAuthFrom`, explicit `X-Registry-Auth`, and `rollback=previous`.
- Service/task log tests covering `stdout`, `stderr`, `tail`, `since`, `timestamps`, `details`, `follow=false` `200` responses, `follow=true` `101` hijack/raw-stream responses, missing resource `404`, non-swarm `503`, and unsupported logging drivers.
- Task tests covering filters by desired state/id/label/name/node/service, task history for repeated service slots, network attachment data, container status fields, and inspect by task ID.
- Secret and config tests covering list filters, create with labels/data, duplicate-name `409`, inspect without exposing secret payload unexpectedly, delete `204`, label-only update with required version, attempted non-label updates, stale versions, and non-swarm `503`.
- Distribution tests covering successful descriptor/platform decoding, multi-platform manifest lists, private registry auth failure, missing image behavior documented as `401`, and registry/server `500` errors.
- Session tests covering daemon experimental feature gating, h2c upgrade headers, `101` response handling, bad parameter `400`, server `500`, and client-daemon callback behavior over the hijacked transport.
