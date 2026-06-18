# sources/cloud-native/moby/api/docs/v1.47.yaml lines 1-7686

## Scope And Purpose

This chunk is the opening portion of the Docker Engine API v1.47 Swagger 2.0 specification. It defines the document metadata, API versioning contract, tags used by generated documentation, the bulk of reusable response/request schemas, and the first container endpoints under `paths`.

The file is not runtime implementation code, but it is a central contract source for generated API documentation and generated client/server types. The top-level API description establishes that the Engine API is the HTTP interface used by the Docker client, that unversioned routes currently resolve to v1.47, that unversioned use is deprecated, and that the API uses an open schema model where servers may add response fields and ignore unknown request fields. This is important for client compatibility: consumers must tolerate unknown properties instead of treating the spec as a closed JSON schema.

Lines 1-7686 cover:

- Top-level Swagger metadata, content types, base path `/v1.47`, error response format, registry-auth header semantics, and documentation tags.
- Reusable definitions for containers, images, volumes, networks, plugins, swarm nodes/services/tasks/secrets/configs, daemon system/version/info data, registry configuration, events, OCI descriptors/platforms, distribution inspect responses, swarm CSI cluster volumes, and image manifest summaries.
- Initial container API routes: list containers, create container, inspect container, list container processes, stream container logs, and the start of container filesystem changes.

The chunk ends inside the `/containers/{id}/changes` operation parameter list, so only the visible portion of that operation is covered here.

## API Model And Generation Contract

The document is Swagger 2.0 and declares both HTTP and HTTPS schemes. It globally consumes and produces `application/json` and `text/plain`, with individual streaming endpoints overriding output media types when needed.

`operationId` values are named with a singular noun and verb, such as `ContainerList`, `ContainerCreate`, `ContainerInspect`, `ContainerTop`, `ContainerLogs`, and `ContainerChanges`. These IDs are the stable anchors for generated clients, generated server bindings, and ReDoc operation links. Schema extensions such as `x-go-name`, `x-nullable`, and `x-omitempty` are generation hints for Go type names, pointer/nullability behavior, and JSON omission behavior.

The definitions are highly interconnected through `$ref`. Important composition patterns include:

- `HostConfig` uses `allOf` to include all `Resources` fields and then extend with host-specific container settings.
- `Swarm` composes `ClusterInfo` with `JoinTokens`.
- `ContainerCreate` request body composes `ContainerConfig` with `HostConfig` and `NetworkingConfig`.
- Many objects reuse shared leaf schemas such as `PortMap`, `Mount`, `MountPoint`, `EndpointSettings`, `ObjectVersion`, `HealthConfig`, `Driver`, `OCIDescriptor`, and `OCIPlatform`.

Because this spec drives both docs and generated types, small schema changes can affect user-visible docs, generated Go structs, client compatibility, and daemon request validation behavior.

## Important Definitions

### Container And Runtime Configuration

`ContainerConfig` represents portable container configuration: hostname/domain, user, stdio attachment, TTY/stdin behavior, environment, command, entrypoint, healthcheck, image reference, declared volumes, working directory, labels, stop signal/timeout, shell, and legacy/deprecated fields such as container-level `MacAddress`.

`HostConfig` represents host-dependent configuration by combining `Resources` with runtime, namespace, security, mount, logging, network, and platform-specific fields. It covers bind strings, structured `Mounts`, port bindings, restart policy, auto-remove, volume inheritance, console size, annotations, capability add/drop, cgroup namespace mode, DNS settings, extra hosts, IPC/PID/UTS/user namespace modes, privileged mode, read-only rootfs, SELinux/security options, storage options, tmpfs maps, sysctls, runtime selection, shared memory size, Windows isolation, masked paths, and read-only paths.

`Resources` captures cgroup and platform resource controls. It includes CPU shares/quota/period/realtime controls, cpusets, memory/swap/reservation/swappiness, OOM behavior, init, PIDs limit, ulimits, device mappings, device cgroup rules, device driver requests, block I/O weights and throttles, and Windows CPU/I/O controls. `ThrottleDevice`, `DeviceMapping`, and `DeviceRequest` provide reusable substructures.

