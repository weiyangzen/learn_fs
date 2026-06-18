# sources/cloud-native/moby/api/docs/v1.38.yaml lines 7536-10240

## Scope

This chunk covers Docker Engine API v1.38 Swagger path definitions from the tail of the exec start request schema through the experimental session endpoint. It includes exec resize/inspect, volume lifecycle, network lifecycle, plugin lifecycle, swarm node and cluster operations, service and task APIs, secret and config lifecycle APIs, registry distribution inspection, and `POST /session`.

The source is an OpenAPI/Swagger YAML contract rather than executable daemon code. The behavior researched here is the public HTTP API surface consumed by Docker clients, generated SDKs, API compatibility tests, documentation renderers, and daemon handler routing.

## Purpose

The chunk exposes several major Docker Engine control surfaces:

- Exec session management for TTY resize and process inspection.
- Local daemon resources such as volumes, networks, and plugins.
- Swarm-mode control-plane resources including nodes, swarm membership/configuration, services, tasks, secrets, and configs.
- Registry metadata lookup through distribution inspection.
- Experimental bidirectional session initialization over an upgraded HTTP/2 connection.

Most endpoints are stateful daemon or swarm operations. Volume, network, plugin, swarm, service, secret, and config mutations create, update, remove, or prune persisted resources. Task endpoints are read-only observation APIs over scheduler state. Log and session endpoints are stream-oriented and require clients to handle connection upgrade or Docker raw-stream behavior.

## Important APIs And Types

- The chunk starts inside `POST /exec/{id}/start` body fields, preserving request options `Detach` and `Tty`, then defines `POST /exec/{id}/resize` (`ExecResize`) with required path `id` and query dimensions `h` and `w`.
- `GET /exec/{id}/json` (`ExecInspect`) returns `ExecInspectResponse` with `CanRemove`, `DetachKeys`, `ID`, `Running`, `ExitCode`, `ProcessConfig`, stdio openness flags, `ContainerID`, and host process `Pid`.
- `GET /volumes` (`VolumeList`) returns `VolumeListResponse` with non-null `Volumes` and `Warnings`; filters are JSON-encoded `map[string][]string` entries for `dangling`, `driver`, `label`, and `name`.
- `POST /volumes/create` (`VolumeCreate`) accepts name, driver, driver options, and labels, returning a `Volume`.
- `GET /volumes/{name}` (`VolumeInspect`), `DELETE /volumes/{name}` (`VolumeDelete`), and `POST /volumes/prune` (`VolumePrune`) inspect, remove, and prune volumes. Prune returns `VolumesDeleted` and `SpaceReclaimed`.
- Network APIs include list/inspect/delete/create/connect/disconnect/prune: `NetworkList`, `NetworkInspect`, `NetworkDelete`, `NetworkCreate`, `NetworkConnect`, `NetworkDisconnect`, and `NetworkPrune`.
- `NetworkCreate` accepts required `Name`, best-effort `CheckDuplicate`, `Driver`, `Internal`, `Attachable`, `Ingress`, `IPAM`, `EnableIPv6`, driver `Options`, and `Labels`, returning `NetworkCreateResponse` with `Id` and `Warning`.
- `NetworkConnect` accepts a container ID/name plus `EndpointSettings`; `NetworkDisconnect` accepts a container ID/name and optional `Force`.
- Plugin APIs include list, privilege discovery, pull, inspect, delete, enable, disable, upgrade, create from tar, push, and configure: `PluginList`, `GetPluginPrivileges`, `PluginPull`, `PluginInspect`, `PluginDelete`, `PluginEnable`, `PluginDisable`, `PluginUpgrade`, `PluginCreate`, `PluginPush`, and `PluginSet`.
- Plugin pull/upgrade use registry auth through `X-Registry-Auth` and an accepted privileges body of `PluginPrivilegeItem`-shaped objects (`Name`, `Description`, `Value[]`).
- Node APIs include `NodeList`, `NodeInspect`, `NodeDelete`, and versioned `NodeUpdate` with a `NodeSpec` body.
- Swarm APIs include `SwarmInspect`, `SwarmInit`, `SwarmJoin`, `SwarmLeave`, `SwarmUpdate`, `SwarmUnlockkey`, and `SwarmUnlock`.
- `SwarmInit` accepts listen/advertise/data-path addresses, `ForceNewCluster`, and `SwarmSpec`; `SwarmJoin` requires `ListenAddr`, `RemoteAddrs`, and `JoinToken`.
- `SwarmUpdate` takes required `SwarmSpec` and required `version`, plus token/key rotation booleans: `rotateWorkerToken`, `rotateManagerToken`, and `rotateManagerUnlockKey`.
- Service APIs include list/create/inspect/delete/update/logs: `ServiceList`, `ServiceCreate`, `ServiceInspect`, `ServiceDelete`, `ServiceUpdate`, and `ServiceLogs`.
- `ServiceCreate` and `ServiceUpdate` use `ServiceSpec`, can take `X-Registry-Auth`, and expose warnings for image digest pinning or update work. `ServiceUpdate` requires `version`, supports `registryAuthFrom=spec|previous-spec`, and can rollback with `rollback=previous`.
- Task APIs include `TaskList`, `TaskInspect`, and `TaskLogs`; task list filters include desired state, ID, label, name, node, and service.
- Secret and config APIs mirror each other: list/create/inspect/delete/update through `SecretList`, `SecretCreate`, `SecretInspect`, `SecretDelete`, `SecretUpdate`, `ConfigList`, `ConfigCreate`, `ConfigInspect`, `ConfigDelete`, and `ConfigUpdate`.
- Secret/config updates require `version` and document label-only mutation even though the request body uses the broader `SecretSpec` or `ConfigSpec`.
- `GET /distribution/{name}/json` (`DistributionInspect`) returns required `Descriptor` and `Platforms` fields. Descriptor contains media type, size, digest, and URLs; platform records contain architecture, OS, OS version/features, variant, and features.
- `POST /session` (`Session`) is experimental, produces `application/vnd.docker.raw-stream`, and upgrades the connection to h2c so the daemon can call back into client-exposed gRPC services.

