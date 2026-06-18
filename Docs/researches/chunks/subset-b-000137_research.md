# sources/cloud-native/moby/api/docs/v1.44.yaml lines 1-7748

## Scope And Purpose

This chunk is the opening section of the Docker Engine API v1.44 Swagger 2.0 contract. It defines global API metadata, versioning guidance, registry authentication format, documentation tags, the full shared `definitions` model, and the beginning of the `paths` section through the opening of `POST /containers/{id}/restart`.

The file is not daemon runtime code. Its purpose is to be the versioned HTTP API source of truth for documentation and generated client/server types. The chunk establishes the object schemas used by most later endpoints: containers, images, mounts, resources, health checks, networks, volumes, plugins, swarm objects, services, tasks, secrets, configs, system info, events, OCI distribution metadata, and swarm CSI cluster volumes. The path portion covers container listing, creation, inspection, process listing, logs, filesystem changes, export, stats, TTY resize, start, and stop; the restart operation body continues after this chunk.

## Important API Contracts And Types

Global API metadata sets `basePath: /v1.44`, JSON/text media defaults, HTTP/HTTPS schemes, and an open-schema compatibility model. The prose makes versioned URLs the compatibility boundary, deprecates unversioned API use, and tells clients to ignore additional response properties and servers to ignore extra request properties. Registry-authenticated endpoints use an `X-Registry-Auth` header containing base64url-encoded JSON credentials or an identity token.

Core container and host configuration schemas are concentrated in `ContainerConfig`, `HostConfig`, `Resources`, `Mount`, `MountPoint`, `DeviceMapping`, `DeviceRequest`, `RestartPolicy`, `HealthConfig`, `Health`, `HealthcheckResult`, `ContainerState`, `ContainerSummary`, `ContainerCreateResponse`, and `ContainerWaitResponse`. These types model image defaults, runtime command/env/TTY behavior, health probes, mounts, port bindings, cgroup and platform-specific resource controls, device access, logging config, namespace/security settings, restart behavior, network attachment, and observable container lifecycle state.

Image and content schemas include `ImageConfig`, `ImageInspect`, `ImageSummary`, `ImageHistoryResponseItem`, `ImageDeleteResponseItem`, `ImageID`, `CreateImageInfo`, `PushImageInfo`, `GraphDriverData`, `FilesystemChange`, `ChangeType`, `ErrorDetail`, `ProgressDetail`, `ErrorResponse`, and `IdResponse`. They distinguish local image config digests from repository manifest digests, expose storage-driver metadata as informational maps, and use stream-progress structures for pull/push/create flows used elsewhere in the API.

Networking schemas include `NetworkingConfig`, `NetworkSettings`, `EndpointSettings`, `EndpointIPAMConfig`, `PortMap`, `PortBinding`, `Network`, `IPAM`, `IPAMConfig`, `NetworkContainer`, `PeerInfo`, and `NetworkAttachmentConfig`. They separate create/connect-time endpoint configuration from inspect-time operational data, document deprecated default-bridge fields, and add v1.44-era endpoint DNS names and MAC-address placement at `EndpointSettings`.

Volume and storage schemas include `Volume`, `VolumeCreateOptions`, `VolumeListResponse`, `ClusterVolume`, `ClusterVolumeSpec`, and `Topology`. Plain volumes model local/global scope, driver options, labels, mountpoints, optional usage data, and optional cluster-volume detail. Cluster volumes model Swarm CSI state: swarm object IDs and versions, controller-reported capacity/context/plugin IDs, publish state per node, access mode, topology requirements, capacity range, plugin secrets, and volume availability.

Plugin schemas include `PluginMount`, `PluginDevice`, `PluginEnv`, `PluginInterfaceType`, `PluginPrivilege`, and `Plugin`. They describe installed managed plugins, mutable user settings, plugin rootfs metadata, interface socket/protocol, requested Linux capabilities/devices/mounts, propagated mounts, host namespace flags, and privilege prompts accepted during install or upgrade endpoints in later chunks.

Swarm and orchestration schemas include `ObjectVersion`, `NodeSpec`, `Node`, `NodeDescription`, `Platform`, `EngineDescription`, `TLSInfo`, `NodeStatus`, `NodeState`, `ManagerStatus`, `Reachability`, `SwarmSpec`, `ClusterInfo`, `JoinTokens`, `Swarm`, `TaskSpec`, `TaskState`, `TaskStatus`, `Task`, `ServiceSpec`, `EndpointPortConfig`, `EndpointSpec`, `Service`, `ServiceCreateResponse`, and `ServiceUpdateResponse`. The critical contract is optimistic concurrency via `ObjectVersion.Index` for swarm object updates. `SwarmSpec` models raft, CA, dispatcher, encryption-at-rest, and task defaults. `TaskSpec` models mutually exclusive container/plugin/network-attachment specs plus resources, restart policy, placement constraints/preferences, runtime, networks, log driver, secrets, configs, sysctls, capabilities, and service-task security options. `ServiceSpec` adds replicated/global/job scheduling modes and update/rollback strategies.