`MountType`, `Mount`, and `MountPoint` split requested mounts from reported mounts. `Mount` is the create/service input shape with bind, volume, tmpfs, cluster, and npipe behavior; it includes bind propagation, non-recursive and recursive read-only controls, volume labels/driver/subpath, and tmpfs size/mode/options. `MountPoint` is the inspect/list output shape with source, destination, driver, mode, read/write state, and propagation.

`RestartPolicy` defines container restart behavior, including the important daemon-side backoff behavior for repeated restarts. `HealthConfig`, `Health`, and `HealthcheckResult` describe healthcheck configuration and observed health state.

`ContainerState`, `ContainerCreateResponse`, `ContainerWaitResponse`, and `ContainerWaitExitError` are response shapes used by container lifecycle endpoints. `ContainerState` documents the subtle relationship between `Running` and `Paused`: paused Linux containers are both running and paused, so clients should use `Status` for state decisions.

### Container, Image, And Filesystem Views

`ContainerSummary` is the compact list representation returned by `GET /containers/json`. It intentionally differs from inspect output and includes ID, names, image metadata, command, created timestamp, exposed ports, size fields, labels, state/status, host network mode/annotations, summarized network settings, and mount points.

`FilesystemChange` and `ChangeType` define the diff representation returned by container changes endpoints. `Kind` is an integer enum: modified, added, or deleted.

`ImageHistoryResponseItem`, `ImageConfig`, `ImageInspect`, `ImageSummary`, `ImageDeleteResponseItem`, `ImageID`, and `ImageManifestSummary` model image history, configuration defaults, local image inspection, list summaries, delete results, digest IDs, and manifest-level summaries. `ImageConfig` explicitly marks several old container-runtime fields as deprecated and not part of the image specification, with planned removal notes. `ImageSummary.Manifests` and `ImageManifestSummary` expose experimental per-manifest data for multi-platform images, image/attestation distinction, local availability, content-store size, unpacked size, container users, and attestation target digest.

`DriverData` exposes storage-driver metadata such as overlay directories. The spec warns that this data is driver-specific and informational, which is a compatibility signal for clients not to depend on exact keys.

### Volumes And Networks

`Volume`, `VolumeCreateOptions`, and `VolumeListResponse` describe local volume metadata, creation options, labels, driver options, cluster-volume flags, warnings, and list responses. `ClusterVolume`, `ClusterVolumeSpec`, and `Topology` add swarm CSI volume concepts: swarm object IDs, object versions, publish state per node, capacity, plugin volume IDs, access mode, sharing mode, mount/block volume choices, topology requirements, secret references, capacity ranges, and availability.

`Network`, `NetworkingConfig`, `NetworkSettings`, `EndpointSettings`, `EndpointIPAMConfig`, `NetworkContainer`, `IPAM`, `IPAMConfig`, `PeerInfo`, `NetworkCreateResponse`, and `NetworkAttachmentConfig` define both container network configuration and operational network state. The spec distinguishes request-time endpoint config from inspect-time operational fields such as network IDs, endpoint IDs, gateways, IP addresses, DNS names, and default bridge legacy fields.

Several network fields are explicitly deprecated or default-network-only. `NetworkSettings` retains old default bridge fields such as `EndpointID`, `Gateway`, `IPAddress`, and `MacAddress`, but directs clients to the `Networks` map instead.

### Build, Registry, And Progress Types

`BuildInfo`, `BuildCache`, `CreateImageInfo`, `PushImageInfo`, `ProgressDetail`, `ErrorDetail`, and `ErrorResponse` define streaming and structured status messages used by build, image pull/create/push, and cache APIs. `BuildCache` includes cache record IDs, parents, type enum, description, in-use/shared flags, size, creation/last-used timestamps, and usage count.

`AuthConfig` models registry credentials used with registry-auth headers and auth endpoints. `RegistryServiceConfig` and `IndexInfo` expose daemon registry configuration, mirrors, insecure registries, and deprecated nondistributable artifact settings. The spec warns that insecure registries are suitable only for testing because they permit HTTP or untrusted TLS.

