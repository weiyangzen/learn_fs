# sources/cloud-native/moby/api/docs/v1.43.yaml lines 1-7769

## Scope

This chunk covers the opening 7,769 lines of the Docker Engine API v1.43 Swagger 2.0 document. It includes the global API metadata, tag taxonomy, the complete `definitions:` block, the start of `paths:`, and the container endpoint group from `GET /containers/json` through a partial `POST /containers/{id}/rename` entry. Lines after this chunk continue the remaining container endpoints and all later image, system, exec, volume, network, plugin, swarm, service, task, secret, config, distribution, and session paths.

## Purpose

The file is the versioned API contract for Docker Engine API v1.43. It is used to generate public API documentation and client/server types. The contract declares common transport defaults (`http`, `https`, JSON/text payloads, base path `/v1.43`), documents API versioning and error format, and gives registry authentication rules for endpoints that interact with registries through the `X-Registry-Auth` header.

The chunk establishes the canonical schema vocabulary for the whole API. Most runtime behavior elsewhere in Moby is represented here as OpenAPI request/response shapes, status codes, media types, query parameters, and references between schemas. It does not implement daemon logic itself, but it is a high-impact source for generated models, generated docs, compatibility expectations, and tests that validate the API specification.

## Important API Surface

### Global API Metadata

- `swagger: "2.0"`, `basePath: "/v1.43"`, and global `produces`/`consumes` defaults set the versioned REST contract.
- `info.description` defines standard JSON error bodies with a `message` field and explains the version-prefix behavior for `/v1.43/...` versus unversioned routes.
- The document explicitly uses an open schema model: servers may add response fields and ignore unknown query/body properties. Generated clients should therefore tolerate additional properties.
- Registry auth is documented as base64url-encoded JSON in `X-Registry-Auth`, either username/password/serveraddress credentials or an identity token returned by `/auth`.
- Tags define ReDoc grouping and drive documentation navigation: `Container`, `Image`, `Network`, `Volume`, `Exec`, `Swarm`, `Node`, `Service`, `Task`, `Secret`, `Config`, `Plugin`, and `System`.

### Definition Families

The full `definitions:` section is present in this chunk. The important groups are:

- Container creation, inspection, and state:
  `ContainerConfig`, `HostConfig`, `Resources`, `RestartPolicy`, `ContainerState`, `ContainerCreateResponse`, `ContainerWaitResponse`, `ContainerWaitExitError`, `ContainerSummary`, `Mount`, `MountPoint`, `MountType`, `DeviceMapping`, `DeviceRequest`, `ThrottleDevice`, `HealthConfig`, `Health`, and `HealthcheckResult`.
- Container networking:
  `NetworkingConfig`, `NetworkSettings`, `EndpointSettings`, `EndpointIPAMConfig`, `Port`, `PortMap`, `PortBinding`, and `Address`.
- Image and build:
  `ImageInspect`, `ImageSummary`, `ImageHistoryResponseItem`, `ImageConfig`, `ImageDeleteResponseItem`, `ImageID`, `BuildInfo`, `BuildCache`, `CreateImageInfo`, `PushImageInfo`, `ProgressDetail`, and `ErrorDetail`.
- Volumes and cluster volumes:
  `Volume`, `VolumeCreateOptions`, `VolumeListResponse`, `ClusterVolume`, `ClusterVolumeSpec`, and `Topology`.
- Networks:
  `Network`, `ConfigReference`, `IPAM`, `IPAMConfig`, `NetworkContainer`, `PeerInfo`, and `NetworkAttachmentConfig`.
- Plugins:
  `Plugin`, `PluginMount`, `PluginDevice`, `PluginEnv`, `PluginInterfaceType`, and `PluginPrivilege`.
- Swarm, nodes, services, and tasks:
  `ObjectVersion`, `NodeSpec`, `Node`, `NodeDescription`, `Platform`, `EngineDescription`, `TLSInfo`, `NodeStatus`, `NodeState`, `ManagerStatus`, `Reachability`, `SwarmSpec`, `ClusterInfo`, `JoinTokens`, `Swarm`, `SwarmInfo`, `LocalNodeState`, `PeerNode`, `TaskSpec`, `TaskState`, `Task`, `ServiceSpec`, `EndpointPortConfig`, `EndpointSpec`, `Service`, and `ServiceUpdateResponse`.
- Secrets and configs:
  `Driver`, `SecretSpec`, `Secret`, `ConfigSpec`, and `Config`.
- System, version, events, registry, and OCI/distribution:
  `SystemVersion`, `SystemInfo`, `PluginsInfo`, `RegistryServiceConfig`, `IndexInfo`, `Runtime`, `Commit`, `EventActor`, `EventMessage`, `OCIDescriptor`, `OCIPlatform`, and `DistributionInspect`.
- Common response types:
  `ErrorResponse` and `IdResponse`.

### Container Endpoints In This Chunk

The `paths:` block starts at line 6433 and this chunk covers these operation IDs:

