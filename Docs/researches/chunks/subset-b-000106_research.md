# sources/cloud-native/moby/api/docs/v1.28.yaml lines 7788-8189

## Scope

This chunk is part of Docker Engine API v1.28's Swagger/OpenAPI document. It starts inside the `ServiceLogs` endpoint parameter list, then covers Swarm task read APIs and the Swarm secret lifecycle APIs:

- `GET /services/{id}/logs`, operation `ServiceLogs`, lines 7788-7829 in this chunk.
- `GET /tasks`, operation `TaskList`, lines 7830-7975.
- `GET /tasks/{id}`, operation `TaskInspect`, lines 7976-8005.
- `GET /secrets`, operation `SecretList`, lines 8006-8043.
- `POST /secrets/create`, operation `SecretCreate`, lines 8044-8087.
- `GET /secrets/{id}`, operation `SecretInspect`, lines 8088-8125.
- `DELETE /secrets/{id}`, operation `SecretDelete`, lines 8126-8152.
- `POST /secrets/{id}/update`, operation `SecretUpdate`, lines 8153-8189.

The document is declarative API metadata rather than executable code. Its behavior matters because Docker clients, generated SDKs, documentation pages, compatibility tests, and API conformance tooling can use these operation IDs, schemas, parameter names, and response codes as the contract for Engine v1.28.

## Purpose

The `ServiceLogs` tail in this range defines how callers select and stream service task logs. It documents an `id` path parameter accepting a service ID or name, booleans for `details`, `follow`, `stdout`, `stderr`, and `timestamps`, an integer `since` UNIX timestamp, and a string `tail` selector that accepts an integer or `all`. When `follow=true`, the endpoint returns a `101` upgrade and hijacks the connection to send raw output using the attach stream format; otherwise it can return logs as a normal response body.

The task endpoints expose Swarm scheduler state. `TaskList` returns an array of `#/definitions/Task` objects and supports a JSON-encoded `filters` query parameter. The documented filters are `desired-state`, `id`, `label`, `name`, `node`, and `service`. `TaskInspect` returns one `Task` by path `id`.

The secret endpoints expose Swarm secret metadata and management. `SecretList` returns an array of `#/definitions/Secret` and supports filtering by secret names. `SecretCreate` accepts a `SecretSpec` body and returns a small object containing the created secret `ID`. `SecretInspect` returns one `Secret`; `SecretDelete` removes one secret; `SecretUpdate` accepts a `SecretSpec` body plus a required `version` query parameter for optimistic concurrency.

## Important APIs, Types, And Functions

- `ServiceLogs` uses service-scoped log options: `details`, `follow`, `stdout`, `stderr`, `since`, `timestamps`, and `tail`. Its streaming mode is not ordinary JSON; it upgrades and hijacks the HTTP connection.
- `TaskList` is a read-only collection API returning `array<Task>`. The example shows task identity, object version, creation/update timestamps, `TaskSpec`, `ServiceID`, `Slot`, `NodeID`, `Status`, `DesiredState`, and `NetworksAttachments`.
- `TaskInspect` is a read-only item API returning `Task` or an `ErrorResponse` for missing tasks, daemon errors, or non-Swarm nodes.
- `SecretList` is a read-only collection API returning `array<Secret>` with a JSON-encoded filter map. The only documented filter in this chunk is `names=<secret name>`.
- `SecretCreate` is a mutating API consuming JSON. Its body is `SecretSpec`; the example includes `Name`, `Labels`, and base64-looking `Data`.
- `SecretInspect` returns secret metadata and spec fields for a specific secret ID.
- `SecretDelete` returns `204` with no body on success and error objects for missing secrets, daemon errors, or non-Swarm nodes.
- `SecretUpdate` is a mutating API on `/secrets/{id}/update`. It requires path `id`, body `SecretSpec`, and query `version` as `int64`.
- `Task`, `Secret`, `SecretSpec`, and `ErrorResponse` are shared definitions elsewhere in this file. `Task` references `ObjectVersion`, `TaskSpec`, and `TaskState`. `SecretSpec` defines `Name`, `Labels`, and `Data`; `ErrorResponse` has required `message`.

## Control Flow

At runtime these paths are expected to map to Engine daemon handlers, but this YAML chunk only defines the external contract:

1. A client sends an HTTP request to the documented path and method.
2. Path parameters are bound from URL segments, query parameters are parsed from the request URL, and JSON request bodies are decoded for secret create/update.
3. Swarm-aware endpoints require the daemon to be part of a Swarm; otherwise the documented failure mode is `503` with `ErrorResponse`.
4. Read endpoints return JSON schemas on success: `TaskList`, `TaskInspect`, `SecretList`, and `SecretInspect`.
5. Secret mutations return status-only or small JSON responses: `SecretCreate` returns `201` plus an ID object; `SecretDelete` returns `204`; `SecretUpdate` returns `200` with no response schema in this chunk.
6. `ServiceLogs` has a split response flow. Non-following calls can return a normal log body, while following calls switch to `101` connection upgrade and stream raw bytes after hijack.

The `filters` parameters are strings containing JSON-encoded `map[string][]string` data, so client generators must not model them as ordinary structured query objects unless they add custom encoding logic.

## State And Persistence Behavior

The YAML itself persists no state. It describes daemon state exposed by the API:

- `TaskList` and `TaskInspect` read Swarm task state, including scheduler desired state, current status, container status, network attachments, object versions, and timestamps.
- `SecretList` and `SecretInspect` read Swarm secret objects. Secrets are versioned objects with create/update timestamps and a spec.
- `SecretCreate` persists a new secret object in the Swarm manager state. A duplicate name produces `409`.
- `SecretDelete` removes a secret object by ID.
- `SecretUpdate` mutates an existing secret object but is constrained by object version. The chunk says only `Labels` can be updated; every other field must remain unchanged from `SecretInspect`.
- `ServiceLogs` reads log data and may hold an upgraded streaming connection open when following logs.

The required `version` parameter on `SecretUpdate` is the main concurrency-control signal. It prevents blind overwrites of a secret that has changed since the caller inspected it.

## Dependencies

This chunk depends on shared OpenAPI definitions in the same file:

- `#/definitions/Task` for task list and inspect responses.
- `#/definitions/Secret` for secret list and inspect responses.
- `#/definitions/SecretSpec` for secret create/update request bodies.
- `#/definitions/ErrorResponse` for error responses.

It also depends on conventions documented elsewhere in the API spec:

- HTTP connection hijacking and stream framing are delegated to the attach endpoint documentation referenced by `ServiceLogs`.
- Swarm object versioning uses `ObjectVersion.Index`.
- API consumers need Docker's filter encoding convention: JSON string values representing `map[string][]string`.

Operationally, all task and secret endpoints are Swarm integration points. A non-Swarm daemon reports `503`, so clients must be prepared to distinguish "object not found" from "daemon not in Swarm mode".

## Integration Points

The operation IDs are stable integration anchors for generated clients and docs: `ServiceLogs`, `TaskList`, `TaskInspect`, `SecretList`, `SecretCreate`, `SecretInspect`, `SecretDelete`, and `SecretUpdate`.

`TaskList` integrates with service orchestration, node scheduling, and network inspection views. Its example includes `ServiceID`, `NodeID`, slot numbers, task status, desired state, and overlay network attachments, so clients can join task data with services, nodes, containers, and networks.

`ServiceLogs` integrates with terminal-style clients and log collectors. Because following logs hijacks the connection, generated HTTP clients need special handling similar to attach/exec streaming paths rather than treating every success as JSON.

Secret APIs integrate with service deployment and secret distribution. `SecretCreate` accepts secret material in `SecretSpec.Data`, `SecretInspect` returns metadata needed for update, and `SecretUpdate` requires the inspected version. The update endpoint explicitly depends on clients preserving all non-label fields from inspect responses.

## Risks And Edge Cases

- The chunk begins in the middle of `ServiceLogs`; the response definitions and path header are just before the requested range. This research treats only the visible parameters and continuation contract as in scope.
- `ServiceLogs` path parameter description says "ID or name of the container" even though the path is `/services/{id}/logs` and the tag is `Service`. That wording can confuse users and generated documentation.
- `follow=true` changes the HTTP behavior to `101` upgrade and raw stream hijacking. Clients that assume JSON or normal response-body handling will fail or hang.
- The `stdout` and `stderr` booleans default to false. If callers omit both, daemon behavior needs implementation-level confirmation; the spec chunk does not state whether no streams means empty output or a server-side default.
- `tail` is typed as string because it accepts either an integer-like value or `all`. Client generators may not validate this well.
- `filters` is a JSON-encoded string, which is easy to double-encode or encode as normal repeated query keys by mistake.
- The secret update contract is strict: only `Labels` are mutable, and all other fields must remain unchanged. Partial update clients can accidentally send an invalid spec if they do not fetch and preserve the current object first.
- The `SecretSpec.Data` definition elsewhere in the file says `type: array` of strings while the create example shows a single base64 string. This schema/example mismatch can break generated clients or validators.
- The `Secret` definition elsewhere in the file references `#/definitions/ServiceSpec` for `Spec`, which appears inconsistent with the secret examples and with `SecretSpec`. This is a documentation/schema risk for consumers of `SecretInspect` and `SecretList`.
- Secret operations expose names, labels, and possibly data shape through schemas. Documentation and clients must avoid logging or displaying secret material from create/update payloads.
- `SecretUpdate` documents path `id` as ID or name, while inspect/delete path descriptions say ID only. That inconsistency affects client UX and validation.

## Test Signals

Useful validation and regression signals for this chunk include:

- OpenAPI validation that every `$ref` resolves and every operation has unique `operationId` values.
- Contract tests for `TaskList` filters using JSON-encoded `desired-state`, `id`, `label`, `name`, `node`, and `service` maps.
- Contract tests for `SecretList` name filtering with correctly encoded `map[string][]string` query strings.
- API tests confirming non-Swarm daemons return `503` with `ErrorResponse` for task and secret endpoints.
- API tests for task inspect not-found behavior returning `404` with `ErrorResponse`.
- Secret lifecycle tests covering create success `201`, duplicate-name conflict `409`, inspect success, delete success `204`, delete/inspect missing `404`, and update missing `404`.
- Secret update tests covering required `version`, stale-version conflict behavior in implementation, label-only mutation, and rejection or preservation semantics for non-label fields.
- Streaming tests for `ServiceLogs` covering normal log response, `follow=true` upgrade/hijack, `stdout`/`stderr` selection, timestamp formatting, `since`, `tail=all`, numeric `tail`, and invalid tail values.
- Generated-client tests around `SecretSpec.Data` and `Secret.Spec` are especially important because the local schema definitions appear inconsistent with examples and expected secret semantics.
