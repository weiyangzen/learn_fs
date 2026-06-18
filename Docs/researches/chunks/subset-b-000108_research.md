# sources/cloud-native/moby/api/docs/v1.29.yaml lines 7775-8320

## Scope

This chunk is an OpenAPI/Swagger 2.0 slice of Docker Engine API v1.29. It starts at the tail of the `POST /services/{id}/update` parameter list, then covers service log retrieval, swarm task listing/inspection/log retrieval, and swarm secret list/create/inspect/delete/update endpoints.

The range is API contract documentation rather than executable implementation. It defines request parameters, response schemas, examples, media types, operation IDs, tags, and status codes used by Docker clients, SDK generators, API documentation, and daemon route conformance tests.

## Purpose

The endpoints in this chunk expose swarm runtime observability and secret-management operations:

- service and task log endpoints let clients fetch stdout/stderr for swarm workloads, either as a bounded response body or as a hijacked raw stream;
- task endpoints let clients enumerate and inspect the scheduler's per-replica task objects;
- secret endpoints let clients manage Docker swarm secrets through the API, including optimistic-concurrency updates.

The service-update fragment also documents registry authentication and rollback controls for mutating a swarm service, which is relevant to private image pulls and safe update retries.

## Important APIs And Types

- `ServiceUpdate` fragment: requires a `version` query integer to avoid conflicting writes, accepts `registryAuthFrom` with `spec` or `previous-spec`, accepts a `rollback` query value of `previous`, and can receive `X-Registry-Auth` as a base64-encoded registry auth header.
- `GET /services/{id}/logs` with operation ID `ServiceLogs`: returns service `stdout`/`stderr` logs. It produces `application/vnd.docker.raw-stream` for upgraded streaming and `application/json` for non-upgraded response handling.
- `GET /tasks` with operation ID `TaskList`: returns an array of `#/definitions/Task`. The example task shape includes `ID`, `Version.Index`, timestamps, `Spec`, `ServiceID`, `Slot`, `NodeID`, `Status`, `DesiredState`, and `NetworksAttachments`.
- `GET /tasks/{id}` with operation ID `TaskInspect`: returns a single `Task` by ID.
- `GET /tasks/{id}/logs` with operation ID `TaskLogs`: mirrors service log behavior for one task.
- `GET /secrets` with operation ID `SecretList`: returns an array of `#/definitions/Secret`.
- `POST /secrets/create` with operation ID `SecretCreate`: consumes a `SecretSpec` body and returns a `201` object containing the created secret `ID`. The example body includes `Name`, `Labels`, and base64 `Data`.
- `GET /secrets/{id}` with operation ID `SecretInspect`: returns a `Secret`.
- `DELETE /secrets/{id}` with operation ID `SecretDelete`: deletes a secret and returns `204` on success.
- `POST /secrets/{id}/update` with operation ID `SecretUpdate`: accepts a `SecretSpec` body and a required `version` query value. The description says only `Labels` can currently be updated; all other fields must remain unchanged from `SecretInspect`.

Referenced schema definitions in this range are `Task`, `Secret`, `SecretSpec`, and `ErrorResponse`.

## Control Flow

The service and task log endpoints use the same request flow. The client identifies the service or task with a path `id`, selects log streams with `stdout` and/or `stderr`, optionally includes contextual `details`, filters by `since`, controls timestamp decoration with `timestamps`, and limits output with `tail`. If `follow=true`, the server returns `101 Switching Protocols` with a connection upgrade and then hijacks the HTTP connection to stream Docker's raw multiplexed output. Without follow, successful output is represented as a `200` string response body.

Task listing accepts an optional `filters` query parameter encoded as JSON `map[string][]string`. The documented filters narrow scheduler objects by desired state, task ID, label, task name, node, or service. Task inspection is a direct path lookup by task ID.

Secret creation consumes a JSON `SecretSpec` and produces a newly allocated secret ID. Secret inspection and deletion are path-ID operations. Secret update is a versioned write: clients are expected to inspect the current secret, preserve immutable fields, change only labels, and submit the current object version so the daemon can reject stale writes.

Error flow is consistent across the swarm endpoints: `404` identifies missing resources, `500` covers daemon/server errors, and `503` signals that the target node is not part of a swarm. `SecretCreate` adds `409` for name conflicts.

## State And Persistence Behavior

The YAML itself has no runtime state. It describes daemon operations that read or mutate swarm state:

- task and service log endpoints read log data from task containers through supported logging drivers and may keep a connection open when following;
- task list/inspect endpoints read swarm manager task state, including task versions, desired state, runtime status, container status, and network attachments;
- secret list/inspect read swarm secret metadata and specs;
- secret create persists a new swarm secret object, including secret data supplied in `SecretSpec.Data`;
- secret delete removes a swarm secret object;
- secret update mutates secret metadata under optimistic concurrency, with labels documented as the only mutable field in this API version.

