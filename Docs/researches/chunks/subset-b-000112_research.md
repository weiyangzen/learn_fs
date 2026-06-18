# sources/cloud-native/moby/api/docs/v1.31.yaml lines 7635-9052

## Scope

This chunk is an OpenAPI/Swagger 2.0 slice of Docker Engine API v1.31. It starts inside the `POST /swarm/init` request-body schema, then covers swarm join/leave/update/unlock operations, service lifecycle and logs, task listing/inspection/logs, secret and config lifecycle operations, registry distribution inspection, and the experimental interactive session endpoint.

The source is API contract documentation, not executable implementation. It defines request parameters, response schemas, examples, media types, operation IDs, tags, and status codes used by Docker API documentation, generated clients, SDK bindings, and daemon route conformance tests.

## Purpose

The endpoints in this chunk expose swarm-mode cluster administration and workload control:

- swarm endpoints initialize or join manager state, leave the cluster, update persisted swarm configuration, rotate join/unlock material, and unlock autolocked managers;
- service endpoints create, inspect, update, delete, list, and stream logs for swarm services;
- task endpoints expose scheduler task state and task logs;
- secret and config endpoints manage swarm-scoped data objects consumed by service task templates;
- distribution inspection queries a registry for image descriptor and supported-platform metadata;
- the experimental session endpoint upgrades the client connection to an HTTP/2 transport that lets the daemon call client-side services.

The range also documents several operational guardrails: required version parameters for concurrent swarm/service/secret/config updates, `503` responses when the daemon is not in the right swarm state, registry auth headers for private service images, and raw-stream connection hijacking for logs/session flows.

## Important APIs And Types

- `SwarmInit` fragment: the chunk includes the request-body fields `AdvertiseAddr`, `DataPathAddr`, `ForceNewCluster`, and `Spec`. The omitted start of the operation is immediately before this range; the visible response returns the new node ID on `200`.
- `POST /swarm/join` (`SwarmJoin`): accepts a body with required `ListenAddr`, `RemoteAddrs`, and `JoinToken`; optional `AdvertiseAddr` and `DataPathAddr` control node advertisement and data-path traffic.
- `POST /swarm/leave` (`SwarmLeave`): accepts a `force` query boolean for leaving even when doing so may break the cluster or remove the last manager.
- `POST /swarm/update` (`SwarmUpdate`): consumes `#/definitions/SwarmSpec`, requires a `version` query integer, and can rotate worker tokens, manager tokens, or the manager unlock key.
- `GET /swarm/unlockkey` (`SwarmUnlockkey`): returns an object containing `UnlockKey`.
- `POST /swarm/unlock` (`SwarmUnlock`): accepts an `UnlockKey` body to unlock a locked manager.
- `GET /services` (`ServiceList`): returns an array of `#/definitions/Service` and supports JSON-string filters for service id, label, mode, and name.
- `POST /services/create` (`ServiceCreate`): consumes `#/definitions/ServiceSpec` with examples for task template, mounts, DNS, secrets, logging driver, resources, restart policy, replicated mode, update/rollback config, endpoint ports, and labels. It may receive `X-Registry-Auth`.
- `GET /services/{id}` (`ServiceInspect`): returns `#/definitions/Service`; `insertDefaults=true` asks the daemon to fill empty fields with defaults.
- `DELETE /services/{id}` (`ServiceDelete`): deletes a service by ID or name.
- `POST /services/{id}/update` (`ServiceUpdate`): consumes a full `ServiceSpec`, requires a `version` query integer, supports `registryAuthFrom=spec|previous-spec`, supports `rollback=previous`, and can receive `X-Registry-Auth`. Successful responses use `#/definitions/ServiceUpdateResponse`.
- `GET /services/{id}/logs` (`ServiceLogs`) and `GET /tasks/{id}/logs` (`TaskLogs`): return service/task stdout and stderr as either `101` raw stream after connection hijack or `200` string body. Query controls include `details`, `follow`, `stdout`, `stderr`, `since`, `timestamps`, and string-typed `tail`.
- `GET /tasks` (`TaskList`) and `GET /tasks/{id}` (`TaskInspect`): expose `#/definitions/Task`; task-list filters are `desired-state`, `id`, `label`, `name`, `node`, and `service`.
- `SecretList`, `SecretCreate`, `SecretInspect`, `SecretDelete`, and `SecretUpdate`: manage `#/definitions/Secret` and `#/definitions/SecretSpec`. Secret update requires `version` and documents labels as the only mutable field.
- `ConfigList`, `ConfigCreate`, `ConfigInspect`, `ConfigDelete`, and `ConfigUpdate`: mirror the secret lifecycle for `#/definitions/Config` and `#/definitions/ConfigSpec`. Config update also requires `version` and documents labels as the only mutable field.
- `GET /distribution/{name}/json` (`DistributionInspect`): returns an inline `DistributionInspect` object with required `Descriptor` and `Platforms`.
- `POST /session` (`Session`): experimental endpoint that upgrades to `h2c` and produces `application/vnd.docker.raw-stream`.

