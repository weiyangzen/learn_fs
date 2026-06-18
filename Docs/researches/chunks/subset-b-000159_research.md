# sources/cloud-native/moby/api/docs/v1.55.yaml lines 1-7937

## Scope

This chunk covers the opening and shared-schema portion of the Docker Engine API v1.55 Swagger 2.0 contract. It includes global API metadata, tag organization, authentication/versioning notes, and the first 158 top-level `definitions` entries. The `paths:` section does not start until line 8283, so this chunk defines the model vocabulary consumed by later endpoint chunks rather than concrete HTTP operations.

The range ends inside the `ClusterVolume` definition at `Info.VolumeContext`; the remainder of `ClusterVolume`, `ClusterVolumeSpec`, `Topology`, `ImageManifestSummary`, and all paths are outside this chunk and must be reconciled by later chunk reports.

## Purpose

The file is the authoritative OpenAPI document for Docker Engine API version `1.55` with `basePath: /v1.55`. It drives API documentation, generated client/server types, and compatibility expectations for Docker Engine objects. The opening comments explicitly describe it as an API documentation and type-generation source, not runtime implementation code.

The metadata establishes common protocol behavior: HTTP/HTTPS schemes, JSON and plain-text content types, standard JSON error bodies, API version-prefix semantics, open response schemas that can gain extra properties, and registry authentication via the `X-Registry-Auth` header. The tag list groups later endpoints into Docker object areas: containers, images, networks, volumes, exec, swarm, nodes, services, tasks, secrets, configs, plugins, and system.

## Important APIs And Types

- Global Swagger metadata defines version `1.55`, Docker Engine API title, versioning rules, open-schema compatibility behavior, and registry authentication payload forms for username/password/serveraddress or identity token.
- Container creation and inspection models are built from `ContainerConfig`, `HostConfig`, `Resources`, `Mount`, `NetworkingConfig`, `EndpointSettings`, `ContainerInspectResponse`, `ContainerSummary`, `ContainerCreateResponse`, `ContainerUpdateResponse`, `ContainerState`, `ContainerTopResponse`, and `ContainerWaitResponse`.
- Runtime resource models include CPU, memory, block I/O, PID, ulimit, device, namespace, init, sysctl, logging, and Windows isolation fields. The definitions distinguish portable container config from host-dependent `HostConfig`.
- Mount and storage models include `MountType`, `MountPoint`, `Mount`, `DeviceMapping`, `DeviceRequest`, `ThrottleDevice`, `DriverData`, `Storage`, `RootFSStorage`, `RootFSStorageSnapshot`, and `FilesystemChange`.
- Image models include `ImageHistoryResponseItem`, `ImageConfig`, `ImageInspect`, `ImageSummary`, `ImagesDiskUsage`, `ImageDeleteResponseItem`, registry auth/streaming status shapes, image identity/provenance structures, signature metadata, and OCI descriptor references for multi-platform image stores.
- Volume models include `Volume`, `VolumeCreateRequest`, `VolumeListResponse`, `VolumesDiskUsage`, and the beginning of `ClusterVolume` for Swarm CSI cluster volumes.
- Network models include `Network`, `NetworkSummary`, `NetworkInspect`, `NetworkStatus`, `ServiceInfo`, `NetworkTaskInfo`, `ConfigReference`, `IPAM`, `IPAMConfig`, `IPAMStatus`, `SubnetStatus`, `EndpointResource`, `PeerInfo`, `NetworkCreateResponse`, `NetworkConnectRequest`, `NetworkDisconnectRequest`, `EndpointSettings`, and `EndpointIPAMConfig`.
- Build and streaming models include `BuildInfo`, `BuildCache`, `BuildCacheDiskUsage`, `CreateImageInfo`, `PushImageInfo`, `ImageID`, `ErrorDetail`, and `ProgressDetail`.
- Plugin models include plugin privilege/configuration structures such as `PluginMount`, `PluginDevice`, `PluginEnv`, `PluginPrivilege`, and `Plugin`.
- Swarm models include `ObjectVersion`, `NodeSpec`, `Node`, `NodeDescription`, `Platform`, `EngineDescription`, `TLSInfo`, `NodeStatus`, `NodeState`, `ManagerStatus`, `Reachability`, `SwarmSpec`, `ClusterInfo`, `JoinTokens`, `Swarm`, `TaskSpec`, `TaskState`, `TaskStatus`, `Task`, `ServiceSpec`, `EndpointPortConfig`, `EndpointSpec`, `Service`, `ServiceCreateResponse`, and `ServiceUpdateResponse`.
- Secret/config models include `SecretSpec`, `Secret`, `ConfigSpec`, and `Config`. In v1.55 `SecretSpec.Data` and `ConfigSpec.Data` are standard base64-encoded strings, with secret data omitted from non-create responses.
- Statistics and system models include `ContainerStatsResponse`, CPU/memory/network/storage/blkio stats subtypes, `ContainersDiskUsage`, `SystemVersion`, `SystemInfo`, `ContainerdInfo`, `FirewallInfo`, `PluginsInfo`, `RegistryServiceConfig`, `IndexInfo`, `Runtime`, `Commit`, `SwarmInfo`, `LocalNodeState`, `PeerNode`, `EventActor`, and `EventMessage`.
- OCI and distribution models include `OCIDescriptor`, `OCIPlatform`, and `DistributionInspect`.
- Shared response/error models include `ErrorResponse`, `IDResponse`, and many operation-specific warning/id response objects.