`OCIDescriptor`, `OCIPlatform`, and `DistributionInspect` align the Engine API with OCI image/distribution metadata: descriptors carry media type, digest, and size; platforms carry architecture, OS, OS version/features, and variant; distribution inspection returns a descriptor plus supported platforms.

### Plugins

`PluginMount`, `PluginDevice`, `PluginEnv`, `PluginInterfaceType`, `PluginPrivilege`, and `Plugin` model managed plugin configuration and runtime state. `Plugin` is a large nested object containing mutable user settings, remote references, interface/socket details, entrypoint/workdir/user, Linux capabilities/devices, network mode, propagated mount, IPC/PID host flags, environment/args, and rootfs diff IDs.

Plugin definitions are integration points between the engine, plugin root filesystems, plugin sockets, volume/network/logging capabilities, and user acceptance of plugin privileges.

### Swarm Objects

`ObjectVersion` is the central optimistic concurrency mechanism for swarm objects. Updates must include the current version index so concurrent writes do not silently overwrite each other.

`NodeSpec`, `Node`, `NodeDescription`, `Platform`, `EngineDescription`, `TLSInfo`, `NodeStatus`, `NodeState`, `ManagerStatus`, and `Reachability` describe swarm nodes, manager reachability, node roles, availability, resources, engine plugins, and TLS identity material.

`SwarmSpec`, `ClusterInfo`, `JoinTokens`, `Swarm`, `SwarmInfo`, `LocalNodeState`, and `PeerNode` describe cluster configuration, raft settings, dispatcher heartbeat, CA configuration, manager autolock, task defaults, root CA rotation, address pools, join tokens, local swarm state, and remote managers.

`TaskSpec`, `TaskState`, `ContainerStatus`, `PortStatus`, `TaskStatus`, and `Task` define swarm task scheduling and runtime state. `TaskSpec` is especially broad: it supports mutually exclusive `ContainerSpec`, `PluginSpec`, and `NetworkAttachmentSpec`; container command/env/user/hostname; credential specs for Windows; SELinux/seccomp/AppArmor/no-new-privileges; TTY/stdin/read-only rootfs; mounts; healthchecks; DNS; secrets; configs; sysctls; capabilities; ulimits; resource limits/reservations; restart policy; placement constraints/preferences/platforms; forced updates; runtime; networks; and log driver.

`ServiceSpec`, `EndpointPortConfig`, `EndpointSpec`, `Service`, `ServiceCreateResponse`, and `ServiceUpdateResponse` describe swarm service creation/update and status. Service scheduling modes include replicated, global, replicated job, and global job. Update and rollback configs include parallelism, delay, failure action, monitor period, max failure ratio, and stop/start ordering. Endpoint publishing supports TCP/UDP/SCTP and ingress or host publish modes.

`SecretSpec`, `Secret`, `ConfigSpec`, and `Config` model swarm-distributed sensitive data and configs. Secret data is base64-encoded, create-only, and capped at a documented maximum; configs have a separate larger maximum and optional templating. Service task specs reference secrets/configs by ID while retaining names for lookup/display.

### System And Event Data

`SystemVersion` describes `/version` output: component versions, daemon version, API version range, Git commit, Go version, OS/architecture, kernel, experimental flag, and build time.

`SystemInfo` describes `/info` output and is one of the highest-risk schemas in the chunk because it exposes many daemon and host capabilities. It includes container/image counts, storage driver and driver status, Docker root directory, plugin lists, cgroup/memory/CPU/PID feature support, networking kernel toggles, debug counters, system time, default logging/cgroup/runtime settings, host OS/kernel/architecture, proxy settings with masked credentials, daemon labels, experimental status, swarm status, live-restore flag, Windows isolation default, init binary, component commits, security options, license, default address pools, warnings, CDI specification directories, and containerd connection information.

`ContainerdInfo` is explicitly debugging-only and warns that daemon-owned containerd namespaces should be treated as exclusive to Docker. `PluginsInfo` only lists unmanaged V1 plugins that have been lazily loaded.

`EventActor` and `EventMessage` define engine event payloads with event type, action, actor attributes, scope, and second/nanosecond timestamps.