System, registry, event, and OCI schemas include `SystemVersion`, `SystemInfo`, `PluginsInfo`, `RegistryServiceConfig`, `IndexInfo`, `Runtime`, `Commit`, `SwarmInfo`, `LocalNodeState`, `PeerNode`, `EventActor`, `EventMessage`, `OCIDescriptor`, `OCIPlatform`, and `DistributionInspect`. These describe daemon version/build metadata, host capability flags, Docker root directory, proxy settings with masked credentials, registry mirror/insecure-registry configuration, configured OCI runtimes, swarm local state, event stream envelopes, and registry manifest descriptor/platform metadata.

The container endpoints present in this chunk are `ContainerList`, `ContainerCreate`, `ContainerInspect`, `ContainerTop`, `ContainerLogs`, `ContainerChanges`, `ContainerExport`, `ContainerStats`, `ContainerResize`, `ContainerStart`, and `ContainerStop`. The document line 7748 begins `ContainerRestart` but does not include its parameters/responses in this chunk.

## Control Flow

The control flow is HTTP-contract control flow. `GET /containers/json` returns a compact `ContainerSummary` list and accepts query flags for all containers, recent limit, size calculation, and JSON-encoded filters. The filter contract accepts status, health, image ancestor, before/since, exposed/published ports, exit code, ID/name, network, volume, label, swarm-task flag, and Windows isolation filters.

`POST /containers/create` composes `ContainerConfig`, `HostConfig`, and `NetworkingConfig` into a new container object. The optional `name` query parameter is validated by a documented pattern, and the optional `platform` query parameter controls local image platform lookup and warning behavior. Successful creation returns `201` with a container ID and warnings; documented failures include bad parameters, missing images, name/state conflicts, and server errors.

`GET /containers/{id}/json` returns the low-level inspect model for an ID or name. It joins immutable creation/config fields with mutable runtime state, graph-driver data, host config, mounts, network settings, log/config file paths, exec IDs, restart count, process labels, and optional size fields when `size=true`.

Read-only runtime views are modeled by `ContainerTop`, `ContainerLogs`, `ContainerChanges`, `ContainerExport`, and `ContainerStats`. `ContainerTop` runs a daemon-side process listing with configurable `ps_args`. `ContainerLogs` returns stdout/stderr log bytes with `follow`, `since`, `until`, `timestamps`, and `tail` controls, and is limited to containers using the `json-file` or `journald` log drivers. `ContainerChanges` returns filesystem diff entries using `ChangeType` values. `ContainerExport` returns a tar stream. `ContainerStats` streams or emits one resource-usage sample and documents CPU/memory formulas plus cgroup v1/v2 field differences.

State-changing container actions in this chunk are TTY resize, start, and stop. `ContainerResize` requires `h` and `w` query dimensions. `ContainerStart` returns `204` on success and `304` if already started, with optional detach-key override. `ContainerStop` returns `204` on success and `304` if already stopped, with optional signal and grace-period query parameters.

## State And Persistence Behavior

The YAML itself persists no state, but it describes persistent daemon and swarm state. Container creation writes a new container record tied to image, host configuration, network endpoint intent, mounts, labels, restart policy, logging config, resource limits, namespace/security settings, and generated or requested name. Container inspect exposes persisted metadata under the daemon root, including log path, hosts/resolv/hostname paths, graph-driver state, and current runtime state.

Container start and stop mutate lifecycle state and can affect port allocations, restart counters, process IDs, health state, timestamps, and log production. Stop uses a signal plus timeout before kill semantics. Resize mutates the active TTY dimensions rather than persisted configuration. Logs, top, changes, export, and stats are read-side views over runtime/container filesystem/logging/cgroup state, though `ContainerStats` can hold open a live stream by default.

Image, volume, network, plugin, swarm, service, task, secret, config, system, event, and distribution definitions model state used by later paths. Several objects carry persistence-specific caveats: image metadata such as `LastTagTime` is local to the daemon; volume usage data is only included for `GET /system/df`; secrets return metadata but not secret `Data` after creation; configs and secrets use base64 payloads with size limits; swarm-managed objects carry `ObjectVersion` to avoid conflicting writes; cluster volumes have swarm object versions and CSI controller/node publish status.

The system info model exposes host and daemon state that may be static at daemon start (`NCPU`), optional/debug-gated (`NFd`, `NGoroutines`), feature-gated (`CDISpecDirs` requiring experimental mode), or intentionally unstable in formatting (`DriverStatus`, runtime `status`, OS version fields). Registry config and proxy fields reflect daemon configuration, with proxy credentials masked and not inherited automatically by containers.