The log endpoints explicitly depend on `json-file` or `journald` logging drivers. The secret update `version` parameter and service update `version` parameter are concurrency guards for persisted swarm objects.

## Dependencies

This chunk depends on shared Docker API definitions and conventions:

- Swagger 2.0 path, parameter, response, and schema syntax from the surrounding `v1.29.yaml` file.
- `#/definitions/Task`, `#/definitions/Secret`, `#/definitions/SecretSpec`, and `#/definitions/ErrorResponse`.
- Docker raw-stream framing and HTTP hijacking semantics documented by the `ContainerAttach` operation.
- Swarm manager state for tasks, services, and secrets; most endpoints can fail with `503` when the daemon is not a swarm node.
- Logging-driver support from `json-file` or `journald` for service/task logs.
- Registry-auth handling for service updates through `X-Registry-Auth` and `registryAuthFrom`.

## Integration Points

The `operationId` values are integration names for generated Docker API clients and documentation navigation: `ServiceLogs`, `TaskList`, `TaskInspect`, `TaskLogs`, `SecretList`, `SecretCreate`, `SecretInspect`, `SecretDelete`, and `SecretUpdate`.

The task endpoints integrate with service orchestration workflows. Operators can list tasks for a service, inspect a task's current status and network attachments, then request logs for a specific task. The examples show task objects linked to `ServiceID`, `NodeID`, slot, desired state, and network attachments, which are the fields higher-level CLI and SDK tooling usually expose.

The secret endpoints integrate with swarm secret lifecycle management. `SecretCreate` accepts `SecretSpec` data, `SecretList` and `SecretInspect` expose metadata and spec details, `SecretDelete` removes the object, and `SecretUpdate` preserves the API invariant that secret payloads and most spec fields are immutable after creation.

The log endpoints integrate with clients that understand both ordinary HTTP response bodies and Docker's upgraded raw stream protocol. Clients must negotiate or handle `101` differently from `200`.

## Risks And Edge Cases

- The chunk starts inside `ServiceUpdate`, so whole-operation conclusions for service update require the preceding lines. This range still captures the important version, rollback, registry-auth, and tag fields.
- `follow=true` changes response handling from normal HTTP body consumption to connection hijacking. Client generators that treat `101` like a JSON response will mishandle streamed logs.
- The service/task log descriptions say logs work only with `json-file` or `journald`; callers may receive errors or empty behavior with other logging drivers.
- `stdout` and `stderr` both default to `false`. Clients that omit both may not get useful log output unless daemon-side behavior chooses defaults outside this spec.
- `tail` is typed as a string because it accepts either an integer or `all`, so client validation must not force it to a numeric-only type.
- `filters` is a JSON-encoded string, not a structured query object. Incorrect escaping or incompatible `map[string][]string` encoding can silently broaden or break task/secret list queries.
- The task log endpoint lacks a `tags: ["Task"]` line in this displayed range, unlike nearby endpoints. If absent in the full file, generated documentation/client grouping may be inconsistent.
- Secret update accepts a full `SecretSpec` but only labels are mutable. Sending a spec built from partial local state risks rejection or unintended incompatibility because non-label fields must match `SecretInspect` response values.
- Secret creation can return `409` on name conflict; clients need create-or-get or retry behavior to be explicit.
- Secrets are swarm-scoped; all secret endpoints can fail with `503` when the daemon is not in a swarm, which is a deployment-state error rather than a missing-route error.

## Test Signals

Useful validation for this API contract includes:

- OpenAPI linting that verifies path parameters are declared, response schemas resolve, `operationId` values are unique, and produced/consumed media types are valid.
- Client-generation tests confirming `tail` and `filters` stay string-typed, `version` remains required for updates, and log operations can represent both `101` stream and `200` body responses.
- API integration tests for `GET /tasks` filters: `desired-state`, `id`, `label`, `name`, `node`, and `service`.
- Swarm-mode tests for `TaskInspect`, `SecretInspect`, and missing-object `404` behavior.
- Secret lifecycle tests covering create success, duplicate-name `409`, list visibility, inspect shape, label-only update with stale-version rejection, immutable-field rejection, and delete `204`.
- Log endpoint tests covering `stdout`, `stderr`, `timestamps`, `since`, `tail=all`, numeric `tail`, `details`, `follow=false` `200`, and `follow=true` `101` hijacked raw-stream behavior.
- Negative tests outside swarm mode should assert the documented `503` response for task, service-log, and secret endpoints.
