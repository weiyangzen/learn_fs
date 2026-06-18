# sources/cloud-native/moby/api/docs/v1.30.yaml lines 7611-8879

## Scope

This chunk covers Docker Engine API v1.30 Swagger paths from the end of `POST /swarm/join` through the distribution inspection endpoint. It includes swarm leave/update/unlock operations; full service list/create/inspect/delete/update/log endpoints; task list/inspect/log endpoints; full secret and config lifecycle endpoints; and `GET /distribution/{name}/json`.

The source is an OpenAPI/Swagger YAML contract, not executable daemon code. The behavior researched here is the API surface that Docker clients, generated SDKs, daemon compatibility tests, and API documentation consume.

## Purpose

The chunk exposes the swarm-mode control plane after a node has already joined or initialized a swarm. It lets clients leave and update the swarm, retrieve or submit manager unlock keys, manage swarm services, inspect task state, stream service/task logs, manage secret/config objects, and query registry image distribution metadata.

Most endpoints are stateful manager-facing APIs. Service, task, secret, and config operations depend on swarm state and consistently document `503` responses when the daemon is not part of a swarm. Distribution inspection is different: it contacts a registry for image descriptor and platform data and can fail with authentication or missing-image errors.

## Important APIs And Types

- `POST /swarm/leave` (`SwarmLeave`) accepts a `force` boolean query parameter. Forced leave may break the cluster or remove the last manager; success is `200`, non-swarm is `503`.
- `POST /swarm/update` (`SwarmUpdate`) takes a `SwarmSpec` body plus a required `version` query parameter for conflicting-write protection. It also supports `rotateWorkerToken`, `rotateManagerToken`, and `rotateManagerUnlockKey` booleans.
- `GET /swarm/unlockkey` (`SwarmUnlockkey`) returns an object containing `UnlockKey`. `POST /swarm/unlock` (`SwarmUnlock`) accepts the same key shape to unlock a locked manager.
- `GET /services` (`ServiceList`) returns an array of `Service` objects and accepts JSON-encoded `filters` for `id`, `label`, `mode`, and `name`.
- `POST /services/create` (`ServiceCreate`) consumes `ServiceSpec`, may use `X-Registry-Auth`, and returns an object with created service `ID` plus optional `Warning`. It documents `400`, `403`, `409`, `500`, and `503` errors.
- `GET /services/{id}` (`ServiceInspect`) resolves a service by ID or name and supports `insertDefaults`. `DELETE /services/{id}` (`ServiceDelete`) removes the service.
- `POST /services/{id}/update` (`ServiceUpdate`) consumes `ServiceSpec`, requires a `version` query parameter, can use `X-Registry-Auth`, can source credentials from `registryAuthFrom=spec|previous-spec`, and can perform server-side rollback when `rollback=previous`.
- `GET /services/{id}/logs` (`ServiceLogs`) streams or returns service stdout/stderr logs, with `details`, `follow`, `stdout`, `stderr`, `since`, `timestamps`, and `tail` query parameters. Follow mode can return `101` and hijack the HTTP connection using Docker raw-stream framing.
- `GET /tasks` (`TaskList`) returns `Task` objects and accepts JSON-encoded filters for desired state, ID, label, name, node, and service.
- `GET /tasks/{id}` (`TaskInspect`) returns one `Task` by ID. `GET /tasks/{id}/logs` (`TaskLogs`) mirrors service log parameters and response modes for one task.
- `GET /secrets`, `POST /secrets/create`, `GET /secrets/{id}`, `DELETE /secrets/{id}`, and `POST /secrets/{id}/update` define secret list/create/inspect/delete/update. `SecretUpdate` requires `version` and only allows label changes even though the body schema is `SecretSpec`.
- `GET /configs`, `POST /configs/create`, `GET /configs/{id}`, `DELETE /configs/{id}`, and `POST /configs/{id}/update` mirror secret lifecycle behavior for config objects. `ConfigUpdate` also requires `version` and only allows label changes.
- `GET /distribution/{name}/json` (`DistributionInspect`) returns a response named `DistributionInspect` containing required `Descriptor` and `Platforms`. The descriptor has media type, size, digest, and URLs; platform entries include architecture, OS, OS version/features, variant, and features.

Shared definitions referenced in this chunk include `SwarmSpec`, `ServiceSpec`, `Service`, `ServiceUpdateResponse`, `Task`, `SecretSpec`, `Secret`, `ConfigSpec`, `Config`, and `ErrorResponse`.