## Path Operations In This Chunk

### `GET /containers/json` - `ContainerList`

This operation returns a list of `ContainerSummary` objects. Query parameters include:

- `all` to include non-running containers.
- `limit` for most recently created containers.
- `size` to include `SizeRw` and `SizeRootFs`.
- `filters`, encoded as JSON `map[string][]string`.

The documented filters cover image ancestry, before/since containers, exposed/published ports, exit code, health, ID, Windows isolation, swarm task flag, labels, name, network, status, and volume. Successful responses are arrays of compact summaries; errors include 400 for bad parameters and 500 for server errors.

### `POST /containers/create` - `ContainerCreate`

This operation creates a container from a JSON or octet-stream request body. Query parameters include:

- `name`, validated with the documented container-name pattern.
- `platform`, in `os[/arch[/variant]]` form, used for image lookup.

The platform behavior is important: if a platform is specified and the local image cache does not contain that OS/architecture, the daemon returns 404. If no platform is specified and the image exists but does not match the host platform, the container may still be created and a warning is returned.

The body combines `ContainerConfig`, `HostConfig`, and `NetworkingConfig`. The example shows the breadth of accepted inputs: environment, command, image, labels, volumes, exposed ports, stop settings, bind mounts, links, CPU/memory/block-I/O controls, device requests, port bindings, DNS, volumes-from, capabilities, groups, restart policy, auto-remove, network mode, ulimits, logging, security options, cgroup parent, volume driver, shared memory size, and endpoint IPAM/aliases.

Responses are 201 with `ContainerCreateResponse`, 400 for bad parameters, 404 for missing images, 409 for conflicts such as name collisions, and 500 for server errors.

### `GET /containers/{id}/json` - `ContainerInspect`

This operation returns low-level container inspection data. It takes path parameter `id` and query parameter `size`. The response includes container identity, creation time, command path/args, `ContainerState`, image ID, generated config file paths (`ResolvConfPath`, `HostnamePath`, `HostsPath`), log path, name, restart count, storage driver, platform, security labels/profiles, active exec IDs, `HostConfig`, storage `GraphDriver`, optional size fields, mount points, original `ContainerConfig`, and `NetworkSettings`.

The operation returns 404 for unknown containers and 500 for server errors. Its response combines persistent metadata, host-generated paths, current runtime state, and network/storage details, so clients should not assume all fields are stable across platforms, storage drivers, or daemon configurations.

### `GET /containers/{id}/top` - `ContainerTop`

This operation returns processes running inside a container. It is Unix-only and not supported on Windows. It takes `id` and optional `ps_args`, defaulting to `-ef`. The 200 response includes `Titles` and `Processes`, where each process is an array aligned to the title list. Errors are 404 for unknown containers and 500 for server errors.

Because this endpoint shells out to or otherwise follows `ps`-style output on Unix, clients should treat column sets as dependent on `ps_args` and platform behavior rather than a fixed process schema.

### `GET /containers/{id}/logs` - `ContainerLogs`

This operation streams `stdout` and/or `stderr` logs for a container. It only works for containers using the `json-file` or `journald` logging drivers. It produces Docker raw or multiplexed stream media types and returns binary stream data on 200.

Parameters include `id`, `follow`, `stdout`, `stderr`, `since`, `until`, `timestamps`, and `tail`. `tail` accepts either an integer-like string or `all`. Errors are 404 for unknown containers and 500 for server errors.

The stream format references the attach endpoint, but unlike attach, this route does not upgrade the connection and does not set `Content-Type`. That distinction matters for HTTP client code and generated clients that otherwise expect normal JSON responses.

### `GET /containers/{id}/changes` - `ContainerChanges`

The visible portion of this operation returns an array of `FilesystemChange` objects describing added, modified, and deleted paths in a container filesystem. It produces JSON and returns 404 for unknown containers or 500 for server errors. The chunk ends after the required `id` path parameter begins, so any later parameters or tags are outside this chunk.

## Control Flow And Behavioral Contracts

Although this YAML file has no executable control flow, it describes daemon API flows:

- Version selection occurs through the URL prefix. `/v1.47/...` locks clients to this contract, while unversioned routes use the current daemon API version but are deprecated.
- Registry authentication is caller-supplied. Clients send `X-Registry-Auth` as a base64url-encoded JSON credential or identity-token payload to endpoints that contact registries.
- Container creation flows from image/platform selection, body validation, host resource/security/network configuration, network endpoint setup, persistent container metadata creation, and warning/error reporting.
- Container inspection flows back through persistent metadata, runtime state, storage-driver data, generated daemon paths, mount state, and network endpoint state.
- Container logs flow through daemon log drivers. The endpoint is constrained by driver support and returns a stream rather than a JSON envelope.
- Swarm updates use `ObjectVersion.Index` as an optimistic concurrency guard; update requests based on stale versions can be rejected rather than overwriting newer changes.
- Service scheduling flows from `ServiceSpec` to `TaskSpec`, placement constraints/preferences/platforms, resources, restart policy, networks, secrets/configs, and runtime-specific executor behavior.
- System introspection flows from daemon startup/runtime state: some values are fixed at daemon start, some are debug-only, some are omitted when unsupported, and some are intentionally informational and unstable.

## State And Persistence Behavior

The schemas describe several distinct state stores:

- Container metadata persists daemon-side and includes the create-time config, host config, generated filesystem paths, labels, restart policy, mounts, log path, and network attachments.
- Container runtime state is mutable and reported through `ContainerState`, process listings, logs, and filesystem changes.
- Image state is content-addressed by configuration digest and manifest digests. Image summaries can expose local manifest availability, content-store bytes, unpacked snapshot bytes, container users, and BuildKit attestation manifests.
- Volume state persists on the host or, for cluster volumes, as swarm objects coordinated with CSI plugins. Cluster volume publish status tracks per-node publishing lifecycle.
- Network state includes daemon-created networks, IPAM allocations, endpoint IDs, gateways, aliases, DNS names, and overlay peer data.
- Swarm state uses versioned raft-managed objects: nodes, services, tasks, secrets, configs, swarm config, cluster volumes, and join tokens.
- Secrets/configs persist in swarm state, but secret/config payloads are create-time inputs and are not returned by general read endpoints.
- System state includes daemon root directories, containerd namespaces, storage driver state, plugin state, registry configuration, daemon labels, default address pools, proxy configuration, and security/runtime feature flags.
- Events are transient stream/message payloads with actor attributes and timestamps.

The spec repeatedly distinguishes stable API contract fields from informational implementation details. Driver status, runtime status, daemon ID format, containerd debug info, storage metadata, OS version formatting, and plugin lazy-loading behavior are explicitly not stable enough for clients to make hard behavioral assumptions.

## Dependencies And Integration Points

This chunk documents integration points with:

- Docker CLI and generated Docker Engine clients using the HTTP API.
- ReDoc and API documentation tooling consuming tags, markdown descriptions, examples, and operation IDs.
- Go code generation using `x-go-name`, `x-nullable`, `x-omitempty`, `$ref`, and `allOf`.
- OCI image/runtime specifications through image descriptors, platforms, runtimes, content digests, and runtime feature status.
- containerd through runtime invocation, content/image stores, daemon-owned namespaces, and debug connection info.
- Linux kernel facilities including cgroups v1/v2, namespaces, capabilities, SELinux, AppArmor, seccomp, bridge netfilter, tmpfs, mount propagation, OOM killer behavior, PID limits, CPU/memory/block-I/O controls, and sysctls.
- Windows container facilities including process/hyperv isolation, credential specs from file/registry/config, registry-based OS version discovery, and Windows-specific CPU/I/O controls.
- Registry and distribution systems through auth config, mirrors, insecure registry settings, descriptor inspection, push/pull progress, and nondistributable artifact settings.
- SwarmKit concepts including raft object versions, managers/workers, nodes, services, tasks, secrets, configs, join tokens, external CAs, autolock, overlay networks, and CSI cluster volumes.
- Logging drivers, especially `json-file` and `journald` for `ContainerLogs`.
- Plugin subsystems for volume, network, authorization, log, and managed plugin rootfs/socket/capability integration.
- CDI device injection through daemon-exposed CDI spec directories.