Referenced schema definitions include `SwarmSpec`, `ServiceSpec`, `Service`, `ServiceUpdateResponse`, `Task`, `SecretSpec`, `Secret`, `ConfigSpec`, `Config`, `Driver`, and `ErrorResponse`.

## Control Flow

Swarm setup and maintenance are request-body driven. `SwarmJoin` requires a listening address, existing manager addresses, and a join token. `SwarmLeave` is a small state transition controlled by `force`. `SwarmUpdate` follows an optimistic-concurrency flow: clients read the current swarm object version, submit a `SwarmSpec` with `version`, and optionally ask the manager to rotate tokens or the unlock key. Autolock flows split key retrieval (`SwarmUnlockkey`) from key submission (`SwarmUnlock`).

Service creation and update accept the service's desired state as a `ServiceSpec`. The spec composes task template, scheduling mode, update/rollback strategy, attached networks, and endpoint/load-balancing configuration. Create returns a generated service ID plus an optional warning. Update is versioned and can either apply the supplied spec or, when `rollback=previous`, ignore the supplied spec and roll back server-side to the previous service spec. Registry credentials are supplied either by `X-Registry-Auth` or, for update, by the `registryAuthFrom` selector.

Service and task log endpoints share the same flow. The path `id` selects a service or task, stream selectors choose stdout and/or stderr, and additional query parameters control context, timestamps, time filtering, and tailing. With `follow=true`, the daemon returns `101` with connection-upgrade semantics and then hijacks the HTTP connection to stream Docker raw multiplexed output. Without follow, a successful response is modeled as a `200` string body.

Task list is a read-only scheduler query with a JSON-encoded `filters` query string. Task inspect is a direct lookup. Secret and config list endpoints use the same JSON-string filter pattern, create endpoints return a generated ID, inspect endpoints return versioned objects, delete endpoints return `204`, and update endpoints are versioned writes over object specs.

`DistributionInspect` is a registry-backed read: the daemon contacts the registry for the named image and returns descriptor digest/media/size/URL information plus platform records. `Session` is a transport handshake: clients request an HTTP/1.1 upgrade to `h2c`, and the daemon replies with `101 UPGRADED` before using the raw connection for an HTTP/2-based session.

## State And Persistence Behavior

The YAML file itself has no runtime state, but it documents endpoints that read and mutate several persisted stores:

- swarm init/join/leave/update mutate local swarm membership and Raft-backed cluster configuration;
- join tokens and manager unlock keys are sensitive cluster credentials that can be rotated or submitted through this API;
- service create/update/delete mutate swarm service objects and cause the orchestrator to create, update, roll back, or remove tasks;
- task list/inspect read scheduler state such as task version, desired state, runtime status, container ID/PID/exit code, service ID, node ID, slot, and network attachments;
- service and task logs read log data from task containers and can keep a live stream open;
- secret create persists secret metadata plus secret data or external-driver references, while inspect/list omit secret payload data according to the `SecretSpec.Data` definition;
- config create persists base64 config data, with a larger documented size limit than secrets;
- secret/config updates mutate labels under object-version concurrency checks, while data and most spec fields are immutable in this API version;
- distribution inspection reads remote registry state rather than local image store state;
- session setup creates a live bidirectional integration channel rather than a persisted object.

The visible definitions document important data limits and persistence behavior: `SecretSpec.Data` is base64 RFC 4648 data, must be empty when an external secret driver is used, is create-only, is not returned by other endpoints, and has a 500KB maximum. `ConfigSpec.Data` is base64 data with a 1000KB maximum.

## Dependencies

This chunk depends on the surrounding Docker Engine Swagger conventions: Swagger 2.0 path syntax, `$ref` references into `definitions`, `allOf` schema composition, `x-go-name`, operation IDs, ReDoc markdown descriptions, and a shared `ErrorResponse` body shape.

Runtime dependencies implied by the contract include:

- swarmkit manager state, Raft object versions, scheduler tasks, join tokens, unlock keys, CA/encryption settings, and service update/rollback machinery;
- Docker networking and overlay data-path configuration through `AdvertiseAddr`, `DataPathAddr`, service networks, endpoint specs, VIP/DNSRR modes, published ports, and task network attachments;
- registry authentication and image resolution for service create/update through `X-Registry-Auth`;
- supported logging drivers, specifically `json-file` or `journald`, for service/task log retrieval;
- external secret drivers through the shared `Driver` schema;
- registry distribution APIs for descriptor/platform lookup;
- HTTP connection hijacking and h2c upgrade support for logs and experimental sessions.

## Integration Points

The operation IDs are stable integration names for generated clients and API docs: `SwarmJoin`, `SwarmLeave`, `SwarmUpdate`, `SwarmUnlockkey`, `SwarmUnlock`, `ServiceList`, `ServiceCreate`, `ServiceInspect`, `ServiceDelete`, `ServiceUpdate`, `ServiceLogs`, `TaskList`, `TaskInspect`, `TaskLogs`, `SecretList`, `SecretCreate`, `SecretInspect`, `SecretDelete`, `SecretUpdate`, `ConfigList`, `ConfigCreate`, `ConfigInspect`, `ConfigDelete`, `ConfigUpdate`, `DistributionInspect`, and `Session`.

Swarm endpoints integrate with cluster bootstrap, manager recovery, token rotation, and autolock workflows. Service endpoints integrate with CLI commands and orchestration tooling that maintain desired service state, pass registry credentials, inspect service endpoint state, and monitor rollout warnings. Task endpoints integrate with schedulers, dashboards, and incident workflows that need per-replica placement, status, and logs.

Secrets and configs integrate with `TaskSpec.ContainerSpec.Secrets` and `TaskSpec.ContainerSpec.Configs` definitions outside this path chunk: services reference IDs/names plus file targets, UID/GID, and file modes so swarm can materialize data into task containers. `DistributionInspect` integrates the engine API with registry metadata checks. `Session` integrates the daemon with advanced client-side capabilities over an upgraded connection.

## Risks And Edge Cases

