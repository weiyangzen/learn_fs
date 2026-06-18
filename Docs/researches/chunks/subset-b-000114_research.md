# sources/cloud-native/moby/api/docs/v1.32.yaml lines 7575-10011

## Scope

This chunk is an OpenAPI/Swagger 2.0 slice of Docker Engine API v1.32. It starts at the tail of the volume delete endpoint, then covers volume pruning, network lifecycle operations, plugin lifecycle operations, swarm nodes, swarm cluster control, services, tasks, secrets, configs, registry distribution inspection, and the experimental session endpoint.

The file is API contract documentation rather than executable implementation. It defines paths, methods, request parameters, response schemas, examples, media types, operation IDs, tags, and status codes consumed by Docker API documentation, SDK/client generators, daemon route conformance tests, and compatibility checks for API v1.32.

## Purpose

The endpoints in this range expose several major Docker Engine management surfaces:

- Volume cleanup and the tail of volume deletion, including force removal and reclaim reporting.
- Network listing, inspect, create, delete, connect, disconnect, and prune operations.
- Plugin discovery, privilege negotiation, install, inspect, remove, enable, disable, upgrade, create from tar, push, and configuration.
- Swarm mode state and control, including nodes, swarm init/join/leave/update/unlock, services, tasks, logs, secrets, and configs.
- Registry-facing image distribution inspection for digest and platform metadata.
- Experimental interactive sessions that upgrade an HTTP connection to h2c for daemon callbacks to the client.

Together these paths describe how Docker clients manage persistent resources, networking, extension points, swarm orchestration state, sensitive/config data, registry metadata, and advanced client-daemon sessions.

## Important APIs And Types

- Tail of `VolumeDelete`: path parameter `name`, optional query `force`, and errors for missing volumes, in-use volumes, and server failures.
- `POST /volumes/prune` with operation ID `VolumePrune`: accepts JSON-encoded filter string for label include/exclude rules and returns `VolumesDeleted` plus `SpaceReclaimed`.
- `GET /networks` / `GET /networks/{id}` / `DELETE /networks/{id}`: list, inspect, and remove networks using `#/definitions/Network` and `#/definitions/ErrorResponse`. List filters include driver, id, label, name, scope, and type.
- `POST /networks/create`: accepts a required `Name` plus `CheckDuplicate`, `Driver`, `Internal`, `Attachable`, `Ingress`, `IPAM`, `EnableIPv6`, driver `Options`, and `Labels`; returns created `Id` and `Warning`.
- `POST /networks/{id}/connect` and `POST /networks/{id}/disconnect`: attach or detach a container from a network using `Container`, optional `EndpointConfig` (`#/definitions/EndpointSettings`), and disconnect `Force`.
- `POST /networks/prune`: deletes unused networks with `until` and label filters and returns `NetworksDeleted`.
- Plugin operations: `PluginList`, `GetPluginPrivileges`, `PluginPull`, `PluginInspect`, `PluginDelete`, `PluginEnable`, `PluginDisable`, `PluginUpgrade`, `PluginCreate`, `PluginPush`, and `PluginSet`. They reference `#/definitions/Plugin`, registry auth headers, accepted privilege arrays, tar plugin contexts, and string setting arrays.
- Node operations: `NodeList`, `NodeInspect`, `NodeDelete`, and `NodeUpdate`, with `#/definitions/Node`, `#/definitions/NodeSpec`, swarm `503` behavior, filters by id/label/membership/name/role, and versioned updates.
- Swarm operations: `SwarmInspect`, `SwarmInit`, `SwarmJoin`, `SwarmLeave`, `SwarmUpdate`, `SwarmUnlockkey`, and `SwarmUnlock`, with `#/definitions/Swarm`, `#/definitions/SwarmSpec`, join token and address payloads, token/key rotation flags, and manager unlock data.
- Service operations: `ServiceList`, `ServiceCreate`, `ServiceInspect`, `ServiceDelete`, `ServiceUpdate`, and `ServiceLogs`, with `#/definitions/Service`, `#/definitions/ServiceSpec`, and `#/definitions/ServiceUpdateResponse`.
- Task operations: `TaskList`, `TaskInspect`, and `TaskLogs`, with `#/definitions/Task` examples showing task versions, service/node links, desired state, runtime status, container status, and network attachments.
- Secret operations: `SecretList`, `SecretCreate`, `SecretInspect`, `SecretDelete`, and `SecretUpdate`, using `#/definitions/Secret` and `#/definitions/SecretSpec`.
- Config operations: `ConfigList`, `ConfigCreate`, `ConfigInspect`, `ConfigDelete`, and `ConfigUpdate`, using `#/definitions/Config` and `#/definitions/ConfigSpec`.
- `GET /distribution/{name}/json` with operation ID `DistributionInspect`: returns a `DistributionInspect` object containing a descriptor (`MediaType`, `Size`, `Digest`, `URLs`) and platform entries (`Architecture`, `OS`, `OSVersion`, `OSFeatures`, `Variant`, `Features`).
- `POST /session` with operation ID `Session`: experimental raw-stream endpoint that upgrades the connection to h2c so the daemon can call client-exposed gRPC services.

