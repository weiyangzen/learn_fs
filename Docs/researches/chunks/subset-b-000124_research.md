# sources/cloud-native/moby/api/docs/v1.37.yaml lines 7562-10180

## Scope And Purpose

This chunk is the final path section of the Docker Engine API v1.37 Swagger/OpenAPI 2.0 specification. It is not executable code, but it is a contract source for API documentation, generated clients, and implementation conformance tests. The chunk starts at the tail of `GET /exec/{id}/json`, then defines the volume, network, plugin, swarm node, swarm cluster, service, task, secret, config, distribution, and experimental session endpoints through the end of the file.

The in-scope operations are stateful daemon APIs. They expose local Docker resources such as volumes, networks, and plugins; swarmkit-managed cluster resources such as nodes, services, tasks, secrets, and configs; registry inspection via distribution metadata; and an experimental hijacked session transport. Most operations reference schemas defined earlier in the file, such as `Volume`, `Network`, `Plugin`, `Node`, `Swarm`, `SwarmSpec`, `ServiceSpec`, `Service`, `Task`, `SecretSpec`, `Secret`, `ConfigSpec`, `Config`, `ErrorResponse`, and `IdResponse`.

## API Surface

The chunk closes the exec inspect operation with a response body that reports `CanRemove`, `ContainerID`, detach keys, exit code, stream-open booleans, `ProcessConfig`, `Running`, and daemon-side `Pid`. Error handling is limited to `404` for a missing exec instance and `500` for server failure, with an `id` path parameter identifying the exec instance.

Volume APIs include `VolumeList`, `VolumeCreate`, `VolumeInspect`, `VolumeDelete`, and `VolumePrune`. `GET /volumes` returns a `VolumeListResponse` object with required `Volumes` and `Warnings` arrays. The list filter is a JSON-encoded `map[string][]string` query string supporting `dangling`, `driver`, `label`, and `name`. Creation accepts an inline body with `Name`, `Driver` defaulting to `local`, driver-specific `DriverOpts`, and `Labels`. Removal accepts a `force` query flag and distinguishes not found from in-use conflict. Prune returns `VolumesDeleted` plus `SpaceReclaimed`.

Network APIs include `NetworkList`, `NetworkInspect`, `NetworkDelete`, `NetworkCreate`, `NetworkConnect`, `NetworkDisconnect`, and `NetworkPrune`. Listing returns the smaller `Network` representation and explicitly notes that attached container lists are not propagated in API versions 1.28 and newer. Filters support driver, id, label, name, scope, and custom/builtin type. Inspect accepts `verbose` and `scope` query controls. Creation requires `Name` and accepts duplicate checking, driver, internal/attachable/ingress flags, `IPAM`, IPv6, driver options, and labels. Connect accepts a container identifier plus optional `EndpointSettings`; disconnect accepts a container identifier and a `Force` boolean. Prune supports `until` and label inclusion/exclusion filters.

Plugin APIs include list, privilege discovery, pull/install, inspect, delete, enable, disable, upgrade, create from tar, push, and set configuration. They use the `Plugin` schema for list/inspect/delete responses, inline privilege arrays for privilege discovery and install/upgrade acceptance, `X-Registry-Auth` for registry-backed pull and upgrade, and `application/x-tar` for local plugin creation. Enable has a `timeout`; disable has a `force`; delete has a `force` that can disable first. Configuration accepts an array of strings such as environment assignments.

Node APIs include `NodeList`, `NodeInspect`, `NodeDelete`, and `NodeUpdate`. They are swarm-only operations and can return `503` when the daemon is not part of a swarm. Listing filters by id, engine label, membership, name, and role. Updates accept a `NodeSpec` body and require a `version` query integer, making node writes optimistic-concurrency operations rather than blind updates.

