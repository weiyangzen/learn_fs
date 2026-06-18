# sources/cloud-native/moby/api/docs/v1.50.yaml lines 1-7734

## Scope And Purpose

This chunk is the first 7,734 lines of the Docker Engine API v1.50 Swagger/OpenAPI 2.0 specification. It is not daemon runtime code, but it is an authoritative API contract used to generate Docker Engine API documentation and client/server API types. The chunk declares global protocol metadata for API version `/v1.50`, ReDoc tag organization, the shared `definitions` model for most Engine resources, and only the opening of the `paths` table.

The path surface included here begins at `GET /containers/json` and stops inside that operation's `filters` parameter description. The full `ContainerList` operation and all later endpoints are outside this chunk, so this document treats endpoint behavior mainly through the schemas and the visible beginning of the list-containers path. The final per-file report should reconcile this with later chunks that contain the rest of the paths.

## API Contract Structure

The document declares `swagger: "2.0"`, HTTP and HTTPS schemes, JSON and plain-text global media types, and `basePath: "/v1.50"`. The `info` block describes the Engine API as the HTTP API used by the Docker client, documents JSON error bodies with a `message` field, explains URL version prefixes, says unversioned API use is deprecated, and establishes the open-schema compatibility rule: clients must tolerate additional response properties and the server ignores unknown query parameters and request-body properties.

Top-level tags drive generated documentation grouping: primary objects (`Container`, `Image`, `Network`, `Volume`, `Exec`), swarm objects (`Swarm`, `Node`, `Service`, `Task`, `Secret`, `Config`), and system objects (`Plugin`, `System`). The definitions section starts at line 174 and runs through `ImageManifestSummary` immediately before `paths` at line 7698. Vendor extensions such as `x-go-name`, `x-nullable`, `x-omitempty`, titles, and examples are part of the generation contract and affect generated Go names, nullability, and rendered documentation.

## Important Schemas And Types

Container configuration and runtime state are centered on `ContainerConfig`, `HostConfig`, `Resources`, `NetworkingConfig`, `NetworkSettings`, `ContainerState`, `ContainerInspectResponse`, `ContainerSummary`, `ContainerCreateResponse`, and `ContainerUpdateResponse`. `ContainerConfig` models portable image/runtime settings such as user, attach flags, TTY/stdin behavior, environment, command, healthcheck, image reference, exposed ports, volumes, working directory, entrypoint, labels, stop signal/timeout, and shell. `HostConfig` composes `Resources` with host-dependent settings including binds, logging, network mode, port bindings, restart policy, auto-remove, structured mounts, capabilities, namespace modes, DNS, extra hosts, privileged mode, read-only rootfs, security/storage options, sysctls, runtime, annotations, Windows isolation, console size, masked paths, and readonly paths.

`Resources` captures cgroup and platform resource controls: CPU shares/quota/period/realtime, cpusets, block IO weights and throttles, device mappings, `DeviceRequest` accelerator requests, memory/swap/swappiness/OOM/PIDs controls, ulimits, and Windows CPU/IO controls. `RestartPolicy` documents daemon restart semantics, including backoff. `HealthConfig`, `Health`, and `HealthcheckResult` define health probe configuration and inspect-time health state.

Storage and mount models include `MountType`, `MountPoint`, `Mount`, `Volume`, `VolumeCreateOptions`, `VolumeListResponse`, `ClusterVolume`, `ClusterVolumeSpec`, and `Topology`. v1.50 extends mount coverage to `cluster` and `image` mount types in addition to bind, named pipe, tmpfs, and volume mounts. `Mount` includes bind propagation and recursive read-only controls, volume driver options and subpaths, image subpaths, and tmpfs size/mode/options. `ClusterVolume` and `ClusterVolumeSpec` model Swarm CSI cluster volumes, access modes, sharing rules, topology requirements, capacity ranges, secrets passed to storage plugins, availability, controller/publish status, and plugin-provided volume context.

