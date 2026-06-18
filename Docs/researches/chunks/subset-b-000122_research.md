# sources/cloud-native/moby/api/docs/v1.36.yaml lines 7570-10137

## Scope

This chunk is a Docker Engine API v1.36 Swagger/OpenAPI path slice. It starts inside the `GET /volumes` successful response schema and then covers volume creation/inspection/deletion/pruning, network lifecycle, plugin lifecycle, swarm node and cluster operations, service lifecycle and logs, task listing/inspection/logs, swarm secrets, swarm configs, registry distribution inspection, and the experimental interactive `/session` endpoint.

The source is API contract documentation rather than executable implementation. It defines route paths, HTTP methods, `operationId` names, request parameters, body schemas, response schemas, examples, media types, status codes, and tags consumed by API documentation, generated clients, SDK compatibility layers, and daemon route conformance tests.

## Purpose

The endpoints in this range expose Docker daemon management surfaces for persistent resources and swarm orchestration:

- volumes and networks cover local/container data-plane resources, including list filters, create inputs, inspect/delete operations, connect/disconnect, and prune operations;
- plugins cover installation from registries or tar contexts, privilege acceptance, enable/disable, upgrade, push, remove, inspect, list, and runtime configuration;
- nodes, swarm, services, tasks, secrets, and configs expose swarm-mode control-plane state and writes, with versioned updates to protect against conflicting manager-state writes;
- service/task log endpoints provide swarm workload observability through either normal response bodies or hijacked raw streams;
- distribution inspection contacts image registries for descriptor/platform metadata;
- the experimental session endpoint upgrades a connection to h2c so the daemon can call back into client-provided services.

## Important APIs And Types

- Volume APIs: the chunk includes the tail of `VolumeList`, `POST /volumes/create` (`VolumeCreate`), `GET /volumes/{name}` (`VolumeInspect`), `DELETE /volumes/{name}` (`VolumeDelete`), and `POST /volumes/prune` (`VolumePrune`). These use `#/definitions/Volume`, `VolumePruneResponse`, and `ErrorResponse`.
- Network APIs: `NetworkList`, `NetworkInspect`, `NetworkDelete`, `NetworkCreate`, `NetworkConnect`, `NetworkDisconnect`, and `NetworkPrune` operate on `#/definitions/Network`, `IPAM`, `EndpointSettings`, and prune/create response objects.
- Plugin APIs: `PluginList`, `GetPluginPrivileges`, `PluginPull`, `PluginInspect`, `PluginDelete`, `PluginEnable`, `PluginDisable`, `PluginUpgrade`, `PluginCreate`, `PluginPush`, and `PluginSet` use `#/definitions/Plugin` plus inline privilege objects with `Name`, `Description`, and string-array `Value`.
- Node APIs: `NodeList`, `NodeInspect`, `NodeDelete`, and `NodeUpdate` operate on `#/definitions/Node` and `NodeSpec`; update requires a `version` query integer.
- Swarm APIs: `SwarmInspect`, `SwarmInit`, `SwarmJoin`, `SwarmLeave`, `SwarmUpdate`, `SwarmUnlockkey`, and `SwarmUnlock` operate on `#/definitions/Swarm` and `SwarmSpec`. Init/join request bodies carry listen, advertise, data-path, token, manager address, and cluster-spec fields.
- Service APIs: `ServiceList`, `ServiceCreate`, `ServiceInspect`, `ServiceDelete`, `ServiceUpdate`, and `ServiceLogs` operate on `#/definitions/Service`, `ServiceSpec`, `ServiceUpdateResponse`, and registry-auth headers.
- Task APIs: `TaskList`, `TaskInspect`, and `TaskLogs` operate on `#/definitions/Task`; task examples expose `Version`, `Spec`, `ServiceID`, `Slot`, `NodeID`, `Status`, `DesiredState`, and network attachments.
- Secret APIs: `SecretList`, `SecretCreate`, `SecretInspect`, `SecretDelete`, and `SecretUpdate` use `#/definitions/Secret`, `SecretSpec`, and `IdResponse`. Update accepts a full spec but documents labels as the only mutable field.
- Config APIs: `ConfigList`, `ConfigCreate`, `ConfigInspect`, `ConfigDelete`, and `ConfigUpdate` mirror secret lifecycle semantics using `#/definitions/Config`, `ConfigSpec`, and `IdResponse`.
- Distribution/session APIs: `DistributionInspect` returns an inline `DistributionInspectResponse` with descriptor and platform arrays; `Session` returns `101` raw-stream upgrade behavior and is tagged experimental.