Shared referenced definitions include `ErrorResponse`, `ProcessConfig`, `Volume`, `Network`, `IPAM`, `EndpointSettings`, `Plugin`, `Node`, `NodeSpec`, `Swarm`, `SwarmSpec`, `Service`, `ServiceSpec`, `ServiceUpdateResponse`, `Task`, `Secret`, `SecretSpec`, `Config`, `ConfigSpec`, and `IdResponse`.

## Control Flow

Exec flow is continuation-based. An exec instance is created elsewhere, started by the preceding endpoint whose body tail appears at this chunk boundary, resized only if it was created and started with TTY support, and inspected by ID to observe running state, exit code, stdio flags, process config, container ID, and host PID.

Volume flow is direct daemon state management. Clients list with optional JSON filters, create with driver-specific options, inspect by name/ID, delete with optional force, or prune unused volumes with optional label filters. Delete can fail with `409` when a volume is in use; prune reports both object names and reclaimed bytes.

Network flow combines daemon-level resources and container attachment state. Clients list networks with filters, inspect with optional verbose/scope selectors, create networks using driver/IPAM/options/labels, connect a container with endpoint settings, disconnect it with optional force, delete a network, or prune unused networks. Built-in or swarm-scoped networks are guarded with `403` responses for unsupported mutations.

Plugin flow separates discovery, installation, configuration, lifecycle state, and registry publication. Clients can fetch required privileges before installation, accept privileges in pull/upgrade bodies, pass registry credentials in `X-Registry-Auth`, enable/disable installed plugins, force-disable or force-delete when in use, create a plugin from a tar payload, push to a registry, and configure settings with a string array body such as `DEBUG=1`.

Node and swarm control flow is optimistic and manager-oriented. Node list/inspect/delete expose current swarm membership; node update requires `NodeSpec` plus the object's current `version`. Swarm initialization creates a new cluster and returns the local node ID, join connects to existing managers with a join token, leave removes the local node from the cluster, update requires `SwarmSpec` and version, unlock-key retrieval exposes the manager unlock key, and unlock submits that key to unlock an autolocked manager.