Networking schemas include `Port`, `PortMap`, `PortBinding`, `Network`, `ConfigReference`, `IPAM`, `IPAMConfig`, `NetworkContainer`, `PeerInfo`, `EndpointSettings`, `EndpointIPAMConfig`, and `NetworkAttachmentConfig`. They model host/container port mappings, network driver/IPAM settings, config-only networks, overlay peers, endpoint aliases/links/MAC/static addresses, default-gateway priority, per-network DNS names, and service attachment options.

Image, build, and registry schemas include `ImageHistoryResponseItem`, `ImageInspect`, `ImageConfig`, `ImageSummary`, `ImageDeleteResponseItem`, `BuildInfo`, `BuildCache`, `ImageID`, `CreateImageInfo`, `PushImageInfo`, `AuthConfig`, `RegistryServiceConfig`, `IndexInfo`, `OCIDescriptor`, `OCIPlatform`, `DistributionInspect`, and `ImageManifestSummary`. These definitions cover local image metadata, content-addressable IDs and manifest digests, multi-platform descriptors, image config defaults, build/pull/push progress records, build cache records, registry mirrors/insecure registry state, and detailed manifest summaries for image and attestation manifests.

Plugin and exec-related schemas include `ProcessConfig`, `Plugin`, `PluginMount`, `PluginDevice`, `PluginEnv`, `PluginInterfaceType`, and `PluginPrivilege`. The plugin contract captures installed/enabled state, remote references, mutable settings, declared privileges, rootfs layers, entrypoint/workdir/user, plugin interface/socket/protocol, network mode, Linux capabilities/devices, propagated mounts, and host namespace requirements.

Swarm schemas include `ObjectVersion`, `NodeSpec`, `Node`, `NodeDescription`, `Platform`, `EngineDescription`, `TLSInfo`, `NodeStatus`, `NodeState`, `ManagerStatus`, `Reachability`, `SwarmSpec`, `ClusterInfo`, `JoinTokens`, `Swarm`, `TaskSpec`, `TaskState`, `TaskStatus`, `Task`, `ServiceSpec`, `EndpointPortConfig`, `EndpointSpec`, `Service`, `ServiceCreateResponse`, `ServiceUpdateResponse`, `SecretSpec`, `Secret`, `ConfigSpec`, and `Config`. They define optimistic concurrency through object versions, node state and manager reachability, Raft/dispatcher/CA/encryption settings, service scheduling modes including job modes, update and rollback policy, task placement and resources, service ports, secrets/configs, and Windows credential-spec options.

System and telemetry schemas include `ContainerStatsResponse` and its detailed nested stats types, `ContainerTopResponse`, `ContainerWaitResponse`, `SystemVersion`, `SystemInfo`, `ContainerdInfo`, `FirewallInfo`, `PluginsInfo`, `Runtime`, `Commit`, `SwarmInfo`, `LocalNodeState`, `PeerNode`, `EventActor`, and `EventMessage`. v1.50 gives stats a structured schema for CPU, memory, blkio, PIDs, network, and Windows storage data instead of a fully loose object. `SystemInfo` exposes daemon feature support, host OS/architecture, root dir, proxy settings, registry config, runtimes, swarm state, live restore, default address pools, firewall backend, CDI spec directories, discovered CDI devices, and containerd namespace/socket information.

## In-Scope Path Surface

The only path begun in this chunk is `GET /containers/json`, operationId `ContainerList`, summarized as "List containers". The visible contract says it returns a smaller representation than `ContainerInspect`, produces JSON, and starts defining query parameters: `all` to include non-running containers, `limit` for the most recently created containers including stopped ones, `size` to include `SizeRw` and `SizeRootFs`, and the beginning of `filters`, which is described as JSON-encoded filter data. The operation's complete filter list, responses, and later container paths are in the next chunk.