## Control Flow

There are no executable functions or endpoint handlers in this range. The control flow is contract-level composition: later path operations reference these definitions through `$ref`, and generated clients/servers use the definitions to marshal request bodies, decode response bodies, and model status/error results.

Container-related flow is expressed through type layering. `ContainerConfig` holds portable image/runtime defaults, `HostConfig` composes `Resources` plus host-specific network, mount, namespace, security, logging, and platform options, `NetworkingConfig` maps requested network attachments, and `ContainerInspectResponse` combines created state, host config, graph/storage data, mounts, config, and network settings. Summary/list responses intentionally use reduced forms such as `ContainerSummary`.

Swarm flow is encoded as versioned state objects. `ObjectVersion` documents optimistic concurrency for nodes, services, swarm objects, secrets, configs, tasks, and cluster volumes: callers read a version and send that version with updates so concurrent writers do not overwrite each other unintentionally. Service scheduling flow is represented by `ServiceSpec` -> `TaskSpec` -> task status/state, with restart/update/rollback policies, placement constraints, resources, networks, secrets, configs, endpoint ports, and job-mode status fields.

Image and registry flow is represented by identity and descriptor types. `ImageInspect` and `ImageSummary` can expose OCI descriptors and manifest summaries when the daemon has a multi-platform image store. Pull/build/signature provenance is modeled through `Identity`, `PullIdentity`, `BuildIdentity`, and signature/timestamp/signer structures.

System and stats flow is sampling/reporting oriented. `ContainerStatsResponse` contains current and previous CPU samples, memory, network, blkio, PID, and Windows storage fields. `SystemInfo` and `SystemVersion` expose daemon configuration and host/runtime capabilities that clients use to decide which options and endpoint behaviors are available.

## State And Persistence Behavior

This YAML does not persist data itself, but many definitions describe persistent Docker and Swarm state. Containers have stable 64-character IDs, creation timestamps, persisted host-managed files under the Docker root, image references, restart counts, mounts, configs, state, health, and size fields. The spec warns that generated files such as resolv.conf, hostname, hosts, and log files are daemon-managed and should not be modified by other tools.

Images are content-addressed by configuration digest and may also be referenced by repo tags and repo digests. Local cache metadata such as graph driver data, layer lists, last tag time, image identity, signatures, and multi-platform descriptors is daemon-local and may be absent depending on store capabilities.

Volumes are persistent resources with drivers, mountpoints, labels, scope, driver options, usage data, and optional cluster-volume state. Usage data is only populated for system disk usage responses, with unavailable values represented by `-1`.

Networks are persisted with ID, name, driver, IPAM configuration, labels, options, config-only/config-from relationships, overlay peers, service attachments, and runtime IPAM status. Endpoint settings combine create-time configuration with inspect-time operational data such as endpoint IDs, gateways, addresses, DNS names, and driver options.

Swarm objects carry creation/update timestamps, `ObjectVersion`, specs, and status fields. `SwarmSpec` captures Raft, dispatcher, CA, encryption-at-rest, task-default, and address-pool settings. `ClusterInfo` intentionally omits join tokens while `Swarm` includes them. Secrets/configs are stored as Swarm objects; secret payload data is accepted on create but is not returned by ordinary endpoints.

System and stats definitions describe observed daemon/host state, not user-controlled persistent records. Many fields are informational, debug-only, daemon-start snapshots, optional, or unstable in formatting.

## Dependencies

The document depends on Swagger/OpenAPI 2.0 conventions plus Docker-specific vendor extensions:

- `$ref` links compose most larger objects from shared definitions.
- `x-go-name`, `x-go-package`, `x-go-type`, `x-nullable`, and `x-omitempty` guide generated Go API types and JSON behavior.
- `format` values such as `int64`, `uint64`, `uint32`, `uint16`, `dateTime`, `date-time`, `ip-address`, and `CIDR` guide validation and code generation.
- `net/netip` is explicitly requested for several IP address fields through `x-go-type`.
- Runtime semantics depend on Docker Engine subsystems: containerd, OCI runtimes, graph drivers or snapshotters, cgroups v1/v2, swarmkit, BuildKit build cache/history, registry configuration, CDI, NRI, firewall backends, volume/network/logging/secret drivers, and OCI image/distribution specs.

