# sources/cloud-native/moby/api/docs/v1.45.yaml lines 1-7751

## Scope And Purpose

This chunk is the first 7,751 lines of the Docker Engine API v1.45 Swagger/OpenAPI 2.0 specification. It is not executable daemon code; it is a contract source used for generated Engine API documentation and generated client/server API types. The in-scope content defines global API metadata for `/v1.45`, documentation tags, all reusable schema definitions, and the beginning of the `paths` table.

The path surface covered here starts the Container API and runs through the beginning of `POST /containers/{id}/restart`. It fully covers container list, create, inspect, top, logs, filesystem changes, export, stats, resize, start, and stop, then stops mid-operation at the `parameters:` key for restart. Later container lifecycle endpoints, attach, wait, archive, image, system, exec, volume, network, plugin, swarm, node, service, task, secret, config, distribution, and session paths are outside this chunk, although their shared model definitions are present here.

## API Contract Structure

The document declares `swagger: "2.0"`, supports `http` and `https`, globally produces and consumes JSON and plain text, and sets `basePath: "/v1.45"`. The `info` block identifies this as the Docker Engine API and describes the API as the HTTP interface used by the Docker CLI. It documents standard JSON error responses shaped as `{ "message": "..." }`, version-prefix behavior, the deprecation of unversioned API calls, and the open-schema compatibility model: clients must ignore unknown response fields, while the server ignores extra query parameters and request body properties.

The tag block drives ReDoc grouping and declares primary object groups (`Container`, `Image`, `Network`, `Volume`, `Exec`), swarm groups (`Swarm`, `Node`, `Service`, `Task`, `Secret`, `Config`), and system groups (`Plugin`, `System`). In this chunk, only Container path operations have begun, but definitions for all of these resource families are already declared.

## Important Schemas And Types

Container schemas dominate the runtime configuration model. `ContainerConfig` represents portable image/process settings such as hostname, user, attach flags, TTY/stdin behavior, environment, command, healthcheck, image, volumes, working directory, entrypoint, labels, stop signal/timeout, and shell. `HostConfig` composes `Resources` and adds host-dependent behavior: bind strings, log driver config, network mode, port bindings, restart policy, auto-remove, volume inheritance, typed mounts, console size, runtime annotations, Linux capabilities and namespaces, DNS/hosts, privileged mode, security/storage options, tmpfs, sysctls, runtime, masked/readonly paths, and Windows isolation controls. `ContainerState`, `ContainerCreateResponse`, `ContainerWaitResponse`, `ContainerWaitExitError`, and `ContainerSummary` define inspect/list/wait output shapes.

Resource and device schemas include `Resources`, `Limit`, `ResourceObject`, `GenericResources`, `DeviceMapping`, `DeviceRequest`, and `ThrottleDevice`. They encode cgroup and runtime controls for CPU shares/quota/period/realtime, cpuset placement, memory/swap/swappiness/OOM/PID limits, ulimits, block IO throttling, device passthrough, accelerator requests, Windows CPU/IO controls, and swarm task resource accounting. `GenericResources` supports both named and discrete resources for scheduler decisions.

Health and lifecycle-related schemas include `HealthConfig`, `Health`, and `HealthcheckResult`. These describe side-effect-free probes, inherited or disabled checks, nanosecond intervals/timeouts/start periods, exit-code interpretation, failing streaks, and the recent probe log. `RestartPolicy` defines daemon restart behavior, including exponential delay and retry counts for `on-failure`.

Storage schemas include `MountType`, `MountPoint`, `Mount`, `Volume`, `VolumeCreateOptions`, `VolumeListResponse`, `ClusterVolume`, `ClusterVolumeSpec`, and `Topology`. `Mount` is create-time input for bind, cluster, npipe, tmpfs, and named volume mounts, with bind recursion/readonly options, volume driver options and subpaths, and tmpfs size/mode. `MountPoint` is inspect/list output for mounted container paths. `Volume` represents persistent daemon-managed storage, with optional `ClusterVolume` data for Swarm CSI cluster volumes and optional `UsageData` used by data-usage reporting. `ClusterVolumeSpec` captures CSI access mode, sharing, mount/block behavior, plugin secrets, topology requirements, capacity range, and availability.

Image and distribution schemas include `ImageHistoryResponseItem`, `ImageConfig`, `ImageInspect`, `ImageSummary`, `ImageDeleteResponseItem`, `BuildInfo`, `BuildCache`, `ImageID`, `CreateImageInfo`, `PushImageInfo`, `OCIDescriptor`, `OCIPlatform`, and `DistributionInspect`. They model local image metadata, image config defaults, graph driver data, rootfs layers, repo tags/digests, build/pull/push progress messages, build cache records, and registry distribution metadata including OCI descriptor/platform information.

