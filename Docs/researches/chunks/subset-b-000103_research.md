# sources/cloud-native/moby/api/docs/v1.27.yaml lines 1-7807

## Scope And Purpose

This chunk is the main body of the Docker Engine API v1.27 Swagger 2.0 contract. It defines the API metadata, tags, shared schema definitions, and most path operations from container management through the beginning of task listing. The source is not executable runtime code; it is an authoritative HTTP API description used for generated API documentation and for client/server type generation, as noted in the file header.

The contract exposes Docker Engine behavior over versioned HTTP paths under `/v1.27`. It models the same functional surface that Docker CLI commands call: containers, images, auth, system information, events, exec sessions, volumes, networks, plugins, swarm, nodes, services, and tasks. The chunk stops at line 7807 inside the `TaskList` filter description, before the remaining task and secret path definitions in the file.

## API Metadata And Structure

The top-level Swagger document declares `swagger: "2.0"`, HTTP/HTTPS schemes, JSON and plain-text media types, and `basePath: "/v1.27"`. The `info` section documents the Engine API, standard JSON error response shape, version-prefix behavior, the open schema model, and registry authentication through Base64-encoded `X-Registry-Auth` payloads or identity tokens from `/auth`.

The tag list is a documentation and grouping contract for ReDoc and generated clients. Primary object tags include `Container`, `Image`, `Network`, `Volume`, and `Exec`; swarm-related tags include `Swarm`, `Node`, `Service`, `Task`, and `Secret`; system-level tags include `Plugin` and `System`. Operation IDs follow the local convention described in comments: singular noun plus verb, such as `ContainerList`, `ImageBuild`, `SwarmUpdate`, and `ServiceLogs`.

## Shared Definitions

The `definitions` section builds the reusable data model for the path operations. Major object groups are:

- Container and filesystem definitions: `Config`, `HostConfig`, `Resources`, `HealthConfig`, `RestartPolicy`, `Mount`, `MountPoint`, `MountType`, `DeviceMapping`, `ThrottleDevice`, `ContainerSummary`, and `NetworkConfig`.
- Image and registry definitions: `Image`, `ImageSummary`, `ImageHistoryResponseItem`, `GraphDriver`, `BuildInfo`, `CreateImageInfo`, `PushImageInfo`, `ImageDeleteResponse`, `AuthConfig`, `ErrorDetail`, `ProgressDetail`, `ErrorResponse`, and `IdResponse`.
- Volume and network definitions: `Volume`, `Network`, `IPAM`, `NetworkContainer`, and `EndpointSettings`.
- Plugin definitions: `Plugin`, `PluginMount`, `PluginDevice`, `PluginEnv`, and `PluginInterfaceType`.
- Swarm orchestration definitions: `ObjectVersion`, `NodeSpec`, `Node`, `SwarmSpec`, `ClusterInfo`, `TaskSpec`, `TaskState`, `Task`, `ServiceSpec`, `EndpointPortConfig`, `EndpointSpec`, `Service`, `ServiceUpdateResponse`, `SecretSpec`, and `Secret`.

`HostConfig` composes `Resources` with host-dependent container settings through `allOf`, including binds, log configuration, network mode, port bindings, restart policy, mounts, namespace/security options, cgroup options, tmpfs, sysctls, runtime, and Windows isolation fields. `Config` describes portable container/image configuration such as command, entrypoint, environment, labels, healthcheck, exposed ports, stop signal, and shell.

`ObjectVersion` is important for swarm update safety. Its documentation requires clients to send a version number on updates to nodes, services, and swarm objects so concurrent writes do not overwrite each other.

There are a few schema risks visible in the definitions. `Secret.Spec` references `#/definitions/ServiceSpec`, which appears inconsistent with the nearby `SecretSpec`. `NetworkConfig` is explicitly marked `TODO: check is correct`. Some example payloads use fields that are not fully represented in the adjacent schema, so generated examples and generated types may not perfectly agree.

## Container Operations

The container API covers list, create, inspect, process listing, logs, filesystem changes, export, stats, lifecycle, attach, wait, delete, archive transfer, and pruning.

Important operations in this chunk:

- `GET /containers/json` (`ContainerList`) returns `ContainerSummary` arrays with filters for status, labels, image ancestry, network, volume, health, task membership, and related selectors.
- `POST /containers/create` (`ContainerCreate`) accepts `Config` plus `HostConfig` and `NetworkingConfig`, returns the created container ID and warnings, and can fail for bad parameters, missing images, impossible attach configuration, conflicts, and server errors.
- `GET /containers/{id}/json` (`ContainerInspect`) returns detailed container state, paths, host config, graph driver, mounts, config, and network settings.
- Runtime endpoints include `ContainerStart`, `ContainerStop`, `ContainerRestart`, `ContainerKill`, `ContainerUpdate`, `ContainerRename`, `ContainerPause`, and `ContainerUnpause`.
- Stream-oriented endpoints include `ContainerLogs`, `ContainerStats`, `ContainerAttach`, `ContainerAttachWebsocket`, and `ContainerWait`.
- Archive endpoints on `/containers/{id}/archive` support `HEAD` metadata, `GET` tar export of a container path, and `PUT` extraction into the container filesystem.
- `POST /containers/prune` (`ContainerPrune`) deletes stopped containers and reports deleted IDs plus reclaimed bytes.