## Control Flow

Swarm update flow is optimistic and versioned: a client reads current swarm state elsewhere, submits a full `SwarmSpec` with the current version, and can request token or unlock-key rotation through independent query flags. Leave and unlock flows are simpler one-shot mutations: leave uses an optional force flag, unlock submits the manager unlock key, and unlock-key retrieval exposes the current key material when the node can serve swarm state.

Service lifecycle flow follows Docker's inspect-modify-update pattern. List optionally filters services, create validates and persists a new `ServiceSpec`, inspect returns the service representation, delete removes it, and update requires the caller to supply the service version to avoid lost updates. Update can also ignore the submitted spec for rollback when `rollback=previous`, which is a control-flow exception generated clients must preserve. Registry auth can arrive explicitly via `X-Registry-Auth` or indirectly from the new or previous spec.

Service and task log flows share the container attach/log streaming model. Without `follow`, responses can be ordinary `200` string bodies. With `follow`, the API may return `101`, upgrade and hijack the HTTP connection, and emit raw stream data. The endpoints only support services using the `json-file` or `journald` logging drivers.

Task APIs are read-only in this range. `TaskList` returns current and historical task records including desired/current states and network attachments; `TaskInspect` is a point lookup. Task records show how service reconciliation is observable: a service slot can have both running and shutdown task history, each with its own version, status, container status, and network attachment addresses.

Secret and config flows are parallel. List accepts JSON filter strings, create persists a named object with labels and base64 data, inspect returns metadata/spec, delete returns `204`, and update is versioned but label-only. The update descriptions explicitly tell callers to preserve all non-label fields from the inspect response.

Distribution inspection flow resolves the path `name`, contacts a registry, and returns OCI/Docker descriptor and platform metadata. Unlike swarm resource endpoints, failure includes `401` for authentication failure or no image found, plus `500` for server errors.

## State And Persistence Behavior

The YAML itself has no persistence, but it documents persistent daemon/swarm resources. Swarm, service, secret, config, and task objects carry versioned state. Required `version` parameters on swarm, service, secret, and config updates are optimistic concurrency controls and should prevent overwriting newer raft-store objects.

Service state is durable swarm state. `ServiceSpec` controls task template, replicated/global mode, update and rollback strategies, network attachments, endpoint configuration, and labels. The `Service` response also exposes endpoint allocation and update status. Create/update operations can produce warnings when image digest pinning fails, so success does not always mean all auxiliary resolution work succeeded cleanly.

Tasks are scheduler-produced state, not directly mutated by these endpoints. The task examples show immutable task identity and version history plus mutable execution status such as `running` or `shutdown`, container IDs, PIDs, and desired state. Task network attachments expose overlay network and IPAM state attached to task execution.

Secrets and configs are persisted swarm objects with stable IDs, object versions, timestamps, names, labels, and base64 data supplied at creation. Inspect/list examples show only metadata and spec names/labels, not payload data, which is important for secret confidentiality and for clients expecting read-back behavior.

Distribution inspection does not persist local daemon state in this contract. It reports registry descriptor and platform metadata for an image name or ID and therefore depends on external registry availability, authentication, and manifest content.

## Dependencies

This chunk depends on schema definitions elsewhere in `v1.30.yaml`: `SwarmSpec` for swarm updates; `ServiceSpec`, `Service`, `EndpointSpec`, `EndpointPortConfig`, and `ServiceUpdateResponse` for service APIs; `Task`, `TaskSpec`, and `TaskState` for task APIs; `SecretSpec`/`Secret` and `ConfigSpec`/`Config`; and shared `ErrorResponse`.

At runtime, most endpoints depend on Docker Engine swarm mode, manager/state-store access, raft object versions, swarmkit scheduling/reconciliation, overlay networking state, logging drivers, and registry credential handling. The log endpoints additionally depend on Docker's HTTP connection hijack/raw-stream implementation, the same integration pattern documented for container attach.

Generated clients depend on correct Swagger interpretation for path parameters, query booleans, required integer versions, JSON request bodies, header parameters, `allOf` examples, and mixed `101`/`200` response handling.

## Integration Points

The operation IDs are SDK generation hooks: `SwarmLeave`, `SwarmUpdate`, `SwarmUnlockkey`, `SwarmUnlock`, `ServiceList`, `ServiceCreate`, `ServiceInspect`, `ServiceDelete`, `ServiceUpdate`, `ServiceLogs`, `TaskList`, `TaskInspect`, `TaskLogs`, `SecretList`, `SecretCreate`, `SecretInspect`, `SecretDelete`, `SecretUpdate`, `ConfigList`, `ConfigCreate`, `ConfigInspect`, `ConfigDelete`, `ConfigUpdate`, and `DistributionInspect`.