## Control Flow

Most resource operations follow direct REST control flow: list endpoints accept optional `filters` as a JSON-encoded `map[string][]string`, inspect/delete endpoints identify an object by path ID or name, create endpoints accept JSON bodies, and update endpoints use path identity plus a request body and required object version where optimistic concurrency is needed.

Network creation validates and persists a network configuration, then returns the daemon-generated ID and an optional warning. Network connect identifies a network by path and a container by request body, then applies endpoint/IPAM settings. Disconnect reverses that attachment and can force removal. Network and volume prune operations select unused resources through filter strings and return deleted names/IDs, with volume prune also reporting reclaimed bytes.

Plugin install and upgrade have a two-step security shape. Clients can first call `GET /plugins/privileges` for a remote plugin to learn required permissions, then pass accepted permissions in the body of `POST /plugins/pull` or `POST /plugins/{name}/upgrade`. Registry credentials are supplied through `X-Registry-Auth`. Created plugins can also be loaded from an `application/x-tar` body, enabled or disabled by name, configured by posting string settings, pushed to a registry, inspected, and removed.

Swarm init creates a new cluster and returns the local node ID. Join requires `ListenAddr`, `RemoteAddrs`, and `JoinToken`, with optional advertised and data-path addresses. Leave and node delete have force flags for disruptive cases. Swarm, node, service, secret, and config updates use required `version` query parameters to guard against conflicting writes. Swarm update can rotate worker tokens, manager tokens, and the manager unlock key.

Service creation and update consume `ServiceSpec`, with registry credentials optionally provided in `X-Registry-Auth`. Service update can fall back to registry credentials from `spec` or `previous-spec`, or use `rollback=previous` so the supplied spec is ignored and the server rolls back to the prior service spec. Service and task logs use the same flow: with `follow=true`, the server returns `101` and hijacks the connection for raw stream output; otherwise successful logs are a `200` string body. Both support `details`, `stdout`, `stderr`, `since`, `timestamps`, and string-typed `tail`.

Secret and config lifecycle operations are parallel: list with filters, create from spec and base64 data, inspect by ID, delete by ID, and update by ID/name plus required version. Their update descriptions state that only labels can currently be updated and all other fields must remain unchanged from inspect output.

Distribution inspect contacts the registry for the named image and returns digest and platform metadata, with `401` covering failed authentication or missing images. Session initialization upgrades HTTP to h2c using `Upgrade: h2c` and `Connection: Upgrade`, then uses the hijacked transport for client callback services.

## State And Persistence Behavior

The YAML has no runtime state, but it documents daemon operations that read and mutate persistent Docker state:

- volume and network prune/delete operations remove persisted daemon resources and can affect containers that depend on them;
- network create persists driver/IPAM/options/label metadata and connect/disconnect mutates container network attachment state;
- plugin pull/create/upgrade/delete/enable/disable/set/push operations change installed plugin state, runtime enablement, plugin configuration, or remote registry state;
- node and swarm endpoints read and mutate swarm manager state, including cluster membership, node specs, tokens, manager unlock keys, and swarm specs;
- service create/update/delete changes desired orchestration state, which in turn drives task creation, shutdown, rollback, and image pulling;
- task list/inspect reads scheduler state and task runtime status;
- service/task logs read container log storage and may keep connections open for live streaming;
- secrets and configs persist swarm objects and their specs, while updates are constrained to metadata labels in this API version;
- distribution inspect does not mutate local daemon state in this schema, but depends on registry authentication and remote registry contents;
- session creates an upgraded interactive transport and can enable server-to-client callbacks for advanced operations.