Control flow is defined as HTTP request/response state transitions. Container creation combines portable image config, host-specific resource/security settings, and optional endpoint networking. Lifecycle endpoints mutate the daemon's container state. Attach/log/stats endpoints can upgrade or hijack the HTTP connection for raw streams, making generated clients responsible for handling non-JSON streaming responses.

## Image, Build, Auth, And System Operations

Image operations include listing, building, creating or importing, inspecting, history, pushing, tagging, deleting, searching, pruning, exporting, and loading:

- `GET /images/json` (`ImageList`) returns `ImageSummary` data with filters for references, labels, dangling state, and ancestry.
- `POST /build` (`ImageBuild`) consumes a tar build context, supports many query options for Dockerfile path, tags, remote contexts, cache, resource limits, build args, labels, network mode, squash, and registry config headers, and produces JSON progress.
- `POST /images/create` (`ImageCreate`) pulls or imports an image and can use `X-Registry-Auth`.
- `GET /images/{name}/json`, `GET /images/{name}/history`, `POST /images/{name}/push`, `POST /images/{name}/tag`, and `DELETE /images/{name}` implement inspect, history, push, tag, and remove flows.
- `GET /images/{name}/get`, `GET /images/get`, and `POST /images/load` handle image save/load tar streams.
- `POST /images/prune` deletes unused images and reports deleted image records plus reclaimed space.

`POST /auth` (`SystemAuth`) validates registry credentials and may return an identity token. `/info`, `/version`, and `/_ping` expose daemon information, version metadata, and liveness. `/events` streams real-time events from containers, images, volumes, networks, and the daemon. `/system/df` reports storage usage across images, containers, volumes, and build cache-like data represented in this API version. `POST /commit` creates an image from a container, optionally pausing the container and applying Dockerfile-style changes.

State and persistence concerns here are substantial: builds create images and intermediate containers; pushes/pulls communicate with registries; image deletes and prunes mutate the local image store; commits snapshot container filesystem state; events observe daemon state changes; and `SystemInfo` exposes host, storage driver, registry, security, and plugin configuration.

## Exec, Volume, Network, And Plugin Operations

Exec operations are a two-step model: `POST /containers/{id}/exec` (`ContainerExec`) creates an exec instance, then `POST /exec/{id}/start` (`ExecStart`) starts it. `POST /exec/{id}/resize` and `GET /exec/{id}/json` resize and inspect exec sessions. This mirrors the tag description that `docker exec` wraps creation and start in one CLI command.

Volume operations cover list, create, inspect, delete, and prune. `Volume` schemas expose driver, mountpoint, labels, scope, driver options, status, and optional usage data. Deleting or pruning volumes mutates persistent host or driver-backed storage and can fail when volumes are in use.

Network operations cover list, inspect, create, delete, connect, disconnect, and prune. Network creation accepts driver, duplicate-check, internal/attachable flags, IPv6, IPAM, options, and labels. Connect and disconnect bind containers to network endpoints using `EndpointSettings`; swarm-scoped networks are explicitly guarded by `403` responses for unsupported direct connect/disconnect operations.

Plugin operations cover list, privileges, pull/install, inspect, delete, enable, disable, upgrade, create from tar, push, and set configuration. Plugin install and upgrade accept user-approved privilege arrays and optional registry auth. Plugin enable/disable/delete are high-risk daemon mutations because plugins can provide volume, network, and other host-integrated capabilities.

## Swarm, Node, Service, And Task Operations

The swarm model uses versioned objects and optimistic concurrency. `SwarmSpec` contains orchestration retention, Raft, dispatcher heartbeat, CA/external CA configuration, encryption-at-rest manager autolock, and task default logging settings. `ClusterInfo` intentionally mirrors `GET /swarm` data for `GET /info` but omits join tokens.

Node operations include `NodeList`, `NodeInspect`, `NodeDelete`, and `NodeUpdate`. Node updates require a `version` query parameter and a `NodeSpec` body with role, availability, name, and labels.

Swarm operations include `SwarmInspect`, `SwarmInit`, `SwarmJoin`, `SwarmLeave`, `SwarmUpdate`, `SwarmUnlockkey`, and `SwarmUnlock`. Init and join carry listen/advertise addresses and join tokens; update requires the swarm object version and can rotate worker tokens, manager tokens, and manager unlock keys.