Networking schemas include `NetworkingConfig`, `NetworkSettings`, `EndpointSettings`, `EndpointIPAMConfig`, `Port`, `PortMap`, `PortBinding`, `Network`, `ConfigReference`, `IPAM`, `IPAMConfig`, `NetworkContainer`, `PeerInfo`, and `NetworkAttachmentConfig`. They cover create/connect-time endpoint configuration, inspect-time operational data, per-network DNS names, static addressing, port mapping, default bridge compatibility fields, network driver/IPAM config, swarm overlay peers, and service network attachments. Several legacy `NetworkSettings` fields are explicitly deprecated in favor of the `Networks` map.

Plugin schemas include `Plugin`, `PluginMount`, `PluginDevice`, `PluginEnv`, `PluginInterfaceType`, and `PluginPrivilege`. They model installed plugin identity, enabled/running state, remote reference, mutable settings, declared mounts/devices/env/args, interface socket/type/protocol, Linux capabilities/devices, rootfs layers, host namespace needs, and privilege prompts.

Swarm schemas are fully present even though most swarm paths are later in the file. `ObjectVersion` is the optimistic concurrency token used by update APIs. `NodeSpec`, `Node`, `NodeDescription`, `Platform`, `EngineDescription`, `TLSInfo`, `NodeStatus`, `NodeState`, `ManagerStatus`, and `Reachability` model node state. `SwarmSpec`, `ClusterInfo`, `JoinTokens`, `Swarm`, and `SwarmInfo` model cluster configuration, Raft/dispatcher/CA/autolock settings, join tokens, and local daemon swarm status. `TaskSpec`, `TaskState`, `TaskStatus`, `Task`, `ServiceSpec`, `EndpointPortConfig`, `EndpointSpec`, `Service`, `ServiceCreateResponse`, and `ServiceUpdateResponse` model swarm workloads, service update/rollback/job status, endpoint publishing, and scheduler state. `SecretSpec`/`Secret` and `ConfigSpec`/`Config` model swarm secrets and configs, including base64 payload size limits and templating drivers.

Common support schemas include `GraphDriverData`, `FilesystemChange`, `ChangeType`, `AuthConfig`, `ProcessConfig`, `ErrorDetail`, `ProgressDetail`, `ErrorResponse`, `IdResponse`, `SystemVersion`, `SystemInfo`, `PluginsInfo`, `RegistryServiceConfig`, `IndexInfo`, `Runtime`, `Commit`, `LocalNodeState`, `PeerNode`, `EventActor`, and `EventMessage`. These provide shared error/progress bodies, daemon/system introspection, registry mirror/index config, runtime status, event stream payloads, and external component version metadata.

## In-Scope Path Surface

`GET /containers/json` (`ContainerList`) returns a compact `ContainerSummary` array. It supports `all`, `limit`, and `size` query parameters plus JSON-encoded `filters` with `map[string][]string` semantics. Documented filters include image ancestry, before/since, exposed/published ports, exit code, health, ID, Windows isolation, swarm task flag, labels, name, network, status, and volume. It returns `400` for bad parameters and `500` for server errors.

`POST /containers/create` (`ContainerCreate`) creates a stopped container. The query accepts a validated optional name and an optional `platform` string in `os[/arch[/variant]]` format for image lookup. The body combines `ContainerConfig`, `HostConfig`, and `NetworkingConfig`, making this operation the primary integration point for process config, resource limits, mounts, network attachments, labels, logging, security settings, devices, and restart behavior. Success is `201` with `ContainerCreateResponse`; error cases include bad parameter, missing image, conflict, and server error.

`GET /containers/{id}/json` (`ContainerInspect`) returns low-level container state. Its inline response schema includes identity, created time, command path/args, `ContainerState`, image ID, resolver/hosts/log paths, restart count, storage driver, platform, security labels, running exec IDs, `HostConfig`, `GraphDriverData`, optional size fields, `MountPoint` array, original `ContainerConfig`, and `NetworkSettings`. The query `size` controls `SizeRw` and `SizeRootFs` population.

`GET /containers/{id}/top` (`ContainerTop`) reports processes in a container by running `ps` on Unix systems and is not supported on Windows. The response carries `Titles` and a two-dimensional `Processes` array, with `ps_args` defaulting to `-ef`.