Service flow follows the inspect-modify-update model. Clients list services, create a `ServiceSpec`, inspect by ID/name, delete, update with a required version, and stream logs. Update includes two important branches: registry credentials may be taken from the header, current spec, or previous spec; and `rollback=previous` tells the daemon to ignore the supplied spec and roll back server-side.

Task flow is read-only in this range. The scheduler produces task records, list filters select current or historical tasks, inspect returns one task, and logs stream stdout/stderr for service tasks. Task examples show multiple task records for one service slot, making task history visible instead of replacing prior executions.

Secret and config flows are parallel swarm object lifecycles. Clients list with JSON filters, create with spec/data, inspect by ID, delete, and update labels with required version. The update descriptions explicitly require callers to preserve every non-label field from inspect output.

Log and session flows are stream-sensitive. Service/task logs can return a normal `200` string body or a `101` upgraded raw stream when `follow=true`, and they are documented as supported only for `json-file` or `journald` logging drivers. The session endpoint always centers on an HTTP upgrade to h2c and then transports callback-capable gRPC services over the hijacked connection.

## State And Persistence Behavior

The YAML does not persist state itself, but it describes persistent daemon and swarm resources. Volumes retain names, drivers, labels, options, mountpoints, creation timestamps, and scope. Networks retain IDs, names, drivers, IPAM configuration, labels, options, internal/attachable/ingress flags, and container endpoint attachments.

Plugins are installed daemon artifacts with privileges, enabled/disabled runtime state, configurable settings, registry references, and rootfs/manifest data when created from tar. Force operations are explicitly risky because a plugin may still be used by containers or other resources.

Swarm, node, service, secret, and config objects are versioned swarm-store objects. Required `version` query parameters on node, swarm, service, secret, and config updates implement optimistic concurrency and protect against conflicting writes. `SwarmUpdate` can rotate join tokens and manager unlock keys, changing security-sensitive cluster state without changing ordinary service/task state.

Services are durable desired state. Their specs include task template, image, mounts, hosts, DNS config, secrets, log driver, placement, resources, restart policy, update and rollback config, endpoint ports, labels, and replicated/global mode. The daemon reconciles service desired state into task records.

Tasks are scheduler and runtime state. They expose desired state, current status, container status, node placement, slot, service ID, timestamps, and network attachments. Task records are not mutated directly through this chunk's APIs, but service updates, node state, image pulls, network attachments, and runtime health all affect them.

Secrets and configs persist named objects with IDs, versions, timestamps, labels, and base64 payload data supplied at creation. The examples expose secret/config metadata and specs, while update rules limit changes to labels. That separation matters for secret confidentiality and for avoiding accidental payload replacement.

Distribution inspection is externally stateful. It contacts a registry and returns descriptor/platform metadata for the requested image reference; it does not describe local image persistence.

The session endpoint creates transient connection state rather than a durable daemon object. It depends on an open upgraded connection and experimental daemon mode.

## Dependencies

This chunk depends heavily on schema definitions outside the selected line range, especially the shared model definitions listed above and the global authentication section referenced by plugin and service registry auth parameters.

Runtime dependencies include Docker daemon resource stores, volume drivers, network drivers and IPAM, plugin registry/install machinery, swarmkit raft state, manager quorum, node membership, service scheduling, secret/config storage, container runtime status, log drivers, registry clients, and HTTP connection hijacking/upgrade support.

Several endpoints depend on swarm mode and consistently document `503` when the node is not part of a swarm. Service, task, node, swarm, secret, and config APIs should be treated as swarm control-plane APIs even though they share the same Engine API document as local daemon resources.

Generated clients depend on accurate Swagger interpretation for path parameters, JSON-encoded filter query strings, required body objects, boolean query flags, header auth, binary tar bodies, `allOf` request examples, mixed response status codes, and stream-upgrade responses.

## Integration Points

