# sources/cloud-native/moby/api/docs/v1.33.yaml lines 7570-10019

## Scope And Purpose

This chunk is the later `paths` portion of the Docker Engine API v1.33 Swagger 2.0 contract. It starts inside `/volumes/{name}` at the `VolumeDelete` operation and continues through volume pruning, network management, plugin lifecycle, swarm/node/service/task APIs, swarm secrets and configs, registry distribution inspection, and the experimental interactive session endpoint.

The file is API documentation and schema, not runtime implementation code. Its purpose is to define stable HTTP routes, request parameters, response status codes, response schemas, examples, tags, and generated-client operation IDs for this slice of the versioned Docker Engine API. The chunk is dominated by stateful daemon operations: deleting or pruning resources, attaching containers to networks, installing and enabling plugins, managing swarm membership and object specs, rotating credentials, reading logs, and inspecting registry metadata.

## Important APIs And Operation Groups

Volume operations in this range include `VolumeDelete` and `VolumePrune`. `VolumeDelete` removes a named or ID-addressed volume with optional `force`; it distinguishes missing volumes or drivers (`404`), in-use volumes (`409`), and server failures (`500`). `VolumePrune` accepts JSON-encoded label filters and returns deleted volume names plus reclaimed bytes.

Network operations include `NetworkList`, `NetworkInspect`, `NetworkDelete`, `NetworkCreate`, `NetworkConnect`, `NetworkDisconnect`, and `NetworkPrune`. Network listing supports JSON filters by driver, partial ID, label, name, scope, and builtin/custom type. Creation accepts `Name`, duplicate-check hints, driver, `Internal`, `Attachable`, `Ingress`, IPAM, IPv6, options, and labels. Container connect/disconnect uses path network ID/name plus body container ID/name and optional `EndpointSettings` or `Force`. Pruning supports `until` and label filters and returns deleted network identifiers.

Plugin operations cover the full plugin lifecycle: `PluginList`, `GetPluginPrivileges`, `PluginPull`, `PluginInspect`, `PluginDelete`, `PluginEnable`, `PluginDisable`, `PluginUpgrade`, `PluginCreate`, `PluginPush`, and `PluginSet`. Pull and upgrade accept remote references, optional local names, `X-Registry-Auth`, and user-accepted privilege arrays containing names, descriptions, and values. Create consumes an `application/x-tar` plugin rootfs/manifest body. Set accepts an array of configuration strings such as `DEBUG=1`.

Node and swarm operations include `NodeList`, `NodeInspect`, `NodeDelete`, `NodeUpdate`, `SwarmInspect`, `SwarmInit`, `SwarmJoin`, `SwarmLeave`, `SwarmUpdate`, `SwarmUnlockkey`, and `SwarmUnlock`. Node updates require a `NodeSpec` body and a `version` query parameter. Swarm init/join bodies carry listen/advertise/data-path addresses, join tokens, manager addresses, and `SwarmSpec`. Swarm updates require a version and can rotate worker tokens, manager tokens, and manager unlock keys.

Service operations include `ServiceList`, `ServiceCreate`, `ServiceInspect`, `ServiceDelete`, `ServiceUpdate`, and `ServiceLogs`. Creation and update are driven by `ServiceSpec` bodies with examples covering container image, mounts, hosts, DNS, secrets, log driver, placement, resource limits/reservations, restart policy, replicated mode, update and rollback configs, endpoint ports, and labels. Create/update can use `X-Registry-Auth`; update additionally requires a service object version and supports `registryAuthFrom` and server-side rollback to the previous spec.

Task operations include `TaskList`, `TaskInspect`, and `TaskLogs`. Task listing returns `Task` objects containing object versions, timestamps, task specs, service/node IDs, slot, current status, desired state, container status, and network attachments. Filters include desired state, ID, label, name, node, and service. Task logs mirror service logs with stream-capable output and logger limitations.