Service APIs integrate with registry authentication through `X-Registry-Auth` and with image digest resolution through create/update warnings. They also integrate with swarm networking (`EndpointSpec`, published ports, VIP/DNSRR modes), service rollback, update orchestration, task scheduling, secrets, configs, and logs.

Task APIs integrate with service reconciliation and node/container runtime status. The list filters let higher-level tools query by desired state, node, service, name, ID, or label and then inspect/log individual tasks.

Secret and config APIs integrate with service specs because tasks can mount referenced secrets/configs. Their update endpoints link back to inspect semantics by requiring unchanged non-label fields, so client tooling should read before update rather than constructing partial specs blindly.

Distribution inspection integrates the Engine API with Docker registry/manifest metadata and platform selection. Its response shape maps closely to distribution descriptors and image manifest platform records.

## Risks And Edge Cases

- All swarm resource endpoints can fail with `503` outside swarm mode; callers must distinguish that from `404` missing resources and ordinary `500` daemon errors.
- Versioned update endpoints require callers to supply the current object version. Stale versions, omitted versions, or concurrent updates are critical compatibility cases, but several endpoints do not list an explicit conflict status beyond generic `400`/`500`.
- `SwarmLeave force=true` can intentionally break cluster availability or remove the last manager. Automation should avoid defaulting this flag to true.
- `SwarmUpdate` token/key rotation flags are independent booleans. Clients must not lose unrelated `SwarmSpec` fields while rotating only credentials because the body remains required.
- `ServiceUpdate rollback=previous` says the supplied spec is ignored. Client libraries that always serialize and validate a complete spec may accidentally block or alter rollback behavior.
- `registryAuthFrom` is a string with documented valid values but no enum in the schema. Generated clients may not constrain it, and daemon validation must handle invalid strings.
- Service and task log endpoints can return either `101` hijacked streams or `200` bodies and only work for `json-file` or `journald`. HTTP clients that do not support connection hijacking will fail in follow mode.
- `ServiceUpdateResponse` defines `Warnings` as an array but its example uses singular `Warning`, while `ServiceCreate` defines singular `Warning`. This schema/example inconsistency can affect generated models and documentation.
- `SecretSpec.Data` and `ConfigSpec.Data` are described as base64-url-safe-encoded data but typed as arrays of strings, while create examples provide a single string. This is a significant client-generation risk.
- `SecretUpdate` and `ConfigUpdate` use broad spec bodies but allow only label mutation. Clients can accidentally mutate name or data; implementations need clear validation and tests.
- Delete status codes are inconsistent across resources: service delete returns `200`, while secret/config delete return `204`. Generic resource clients should not assume one deletion success status.
- Distribution inspection maps authentication failure and missing image to `401`, which can blur authorization and not-found handling for clients.

## Test Signals

Useful validation signals for this chunk include:

- Swagger/OpenAPI validation for operation IDs, path parameters, required query parameters, response schemas, and `$ref` targets.
- Generated-client tests for required `version` parameters on swarm/service/secret/config updates and correct encoding of boolean rotation/force flags.
- Service lifecycle tests covering create warnings, duplicate-name `409`, non-eligible-network `403`, inspect by ID/name, delete `200`, update with `registryAuthFrom`, explicit `X-Registry-Auth`, stale versions, and `rollback=previous`.
- Log endpoint tests covering `stdout`/`stderr`, `tail`, `since`, `timestamps`, `details`, `follow=false` `200` responses, `follow=true` `101` hijack/raw-stream responses, unsupported logging drivers, missing resources, and non-swarm `503`.
- Task list/inspect tests covering filters for desired state, ID, label, name, node, and service, plus task history where running and shutdown records coexist for the same service slot.
- Secret and config tests covering list filters, create with labels/data, duplicate-name `409`, inspect without leaking secret data, delete `204`, label-only update with required version, attempted name/data updates, stale versions, and non-swarm `503`.
- Distribution tests covering successful descriptor/platform decoding, private registry auth failures, missing image behavior documented as `401`, multi-platform manifest lists, and registry/server errors.
- Contract tests should specifically check the `Warning` versus `Warnings` mismatch and the `SecretSpec.Data`/`ConfigSpec.Data` array-versus-string mismatch against real daemon responses.
