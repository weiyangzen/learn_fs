# sources/cloud-native/moby/api/docs/v1.27.yaml lines 7808-8026

## Scope

This chunk covers the end of the Docker Engine API v1.27 task endpoints and the full secret endpoint group present in this range. It starts with the `TaskInspect` path and then defines `SecretList`, `SecretCreate`, `SecretInspect`, `SecretDelete`, and `SecretUpdate`.

The source is an OpenAPI/Swagger YAML contract rather than executable code. The operational behavior described here is the daemon API surface that clients, generated SDKs, documentation, and compatibility tests consume.

## Purpose

The task endpoint exposes read-only inspection of a single swarm task by ID. The secret endpoints expose swarm secret lifecycle operations: list secrets, create a secret, inspect one secret, delete one secret, and update mutable secret metadata.

These APIs are part of Docker swarm mode. Every operation in this chunk can return `503` when the node is not part of a swarm, which makes swarm membership a required runtime precondition even though the spec itself is static documentation.

## Important APIs And Types

- `GET /tasks/{id}` with operationId `TaskInspect` returns a `Task` object for an ID path parameter. It reports `404` for a missing task, `500` for daemon errors, and `503` outside swarm mode.
- `GET /secrets` with operationId `SecretList` returns an array of `Secret` objects. It accepts a `filters` query parameter encoded as JSON `map[string][]string`; this chunk documents `names=<secret name>` as the available filter.
- `POST /secrets/create` with operationId `SecretCreate` consumes a JSON body shaped as `SecretSpec` and returns a small object containing the created secret `ID`. It can return `409` when the requested name conflicts with an existing object.
- `GET /secrets/{id}` with operationId `SecretInspect` returns a `Secret` for an ID path parameter. The example shows metadata such as `ID`, `Version.Index`, timestamps, and `Spec.Name`, but not secret data.
- `DELETE /secrets/{id}` with operationId `SecretDelete` removes a secret by ID and returns `204` on success.
- `POST /secrets/{id}/update` with operationId `SecretUpdate` accepts an ID path parameter, a `SecretSpec` body, and a required integer `version` query parameter. The version prevents conflicting writes.
- `SecretSpec` is the client-provided shape for secret creation and update. It includes `Name`, `Labels`, and `Data`, with `Data` described as base64-url-safe-encoded secret data.
- `Secret` is the response object for persisted secrets. The definition includes `ID`, `Version`, `CreatedAt`, `UpdatedAt`, and `Spec`.
- `ErrorResponse` is the shared error schema with a required string `message`.

## Control Flow

The task inspection flow is direct: the client supplies `id` in the path, the daemon resolves that task in swarm state, and the response is either the `Task` representation or an `ErrorResponse`. The immediately preceding task list filters in the same API area support narrowing by desired state, ID, label, name, node, or service; `TaskInspect` is the point lookup counterpart.

The secret list flow accepts an optional JSON-encoded filter string, applies the supported `names` selector, and returns zero or more `Secret` summaries. The create flow validates the supplied `SecretSpec`, rejects duplicate names with `409`, persists the secret in swarm state, and returns only the new ID. The inspect flow looks up one secret and returns its metadata/spec representation. The delete flow removes an existing secret and has an empty `204` success body.

The update flow is the most constrained endpoint in the chunk. It requires the caller to send the current object `version` in the query string and a `SecretSpec` body. The description states that only `Labels` can be updated; all other fields must remain unchanged from the `SecretInspect` response. This creates an inspect-modify-update pattern: read the current object, preserve immutable fields, change labels, and submit the matching version.

## State And Persistence Behavior

The YAML does not implement persistence itself, but it documents stateful swarm objects. Secrets are persisted swarm resources with stable IDs, object versions, creation/update timestamps, names, labels, and secret payload material supplied at creation time. Versioned updates imply optimistic concurrency control; a stale or missing version should not overwrite a newer secret state.

Secret data is accepted during create through `SecretSpec.Data`, but the response examples for list and inspect omit data and show only metadata/spec name. That is an important API behavior signal: clients should not expect secret material to be returned by ordinary list or inspect responses.

