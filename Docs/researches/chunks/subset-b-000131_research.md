# sources/cloud-native/moby/api/docs/v1.41.yaml lines 1-7812

## Scope And Purpose

This chunk is the first 7,812 lines of the Docker Engine API v1.41 Swagger/OpenAPI 2.0 specification. It is not executable runtime code, but it is a contract source used for generated Engine API documentation and client/server API types. The chunk declares global protocol metadata for API version `/v1.41`, the ReDoc tag model, the full shared `definitions` section, and the beginning of the `paths` table.

The path surface included in this chunk is limited to container APIs from `GET /containers/json` through `GET /containers/{id}/attach/ws`. Later container endpoints and the image/system/volume/network/plugin/swarm paths start after line 7812 and are not summarized as operations here, even though their shared schemas are already defined in this chunk.

## API Contract Structure

The file declares `swagger: "2.0"`, `http` and `https` schemes, global JSON/plain-text consumes and produces entries, and `basePath: "/v1.41"`. The `info` description documents Docker Engine as the HTTP API used by the Docker CLI, standard JSON error bodies with a `message` field, version-prefix behavior, daemon rejection of unsupported API versions, deprecation of unversioned requests, and the open-schema compatibility rule: clients must ignore extra response properties and the server ignores unknown query parameters or request-body properties.

Top-level tags define documentation grouping and generated navigation: primary objects (`Container`, `Image`, `Network`, `Volume`, `Exec`), swarm objects (`Swarm`, `Node`, `Service`, `Task`, `Secret`, `Config`), and system objects (`Plugin`, `System`). In the path portion of this chunk only `Container` operations appear, but the definitions section already includes schema contracts for the other groups.

## Important Schemas And Types

Container creation and inspection are centered on `ContainerConfig`, `HostConfig`, `Resources`, `NetworkingConfig`, `NetworkSettings`, `ContainerState`, and `ContainerSummary`. `ContainerConfig` covers portable image/runtime settings such as hostname, user, attach flags, TTY/stdin behavior, environment, command, healthcheck, image reference, volumes, working directory, entrypoint, labels, stop signal/timeout, and shell. `HostConfig` composes `Resources` with host-dependent settings: bind mounts, log driver, network mode, port bindings, restart policy, auto-remove, volumes-from, structured mounts, capabilities, namespace modes, DNS, extra hosts, privileged mode, read-only rootfs, security/storage options, sysctls, runtime, Windows isolation/console fields, and masked/read-only paths.

`Resources` is the shared model for container and update resource controls. It includes cgroup parent, CPU shares/quota/period/realtime, cpuset strings, block IO weights and throttles, device mappings and `DeviceRequest` accelerator requests, memory/swap/swappiness/OOM/PIDs controls, ulimits, and Windows CPU/IO controls. `RestartPolicy` captures the daemon's restart behavior and retry count. `HealthConfig`, `Health`, and `HealthcheckResult` define health probe configuration and inspect-time health state.

Storage and mount models include `MountType`, `MountPoint`, `Mount`, `DeviceMapping`, `DeviceRequest`, `ThrottleDevice`, `Volume`, `VolumeCreateOptions`, and `VolumeListResponse`. `Mount` is create-time input for bind, named pipe, tmpfs, and volume mounts, with option objects for bind propagation, volume driver config, and tmpfs size/mode. `MountPoint` is inspect/list output for active mounts. `Volume` records persistent storage state, driver, mountpoint, labels, scope, driver options, optional low-level status, and optional `UsageData` for `GET /system/df`.

Networking definitions include `Port`, `PortMap`, `PortBinding`, `Network`, `ConfigReference`, `IPAM`, `IPAMConfig`, `NetworkContainer`, `PeerInfo`, `EndpointSettings`, `EndpointIPAMConfig`, and `NetworkAttachmentConfig`. They model port exposure/bindings, driver/IPAM configuration, config-only and swarm-scoped networks, container endpoints, static endpoint addressing, aliases, links, gateways, MAC addresses, and network attach options for services.