Version query parameters on node, swarm, service, secret, and config updates are explicit optimistic-concurrency controls. Several APIs expose sensitive or security-relevant state: plugin privileges, registry auth headers, swarm join tokens, manager unlock keys, secret payloads, and configs consumed by services.

## Dependencies

This range depends on shared Swagger 2.0 conventions and shared definitions in the surrounding `v1.32.yaml` file, including `ErrorResponse`, `Network`, `IPAM`, `EndpointSettings`, `Plugin`, `Node`, `NodeSpec`, `Swarm`, `SwarmSpec`, `Service`, `ServiceSpec`, `ServiceUpdateResponse`, `Task`, `Secret`, `SecretSpec`, `Config`, and `ConfigSpec`.

Runtime dependencies described by the contract include Docker's network drivers and IPAM drivers, plugin registry access, plugin permission models, registry authentication through `X-Registry-Auth`, swarm manager state, raft-backed object versions, supported logging drivers (`json-file` or `journald`) for service/task logs, raw-stream connection hijacking shared with container attach behavior, remote registry manifest data for distribution inspection, and experimental daemon support for the `/session` endpoint.

Most swarm-object endpoints can return `503` when the daemon is not part of a swarm. Plugin pull/upgrade and distribution inspect rely on remote registries and auth. Network creation can fail when a requested driver plugin is missing. Service creation can fail when a network is not eligible for services.

## Integration Points

The `operationId` values are stable integration names for generated clients, documentation anchors, tests, and SDK method mappings. This chunk includes major method groups for `Volume`, `Network`, `Plugin`, `Node`, `Swarm`, `Service`, `Task`, `Secret`, `Config`, `Distribution`, and experimental `Session`.

Network endpoints integrate with container lifecycle and service networking. The create/connect/disconnect operations use shared network, IPAM, and endpoint schemas that also appear in container and service APIs. The list endpoint deliberately returns a smaller representation than inspect in API v1.28 and later, so clients that need attached container details should use `NetworkInspect`.

Plugin endpoints integrate with the registry authentication model and with daemon extension points for networking, volumes, logging, authorization, and other capabilities. Privilege negotiation is part of the install/upgrade flow, while enable/disable/delete operations affect whether containers can use plugin-provided capabilities.

Swarm node, service, task, secret, and config endpoints form a connected orchestration surface. Services reference secrets/configs, create tasks, attach networks, use log drivers, and expose task status through scheduler state. Node endpoints expose and mutate the cluster members on which tasks run. Swarm update controls cluster-wide spec and credential rotation. Logs integrate with raw-stream clients as well as ordinary HTTP response handling.

Distribution inspect connects the daemon API to registry metadata lookup without using the image-list API shape. Session integrates the daemon with clients that can expose gRPC services over an upgraded h2c connection and is explicitly gated by experimental daemon support.

## Risks And Edge Cases