Operation IDs in this chunk are direct SDK-generation and handler-identification hooks: `ExecResize`, `ExecInspect`, `VolumeList`, `VolumeCreate`, `VolumeInspect`, `VolumeDelete`, `VolumePrune`, `NetworkList`, `NetworkInspect`, `NetworkDelete`, `NetworkCreate`, `NetworkConnect`, `NetworkDisconnect`, `NetworkPrune`, `PluginList`, `GetPluginPrivileges`, `PluginPull`, `PluginInspect`, `PluginDelete`, `PluginEnable`, `PluginDisable`, `PluginUpgrade`, `PluginCreate`, `PluginPush`, `PluginSet`, `NodeList`, `NodeInspect`, `NodeDelete`, `NodeUpdate`, `SwarmInspect`, `SwarmInit`, `SwarmJoin`, `SwarmLeave`, `SwarmUpdate`, `SwarmUnlockkey`, `SwarmUnlock`, `ServiceList`, `ServiceCreate`, `ServiceInspect`, `ServiceDelete`, `ServiceUpdate`, `ServiceLogs`, `TaskList`, `TaskInspect`, `TaskLogs`, `SecretList`, `SecretCreate`, `SecretInspect`, `SecretDelete`, `SecretUpdate`, `ConfigList`, `ConfigCreate`, `ConfigInspect`, `ConfigDelete`, `ConfigUpdate`, `DistributionInspect`, and `Session`.

Volumes integrate with container mounts and volume drivers. Networks integrate with container endpoint settings, built-in bridge/host/none networks, overlay networks, service endpoint specs, swarm ingress/routing mesh, and IPAM.

Plugins integrate with the registry, accepted privilege prompts, volume/network/log authorization surfaces, and plugin configuration. Because plugins can provide infrastructure used by containers, force deletion or disabling is a cross-resource risk.

Swarm nodes and swarm update endpoints integrate with manager quorum, raft object versions, join tokens, manager autolock/unlock, advertise/listen/data-path address selection, overlay networking, and cluster security posture.

Services integrate with registry authentication and digest pinning, image pull credentials, secrets/configs, volumes, networks, log drivers, service rollback/update orchestration, published ports, and task scheduling. Task APIs integrate that desired service state with observed container runtime state.

Secret and config APIs integrate back into `ServiceSpec` task templates, where services reference them for mounted runtime data. Their label-only update semantics require client tooling to read existing state before writing.

Distribution inspection integrates Engine API clients with Docker registry manifest metadata and platform selection. Session integrates BuildKit-like or advanced client-daemon interactions by letting the daemon call back over client-provided gRPC services on the upgraded transport.

## Risks And Edge Cases