Image and registry schemas include `ImageHistoryResponseItem`, `ImageInspect`, `ImageConfig`, `ImageSummary`, `ImageDeleteResponseItem`, `BuildInfo`, `BuildCache`, `ImageID`, `CreateImageInfo`, `PushImageInfo`, `AuthConfig`, `RegistryServiceConfig`, `IndexInfo`, `OCIDescriptor`, `OCIPlatform`, and `DistributionInspect`. These definitions cover local image metadata, content-addressable IDs and digests, image config defaults, build/pull/push progress messages, build cache records, registry mirror/insecure registry configuration, and OCI descriptor/platform metadata for manifest inspection.

Plugin and exec schemas include `ProcessConfig`, `Plugin`, `PluginMount`, `PluginDevice`, `PluginEnv`, `PluginInterfaceType`, and `PluginPrivilege`. The plugin contract captures installed/enabled state, remote references, mutable settings, declared privileges, mount/device/env/interface requirements, rootfs layers, entrypoint/workdir/user, network mode, Linux capabilities/devices, propagated mount, and host namespace requirements.

Swarm and orchestration definitions are present even though their paths are outside this chunk. `ObjectVersion` defines optimistic concurrency for cluster objects. `NodeSpec`, `Node`, `NodeDescription`, `NodeStatus`, `ManagerStatus`, `SwarmSpec`, `ClusterInfo`, `JoinTokens`, `Swarm`, `TaskSpec`, `TaskState`, `Task`, `ServiceSpec`, `EndpointPortConfig`, `EndpointSpec`, `Service`, `ServiceUpdateResponse`, `SecretSpec`, `Secret`, `ConfigSpec`, and `Config` model swarm managers, nodes, services, tasks, secrets, configs, scheduling policy, update/rollback policy, jobs, networking, TLS/CA settings, Raft settings, manager autolock, and default task logging.

System definitions include `SystemVersion`, `SystemInfo`, `PluginsInfo`, `Runtime`, `Commit`, `SwarmInfo`, `LocalNodeState`, `PeerNode`, `EventActor`, and `EventMessage`. These describe daemon version metadata, host capability inventory, storage/runtime/security configuration, registry configuration, swarm status as returned by `/info`, event stream payloads, and component commit IDs. `ErrorResponse` and `IdResponse` are common response envelopes used across the full API.

## In-Scope Path Surface

`GET /containers/json` (`ContainerList`) returns an array of `ContainerSummary` objects. It supports `all`, `limit`, `size`, and `filters` query parameters. Filters are JSON-encoded `map[string][]string` values despite being typed as strings in Swagger, and include ancestor, before/since, exposed or published ports, exit code, health, id, isolation, task marker, label, name, network, status, and volume.

`POST /containers/create` (`ContainerCreate`) creates a container from a body combining `ContainerConfig`, `HostConfig`, and `NetworkingConfig`. It accepts an optional validated `name` query parameter and a `platform` query parameter in `os[/arch[/variant]]` form for image lookup. Successful creation returns `201` with an ID and warnings. Failure modes include malformed input, missing image, name/resource conflict, and server errors.

`GET /containers/{id}/json` (`ContainerInspect`) returns detailed low-level container state: identifiers, created time, command path/args, `ContainerState`, image ID, resolver/hosts/log paths, name, restart count, graph driver data, platform, security labels, active exec IDs, host config, filesystem sizes when requested, mount points, portable config, and network settings. It has a `size` query flag and returns `404` for unknown containers.

`GET /containers/{id}/top` (`ContainerTop`) lists processes inside a container by running `ps` on Unix systems; the endpoint is explicitly unsupported on Windows. The output has `Titles` and `Processes`, where each process is an array aligned to the title columns. `ps_args` defaults to `-ef`.

`GET /containers/{id}/logs` (`ContainerLogs`) returns stdout/stderr logs as a binary stream. It only works for containers using the `json-file` or `journald` logging drivers. Query controls include `follow`, `stdout`, `stderr`, `since`, `until`, `timestamps`, and `tail`; the stream format is tied to the attach protocol but this endpoint does not upgrade the connection.

`GET /containers/{id}/changes` (`ContainerChanges`) reports modified, added, and deleted filesystem paths in the container writable layer. Each response item has `Path` and a numeric `Kind` enum: `0` modified, `1` added, and `2` deleted. `GET /containers/{id}/export` (`ContainerExport`) exports the container filesystem as an `application/octet-stream` tarball.

