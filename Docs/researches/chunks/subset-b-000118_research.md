# sources/cloud-native/moby/api/docs/v1.34.yaml lines 7563-10059

## Scope

This chunk covers Docker Engine API v1.34 Swagger path definitions from the tail of `POST /volumes/create` through the experimental `POST /session` endpoint. The source is an OpenAPI/Swagger YAML API contract, not daemon implementation code. Its consumers are generated Docker clients, API documentation, compatibility tests, and daemon route/schema validation.

The line range starts inside the `VolumeCreate` request-body schema, so the beginning of `POST /volumes/create` is outside this chunk. Within this chunk, the documented path surface includes volume inspect/delete/prune; network list/inspect/delete/create/connect/disconnect/prune; full plugin lifecycle; node and swarm control-plane operations; service and task APIs; secret and config lifecycle APIs; distribution inspection; and the experimental session hijack endpoint.

## Purpose

The chunk documents stateful Docker Engine APIs for storage, networking, plugins, swarm orchestration, secure swarm objects, registry metadata, and client-daemon callback sessions.

Volume and network endpoints expose local daemon resources and driver-backed objects. Plugin endpoints install, enable, disable, upgrade, push, configure, and remove plugin packages, including privilege acceptance and registry authentication. Node, swarm, service, task, secret, and config endpoints are swarm-mode APIs backed by manager state and consistently document `503` when the daemon is not part of a swarm. `DistributionInspect` reaches out to a registry for descriptor/platform data. `Session` establishes an experimental upgraded HTTP/2 transport so the daemon can call back to client-side services.

## Important APIs And Types

- `VolumeCreate` request fields in this chunk include `Name`, `Driver`, `DriverOpts`, and `Labels`; the response is a `Volume`. `VolumeInspect`, `VolumeDelete`, and `VolumePrune` cover lookup, removal, and label-filtered pruning.
- `NetworkList`, `NetworkInspect`, `NetworkDelete`, `NetworkCreate`, `NetworkConnect`, `NetworkDisconnect`, and `NetworkPrune` operate on `Network`, `IPAM`, and `EndpointSettings` definitions. Network creation accepts `Name`, duplicate checking, driver, `Internal`, `Attachable`, `Ingress`, `EnableIPv6`, IPAM, options, and labels.
- Plugin operations include `PluginList`, `GetPluginPrivileges`, `PluginPull`, `PluginInspect`, `PluginDelete`, `PluginEnable`, `PluginDisable`, `PluginUpgrade`, `PluginCreate`, `PluginPush`, and `PluginSet`. Pull/upgrade accept privilege arrays and `X-Registry-Auth`; create consumes an `application/x-tar` plugin rootfs/manifest archive.
- Node operations include `NodeList`, `NodeInspect`, `NodeDelete`, and `NodeUpdate`. `NodeUpdate` takes a `NodeSpec` body and a required integer `version` query parameter.
- Swarm operations include `SwarmInspect`, `SwarmInit`, `SwarmJoin`, `SwarmLeave`, `SwarmUpdate`, `SwarmUnlockkey`, and `SwarmUnlock`. Init/join handle listen, advertise, and data-path addresses; updates take `SwarmSpec`, required `version`, and token/unlock-key rotation flags.
- Service operations include `ServiceList`, `ServiceCreate`, `ServiceInspect`, `ServiceDelete`, `ServiceUpdate`, and `ServiceLogs`. Create/update consume `ServiceSpec`, use `X-Registry-Auth`, and update adds required `version`, `registryAuthFrom`, and `rollback` query controls.
- Task operations include `TaskList`, `TaskInspect`, and `TaskLogs`, returning `Task` records and task log streams.
- Secret and config operations are parallel: list, create, inspect, delete, and update for `Secret`/`SecretSpec` and `Config`/`ConfigSpec`. Updates are versioned and label-only despite accepting full spec bodies.
- `DistributionInspect` returns an object named `DistributionInspect` with required `Descriptor` and `Platforms` sections.
- `Session` returns a `101` hijacked raw stream for an experimental h2c upgrade.

Shared `$ref` dependencies include `Volume`, `Network`, `IPAM`, `EndpointSettings`, `Plugin`, `Node`, `NodeSpec`, `Swarm`, `SwarmSpec`, `Service`, `ServiceSpec`, `ServiceUpdateResponse`, `Task`, `Secret`, `SecretSpec`, `Config`, `ConfigSpec`, and `ErrorResponse`.