## Control Flow

Volume and network list endpoints accept a JSON-encoded `filters` query string (`map[string][]string`) and return typed collections. Volume create takes a JSON body with `Name`, `Driver`, `DriverOpts`, and `Labels`; network create takes a required `Name` plus duplicate checking, driver, IPAM, IPv6, internal, attachable, ingress, options, and labels. Inspect/delete routes are direct path lookups. Prune routes accept filter strings and return deleted resource names plus reclaimed space for volumes or deleted networks for networks.

Network connect/disconnect are body-driven mutations against a path `id`. Connect requires a target container ID/name and can include `EndpointConfig` for static IPAM settings. Disconnect requires a target container and optional `Force`. Both reject swarm-scoped network operations with `403`.

Plugin flows split registry and local-tar installation. A client can query required privileges for a remote plugin, accept those privileges in the pull/upgrade body, supply `X-Registry-Auth`, then enable or configure the installed plugin. Remove can force disable first. Create consumes `application/x-tar`; set consumes a JSON string array such as `DEBUG=1`; push sends an installed plugin to a registry.

Swarm control-plane flows are stateful. A daemon can initialize a new swarm, join an existing swarm with manager addresses and a join token, inspect/update the cluster, leave it, retrieve the manager unlock key, or unlock a locked manager. Node, service, secret, and config updates all use version query parameters to avoid stale writes against raft-backed objects.

Service create/update consume `ServiceSpec` bodies. Create can include a registry auth header for private image pulls and returns a service ID plus optional warning, such as inability to pin an image digest. Update requires `version`, supports `registryAuthFrom` (`spec` or `previous-spec`), can request rollback to `previous`, and can receive `X-Registry-Auth`.

Service/task logs share the same flow: identify the service or task by path `id`, choose `stdout` and/or `stderr`, optionally request `details`, `timestamps`, `since`, and `tail`, and set `follow=true` to receive a `101` upgraded raw stream. Without follow, success is modeled as a `200` string body.

Secrets and configs use list/create/inspect/delete/update flows. Create returns an ID and can fail with name-conflict `409`. Update requires the current object version; descriptions state that only labels are currently mutable and all other fields must remain unchanged from inspect output.

## State And Persistence Behavior

The YAML does not persist state itself, but it describes operations that mutate Docker daemon state:

- volume create/delete/prune change local volume metadata and storage managed by volume drivers; `VolumePrune` reports reclaimed disk space;
- network create/delete/connect/disconnect/prune change libnetwork state, endpoint attachments, driver options, IPAM allocation, and possibly swarm overlay network membership;
- plugin pull/create/upgrade/delete/enable/disable/set/push change plugin installation metadata, rootfs/manifest content, enabled state, accepted privileges, registry state, and plugin configuration;
- node update/delete, swarm init/join/leave/update/unlock, service create/update/delete, secret/config create/update/delete all act on swarm manager state and can be unavailable outside swarm mode;
- services create tasks, tasks report desired/runtime state, and logs read task container output through supported logging drivers;
- distribution inspect does not create local image state in this contract; it contacts a registry and returns descriptor/platform metadata;
- session hijacking establishes a long-lived upgraded connection for daemon-to-client callbacks.

Version parameters on node, swarm, service, secret, and config updates are the main concurrency signal. They require clients to inspect or otherwise know current raft object versions before issuing writes.

## Dependencies

This chunk depends on shared definitions elsewhere in `v1.36.yaml`, including `Volume`, `Network`, `IPAM`, `EndpointSettings`, `Plugin`, `Node`, `NodeSpec`, `Swarm`, `SwarmSpec`, `Service`, `ServiceSpec`, `ServiceUpdateResponse`, `Task`, `Secret`, `SecretSpec`, `Config`, `ConfigSpec`, `IdResponse`, and `ErrorResponse`.

Runtime dependencies implied by the contract include volume drivers, network drivers and IPAM plugins, plugin registries and tar plugin manifests, registry authentication via `X-Registry-Auth`, swarm mode and its raft object store, Docker raw-stream framing and HTTP hijacking, `json-file` or `journald` logging drivers for service/task logs, image registries for distribution inspect, and experimental daemon support for `/session`.

## Integration Points