`GET /containers/{id}/logs` (`ContainerLogs`) streams stdout/stderr logs for containers using the `json-file` or `journald` log drivers. It produces Docker raw or multiplexed stream media types but explicitly does not upgrade the connection and does not set `Content-Type`; the stream format follows the attach endpoint documentation later in the file. Query parameters control follow mode, stdout/stderr selection, UNIX timestamp `since`/`until`, timestamps, and `tail`.

`GET /containers/{id}/changes` (`ContainerChanges`) returns an array of `FilesystemChange` entries for modifications in the writable container filesystem. `Kind` maps `0` to modified, `1` to added, and `2` to deleted.

`GET /containers/{id}/export` (`ContainerExport`) returns the container filesystem contents as an `application/octet-stream` tarball. It is a binary stream endpoint with standard missing-container and server-error responses.

`GET /containers/{id}/stats` (`ContainerStats`) returns live resource usage statistics and can either stream continuously or return once. The schema is a loose `type: "object"` with a detailed example rather than a named stats definition. The description documents CPU percentage formulas, memory usage formulas, `precpu_stats` semantics, `online_cpus` fallback behavior, cgroup v1/v2 field differences, and the `one-shot` behavior that must be combined with `stream=false`.

`POST /containers/{id}/resize` (`ContainerResize`) resizes a container TTY. It requires integer `h` and `w` query parameters and returns plain text or errors if the container is missing or cannot be resized.

`POST /containers/{id}/start` (`ContainerStart`) starts a stopped container and supports `detachKeys` override syntax. It returns `204` on success, `304` if already started, `404` for no such container, and `500` for server error.

`POST /containers/{id}/stop` (`ContainerStop`) stops a running container. It accepts optional `signal` and timeout `t` parameters and returns `204` on success, `304` if already stopped, `404` if missing, and `500` for server error.

`POST /containers/{id}/restart` (`ContainerRestart`) begins at the end of this chunk. The covered lines include its summary, operation ID, and response statuses `204`, `404`, and `500`; the chunk ends immediately after the `parameters:` key, so restart parameters and tags are intentionally not summarized here.

## Control Flow And Protocol Behavior

The contract encodes Docker CLI workflows as composed HTTP calls. A typical container run flow is create, optionally inspect or attach later, start, stream logs or stats, stop, and eventually remove through endpoints outside this chunk. The create operation is intentionally broad because it wires together image defaults, command/entrypoint, host-specific resource settings, mount setup, logging, and initial network endpoint configuration in one request.

Streaming behavior is a key client concern. Logs and export return byte streams rather than ordinary JSON objects. Stats returns repeated JSON resource snapshots when `stream=true`, and a single object when `stream=false`; `one-shot=true` avoids waiting for two samples and must be coordinated with `stream=false`. Generic OpenAPI clients may need custom handling for these operations because the spec cannot fully express stream framing or long-lived response semantics.

The API uses HTTP status codes to distinguish idempotency and state conflicts. Create returns `201`; start and stop return `204` for successful state change and `304` for already-started/already-stopped. Missing containers are consistently `404` with `ErrorResponse`; malformed list/create inputs use `400`; daemon faults use `500`.

Filters are specified as JSON-encoded strings, not first-class OpenAPI objects. This is a repeated contract pattern in the file and begins here with container listing. Client libraries that expose `filters` as a plain string without helpers are likely to produce integration mistakes.

## State And Persistence Behavior

The definitions expose the daemon's persisted state domains. Containers persist their portable `ContainerConfig`, host-specific `HostConfig`, runtime `ContainerState`, restart count, names, exec IDs, graph driver data, filesystem diff, mounts, log path, and network settings until removed. Inspect responses also surface host paths under the Docker root, such as resolver, hosts, hostname, and log files.

Images persist local content-addressed rootfs data, graph-driver metadata, image config, tags, digests, history, and optional local cache metadata such as last tag time. Build cache records have IDs, parent relationships, size, last-used timestamps, and usage count, making them independently reportable and prunable by later endpoints.

Volumes persist outside container lifecycles unless explicitly removed or pruned. Named volumes and cluster volumes are represented separately from container mount points. Cluster volumes introduce swarm-manager state, CSI plugin identities, topology constraints, publish status, and access modes that affect scheduling.

Networks persist driver/IPAM configuration and endpoint attachments. `NetworkSettings` links a container's runtime network namespace and per-network endpoints to `Network` objects; default bridge compatibility fields are still exposed but marked deprecated in favor of the `Networks` map.

Swarm state is versioned and replicated even though swarm path operations are mostly outside this chunk. `ObjectVersion` documents the update model: clients must pass a version observed from a prior read so concurrent updates cannot silently overwrite each other. `SwarmSpec` persists Raft, CA, dispatcher, autolock, task default, and orchestration settings.

