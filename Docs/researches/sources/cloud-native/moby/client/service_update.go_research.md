# sources/cloud-native/moby/client/service_update.go

## Purpose
Implements swarm service updates, including versioned optimistic concurrency, registry auth metadata, and rollback control.

## APIs, Types, And Functions
`ServiceUpdateOptions` carries `EncodedRegistryAuth`, `RegistryAuthFrom`, `Rollback`, and `QueryRegistry`; `ServiceUpdateResult` carries `Warnings`; `Client.ServiceUpdate` posts a `swarm.ServiceSpec`. It uses API headers such as `X-Registry-Auth`, query values for version/auth/rollback, and `cli.post`.

## Control Flow, State, And Integration
The method trims the service ID, sets `version`, registry auth source, and rollback query parameters, attaches encoded registry auth as a header when present, posts to `/services/{id}/update`, and decodes daemon warnings. It mutates daemon swarm service state, not local client state.

## Risks And Test Signals
Risks include missing version query values causing update conflicts, auth header regressions, rollback semantics drifting, and warning decode failures. Integration is with swarm managers and registry credential resolution.