- `ContainerList` for `GET /containers/json`.
  Lists containers with query parameters `all`, `limit`, `size`, and JSON-encoded `filters`. It returns an array of `ContainerSummary` and documents filter keys such as `ancestor`, `before`, `expose`, `exited`, `health`, `id`, `isolation`, `is-task`, `label`, `name`, `network`, `publish`, `since`, `status`, and `volume`.
- `ContainerCreate` for `POST /containers/create`.
  Creates a container from a body composed with `allOf` over `ContainerConfig`, `HostConfig`, and `NetworkingConfig`. Query parameters include `name` and `platform`. Success returns `ContainerCreateResponse` with status `201`; missing image is `404`; conflicts are `409`.
- `ContainerInspect` for `GET /containers/{id}/json`.
  Returns low-level container details including state, image ID, host paths, restart count, platform, labels, `HostConfig`, `GraphDriver`, `Mounts`, `Config`, and `NetworkSettings`.
- `ContainerTop` for `GET /containers/{id}/top`.
  Returns process titles and processes for a container; accepts `ps_args` and returns `404` for missing containers.
- `ContainerLogs` for `GET /containers/{id}/logs`.
  Streams logs using Docker raw or multiplexed stream media types. It only works with `json-file` or `journald` logging drivers and supports `follow`, `stdout`, `stderr`, `since`, `until`, `timestamps`, and `tail`.
- `ContainerChanges` for `GET /containers/{id}/changes`.
  Returns an array of `FilesystemChange`, whose `Kind` uses `ChangeType` values `0` modified, `1` added, and `2` deleted.
- `ContainerExport` for `GET /containers/{id}/export`.
  Exports a container filesystem as `application/octet-stream`.
- `ContainerStats` for `GET /containers/{id}/stats`.
  Streams or returns a single object with resource usage statistics. The description documents cgroup v1/v2 differences and formulas for memory and CPU percentage calculations.
- `ContainerResize` for `POST /containers/{id}/resize`.
  Resizes a TTY using required `h` and `w` query parameters.
- `ContainerStart`, `ContainerStop`, `ContainerRestart`, and `ContainerKill`.
  Mutate lifecycle state. Start accepts `detachKeys`; stop/restart accept `signal` and timeout `t`; kill defaults `signal` to `SIGKILL` and has a `409` response when the container is not running.
- `ContainerUpdate` for `POST /containers/{id}/update`.
  Updates selected runtime resources and restart policy without recreating the container. The body composes `Resources` plus `RestartPolicy`; success returns warning strings.
- `ContainerRename` for `POST /containers/{id}/rename`.
  The operation declaration and response codes begin in this chunk, but the parameter list is cut at line 7769. The next chunk is needed for the complete parameter and tag details.

## Schema And Control Flow

This YAML expresses API control flow through HTTP operations and schema composition rather than through functions:

- Client requests enter versioned routes under `/v1.43`.
- Operation-specific path, query, header, and body parameters select daemon objects or behavior.
- Request bodies frequently use `$ref` and `allOf` composition to reuse common model definitions. For example, container creation composes portable `ContainerConfig`, host-specific `HostConfig`, and per-network `NetworkingConfig`; container update composes `Resources` and `RestartPolicy`.
- Successful responses either return JSON model references, binary streams, raw/multiplexed streams, or no body depending on operation semantics.
- Error responses generally use `ErrorResponse` with a single required `message` field and standard HTTP status codes.
- The spec uses ReDoc tags to group operations, and code generation relies on `operationId` values such as `ContainerCreate` and `ContainerStats`.

The state-changing container lifecycle flow visible in this chunk is:

1. `ContainerCreate` records a stopped container from an image plus configuration.
2. `ContainerStart` transitions it to running unless already started.
3. `ContainerLogs`, `ContainerStats`, `ContainerTop`, `ContainerChanges`, `ContainerExport`, and `ContainerInspect` expose runtime or filesystem state.
4. `ContainerResize` adjusts TTY dimensions for interactive containers.
5. `ContainerStop`, `ContainerRestart`, and `ContainerKill` signal or restart the process.
6. `ContainerUpdate` changes resource controls and restart policy in place.
7. `ContainerRename` begins in this chunk and will rename the container when fully specified in the next chunk.

## State And Persistence Behavior

The schemas describe daemon state persisted or derived by Docker Engine:

- Container filesystem state is represented by `GraphDriverData`, `MountPoint`, `FilesystemChange`, `SizeRw`, and `SizeRootFs`. Storage-driver metadata is explicitly driver-specific and informational.
- Container runtime state is represented by `ContainerState`, including status enum, booleans such as `Running`, `Paused`, `Restarting`, `OOMKilled`, process ID, exit code, health, and start/finish timestamps.
- Container configuration is split between portable image/container defaults (`ContainerConfig`, `ImageConfig`) and host-bound settings (`HostConfig`, `Resources`, mounts, namespace modes, security settings, cgroup controls, logging, and runtime selection).
- Volumes and mounts are persistent storage abstractions. Named volumes are not removed with containers; cluster volumes add Swarm/CSI state including topology, access mode, capacity, publish state, and plugin-provided context.
- Swarm objects use `ObjectVersion.Index` for optimistic concurrency on updates. This is the main schema-level protection against lost writes for nodes, services, secrets, configs, and swarm objects.
- Swarm cluster state includes Raft, CA, encryption-at-rest, join tokens, node TLS info, dispatcher heartbeats, and task history retention.
- `SystemInfo` exposes daemon state such as root directory, storage driver, cgroup version, available runtimes, security options, proxy settings, swarm state, live restore, and warnings.
- Secrets/config payloads are base64 data at creation time; secret data is not returned by other endpoints. Configs and secrets are Swarm-scoped persisted objects.