Plugin state is persistent and capability-extending. Installed plugins have rootfs, settings, privileges, enabled state, network/namespace/device/mount requirements, and interface sockets. This makes plugin API changes high-impact for volume, network, logging, and authorization integration points.

## Dependencies And Integration Points

This file depends on Swagger/OpenAPI 2.0 tooling, ReDoc Markdown rendering, and Docker's API code-generation pipeline. Vendor fields such as `x-go-name` and `x-nullable` are significant because they influence generated Go type names and nullability/pointer behavior, not just documentation.

The represented Docker subsystems include container runtime execution, cgroups and resource accounting, graph/storage drivers, logging drivers, registry auth/distribution, BuildKit/build cache, volume drivers, network drivers and IPAM, plugin management, events, OCI image/runtime metadata, and swarmkit orchestration.

External standards and dependencies appear throughout the schema descriptions: RFC 3339 timestamps, RFC 4648 base64/base64url payloads, OCI image descriptors/platforms, OCI runtime features, Linux cgroups/namespaces/SELinux/AppArmor, Windows isolation and credential specs, CSI volume concepts, and swarm external CA integration using the `cfssl` protocol.

The first covered paths integrate most directly with clients that need Docker socket access. Container create and inspect are schema-heavy JSON operations; logs, stats, and export require stream-aware HTTP clients; list filters require correct JSON query encoding; platform selection affects image lookup and multi-architecture behavior.

## Risks And Edge Cases

Schema drift is high-risk because this spec is a generation source. A field renamed, nullability changed, enum narrowed, or `$ref` broken here can affect generated client/server types and published API documentation. Inline schemas, especially inspect and stats, are more prone to drift from implementation structs because they are not always named reusable definitions.

Open-schema compatibility is explicit. Strict clients that reject additional response fields can break against newer daemons, while tests that assert exact JSON payloads may become brittle. Servers ignoring unknown inputs can also hide client bugs unless tests validate the effective daemon state after create/update calls.

Streaming endpoints are poorly represented by generic OpenAPI tooling. Logs can be raw or multiplexed Docker stream data; stats can be endless; export is a tar stream. Generated clients may compile but still be unusable without hand-written transport and cancellation behavior.

Resource and platform fields have many conditional semantics. Cgroup v2 omits or changes several stats fields; Windows CPU controls and isolation differ from Linux controls; `ContainerTop` is Unix-only; `KernelMemoryTCP` may be ignored or unsupported; `PidsLimit`, `Init`, and many nullable fields distinguish omitted, null, zero, and false.

Mount and storage inputs have safety-sensitive behavior. Bind mounts may create host paths when `CreateMountpoint` is true; recursive readonly options changed in API v1.44; named volumes persist beyond container removal; cluster volumes depend on CSI plugins, topology, secret references, and swarm scheduling.

The create endpoint has broad blast radius. It accepts host paths, devices, privileged mode, capabilities, namespace settings, sysctls, runtime annotations, DNS/hosts entries, and logging options. Bad validation or overly permissive clients can expose host resources or create containers that cannot be started.

The chunk boundary itself is a documentation risk: `ContainerRestart` is incomplete in this chunk. Merge/reconciliation should combine the next chunk before making final statements about restart parameters, tags, or complete behavior.

## Test Signals

YAML/OpenAPI validation should parse the full `v1.45.yaml` and confirm that all `$ref` targets introduced in lines 1-7751 resolve. Chunk-only validation should not expect standalone YAML validity because this segment ends mid-operation under `ContainerRestart`.

Generated-code tests should verify `x-go-name`, `x-nullable`, required fields, enum values, and composed schemas such as `HostConfig` plus `Resources` produce the expected Go types. Pay particular attention to nullable booleans/integers, maps with object values, arrays of polymorphic resource specs, and inline operation response schemas.

Container contract tests should cover list filters, create with name/platform/body combinations, inspect with and without `size=true`, top with custom `ps_args`, logs with stdout/stderr/follow/tail/since/until, changes kind mapping, export tar output, stats streaming and one-shot behavior, resize required dimensions, and start/stop status-code distinctions.

Compatibility tests should ensure clients ignore unknown fields, tolerate omitted optional fields, encode filters as JSON map-of-list query strings, handle documented `304`, `400`, `404`, `409`, and `500` responses, and preserve daemon warnings such as image platform mismatch warnings from create responses.

Stateful integration tests should create containers with representative host config, mounts, resource limits, endpoint settings, healthchecks, and labels, then inspect the resulting persisted state and cleanup explicitly. Additional tests should run on both cgroup v1 and cgroup v2 hosts where possible to confirm stats field differences and CPU/memory formula expectations.