Secret and config operations include `SecretList`, `SecretCreate`, `SecretInspect`, `SecretDelete`, `SecretUpdate`, `ConfigList`, `ConfigCreate`, `ConfigInspect`, `ConfigDelete`, and `ConfigUpdate`. Both object families are swarm-scoped and versioned. Create returns a new `ID`, list supports ID/label/name filters, inspect returns the versioned object, delete returns `204`, and update requires a version query parameter. The update descriptions explicitly say only labels can be changed; all other fields must remain unchanged from inspect output values.

The final two operation groups are `DistributionInspect` and `Session`. `DistributionInspect` contacts a registry and returns a descriptor plus supported platforms for an image name or ID. `Session` is experimental and hijacks/upgrades an HTTP connection to h2c so the daemon can call back to client-exposed gRPC services.

## Control Flow

The control flow is expressed through HTTP method semantics. `GET` operations list or inspect current daemon, swarm, plugin, registry, or log state. `POST` operations create, update, connect, disconnect, enable, disable, pull, upgrade, prune, initialize, join, leave, unlock, or stream. `DELETE` operations remove volumes, networks, plugins, nodes, services, secrets, and configs.

Many operations use path identifiers that accept either IDs or user-facing names. Clients generally resolve objects through daemon handlers rather than pre-validating ID/name type. Query-encoded filters are consistently documented as JSON maps from string keys to string arrays, creating a common parsing contract across network, plugin, node, service, task, secret, and config list/prune endpoints.

Swarm, node, service, secret, and config updates follow an optimistic-concurrency flow. Clients inspect or list the object, capture `Version.Index`, submit the replacement spec plus a required `version` query parameter, and receive an error if the object is missing, stale, invalid, or the daemon is not in swarm mode. This contract is central to preventing conflicting writes to Raft-backed swarm objects.

Streaming control flow appears in `ServiceLogs`, `TaskLogs`, and `Session`. Log endpoints can return a `101` upgrade with a raw stream when `follow=true`, or a `200` string body otherwise. `Session` always models the successful path as a `101` hijack to an h2c transport and is explicitly gated by experimental daemon features.

## State And Persistence Behavior

This YAML has no local persistence, but it describes persistent daemon state transitions. Volume and network delete/prune operations mutate host or driver-managed resources and must respect in-use objects. Network connect/disconnect mutates container endpoint membership and interacts with IPAM-assigned addresses.

Plugin operations mutate installed plugin state, plugin configuration, registry-distributed plugin content, and enabled/disabled status. Pull and upgrade also depend on registry credentials and privilege acceptance. Force flags on plugin deletion/disablement can break consumers if the plugin is still in use.

Swarm operations mutate cluster membership, manager state, certificates, Raft-backed specs, join tokens, and manager unlock keys. `SwarmInit` creates a new cluster, `SwarmJoin` enrolls a node with a secret token, `SwarmLeave` removes local participation, and `SwarmUpdate` changes the cluster spec and can rotate credentials. `NodeDelete` can force-remove a node from the swarm.

Services and tasks represent orchestrated desired and observed state. Service creation/update/deletion changes the desired scheduler state. Tasks expose derived execution state, including `DesiredState`, current `Status`, container status, and network attachments. Service and task logs are transient/read-side views of task/container execution logs and are documented as available only for `json-file` or `journald` logging drivers.

Secrets and configs are persisted swarm objects. Their data is supplied during create, but updates in this API version are constrained to labels only. Both require swarm availability and use version indexes to avoid conflicting writes.

`DistributionInspect` does not mutate local daemon objects in the schema; it reaches out to a registry to resolve digest and platform metadata. `Session` establishes an interactive transport rather than a persistent object, but it creates a privileged callback channel between client and daemon for advanced operations.

## Dependencies And Integration Points