- This chunk begins mid-`SwarmInit`, so complete conclusions for that operation require the preceding lines. The visible fragment still documents advertised/data-path addresses, forced cluster creation, and `SwarmSpec`.
- Most swarm, service, task, secret, and config endpoints can return `503` when the node is not part of a swarm. `SwarmJoin` also uses `503` when the node is already part of a swarm.
- Version parameters on `SwarmUpdate`, `ServiceUpdate`, `SecretUpdate`, and `ConfigUpdate` are required concurrency guards. Clients that update from stale inspected objects should expect rejection or conflict-like errors.
- `force=true` on `SwarmLeave` can intentionally break the cluster or remove the last manager, so automation should make this opt-in.
- Token and unlock-key rotation are security-sensitive state changes; logging request URLs with rotation flags or response bodies with unlock keys can leak operational material.
- `X-Registry-Auth` is base64-encoded authentication data. Debug logging and client tracing must treat it as secret.
- `ServiceCreate` can return `403` for networks not eligible for services and `409` on name conflicts; clients need distinct handling from ordinary validation errors.
- `ServiceUpdate` rollback semantics ignore the supplied spec when `rollback=previous`; callers must not assume the request body was applied in that mode.
- Service/task logs require `json-file` or `journald`; other logging drivers may not support these endpoints as documented.
- `follow=true` changes response handling from ordinary HTTP body reads to `101` connection hijacking. Generic JSON clients often need special transport code here.
- Log `stdout` and `stderr` default to false, and `tail` is string-typed because it accepts either an integer or `all`.
- List filters are JSON-encoded strings, not structured query objects. Bad escaping or single-value encoding mistakes can produce incorrect filtering.
- The `TaskLogs` operation in this chunk does not have a visible `tags: ["Task"]` line before `/secrets`; generated grouping may differ from nearby operations if the full file also lacks it.
- Secret and config update bodies are full specs even though only `Labels` are mutable. Partial specs or changed immutable fields can be rejected.
- `SecretSpec.Data` is create-only and not returned by inspect/list. Clients cannot use inspect responses to recover secret payloads.
- `DistributionInspect` contacts a registry and can return `401` for failed authentication or no image found, so callers should not treat it as a local image lookup.
- `Session` is explicitly experimental and only available with daemon experimental features enabled; its protocol may change.

## Test Signals

Useful validation for this API contract includes:

- Swagger/OpenAPI linting over `api/docs/v1.31.yaml` for `$ref` resolution, declared path parameters, unique `operationId` values, valid response schemas, and valid `allOf` composition.
- Client-generation tests confirming version query parameters remain required for swarm/service/secret/config updates and that `filters`, `tail`, `registryAuthFrom`, and `rollback` stay string-typed where documented.
- Swarm integration tests for join required fields, already-in-swarm `503`, forced and unforced leave behavior, update with stale/current versions, token rotation flags, unlock-key retrieval, and unlock with valid/invalid keys.
- Service lifecycle tests for create warnings, private registry auth, ineligible-network `403`, name-conflict `409`, inspect by ID/name, `insertDefaults`, delete missing service `404`, versioned update, registry auth source selection, and rollback to previous spec.
- Service update strategy tests covering replicated/global mode, update and rollback config fields, endpoint modes, published ports, secret/config references, DNS config, mounts, resources, restart policy, and log-driver configuration.
- Task API tests for list filters (`desired-state`, `id`, `label`, `name`, `node`, `service`), inspect missing task `404`, and response shape around status, desired state, container status, and network attachments.
- Log endpoint tests for `stdout`, `stderr`, `details`, `since`, `timestamps`, `tail=all`, numeric tail, `follow=false` `200`, and `follow=true` `101` raw-stream handling against supported and unsupported logging drivers.
- Secret lifecycle tests for create with inline base64 data, create with external `Driver`, duplicate-name `409`, list filters, inspect without returned secret data, label-only update with version, immutable-field rejection, stale-version rejection, and delete `204`.
- Config lifecycle tests parallel to secret tests, including base64 data handling, documented size limit behavior, list filters, label-only updates, stale version handling, and delete `204`.
- Distribution inspection tests for successful descriptor/platform payloads, authenticated/private registry failure, missing image `401`, and registry/server error mapping.
- Experimental session tests for feature-gate behavior, bad upgrade parameters, `101` h2c upgrade, and compatibility with client-side gRPC service exposure over the hijacked connection.