## Control Flow

Volume flow is conventional CRUD plus pruning: clients create a driver-backed volume, inspect by name or ID, delete with optional `force`, and prune unused volumes through JSON-encoded label filters. Delete distinguishes not found, driver missing, and in-use conflicts.

Network flow is also lifecycle-oriented but with attachment operations. Clients list with JSON filters, inspect by ID/name with optional verbose/scope filtering, create a named driver-backed network with IPAM and behavior flags, connect or disconnect containers by sending container IDs/names and endpoint settings, delete networks, or prune unused networks by `until` and label filters. Predefined networks reject unsupported operations with `403`.

Plugin flow combines registry, local package, lifecycle, and configuration paths. A client can ask for required privileges before install, pull a remote plugin after accepting privileges, inspect installed metadata, enable with a timeout, disable optionally with force, upgrade from another remote with accepted privileges and registry auth, create from a tar archive, push to a registry, set string configuration values, and delete with optional force disable.

Swarm/node/service flows follow an inspect-modify-update pattern with optimistic concurrency. Node, swarm, service, secret, and config updates require the current object version in the query string. Service update has two notable branches: registry credentials can come from the header or from `registryAuthFrom=spec|previous-spec`, and `rollback=previous` causes the server to ignore the submitted spec and roll back to the previous service spec.

Log flow for services and tasks mirrors Docker's attach/raw-stream model. Without follow, the API may return a `200` string body. With `follow=true`, it can return `101`, upgrade the connection, and stream multiplexed raw output. Both log endpoints document support only for `json-file` and `journald` logging drivers.

Secret and config flows are intentionally similar. Create stores a named object with labels and base64 data, inspect/list expose object metadata/spec, delete returns `204`, and update requires a version while allowing only label changes. The descriptions instruct clients to preserve all non-label fields from inspect responses.

Distribution flow resolves an image name or ID against a registry, then returns descriptor and platform metadata. Session flow performs an HTTP upgrade to h2c and hands the connection to a client/server callback transport.

## State And Persistence Behavior

The YAML itself persists no state, but it defines durable daemon and swarm resources. Volumes persist through volume drivers and expose driver options, labels, mountpoints, and reclaimed disk space on prune. Networks persist local or swarm/global network state, including driver, IPAM, bridge/overlay options, labels, container attachments, and pruning eligibility.

Plugin state spans installed package metadata, enabled/disabled lifecycle state, accepted privileges, plugin rootfs/manifest contents, registry identity, and runtime configuration. Force removal or disable can affect containers using a plugin.

Swarm, node, service, secret, and config objects are versioned manager-state resources. Required `version` parameters are concurrency controls for raft-backed objects. Services persist desired state through `ServiceSpec`; tasks are scheduler-produced execution records showing current/historical status, desired state, container IDs/PIDs, and network attachments. Task APIs in this chunk are read-only.

Secrets and configs are persisted swarm objects with IDs, object versions, timestamps, names, labels, drivers for secrets, and base64 data at creation. Inspect/list examples expose metadata and spec fields, not secret payload contents, which is an important confidentiality contract.

`DistributionInspect` depends on external registry state rather than local object persistence. `Session` creates a live upgraded connection rather than a durable object.

## Dependencies

Runtime behavior depends on Docker Engine route handlers, storage and network drivers, plugin manager/registry integration, swarmkit manager state, raft object versions, scheduler reconciliation, logging backends, and Docker's HTTP connection hijack/raw-stream support.

The contract depends on schema definitions earlier in `v1.34.yaml` for the resource models and shared `ErrorResponse`. Generated clients depend on correct handling of JSON-encoded filter strings, path parameters accepting IDs or names, required body schemas, required update versions, boolean query flags, header auth parameters, tar and raw-stream content types, and mixed `200`/`101` response modes.

## Integration Points

Operation IDs are the main SDK and documentation hooks for this chunk: `VolumeInspect`, `VolumeDelete`, `VolumePrune`, `NetworkList`, `NetworkInspect`, `NetworkDelete`, `NetworkCreate`, `NetworkConnect`, `NetworkDisconnect`, `NetworkPrune`, all `Plugin*` operations plus `GetPluginPrivileges`, `Node*`, `Swarm*`, `Service*`, `Task*`, `Secret*`, `Config*`, `DistributionInspect`, and `Session`.