- The chunk begins mid-endpoint, so research consumers must merge it with the previous chunk for the full `ExecStart` contract. Only the tail fields `Detach` and `Tty` are visible here.
- `ExecResize` only works for TTY exec sessions; clients need to preserve whether `Tty` was set during exec creation/start.
- JSON filter query parameters are typed as strings. Generated clients may not provide typed helpers, and daemon handlers must robustly parse invalid JSON or unsupported filter names.
- `VolumeDelete force=true`, plugin force delete/disable, network disconnect force, node delete force, and swarm leave force can remove or detach resources that are still in use. Automation should not default force flags to true.
- `VolumeDelete` returns `409` for in-use volumes, while other delete endpoints use different success and error status codes. Generic delete code cannot assume a single success status or conflict model.
- `NetworkCreate.CheckDuplicate` is explicitly best-effort because networks are keyed by random ID, not name. Name collision checks are advisory rather than a hard uniqueness guarantee.
- Built-in networks and swarm-scoped networks have `403` guardrails on unsupported operations. Clients should distinguish unsupported resource class from missing resource.
- Plugin pull/upgrade require privilege acceptance and may require registry auth. The privilege body is not explicitly marked required in the schema, so real daemon validation is an important compatibility check.
- Plugin delete can return a `Plugin` object on `200`, unlike many delete endpoints that return no body.
- Swarm, node, service, secret, and config updates require current `version`; stale versions and missing versions are expected failure modes. The contract often documents `400` but not a dedicated conflict code.
- `SwarmInit`/`SwarmJoin` address fields accept either IP:port or interface:port forms, with defaults inferred from listen/advertise addresses. Address auto-detection and interface parsing are high-risk platform-dependent behavior.
- `SwarmUpdate` rotation flags are independent of the required full `SwarmSpec`; clients rotating only a token must still avoid dropping unrelated spec fields.
- `ServiceUpdate rollback=previous` says the submitted spec is ignored. Client libraries that always require a valid replacement spec may block legitimate rollback workflows.
- `registryAuthFrom` documents valid values but is plain string, not an enum. Invalid values are a daemon validation concern and a generated-client ergonomics gap.
- Service/task logs can return either `101` upgraded raw streams or `200` string bodies. HTTP clients without hijack/upgrade support will fail in follow mode.
- Log endpoints only work for `json-file` or `journald`, so daemon tests must cover unsupported logging drivers and the documented `404`/`500`/`503` cases.
- Secret/config update bodies are broad specs but only labels may change. Partial specs or accidental name/data mutation should be rejected or carefully preserved by clients.
- Distribution inspection uses `401` for both authentication failure and no image found, blurring auth and not-found semantics for callers.
- `Session` is experimental and requires daemon experimental features. It also says "gPRC" in the prose, likely meaning gRPC; documentation tooling should preserve or correct this carefully depending on policy.

## Test Signals

Useful validation signals for this chunk include:

- Swagger/OpenAPI validation that every `$ref` target resolves and every operation has the expected path, method, tag, operation ID, parameters, response statuses, consumes/produces values, and schema title.
- Generated-client tests for JSON filter encoding on volume, network, node, service, task, secret, and config list/prune endpoints.
- Exec tests covering resize success for TTY exec sessions, resize failure for non-TTY sessions or bad dimensions, inspect of running and exited exec processes, exit code propagation, stdio flags, and missing exec IDs.
- Volume tests covering create with generated and explicit names, driver options, labels, list filters, inspect by name/ID, delete success, delete in-use `409`, force behavior, prune label filters, warnings, and reclaimed-byte reporting.
- Network tests covering list filters, inspect `verbose` and `scope`, create with IPAM/IPv6/options/labels, duplicate-name best effort, connect with endpoint IPAM config, disconnect force, deletion of built-in networks returning `403`, swarm-scoped connect/disconnect guardrails, prune `until` and label filters.
- Plugin tests covering privilege discovery, pull/upgrade with accepted privileges and registry auth, inspect missing plugin `404`, enable timeout, disable force, delete force returning plugin data, create from tar content type, push, and set configuration.
- Node/swarm tests covering non-swarm `503`, node list filters, node update with required version, forced node removal, swarm init/join address parsing, join token validation, leave force, swarm update token/key rotation, unlock key retrieval, and manager unlock.
- Service lifecycle tests covering create warnings, duplicate-name `409`, ineligible-network `403`, inspect with `insertDefaults`, delete `200`, update with required version, stale versions, `X-Registry-Auth`, `registryAuthFrom`, and `rollback=previous`.
- Service/task log tests covering `stdout`, `stderr`, `details`, `since`, `tail`, `timestamps`, `follow=false` `200`, `follow=true` `101`, raw-stream framing, missing resources, unsupported log drivers, and non-swarm `503`.
- Task tests covering filters for desired state, ID, label, name, node, and service, plus scheduler history where running and shutdown tasks coexist for a service slot.
- Secret/config tests covering list filters, create with labels/data, duplicate-name `409`, inspect metadata shape, delete `204`, label-only update with required version, attempted data/name update rejection, stale version handling, and non-swarm `503`.
- Distribution tests covering descriptor/platform response decoding, multi-platform manifest lists, private registry auth, missing image behavior documented as `401`, malformed image names, and registry/server errors.
- Session tests covering experimental feature gating, h2c upgrade headers, `101` response handling, callback transport establishment, bad upgrade requests returning `400`, and connection cleanup.