- The range starts inside the tail of volume deletion, so conclusions about the whole `VolumeDelete` operation require the preceding chunk. This slice still captures `name`, `force`, and key in-use/server error behavior.
- Filter parameters are JSON-encoded strings, not structured query objects. Client generators must preserve string typing for filters on volumes, networks, plugins, nodes, services, tasks, secrets, and configs.
- `NetworkList` returns a smaller network representation than `NetworkInspect` for API v1.28 and up; clients may incorrectly assume attached container detail is present in list responses.
- `CheckDuplicate` on network create is documented as best-effort only because networks are keyed by random ID, not name. It must not be treated as a uniqueness guarantee.
- Network delete/create/connect/disconnect distinguish unsupported built-in or swarm-scoped operations with `403`; clients should not collapse these into generic `500` handling.
- Network prune `until` accepts Unix timestamps, date timestamps, or Go duration strings relative to the daemon machine's time, which can be surprising when client and daemon clocks differ.
- Plugin remove `force` may disable a plugin before removal and can affect containers using that plugin. Plugin disable also has a force path for in-use plugins.
- Plugin pull/upgrade permission bodies are arrays of accepted privileges. Skipping privilege review or serializing the body incorrectly can break installs or silently accept dangerous capabilities.
- Registry auth headers are base64-encoded JSON and appear on plugin pull/upgrade and service create/update. Bad encoding or stale credentials changes failure modes across registry-backed operations.
- Swarm init/join/leave/update operations can be disruptive. `ForceNewCluster`, forced leave, node force delete, and token/key rotation require careful operator intent.
- Update endpoints with required `version` values must be built from fresh inspect/list state. Stale versions should be expected to fail to avoid conflicting writes.
- Service update's `rollback=previous` ignores the supplied spec, which can surprise clients that always populate bodies and expect them to apply.
- Service/task log endpoints switch protocol handling when `follow=true`: `101` raw stream is not a JSON response. `tail` is a string because it accepts an integer or `all`.
- Service/task logs only work for services using `json-file` or `journald`; other logging drivers may not satisfy the endpoint contract.
- `stdout` and `stderr` default to `false` on log endpoints. Clients that omit both may receive no useful output depending on daemon behavior.
- The `TaskLogs` endpoint in this slice lacks an explicit `tags: ["Task"]` line before `/secrets`; if this is not supplied elsewhere by tooling, generated documentation grouping can be inconsistent.
- Secret and config update bodies reference full specs, but only labels are mutable. Partial local specs or changed immutable fields should be rejected.
- Secret and config create can return `409` for duplicate names; idempotent create workflows need explicit conflict handling.
- Distribution inspect returns `401` both for failed auth and no image found, so callers may need additional context to distinguish auth failure from missing content.
- `/session` is experimental and hijacks the connection to h2c. Generated clients or proxies that do not support upgrade semantics will not handle it correctly.

## Test Signals

Useful validation for this API contract includes:

- OpenAPI linting for valid path parameters, unique `operationId` values, resolvable `$ref` schemas, response schemas, media types, and required update parameters.
- Client-generation tests that preserve JSON-encoded filters as strings and keep log `tail` string-typed.
- Volume prune tests for label and label-negation filters, returned deleted volume names, and `SpaceReclaimed`.
- Network lifecycle tests for list filters, inspect by ID/name, create with IPAM/IPv6/options/labels, delete built-in network `403`, connect/disconnect missing objects `404`, swarm-scoped connect/disconnect `403`, and prune `until`/label filters.
- Plugin lifecycle tests for privilege discovery, pull with accepted privileges and `X-Registry-Auth`, inspect missing plugin `404`, enable timeout behavior, forced disable/delete behavior, upgrade remote handling, create from tar, push missing plugin, and `PluginSet` string settings.
- Swarm/node tests outside swarm mode asserting documented `503`, and in swarm mode covering node filters, inspect/delete/update, stale update versions, force node removal, swarm init/join required fields, leave force behavior, token/key rotations, unlock key retrieval, and unlock payload handling.
- Service tests for list filters, create success with warning, private registry auth, network eligibility `403`, duplicate name `409`, inspect `insertDefaults`, delete missing service `404`, update stale version rejection, `registryAuthFrom`, and `rollback=previous`.
- Service/task log tests covering `stdout`, `stderr`, `details`, `timestamps`, `since`, `tail=all`, numeric `tail`, `follow=false` `200`, and `follow=true` `101` raw-stream hijacking.
- Task tests for filters by desired state/id/label/name/node/service, inspect missing task `404`, and example fields such as service ID, node ID, desired state, status, container status, and network attachments.
- Secret/config lifecycle tests for list filters, create success, duplicate name `409`, inspect shape, delete `204`, label-only update, stale version rejection, immutable field rejection, and `503` outside swarm mode.
- Distribution inspect tests for descriptor/platform response shape, registry auth failure, missing image `401`, and server errors.
- Session tests gated behind experimental daemon mode, verifying h2c upgrade headers, `101` success, bad-parameter `400`, and client behavior over the hijacked transport.