The `operationId` values are stable integration names for generated Docker clients and documentation anchors. The tags group endpoints into `Volume`, `Network`, `Plugin`, `Node`, `Swarm`, `Service`, `Task`, `Secret`, `Config`, `Distribution`, and `Session (experimental)`.

Network endpoints integrate with container lifecycle APIs through `Container` IDs/names and `EndpointSettings`. Service specs integrate with volumes, networks, secrets, configs, logging drivers, registry credentials, and update/rollback policy. Task endpoints provide the bridge from service-level desired state to node/container runtime status. Secrets and configs integrate with service task templates while enforcing limited post-create mutability.

Plugin endpoints integrate with registry authentication, privilege prompts, filesystem tar contexts, daemon plugin management, and registry push/pull behavior. Distribution inspect integrates with registry manifest metadata and platform resolution. Session integrates with client-side gRPC services exposed over an upgraded h2c transport.

## Risks And Edge Cases

- The chunk starts mid-`VolumeList`, so the route header and early response fields are outside this slice; this document covers the visible response tail and parameters.
- `filters` parameters are JSON-encoded strings, not structured query objects. Bad escaping or wrong `map[string][]string` shape can silently change list/prune behavior.
- Network `CheckDuplicate` is explicitly best-effort because networks are keyed by random ID, so clients cannot rely on it as a uniqueness guarantee.
- Built-in/predefined networks can reject delete/create-like operations with `403`, and swarm-scoped networks reject connect/disconnect with `403`.
- Plugin privilege acceptance is security-sensitive; pull/upgrade bodies encode host networking, mounts, and devices that can materially change daemon attack surface.
- Plugin remove `force`, plugin disable `force`, node delete `force`, volume delete `force`, and swarm leave `force` can break running workloads or cluster availability.
- Swarm APIs frequently return `503` when the node is not part of a swarm; clients should distinguish deployment state from missing resources.
- Versioned updates for nodes, swarm, services, secrets, and configs will reject stale writes. Partial specs are risky where the API expects the full current spec.
- Secret/config update bodies use full specs but only labels are mutable, so changing payload data or other fields should be treated as invalid.
- `ServiceCreate` can return success with a warning when image digest pinning fails, which clients may need to surface as degraded reproducibility.
- Log endpoints switch from normal response handling to connection hijacking on `follow=true`; generated clients that model only JSON/string responses may mishandle `101`.
- Service/task logs only work with `json-file` or `journald` drivers per the description.
- `tail` is a string because it accepts either an integer or `all`; numeric-only client typing would be incompatible.
- The task logs section in this range has no visible `tags: ["Task"]` line, unlike neighboring endpoint groups, which can affect generated grouping if absent in the full file.
- `/session` is experimental and gated by daemon experimental features; the description also says specs may change in future API versions.

## Test Signals

Useful validation for this API contract includes:

- OpenAPI linting for path parameters, unique `operationId` values, resolvable `$ref`s, valid media types, and consistent response schemas.
- Client generation checks that preserve JSON-filter query parameters as strings, `tail` as string, `X-Registry-Auth` as a header, binary tar bodies for plugin create, and `101` raw-stream responses for logs/session.
- Volume lifecycle tests for list filters, create defaults, inspect missing `404`, delete in-use `409`, forced delete semantics, prune label filters, and reclaimed-space reporting.
- Network tests for list filters, create IPAM/IPv6/options/labels, inspect verbose/scope parameters, built-in network `403`, connect/disconnect endpoint config and force behavior, swarm-scoped operation rejection, and prune `until`/label filters.
- Plugin tests for privilege discovery, pull with accepted privileges and registry auth, inspect missing `404`, enable timeout, disable force, upgrade with new privileges, create from tar, set options, push, and forced removal.
- Swarm tests outside and inside swarm mode, covering init/join/leave, data-path address handling, update token rotation, unlock-key retrieval, unlock body validation, and expected `503` responses when not in swarm mode.
- Node/service/task tests for filters, inspect missing `404`, required update versions, stale-version rejection, service create conflicts, service update rollback behavior, registry auth sourcing, task status/network attachment shapes, and log parameter behavior.
- Secret/config lifecycle tests for create, duplicate-name `409`, list filters, inspect, label-only update with current version, stale-version rejection, immutable-field rejection, delete `204`, and outside-swarm `503`.
- Distribution inspect tests for successful descriptor/platform shape, registry-auth/no-image `401`, and server-error `500`.
- Session tests should assert experimental gating, bad-parameter `400`, successful h2c upgrade `101`, and correct raw-stream handling.