Because all shared definitions are present here, many later operations depend on this chunk even though their `paths` entries are out of range. Create/inspect/update/list container operations depend on the container schemas; image endpoints depend on image, registry, OCI, and manifest schemas; volume/network/plugin/swarm/system endpoints depend on their corresponding definitions; and error handling across the file uses `ErrorResponse` and ID-style responses such as `IDResponse`.

## Control Flow And Protocol Behavior

This chunk models the API's data contracts more than endpoint sequencing. The main control-flow pattern is separation between desired configuration, observed runtime state, and mutable daemon-managed state. `ContainerConfig`, `HostConfig`, and `NetworkingConfig` describe create-time intent. `ContainerInspectResponse`, `ContainerSummary`, `ContainerState`, `MountPoint`, and `NetworkSettings` describe persisted and live daemon observations. Update responses and warning fields indicate partial capability or platform-dependent adjustments.

Swarm control flow is represented through versioned objects and desired-versus-observed state. `ObjectVersion` is required for conflict-aware updates of nodes, services, swarm specs, secrets, and configs. `TaskSpec`, `ServiceSpec`, update/rollback configs, job status, and task desired/current state model the reconciliation loop used by swarm managers: specs are persisted, schedulers place tasks based on resources, constraints, platforms, topology, and network attachments, and status fields reflect the asynchronous outcome.

Streaming and protocol complexity is implied by schemas even where paths are later. `BuildInfo`, `CreateImageInfo`, and `PushImageInfo` are progress-message envelopes for long-running build/pull/push streams. `ContainerStatsResponse` models repeated or one-shot stats samples and explicitly distinguishes `read` and `preread` behavior. `EventMessage` represents event stream payloads. `OCIDescriptor` and manifest summaries connect local image state to OCI registry/content-store flows.

The spec also encodes compatibility flow. Open-schema behavior means clients should ignore extra response fields, and server-side request handling should not fail solely because unknown fields are present. Several fields are explicitly experimental, deprecated, platform-specific, or omitted under certain daemon/storage/cgroup modes, so robust clients must branch on presence rather than assuming uniform payloads.

## State And Persistence Behavior

Container state persists in daemon storage and is exposed through IDs, names, image references, restart counts, graph-driver metadata, host config, generated resolver/hostname/hosts/log paths, mounts, network settings, health state, and live process status. Size fields are optional and only populated when requested by relevant endpoints. `ContainerSummary.Image` can change to a canonical image digest when the original image reference is untagged.

Volumes and mounts describe persistent storage boundaries. Named volumes are not removed just because a container is removed, local volume usage data may be available for disk-usage reporting, and driver-specific options/status maps are opaque. Cluster volumes are Swarm objects with independent IDs, versions, topology, capacity, availability, publish status, and CSI plugin state; they are scheduled and reconciled separately from ordinary local volumes.

Image state is content-addressed and may span local image cache, manifest descriptors, manifest lists/indexes, build cache records, and container usage references. Multi-platform image-store support controls whether descriptors, per-platform manifests, and manifest summaries are present. Registry configuration persists daemon assumptions about secure/insecure registries, mirrors, and official indexes.

System state reflects host and daemon capabilities rather than user-created objects. `SystemInfo` reports kernel/cgroup/storage/runtime/security features, root directory, proxy settings, device discovery, firewall backend, and containerd namespaces. Many of these fields are informational snapshots and can be absent, masked, or unstable in formatting.

Swarm state is persisted as versioned cluster objects. Nodes, services, tasks, secrets, configs, swarm specs, cluster info, join tokens, and cluster volumes all use IDs, versions, timestamps, specs, and status fields to separate desired configuration from manager-observed status. Secrets and configs store base64 payloads at create time, but secret data is explicitly not returned by normal read endpoints.

## Dependencies And Integration Points

The file depends on Swagger/OpenAPI 2.0 tooling, ReDoc rendering, and Docker's API generation pipeline. Schema names, `$ref` targets, required lists, nullability, and vendor extensions are integration points with generated Go types and public docs.