## Dependencies And Integration Points

The contract integrates with several external and internal systems:

- OpenAPI/Swagger tooling, ReDoc, and Moby code-generation pipelines consume the file.
- Docker client commands map to these routes, with multi-step workflows such as container creation/start and exec workflows documented by tag descriptions.
- Registry endpoints rely on client-side registry authentication using `X-Registry-Auth`.
- OCI runtime integration appears in `Runtime`, `SystemInfo.Runtimes`, `DefaultRuntime`, `ContainerdCommit`, `RuncCommit`, and `InitCommit`.
- Container resources depend on Linux cgroups, Windows isolation/resource controls, kernel namespace modes, blkio, cpuset, pids, OOM, sysctls, and SELinux/AppArmor/security options.
- Networking schemas integrate with Docker network drivers, IPAM drivers, overlay peers, bridge settings, endpoint aliases, and per-network driver options.
- Volume schemas integrate with local volume drivers, volume plugins, and Swarm CSI cluster volumes.
- Swarm schemas integrate with swarmkit concepts: Raft, managers, nodes, tasks, services, rolling update/rollback, job modes, CA rotation, secrets, configs, and placement constraints.
- OCI distribution schemas (`OCIDescriptor`, `OCIPlatform`, `DistributionInspect`) align Docker registry metadata with OCI image-spec concepts.

## Risks And Compatibility Concerns

- This is a generated-contract source of truth. Any schema drift from daemon behavior can break generated clients, API docs, or compatibility tests even if the daemon code works.
- The spec intentionally allows unknown response properties and ignored extra request properties. Strict generated clients that reject additional properties would violate the documented compatibility model.
- Many fields are platform-specific. Linux cgroup/resource fields, Windows isolation/credential fields, and cgroup v1/v2 stats differences require tests on the correct platform matrix.
- Several fields are marked deprecated or informational, such as default-bridge network fields, `ImageInspect.VirtualSize`, `ImageSummary.VirtualSize`, and `AuthConfig.email`. Removing or reshaping them is an API compatibility risk.
- `allOf` composition is central to request models. Generators that flatten composition incorrectly may lose fields from `Resources`, `ContainerConfig`, `HostConfig`, or `NetworkingConfig`.
- Some YAML examples are large and are part of documentation quality; malformed examples can break documentation generation even if schemas parse.
- Stream endpoints need special handling. `ContainerLogs` returns raw/multiplexed stream media types without the same connection upgrade behavior as attach; `ContainerStats` can be a live stream or one-shot response.
- `ObjectVersion` concurrency semantics are only encoded as documentation in this chunk. API handlers must enforce version checks elsewhere.
- The chunk boundary cuts through `ContainerRename`; downstream merge must combine the next chunk before treating that endpoint as fully researched.

## Test Signals

Useful validation signals for this chunk include:

- Swagger/OpenAPI parsing succeeds for the full file and preserves `swagger: "2.0"`, `basePath: "/v1.43"`, tags, definitions, and operation IDs.
- Generated docs render all tag groups and large markdown descriptions without truncation or malformed nesting.
- Generated model tests verify key `$ref` and `allOf` expansions for `ContainerCreate`, `ContainerUpdate`, `HostConfig`, `Resources`, `Swarm`, `ServiceSpec`, and `ClusterVolumeSpec`.
- API compatibility tests assert common error schemas use `ErrorResponse.message` for 400/404/409/500 paths.
- Container endpoint tests cover query parameter parsing for list filters, create `name` pattern and `platform`, lifecycle idempotency status codes (`204`, `304`, `404`, `409`), and update warning responses.
- Stream tests should cover `ContainerLogs` media types, stdout/stderr/tail/timestamps behavior, and `ContainerStats` `stream=false` plus `one-shot` behavior.
- Platform tests should exercise Linux and Windows-specific fields, cgroup v1/v2 stats behavior, mount variants, and resource constraints.
- Documentation/schema tests should flag deprecated fields, enum changes, missing required fields, and broken examples before release.

## Cross-Chunk Notes

- Lines 1-6432 define schemas used by paths throughout the remainder of the file, not just by the container operations present in this chunk.
- Paths after line 7769 are required to complete `ContainerRename` and to research all later operation groups.
- The later merge/reconciliation lane should synthesize this chunk with the remaining chunks for `sources/cloud-native/moby/api/docs/v1.43.yaml` into the source-tree-aligned final per-file report.