Task inspection is read-only state access. The returned `Task` object, defined earlier in the file, includes task identity, version, timestamps, labels, `TaskSpec`, service/node placement, current `Status`, container status, and `DesiredState`.

## Dependencies

This chunk depends on shared definitions elsewhere in `v1.27.yaml`:

- `Task` for `TaskInspect` success responses.
- `SecretSpec` for create/update request bodies.
- `Secret` for list/inspect success responses.
- `ObjectVersion` through the `Task` and `Secret` version fields.
- `ErrorResponse` for documented error bodies.

At runtime, the documented endpoints depend on Docker Engine swarm mode and its manager/state-store APIs. Integration clients also depend on correct Swagger semantics for JSON body generation, path parameter handling, query parameter encoding, and response status handling.

## Integration Points

The operation IDs are client-generation hooks. SDKs and API wrappers can expose methods named after `TaskInspect`, `SecretList`, `SecretCreate`, `SecretInspect`, `SecretDelete`, and `SecretUpdate`.

The secret endpoints integrate with swarm service deployment because services can reference secrets by ID/name, while secret lifecycle is managed independently through this API group. Delete/update behavior must therefore respect swarm object references and concurrency; the spec documents response shapes but leaves reference-conflict details to daemon implementation.

The `filters` parameters integrate with Docker's broader API convention of accepting JSON-encoded `map[string][]string` query values. Clients that already implement filter encoding for containers, images, services, or tasks can reuse that mechanism for secret names.

The update endpoint links back to `SecretInspect` in its body description, establishing an API contract that callers should base update bodies on the inspect result and preserve all non-label fields.

## Risks And Edge Cases

- `SecretUpdate` only permits label changes, but its body schema is the broader `SecretSpec`. Clients can accidentally send changed `Name` or `Data` values; daemon-side validation must reject or ignore illegal mutations consistently.
- The required `version` query parameter is the only documented concurrency guard. Generated clients must not omit it, and callers need to handle stale-version conflicts even though this chunk only lists `404`, `500`, and `503` responses for update.
- `SecretCreate` documents a `409` name conflict, but `SecretUpdate` does not list a `409` or `400` response for version conflicts or immutable-field changes. That mismatch can make generated error handling incomplete.
- The `SecretSpec.Data` definition says "Base64-url-safe-encoded secret data" but the local schema declares `Data` as an array of strings, while the create example shows a single string. That schema/example mismatch is a client-generation risk.
- The `Secret` definition elsewhere in this file references `#/definitions/ServiceSpec` for `Spec`, while secret endpoints use `SecretSpec` semantics and examples show `Spec.Name`. This appears inconsistent and can lead generated clients to model secret responses incorrectly.
- Secret list filtering documents `names=<secret name>` plural, whereas other Docker API filters often use singular or multiple accepted aliases. Callers should rely on daemon behavior/tests rather than assuming undocumented filter keys.
- All endpoints are swarm-specific and return `503` outside swarm mode. Tests and clients need to distinguish "resource missing" from "daemon not in swarm".
- Secret inspect/list examples intentionally omit secret payload material. Any implementation or client that exposes `Data` from read responses risks leaking sensitive material.

## Test Signals

Useful validation signals for this API chunk include:

- Swagger/OpenAPI validation should catch structural issues in path parameters, response schemas, required fields, and operation IDs.
- Generated-client tests should verify `TaskInspect` sends the task ID in the path and decodes `Task` plus `ErrorResponse` statuses.
- Secret create tests should cover successful creation with name, labels, and base64 data; duplicate-name `409`; malformed data/body handling; and non-swarm `503`.
- Secret list tests should cover empty lists, populated lists, and JSON-encoded `names` filters.
- Secret inspect/delete tests should cover existing IDs, missing IDs returning `404`, and no-body `204` delete success.
- Secret update tests should exercise the inspect-modify-update pattern, required `version`, stale versions, label-only updates, attempted name/data changes, and missing IDs.
- Compatibility tests should compare generated models against real daemon responses, especially the `SecretSpec.Data` schema/example mismatch and the `Secret.Spec` reference inconsistency.