Swarm APIs include inspect, init, join, leave, update, unlock-key retrieval, and unlock. Init accepts listen, advertise, and data-path addresses, a `ForceNewCluster` boolean, and a `SwarmSpec`; join requires `ListenAddr`, `RemoteAddrs`, and `JoinToken`, with optional advertised and data-path addresses. Leave accepts `force`, with documentation warning it can break a cluster if used on the last manager. Update accepts a `SwarmSpec`, a required `version`, and token/key rotation booleans for worker token, manager token, and manager unlock key. Unlock-key and unlock support manager autolock workflows.

Service APIs include list, create, inspect, delete, update, and logs. Listing filters by id, label, mode, and name. Create and update compose `ServiceSpec` with large examples covering container image, mounts, hosts, user, DNS config, secrets, log driver, placement, resources, restart policy, replicated mode, update/rollback behavior, endpoint ports, and labels. Create can use `X-Registry-Auth`; update can use `X-Registry-Auth`, `registryAuthFrom`, `rollback=previous`, and a required `version`. Inspect supports `insertDefaults`. Service logs can return either a plain string body or a `101` upgraded raw stream.

Task APIs include list, inspect, and logs. Listing returns `Task` objects with examples showing object version, spec, service/node placement, slot, status, desired state, container status, and network attachments. Filters include desired state, id, label, name, node, and service. Task logs mirror service logs and have the same `details`, `follow`, `stdout`, `stderr`, `since`, `timestamps`, and `tail` controls.

Secret APIs include list, create, inspect, delete, and update. They are swarm-only and return `503` outside swarm mode. Create uses `SecretSpec` and returns `IdResponse`; inspect/list use `Secret`; delete returns `204`; update requires a `version` and states that only labels can be updated, with all other fields preserved from inspect output. Config APIs mirror this lifecycle with `ConfigSpec`, `Config`, and the same label-only update restriction.

Distribution inspection exposes `GET /distribution/{name}/json`, which contacts the registry and returns a `DistributionInspectResponse` object with a manifest descriptor (`MediaType`, `Size`, `Digest`, `URLs`) and supported platforms (`Architecture`, `OS`, `OSVersion`, `OSFeatures`, `Variant`, `Features`). It uses `401` for authentication failure or missing image and `500` for server errors.

The final endpoint, `POST /session`, initializes an experimental interactive session. It hijacks an HTTP request into an HTTP/2 cleartext transport using `Upgrade: h2c` and `Connection: Upgrade`, produces `application/vnd.docker.raw-stream`, and returns `101` when hijacking succeeds.

## Control Flow And Protocol Behavior

The chunk defines several lifecycle flows. Volumes are listed or created, inspected by name or ID, removed if not in use, and pruned in bulk. Networks follow a similar lifecycle but add container endpoint membership: clients create a network, connect containers with optional IPAM endpoint overrides, disconnect them, and eventually remove or prune the network. Network delete returns `403` for predefined networks, while connect/disconnect return `403` for unsupported swarm-scoped operations.

Plugin workflows are multi-step and registry-aware. A client can first call `GetPluginPrivileges` for a remote plugin, then pass the accepted privilege list to `PluginPull` or `PluginUpgrade`, optionally with `X-Registry-Auth`. The plugin can then be enabled, disabled, configured, pushed, deleted, or inspected. The spec deliberately separates installation from enabling, so clients should not assume pull creates an active plugin.

Swarm control flow is versioned and cluster-state dependent. Init creates local swarm state and can force a new cluster. Join requires known managers and a join token. Inspect exposes current swarm state, update mutates swarm spec and join/unlock credentials with an explicit `version`, leave detaches the node, unlock-key retrieval supports locked manager recovery, and unlock posts the key back to a locked manager. Node, service, secret, and config APIs all return `503` outside the required swarm state.

Service workflows are orchestrator operations rather than direct container operations. Create records a desired `ServiceSpec`; swarmkit then schedules tasks. Update requires the target service ID/name and current version, and the `rollback=previous` query branch tells the server to ignore the supplied spec and roll back to the prior one. Logs are read from service tasks through logging drivers, with a documented dependency on `json-file` or `journald`.