`GET /containers/{id}/stats` (`ContainerStats`) returns live or one-shot resource usage data. The schema is deliberately loose (`type: object`) because the payload is a nested daemon stats object. The documentation defines CPU and memory percentage formulas, `precpu_stats` semantics, cgroup v1/v2 differences, and fields absent on cgroup v2. Query parameters are `stream` and `one-shot`, where one-shot must be used with `stream=false`.

`POST /containers/{id}/resize` (`ContainerResize`) resizes a container TTY with required `h` and `w` query parameters. Lifecycle operations include `ContainerStart`, `ContainerStop`, `ContainerRestart`, and `ContainerKill`. Start and stop return `204` on success and `304` for already-started or already-stopped states. Stop/restart accept timeout `t`; kill accepts a signal string or integer and returns `409` when the target is not running.

`POST /containers/{id}/update` (`ContainerUpdate`) changes live container resource settings and restart policy using a body composed from `Resources` plus `RestartPolicy`, returning warnings. `POST /containers/{id}/rename` (`ContainerRename`) changes the container name and can conflict if the requested name is already used.

`POST /containers/{id}/pause` and `/unpause` suspend and resume container processes. Pause documents Linux freezer cgroup semantics, where processes do not observe a catchable `SIGSTOP`; this matters because inspect state can report both `Running` and `Paused`.

`POST /containers/{id}/attach` (`ContainerAttach`) and `GET /containers/{id}/attach/ws` (`ContainerAttachWebsocket`) expose interactive stream attachment. Attach supports raw HTTP connection hijacking with `200`, optional `101 UPGRADED` responses when upgrade headers are sent, and `application/vnd.docker.raw-stream`. Query controls include detach keys, prior logs, live stream, stdin, stdout, and stderr. The websocket variant exposes logs and stream booleans with the same container identity and detach-key handling.

## Control Flow And Protocol Behavior

The in-scope operations model the Docker CLI container workflow as multiple HTTP calls: create a container, inspect it, start it, optionally attach/log/resize/stream stats, update resources, pause/unpause, stop/restart/kill, inspect state again, and later remove or archive via endpoints outside this chunk. The API contract separates desired configuration (`ContainerConfig`, `HostConfig`, `NetworkingConfig`) from observed runtime state (`ContainerState`, `NetworkSettings`, `MountPoint`, `GraphDriverData`).

Streaming and raw transport behavior are the main control-flow complexity. Logs can return a continuous binary body when `follow=true`. Stats can stream repeated JSON objects or return a single snapshot. Attach hijacks the HTTP connection or upgrades it, after which the socket is no longer ordinary request/response JSON. When TTY is disabled, stdout and stderr are multiplexed with 8-byte headers: stream type in the first byte and big-endian payload size in the last four bytes. When TTY is enabled, the stream is raw PTY data without multiplexing.

Several operations encode idempotency and state transitions in status codes. `start` and `stop` distinguish success from already-in-that-state with `204` versus `304`. `kill` uses `409` for a non-running container. `create` and `rename` use conflict responses for name or object conflicts. Common missing-object and server-failure behavior is represented with `ErrorResponse`.

The spec repeatedly relies on JSON-in-query patterns. In this chunk the clearest example is `ContainerList.filters`, where the Swagger type is only `string`, but clients must serialize a structured map of lists. This is an integration hotspot for generated clients because the wire contract is more structured than the OpenAPI type can express.

## State And Persistence Behavior

Container state persists in daemon storage and is exposed through list, inspect, logs, changes, export, stats, and lifecycle endpoints. The inspect response includes persisted config, host config, name, restart count, log path, resolver/hosts files, security labels, graph-driver metadata, mounts, network attachments, and active exec IDs. `ContainerState` records running/paused/restarting/removing/exited/dead status, PID, exit code, OOM status, timestamps, and optional health state.

Create-time settings can allocate or reference persistent resources. Named volumes created or used through `Mount` are not removed with the container. Bind mounts and named pipes depend on host paths existing before container creation. Port bindings and `PublishAllPorts` are assigned on start and can change across restarts. `NetworkingConfig` links container state to network endpoint state and can request static IPv4/IPv6/link-local addresses and aliases.

Filesystem endpoints expose the mutable writable layer. `ContainerChanges` reports additions, deletions, and modifications relative to the image filesystem, while `ContainerExport` emits the container filesystem as a tar archive. Logs are persisted only for supported logging drivers in this endpoint. Stats are live runtime observations rather than persisted configuration, and their field availability depends on cgroup version and platform.