Service operations include `ServiceList`, `ServiceCreate`, `ServiceInspect`, `ServiceDelete`, `ServiceUpdate`, and `ServiceLogs`. `ServiceSpec` composes a `TaskSpec`, replicated or global scheduling mode, update strategy, attached networks, and endpoint spec. Create/update can carry `X-Registry-Auth`; update also supports `registryAuthFrom` and requires a version query parameter. Service logs share the same raw stream behavior and logging-driver limitation as container logs.

Task coverage begins at `GET /tasks` (`TaskList`) and includes response examples for running and shutdown tasks with task version, spec, service ID, slot, node ID, status, desired state, and network attachments. The requested chunk ends mid-filter list after `desired-state` and `id`, so the remaining task filters and subsequent task/secret paths are outside this research chunk.

## Dependencies And Integration Points

The file depends on the Swagger/OpenAPI 2.0 schema model and ReDoc rendering conventions. It uses JSON Schema-like constructs, `$ref` links, `allOf` composition, `x-go-name`, and `x-nullable` extensions that are relevant for generated Go client/server types and API documentation.

Primary integration points are:

- Docker Engine HTTP routing and handler behavior, which must conform to the path/method/status/body contracts.
- Docker CLI and SDK clients that use these operation IDs and schemas to call the daemon.
- Registry clients through `X-Registry-Auth`, `X-Registry-Config`, push, pull, build, plugin pull, and plugin upgrade flows.
- Host subsystems: cgroups, namespaces, storage drivers, graph drivers, logging drivers, volumes, network drivers, swarmkit/Raft state, certificate authorities, and plugin interfaces.
- Documentation generation through ReDoc, where tag names, descriptions, examples, and markdown are user-facing API documentation.

## State And Persistence Behavior

This YAML file itself has no runtime state. The API it describes controls persistent Docker daemon state:

- Containers are created, configured, started, stopped, renamed, paused, killed, updated, removed, exported, archived, and pruned.
- Images are built, imported, pulled, tagged, pushed, committed, deleted, saved, loaded, and pruned.
- Volumes and networks can be created, connected to containers, deleted, and pruned, affecting host or driver-managed resources.
- Plugins can be installed, configured, enabled, disabled, upgraded, pushed, and removed.
- Swarm state persists in versioned Raft-backed objects: swarm spec, nodes, services, tasks, join tokens, unlock keys, secrets, certificates, and task history.

The contract repeatedly exposes concurrency and lifecycle guardrails through HTTP status codes: `404` for missing objects, `409` for conflicts or in-use resources, `403` for unsupported operations, `406` for invalid attach semantics, and `503` when a node is not in swarm mode or already is in a swarm for conflicting operations.

## Risks And Edge Cases

- The API uses an open schema model; clients must ignore extra response fields and servers ignore extra inputs. Strict generated clients can become brittle if they reject unknown properties.
- Several operations return streams or upgrade/hijack the connection (`logs`, `attach`, `stats`, `events`, image/build push/pull/load/save paths). Simple JSON-only client generators will not be sufficient.
- Auth headers carry Base64-encoded JSON credentials or tokens. Logging, tracing, or generated client debug output must avoid leaking these values.
- Build args are documented as not intended for secrets, but the schema cannot enforce that. Users can accidentally persist sensitive data in image history or build cache.
- Destructive prune/delete endpoints have broad effects and should be tested against filters, in-use objects, and reclaimed-space accounting.
- Swarm updates depend on object version parameters. Missing or stale versions must be handled to avoid unintended overwrite behavior.
- Platform-specific fields are mixed into shared schemas. Windows-only isolation/CPU fields and Unix-only cgroup/namespace/security fields need platform-aware validation.
- Some schema inconsistencies and TODOs are visible, including `Secret.Spec` referencing `ServiceSpec`, `NetworkConfig` marked as needing verification, and examples containing fields that may not exactly match schemas.

## Test Signals

Useful validation signals for this chunk include:

- Swagger/OpenAPI linting over `api/docs/v1.27.yaml`, especially `$ref` resolution, operation ID uniqueness, required field validity, and response schema correctness.
- Generated client/server type compilation from this file, with attention to `x-go-name`, `x-nullable`, `allOf`, polymorphic string-or-array fields, maps, and binary stream schemas.
- API conformance tests for each operation ID that verify documented status codes, error body shape, required parameters, and examples where practical.
- Stream-specific tests for attach, logs, stats, events, build, image pull/push/save/load, and service logs.
- Persistence tests around prune/delete endpoints, image build/import/export, volume lifecycle, network connect/disconnect, plugin lifecycle, and swarm object version conflicts.
- Backward compatibility tests that confirm v1.27 paths remain stable under newer daemons and that clients tolerate additional properties in responses.