Task APIs are mostly read-only in this chunk. Tasks are listed and inspected as scheduler artifacts of service state, and logs are retrieved similarly to service logs. The examples show task status as a combination of desired state, actual state, timestamp, message, container ID/PID, and network attachments, so clients should treat task state as eventually convergent rather than immediately synchronized after service updates.

Several endpoints use non-trivial HTTP behavior. Service/task logs return `101` and hijack the connection when `follow=true`, otherwise they return `200` with a string body. The session endpoint also uses a `101` upgrade but to HTTP/2 cleartext. Plugin creation consumes a tar body. Many list/prune filters are JSON objects encoded inside a string query parameter, which is a protocol convention not visible from the simple OpenAPI `type: string`.

## State And Persistence Behavior

Volumes are persistent named or generated resources managed by volume drivers. `VolumeCreate` passes driver options directly to the selected driver, so durable state and validation semantics depend on the driver. `VolumeDelete` can fail with `409` if containers still use the volume, while `VolumePrune` deletes unused volumes and reports bytes reclaimed.

Networks persist driver, IPAM, labels, options, scope, and endpoint attachments. Built-in networks have protected behavior, and swarm-scoped networks restrict direct container connect/disconnect. `NetworkList` deliberately omits detailed container attachment information in newer API versions, so full state inspection requires `NetworkInspect`.

Plugins persist installed metadata, accepted privileges, rootfs/manifest content, enabled state, runtime settings, and registry names. Operations such as force delete or force disable can mutate active daemon extension points, affecting volume, network, authorization, or logging behavior provided by plugins.

Swarm objects are cluster state replicated through swarm managers. Node updates, swarm updates, service updates, secret updates, and config updates all depend on object versions to avoid lost writes. Secrets and configs are immutable in their payload content through these update endpoints; only labels are documented as mutable. Join tokens and manager unlock keys are sensitive persisted cluster credentials, and this chunk exposes explicit rotation/query endpoints for them.

Services persist desired state in `ServiceSpec`, including container image, secrets, mounts, DNS, resources, restart policy, update/rollback policy, and published ports. Tasks persist observed scheduler state, container status, and network attachments as the realization of services. Log endpoints read from persisted or streamed logging-driver data and only work for `json-file` and `journald`.

Distribution inspection does not primarily mutate local daemon state; it contacts a registry to resolve descriptor and platform metadata for an image name. The session endpoint creates a live upgraded connection, not a durable resource, but it enables advanced callback services between client and daemon for the lifetime of the session.

## Dependencies And Integration Points

This section depends heavily on definitions outside the chunk: resource schemas (`Volume`, `Network`, `Plugin`, `Node`, `Swarm`, `Service`, `Task`, `Secret`, `Config`), input specs (`SwarmSpec`, `NodeSpec`, `ServiceSpec`, `SecretSpec`, `ConfigSpec`), shared response types (`IdResponse`, `ErrorResponse`, `ServiceUpdateResponse`), networking subtypes (`IPAM`, `EndpointSettings`), and OpenAPI extensions such as `x-nullable` and `x-go-name` used elsewhere in the file.

Daemon subsystems represented here include the local volume store and volume drivers, libnetwork and IPAM, plugin manager and plugin registry support, swarmkit cluster management, service scheduler, task state tracker, secrets/configs stores, logging drivers, registry distribution clients, and the BuildKit-style session/callback transport used by advanced daemon-client interactions.

External integration points include volume/network/plugin drivers, plugin registries and auth via `X-Registry-Auth`, image registries contacted by distribution inspect, remote swarm managers reached through `RemoteAddrs`, external logging backends indirectly constrained by log-driver support, and HTTP clients/proxies that must support connection hijacking and h2c upgrades.

The spec also integrates with documentation generation and client generation. Operation IDs such as `VolumeList`, `NetworkCreate`, `PluginPull`, `SwarmUpdate`, `ServiceUpdate`, `TaskLogs`, `SecretUpdate`, `ConfigUpdate`, `DistributionInspect`, and `Session` are stable anchors for generated SDK methods and API documentation links.

## Risks And Edge Cases