Resource updates mutate daemon-maintained container configuration without recreating the container. The supported update body is narrower than full `HostConfig`, focusing on `Resources` and `RestartPolicy`. Pause/unpause and lifecycle endpoints mutate runtime state but leave the container object and its persisted configuration intact.

## Dependencies And Integration Points

This file depends on Swagger/OpenAPI 2.0 tooling, ReDoc rendering behavior, and Docker's API generation pipeline. Vendor extensions such as `x-go-name`, `x-nullable`, and titles/descriptions influence generated Go types and documentation, so schema edits can affect both docs and generated client/server contracts.

The in-scope container APIs integrate with Docker Engine subsystems for image lookup, container runtime execution through OCI runtimes/containerd, cgroups resource control, storage graph drivers, log drivers, health checks, network drivers/IPAM, volume drivers, namespace/security configuration, and platform-specific Linux and Windows container behavior.

External protocol dependencies include HTTP clients and proxies that can support raw connection hijacking, websocket attachment, binary tar/export bodies, binary log streams, and long-lived stats streams. The schema references registry, OCI, swarmkit, and plugin concepts in definitions used by later paths, so changes in this chunk can still affect generated types for image distribution, swarm, plugin, and system APIs outside the path range.

## Risks And Edge Cases

Because this OpenAPI document is a source contract, mistakes in nullability, required fields, enums, or `$ref` targets can propagate into generated clients, server handlers, and public documentation. The document intentionally uses an open schema model, so strict clients that reject unknown response fields or servers/tests that reject unknown input fields will be incompatible with the documented API behavior.

Generated clients are especially risky for attach, websocket attach, logs, stats, and export. These operations require stream handling, optional HTTP upgrade, raw socket I/O, binary framing, tar output, or long-lived JSON streams that generic Swagger clients often model poorly. Attach behavior also changes depending on the container TTY setting, so tests must cover both multiplexed and raw PTY streams.

Some schemas are broad or intentionally under-specified. Stats is `type: object` even though clients depend on nested CPU, memory, network, blkio, and pids fields. Driver-specific maps appear throughout graph driver data, log config, network options, volume status/options, registry component details, and plugin settings. These maps should be treated as opaque extension points.

Platform and daemon-capability differences are central. `ContainerTop` is Unix-only. Pause uses Linux freezer cgroups. cgroup v2 omits or changes stats fields compared with cgroup v1. Windows isolation, credential specs, CPU controls, named pipes, and console behavior differ from Linux. Deprecated fields such as kernel memory and legacy network settings remain in the schema for compatibility and should not be removed casually.

State-changing endpoints have operational risk. Resource updates can fail or produce warnings depending on kernel support. Forced signals can terminate workloads immediately. Pause can suspend all processes without process-visible signals. Name conflicts and image platform mismatches surface as warnings or conflicts depending on request shape.

## Test Signals

Validation should parse the full `v1.41.yaml` as OpenAPI 2.0 and verify that all `$ref` targets introduced in lines 1-7812 resolve. Since the chunk cuts off exactly at the end of `/containers/{id}/attach/ws`, this chunk is not intended to be a standalone YAML document independent of the full file.

Contract tests should cover container list filters encoded as JSON map-of-list query strings, create requests combining `ContainerConfig`, `HostConfig`, and `NetworkingConfig`, platform mismatch warnings, missing-image `404`, name conflict `409`, inspect responses with and without `size=true`, and required fields marked with `x-nullable: false`.

Stateful integration tests should exercise create, inspect, start, logs, stats, resize, update, rename, pause, unpause, stop, restart, and kill flows. They should assert documented status distinctions such as `204` versus `304` for start/stop and `409` for killing a stopped container.

Transport tests should use real HTTP clients capable of raw stream handling. They should cover attach with and without upgrade headers, websocket attach, TTY and non-TTY stream formats, stdout/stderr multiplex frame parsing, log following without connection upgrade, stats with `stream=true`, stats with `stream=false&one-shot=true`, and export tarball handling.

Compatibility tests should verify clients ignore unknown response properties, tolerate daemon-specific driver option maps, preserve opaque graph/log/network/volume/plugin fields, and handle platform-specific omissions or deprecated fields without failing strict decoding.