## Dependencies And Integration Points

The document depends on Swagger 2.0 syntax, ReDoc/GitHub-Flavored-Markdown descriptions, `$ref` reuse, `allOf` composition, `x-go-name`, `x-nullable`, examples, operation IDs, and tags consumed by Docker API docs and generated Go/client types. The generated type surface is broad, so field names, nullability, required lists, enum values, and examples are integration contracts, not just prose.

Runtime integration points implied by the schemas include dockerd HTTP routing, image store and registry clients, containerd and OCI runtimes, cgroups v1/v2, storage drivers, logging drivers, network drivers and IPAM, volume drivers, managed plugins, swarmkit/Raft, CSI storage plugins, external secret stores, Windows credential specs, SELinux/seccomp/AppArmor, host proxy environment, Docker event broadcasting, and OCI distribution metadata.

Client integrations must support JSON bodies and query parameters, JSON-encoded filter maps, path identifiers that accept names or IDs, base64url registry-auth headers, binary/tar streams, raw and multiplexed log streams, long-lived stats streams, platform selection, optional fields, deprecated fields, and open-schema forward compatibility. Generated clients also need to preserve names whose casing is intentional, such as `Id` in container/image responses versus `ID` in swarm objects.

## Risks And Edge Cases

The largest risk in this chunk is schema drift between documentation, generated types, and daemon behavior. Open-schema compatibility allows additional properties, but clients still depend on documented field casing, enum values, nullability, required properties, response codes, and stream media types. The file contains deprecated fields that remain for compatibility, such as `ImageInspect.Container`, `ImageInspect.ContainerConfig`, image config fields that must not be used, old default-bridge network fields, `ContainerConfig.MacAddress`, and `ServiceSpec.Networks`.

Container creation has a wide blast radius because a single body configures image lookup, process defaults, bind mounts, named volumes, tmpfs, devices and GPU requests, cgroups, namespaces, sysctls, security options, logging, restart policy, host networking, and endpoint-level IP/MAC/DNS aliases. Validation needs to catch impossible combinations such as conflicting capability fields, invalid names, missing mount sources, unsupported platforms, invalid resource values, and platform-specific options on the wrong daemon OS.

Streaming and binary endpoints are easy to mishandle. Logs can be raw or multiplexed and intentionally do not use connection upgrade. Stats streams by default and its CPU/memory calculations differ for cgroups v1 and v2. Export returns a tar stream. Generated clients and proxies must avoid assuming every successful response is JSON.

Security-sensitive schemas include registry credentials, secrets/configs, plugin privileges, external CAs, swarm join tokens, manager autolock, Windows credential specs, CDI device injection, privileged containers, host namespaces, host bind mounts, insecure registries, and daemon proxy settings. The API contract documents masking and post-create omission in some places, but implementations and clients must avoid logging sensitive headers and payloads.

Swarm and cluster-volume definitions are stateful and versioned. Clients must use `ObjectVersion.Index` for updates in later endpoints, and tests should catch stale-version overwrites. Cluster volumes add CSI topology, publish-state, capacity, and plugin-secret semantics that can fail independently across manager/controller/worker boundaries.

There are also documentation-quality risks in example payloads. Large examples include broad host config and device request bodies; malformed examples or stale fields can break generated documentation, client snippets, or conformance assumptions even when the schema is otherwise valid.

## Test Signals

Static test signals should include Swagger/OpenAPI validation for lines 1-7748, full `$ref` resolution across all definitions, operation ID uniqueness, required property validation, enum and format checks, generated Go/client type compilation, and documentation rendering through ReDoc. Since this chunk defines all shared schemas, failures here can cascade into every later path.

Container API conformance tests should cover list filters, `all`/`limit`/`size` behavior, create success and warning paths, invalid names, missing images, platform mismatch behavior, duplicate-name conflicts, inspect size toggling, missing-container `404`s, start/stop `204` versus `304`, resize required dimensions, logs with stdout/stderr/follow/since/until/timestamps/tail, filesystem change kinds, export tar output, and stats stream versus one-shot behavior.

State tests should verify persisted container config round-trips through inspect, including host config, network endpoint settings, mounts, labels, restart policy, health config and health results, graph-driver fields, log path, exec IDs, and runtime state booleans where paused containers can be both `Running` and `Paused`.

Platform and subsystem tests should exercise Linux and Windows-only fields, cgroups v1/v2 stats differences, logging-driver limitations for logs, GPU/device requests, CDI-disabled behavior on non-experimental daemons, insecure registry reporting, proxy credential masking, and deprecated field compatibility.

Compatibility tests should confirm v1.44 clients tolerate unknown response fields, do not depend on deprecated image/container/network fields, preserve documented field casing, encode filters as JSON `map[string][]string`, handle raw/binary streams without JSON decoding, and treat path identifiers consistently as names or IDs.