Filter query parameters are typed as strings but semantically require JSON-encoded `map[string][]string` values. Incorrect encoding can silently broaden list/prune operations, especially for destructive volume/network prune calls.

Versioned updates are easy to misuse. Node, swarm, service, secret, and config updates require the current object version. Clients that cache stale versions should receive errors rather than overwriting newer state. The `rollback=previous` branch of service update is another edge case because the server ignores the submitted spec in that mode.

Several operations have broad or disruptive side effects. `VolumePrune` and `NetworkPrune` delete resources in bulk. Forced volume, plugin, node, swarm leave, or network operations can break workloads, detach cluster members, or disable daemon extension points while in use. The API contract exposes these controls but relies on callers and implementation checks to prevent accidental damage.

Swarm-only endpoints have a common `503` mode when the daemon is not in a swarm. Tests and clients must distinguish `404` resource-not-found from `503` not-in-swarm, because the remediation differs. `SwarmInit` and `SwarmJoin` also use `503` for the opposite state, where the node is already part of a swarm.

Streaming and hijacked transports are poorly served by generic OpenAPI code generators. Service/task logs and session initialization require clients to handle `101` upgrade responses, raw streams, and possibly long-lived connections. Proxies that buffer responses or block h2c upgrade can break these endpoints.

Secrets and configs carry sensitive or configuration-critical data. The spec examples include base64 payloads for create operations but inspect examples omit secret data, consistent with sensitive data handling. Update endpoints document label-only mutation; implementations should reject attempts to change payload or immutable fields.

Distribution inspection depends on remote registry availability and authentication. The `401` response covers both auth failure and missing images, so clients may need additional registry context to produce precise diagnostics. Platform fields are arrays and optional-looking strings in examples, so strict clients should tolerate empty strings and platform variants.

The session endpoint is explicitly experimental and gated by daemon experimental features. Its documentation contains a typo-like `gPRC` spelling where gRPC is likely intended, and the endpoint may change in future API versions. Consumers should avoid treating it as a stable general-purpose OpenAPI-generated call.

## Test Signals

OpenAPI validation should parse the full `v1.37.yaml` and verify all `$ref` targets referenced in this chunk resolve, including `Volume`, `Network`, `Plugin`, `Node`, `Swarm`, `SwarmSpec`, `ServiceSpec`, `ServiceUpdateResponse`, `Task`, `SecretSpec`, `ConfigSpec`, `IdResponse`, and `ErrorResponse`. Chunk-only parsing is not meaningful because this span depends on definitions declared earlier in the file.

Contract tests should cover success and error status codes for each resource family: volume delete `404` and `409`, network delete `403` and `404`, network connect/disconnect `403`/`404`, plugin missing `404`, swarm/node/service/task/secret/config `503` outside swarm mode, service create `403`/`409`, and distribution inspect `401`.

Lifecycle integration tests should exercise volume create/list/inspect/delete/prune; network create/list/inspect/connect/disconnect/delete/prune; plugin privileges/pull/enable/disable/set/upgrade/delete; swarm init/inspect/update/unlock-key/unlock/leave; node list/update/delete; service create/inspect/update/delete/logs; task list/inspect/logs; secret create/list/inspect/update/delete; and config create/list/inspect/update/delete.

Concurrency tests should submit stale and current `version` values for node, swarm, service, secret, and config updates. Service update tests should include both normal spec updates and `rollback=previous`, verifying that the rollback path ignores the supplied spec.

Transport tests should use real HTTP clients, not only generated SDK calls, for `ServiceLogs`, `TaskLogs`, and `Session`. They should verify plain `200` log responses, `101` upgraded follow responses, stdout/stderr/detail/tail/timestamp/since filtering, logging-driver limitations, and h2c upgrade behavior for sessions.

Destructive-operation tests should verify filters and safety boundaries for `VolumePrune` and `NetworkPrune`, including label inclusion/exclusion and network `until` duration/timestamp parsing. Plugin force disable/delete and swarm leave force should be covered with dependent resources to ensure documented risks produce expected errors or state changes.