Runtime integration points include Docker Engine's container lifecycle manager, containerd, OCI runtimes such as runc, cgroups v1/v2, storage graph drivers and snapshotters, logging drivers, health checks, network drivers/IPAM, volume drivers, CSI storage plugins, registry clients, BuildKit/build cache records, plugin management, and swarmkit managers/schedulers. Platform-specific integration is significant for Windows isolation, credential specs, named pipes, Windows CPU/storage stats, and Linux-only cgroup, firewall, SELinux, AppArmor, seccomp, and namespace behavior.

External protocol and data-format dependencies include HTTP APIs, JSON payloads, JSON-in-query parameters, RFC3339 timestamps with nanoseconds, OCI image descriptors/platforms, content digests, tar/binary streams in later paths, base64-encoded secret/config data, base64url registry authentication headers described in the global info block, CIDR notation, and opaque driver-specific key/value maps.

## Risks And Edge Cases

This YAML is a public contract source, so incorrect required fields, enum values, nullability, formats, examples, or `$ref` targets can break generated clients, server bindings, and published documentation. The chunk is not standalone YAML because it cuts off inside a path parameter description; validation must run against the full `v1.50.yaml`.

The open-schema rule conflicts with overly strict generated clients. Clients that reject unknown response properties or assume closed maps will be brittle against newer daemons. Conversely, server tests should not assume unknown request properties or query parameters are rejected unless a specific endpoint documents rejection.

Many fields are conditional. Stats differ across Linux, Windows, cgroups v1, cgroups v2, and Hyper-V isolation. Containerd namespaces are informational and should not be modified by external tools. `KernelMemoryTCP` is deprecated or unsupported under common runtimes. Legacy network fields remain for compatibility but are deprecated. Multi-platform image descriptors, manifest summaries, and CDI device fields depend on daemon features and experimental settings.

Security-sensitive areas include insecure registries, proxy credential masking, registry authentication headers, secrets/config payloads, plugin privileges, host namespace access, device injection, bind mounts, recursive read-only mount options, privileged containers, SELinux/AppArmor/seccomp settings, rootless/userns state, and swarm join tokens. Documentation or generated type changes around these fields need careful review because they can alter operator expectations.

Driver-specific maps are intentionally opaque across graph drivers, log drivers, volume drivers, network drivers, runtimes, registry components, firewall backends, plugin settings, and OCI descriptor annotations. Treating these as fixed schemas would lose compatibility with daemon, plugin, or runtime extensions.

## Test Signals

Validation should parse the full `sources/cloud-native/moby/api/docs/v1.50.yaml` as Swagger/OpenAPI 2.0 and verify that every `$ref` target from lines 1-7734 resolves. Since this chunk ends inside `GET /containers/json`, tests should not attempt to validate the chunk alone as a complete YAML document.

Schema-generation tests should assert generated names and nullability for heavily reused definitions such as `ContainerConfig`, `HostConfig`, `Resources`, `ContainerInspectResponse`, `ContainerSummary`, `ImageInspect`, `ImageSummary`, `Volume`, `Network`, `EndpointSettings`, `TaskSpec`, `ServiceSpec`, `SystemInfo`, `ContainerStatsResponse`, `OCIDescriptor`, and `ImageManifestSummary`.

Compatibility tests should decode payloads with unknown fields, omitted optional fields, `null` values where `x-nullable` allows them, opaque driver maps, platform-specific omissions, cgroup v1/v2 stat differences, and multi-platform image-store fields that are absent unless supported.

Contract tests for the visible path boundary should cover `GET /containers/json` query handling for `all`, `limit`, `size`, and JSON-encoded `filters` once the following chunk supplies the complete filter description and responses. Cross-chunk integration tests should also cover the later endpoints that consume the schemas defined here: container create/inspect/update/stats, image inspect/list/build/pull/push, volume/network/plugin/swarm/system operations, and common `ErrorResponse` handling.