Network APIs integrate with container endpoints through `EndpointSettings`, static IPv4/IPv6 IPAM assignment, swarm/global scopes, ingress routing-mesh semantics, and driver plugins. Service APIs integrate with registry auth and image digest pinning, update/rollback orchestration, secrets/configs, network endpoint allocation, task scheduling, and logs. Task APIs expose the result of service reconciliation and node/container runtime state.

Secret and config APIs integrate with service specs because tasks mount referenced objects. Distribution inspection integrates Docker Engine with registry manifest/descriptor metadata and platform selection. Session integrates the Engine API with BuildKit-style or other advanced client callback capabilities over h2c.

## Risks And Edge Cases

- The chunk begins inside `VolumeCreate`; chunk-level readers need adjacent lines to see the path/method header and `201` response, while this file still captures the request fields.
- JSON filter parameters are typed as strings, and only some include `format: json`. Clients must JSON-encode maps correctly and daemon handlers must validate malformed filters.
- `NetworkCreate.CheckDuplicate` is explicitly best-effort because networks are keyed by random ID, not name. Automation should not treat it as a uniqueness guarantee.
- Network delete rejects predefined networks with `403`; connect/disconnect reject swarm-scoped networks with `403`.
- Plugin force disable/delete can break active containers, and plugin install/upgrade depend on privilege acceptance plus optional registry authentication.
- Swarm endpoints distinguish "not part of a swarm" from other failures with `503`; clients must not collapse this into generic server failure.
- `SwarmLeave force=true` can break cluster availability, especially for the last manager.
- Versioned updates can fail or overwrite user intent if clients submit stale specs or omit fields. `SwarmUpdate` token rotation still requires a full `SwarmSpec`.
- `ServiceUpdate rollback=previous` ignores the submitted spec, which generated clients or validators can mishandle if they always require a meaningful body.
- `registryAuthFrom` documents valid string values but is not modeled as an enum in this schema.
- Service/task logs can return either hijacked `101` raw streams or `200` string bodies and only work for selected logging drivers.
- Secret/config updates accept broad spec bodies but only labels may change; implementations need validation against name/data mutation.
- Delete success codes vary by resource (`204` for volumes, secrets, configs; `200` for plugins, nodes, services, networks in this chunk), so generic clients should not assume one status.
- `DistributionInspect` uses `401` for both authentication failure and no image found, which can blur auth and missing-resource handling.
- `Session` is experimental and gated by daemon experimental mode; the description says the specification may change.

## Test Signals

Useful validation for this chunk includes Swagger/OpenAPI checks for `$ref` targets, operation ID uniqueness, required path/query/body parameters, response status codes, content types, and examples.

Contract and integration tests should cover volume create fields, inspect/delete/prune filters, in-use volume delete `409`, network list filters, network create with IPAM/IPv6/ingress/attachable options, container connect/disconnect endpoint config, predefined or swarm-scoped network `403`, and network prune `until`/label filters.

Plugin tests should exercise privileges lookup, pull/upgrade with accepted privileges and `X-Registry-Auth`, create from tar, enable timeout, disable/delete force behavior, push, set configuration arrays, missing plugin `404`, and registry/server errors.

Swarm tests should cover init/join address parsing and required join fields, non-swarm and already-in-swarm `503` cases, leave force semantics, update version requirements, token and unlock-key rotation, unlock-key retrieval, and manager unlock with valid/invalid keys.

Service/task tests should cover service create warnings, duplicate names, network eligibility, inspect defaults, versioned update, rollback, registry credential source selection, list filters, task history and desired-state filters, and service/task log parameters including `follow=true` `101` hijack behavior.

Secret/config tests should cover list filters, create with labels/data, duplicate names, inspect without leaking secret payload data, delete `204`, label-only versioned update, attempted immutable-field changes, stale versions, and non-swarm `503`.

Distribution/session tests should cover descriptor/platform decoding, multi-platform manifests, private registry authentication, missing image behavior documented as `401`, registry/server failures, experimental-mode gating for `/session`, h2c upgrade headers, `101` raw-stream handling, and malformed session requests.