The chunk also depends on definitions that are outside this line range. `ImageInspect.Manifests` and `ImageSummary.Manifests` reference `ImageManifestSummary`, `VolumeCreateRequest.ClusterVolumeSpec` and `ClusterVolume.Spec` reference `ClusterVolumeSpec`, and the truncated `ClusterVolume` continuation references `Topology` after line 7937.

## Integration Points

Generated clients use these definitions as method request/response types for path operations later in the file. Any schema drift here changes SDK method signatures, nullable pointer behavior, enum handling, response decoding, documentation tables, and compatibility tests.

The definitions integrate with CLI workflows: `docker ps` maps to container summaries, `docker inspect` to inspect responses, `docker stats` to stats models, `docker info` and `docker version` to system models, `docker service` and `docker swarm` to Swarm specs/status, and volume/network/image commands to their corresponding resource models.

Swarm integrations are broad. Service task specs reference secrets, configs, networks, mounts, resources, endpoint ports, plugin runtimes, credential specs, placement constraints, and update/rollback strategies. Node and swarm models integrate with TLS certificate issuance, external CAs, manager autolock, join tokens, Raft settings, and manager reachability.

Runtime integrations include containerd namespaces, OCI runtimes, CDI spec directories and discovered devices, NRI status, cgroup versions, firewall backends, storage drivers, logging drivers, registry mirrors/insecure registries, and image signature/provenance data.

## Risks And Edge Cases

- This chunk ends mid-`ClusterVolume`; any per-file report must merge with later chunks before treating cluster-volume definitions as complete.
- Several fields are explicitly experimental or unstable, including multi-platform image store descriptors/manifests, plugin task specs, NRI detail formatting, runtime status formatting, firewall info formatting, daemon ID format, and OS version formatting. Clients should preserve unknown fields and avoid strict assumptions.
- The API uses an open schema model. Generated clients that reject unknown response properties will break against newer daemons.
- Some references point outside the chunk (`ImageManifestSummary`, `ClusterVolumeSpec`, `Topology`). Chunk-local validation would report missing definitions unless it is run against the whole YAML file.
- Many fields are platform-specific or cgroup-version-specific. Stats models differ across Linux, Windows, cgroups v1, and cgroups v2; absent, null, zero, and default date values have distinct meanings.
- `ContainerState.Running` and `Paused` are not mutually exclusive. Clients should use `Status` when they need a single state.
- Secret/config data is base64-encoded and size-limited. Secret data is create-only and should not be expected or exposed from inspect/list responses.
- Registry insecure configuration is documented as testing-only because it weakens transport security. Clients should not normalize this into a safe default.
- Versioned Swarm updates rely on `ObjectVersion`; missing or stale versions can cause write conflicts, and generated clients must expose those version parameters accurately in endpoint chunks.
- Some schema details are intentionally informational and driver-specific, such as graph driver data, volume status, runtime status, registry details, and system driver status. Tests should avoid asserting exact key sets for those maps unless tied to a controlled daemon.
- There are schema quirks that deserve validation attention: mixed `dateTime` and `date-time` formats, YAML examples where numeric examples are quoted strings, and Docker vendor extensions that generic OpenAPI tooling may ignore.

## Test Signals

Useful validation signals for this chunk include:

- Whole-file Swagger validation should confirm the v1.55 document remains structurally valid, including references that are defined after this chunk.
- Generated Go type tests should verify `x-go-name`, `x-go-package`, `x-go-type`, nullable, and omitempty behavior for container, image, network, volume, swarm, stats, and system models.
- Contract tests against a real daemon should compare representative inspect/list/stats/info/version responses with these schemas while allowing documented optional and open-schema fields.
- Container tests should cover host config/resource options, mount variants, network endpoint configuration, health state, paused/running state semantics, size-only fields, and daemon-managed path fields.
- Image tests should cover tag/digest behavior, local cache metadata, descriptor/manifests only when a multi-platform image store is available, identity/signature warnings, and registry auth payload handling.
- Network tests should cover IPv4/IPv6 enablement, IPAM config/status, config-only networks, overlay peers, service attachments, DNS names, gateway priority, and `netip` typed fields.
- Volume tests should cover local/global scope, usage data availability, driver status/options, and cluster volume references once later chunks provide the complete CSI schema.
- Swarm tests should cover object version concurrency, node roles/availability/reachability, swarm CA/autolock settings, service update/rollback modes, job-mode status, task lifecycle states, secrets/configs references, and platform/resource scheduling.
- Stats tests should exercise Linux cgroups v1, Linux cgroups v2, Windows, one-shot stats, no-network containers, and null/omitted fields.
- System tests should cover debug-only fields, proxy masking, registry insecure/mirror config, CDI/NRI/firewall/containerd optional data, runtime status, security options, warnings, and live restore/default runtime fields.