The schema depends on shared definitions elsewhere in `v1.33.yaml`: `Volume`, `Network`, `IPAM`, `EndpointSettings`, `Plugin`, `Node`, `NodeSpec`, `Swarm`, `SwarmSpec`, `Service`, `ServiceSpec`, `ServiceUpdateResponse`, `Task`, `Secret`, `SecretSpec`, `Config`, `ConfigSpec`, and `ErrorResponse`. The range also uses Swagger constructs such as `$ref`, `allOf`, array/object schemas, binary body formats, examples, tags, and operation IDs consumed by documentation and generated clients.

Runtime integration points include Docker daemon HTTP routing, volume drivers, network drivers and IPAM, plugin manager, registry authentication, swarmkit/Raft object storage, orchestrator scheduling, logging drivers, and experimental session transport. Registry integration appears through `X-Registry-Auth` on plugin pull/upgrade and service create/update, and through `/distribution/{name}/json` for manifest descriptor/platform discovery.

Client integration points are significant. SDKs generated from this document must handle JSON bodies, path/query/header parameters, versioned update parameters, Base64-encoded auth headers, tar/binary request bodies, raw streams, `101` upgrades, and open-ended map/filter inputs. The Docker CLI likely composes many user commands from these lower-level endpoints.

## Risks And Edge Cases

Destructive operations are high risk. Volume/network prune can delete broad sets of resources based on filters; volume delete can be forced; plugin delete/disable can be forced while in use; service, secret, config, and node deletes modify swarm state. Conformance tests should verify that documented filters, force flags, in-use checks, and error codes are implemented consistently.

Swarm update endpoints depend on clients supplying the correct version. Missing, stale, or wrong version values should produce controlled errors rather than silent overwrites. Secret and config updates have an additional contract risk because the body schema permits the full spec but the prose restricts updates to labels only.

Streaming and hijacked endpoints are not ordinary JSON APIs. `ServiceLogs`, `TaskLogs`, and `Session` require clients and proxies to support connection upgrades or raw stream handling. Log endpoints also depend on specific logging drivers, so implementations must return clear failures when logs cannot be read.

Plugin endpoints combine registry access, local rootfs/manifests, privilege acceptance, configuration mutation, and daemon extension loading. Auth headers and accepted privileges are sensitive; implementations and clients should avoid logging them. Upgrade and pull flows must reject missing plugins/remotes and handle registry auth failures cleanly even though this chunk mainly documents `500` for plugin pull failures.

Network APIs mix local and swarm/global scopes. Direct connect/disconnect document `403` for swarm-scoped networks, and network inspect can filter by scope. Tests should ensure builtin networks cannot be removed or recreated incorrectly and that name/ID ambiguity does not mutate the wrong network.

Several response examples are operationally dense and should remain synchronized with definitions. Service examples include fields such as mounts, secrets, DNS, update/rollback config, and endpoints; task examples include nested network attachments. Generated clients can become brittle if example-only fields diverge from referenced definitions.

## Test Signals

Useful static checks include Swagger/OpenAPI linting for this v1.33 chunk, `$ref` resolution against shared definitions, operation ID uniqueness, required parameter validity, response schema validity, and generated Go/client type compilation.

API conformance tests should cover documented status codes and bodies for each operation group: missing objects (`404`), in-use or name conflicts (`409`), unsupported builtin or swarm-scoped operations (`403`), bad specs (`400`), swarm unavailability (`503`), registry/auth failures, and successful `200`/`201`/`204` paths.

Persistence tests should exercise volume and network delete/prune filters, network create/connect/disconnect state, plugin install/enable/disable/set/upgrade/delete flows, swarm init/join/leave/update/unlock flows, service create/update/delete and rollback behavior, node update/delete, and secret/config create/update/delete with version conflicts.

Stream tests should verify service and task logs for `stdout`, `stderr`, `follow`, `since`, `timestamps`, and `tail`, including both `101` follow streams and `200` non-follow responses. Session tests need experimental-mode gating and h2c upgrade behavior.

Compatibility tests should confirm that v1.33 clients tolerate unknown fields in responses, encode filter query parameters as documented JSON maps, preserve Base64 auth header payloads without alteration, and handle path identifiers that can be names or IDs.