## Risks And Edge Cases

- Open schema compatibility is easy to break if generated clients reject unknown response fields or unknown request fields. The top-level description explicitly requires clients to ignore additional response properties.
- Versioning behavior is subtle: clients using unversioned paths implicitly bind to the daemon's current API version, while explicit `/v1.47` paths require daemon support or produce a 400 error.
- `x-nullable`, `required`, `x-omitempty`, and `allOf` combinations can change generated Go pointer/value semantics and JSON output. A schema-only edit can therefore be a behavioral API change.
- `HostConfig` and `Resources` combine many platform-specific fields. Linux-only, Windows-only, cgroup-v1-only, cgroup-v2-unsupported, and runtime-specific fields must remain documented accurately.
- Mount behavior has security-sensitive controls: bind source creation, recursive read-only behavior, propagation modes, SELinux relabel flags, volume subpaths, and tmpfs options can affect host access and isolation.
- Container network fields preserve deprecated default-bridge compatibility while newer clients should use the `Networks` map. Removing or misdocumenting deprecated fields can still break older clients.
- Container create platform selection can create warnings instead of errors when no explicit platform is requested. Tests should distinguish explicit mismatch failure from implicit mismatch warning behavior.
- `ContainerLogs` is stream-oriented and logging-driver-gated. Generated clients must not assume JSON error/response bodies on successful log streams.
- `ContainerTop` is Unix-only and `ps_args`-dependent; fixed process columns are not portable.
- Swarm `ObjectVersion` is the protection against concurrent object updates. Any generated client or endpoint implementation that omits version on update risks lost updates.
- Registry `X-Registry-Auth` handling transports credentials or identity tokens in headers. Redaction, base64url encoding, and endpoint scoping must be tested carefully.
- System info exposes sensitive or operational details such as daemon root path, proxy configuration, security options, runtime status, and containerd address. The spec masks proxy credentials, which is an important security expectation.
- Insecure registry settings are documented as test-only due to security risk. Clients and docs should avoid normalizing them as safe production configuration.
- `ImageManifestSummary` is marked experimental. Consumers should gate strict dependencies on manifest kind, attestation data, and size details.
- Cluster volume schema has nested indentation-sensitive fields for mount/block volume choices. YAML generation or validation changes could accidentally alter the intended shape.

## Test Signals

Useful validation signals for this chunk include:

- Swagger/OpenAPI validation for syntax, `$ref` resolution, duplicate operation IDs, valid enum/type declarations, and line-sensitive YAML nesting.
- Generated Go type diffs for `x-go-name`, `x-nullable`, `x-omitempty`, `required`, and `allOf` changes.
- Golden API documentation checks for tag ordering, operation summaries, markdown rendering, examples, and operation anchors.
- Compatibility tests that deserialize responses with unknown fields and serialize requests with extra fields to confirm open-schema behavior.
- Container list tests covering `all`, `limit`, `size`, and JSON filters for status, label, network, volume, health, publish/expose, ancestor, before, and since.
- Container create tests for name validation, platform lookup, platform mismatch warnings, missing image 404s, name conflict 409s, host config resource/security/mount/network inputs, and networking endpoint config.
- Inspect tests verifying `size` fields, state booleans/status, health state, exec IDs, generated config paths, graph-driver data, mounts, host config, and network settings.
- Logs tests across supported and unsupported log drivers, raw versus multiplexed stream parsing, `follow`, `stdout`, `stderr`, `since`, `until`, `timestamps`, and `tail`.
- Top tests on Unix with default and custom `ps_args`, plus Windows unsupported behavior.
- Filesystem changes tests for modified, added, and deleted paths mapped to `ChangeType` enum values.
- Swarm object update tests that require `ObjectVersion.Index` and reject stale versions.
- System info/version tests that check omitted unsupported fields, debug-only counters, masked proxy credentials, cgroup version behavior, security options, runtime status, and containerd debug info.
- Registry config/auth tests for base64url `X-Registry-Auth`, identity-token payloads, insecure registry CIDRs/hostnames, mirrors, and official registry metadata.
