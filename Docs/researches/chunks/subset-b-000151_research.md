# sources/cloud-native/moby/api/docs/v1.51.yaml lines 1-7726

Chunk research for `subset-b-000151`.

## Scope And Purpose

This chunk contains the opening 7,726 lines of the Docker/Moby Engine API v1.51 Swagger 2.0 document. It establishes the API-wide contract and the reusable type system used by later path operations. The file is not executable code, but it is code-adjacent source of truth: comments at the top state that it is used for generating API documentation and client/server types. Its stability therefore matters to generated Go types, generated clients, ReDoc output, and compatibility tests that compare API responses to the schema.

The chunk includes:

- Global Swagger metadata: `swagger: "2.0"`, `schemes` of HTTP/HTTPS, JSON and text media types, `basePath: "/v1.51"`, API title/version/logo, and the long introduction covering errors, versioning, open schema behavior, and registry authentication.
- Tag taxonomy and menu ordering for ReDoc: Container, Image, Network, Volume, Exec, Swarm, Node, Service, Task, Secret, Config, Plugin, and System.
- The complete `definitions:` section through `ImageManifestSummary`.
- The beginning of `paths:` with only the first three description lines for `GET /containers/json`; its parameters, operation id, response definitions, and the rest of the endpoint are outside this chunk.

The primary role of this chunk is schema composition. Later endpoint operations reference these definitions with `$ref` rather than redefining request and response shapes inline.

## API Contract Model

The file is Swagger 2.0, not OpenAPI 3. It uses `definitions` instead of `components.schemas`, and endpoint definitions under `paths` later use references such as `#/definitions/ContainerSummary` and `#/definitions/ErrorResponse`. Several vendor extensions are important:

- `x-go-name` controls generated Go type names where Swagger names differ from Go API packages, for example `ImageHistoryResponseItem` mapping to `HistoryResponseItem`, `ContainerInspectResponse` mapping to `InspectResponse`, and OCI descriptor/platform aliases.
- `x-nullable` differentiates omitted/null-capable fields from required non-null fields. This is heavily used on optional platform-specific stats, image manifest metadata, swarm fields, plugin settings, and daemon capabilities.
- `x-omitempty` marks generated fields that should be omitted when empty, notably experimental image manifest data and plugin metadata.
- `allOf` composes schemas, most notably `HostConfig` layering `Resources` with host-specific container settings, and `MountPoint.Type` reusing `MountType`.

The introduction explicitly states an open schema model: servers may add response properties and ignore unknown request query/body properties. This is a critical compatibility rule for clients generated from this document. Strict JSON decoders that reject additional response fields would be incompatible with the documented contract.

## Global Behavior And Authentication

The API description defines the common error response as a JSON object with `message`, later formalized as `ErrorResponse`. It also describes version negotiation: clients can prefix URLs with `/v1.51`, and omitting the prefix maps to the daemon's current API version but is deprecated. There is a likely documentation drift in the prose: it says omitting the version uses "current version of the API (v1.50)" while the base path and title are v1.51 and the next sentence says `/info` equals `/v1.51/info`. That mismatch is a risk signal for doc generation and compatibility tests.

Registry authentication is documented as client-side. Endpoints that talk to registries expect an `X-Registry-Auth` header carrying base64url-encoded JSON credentials or an identity token. The `AuthConfig` definition later models `username`, `password`, `email`, `serveraddress`, `identitytoken`, and `registrytoken`, with deprecation guidance for `email`.

## Definition Groups

### Containers, Mounts, Resources, And Health

The container foundation starts with port and mount types:

- `Port`, `PortMap`, and `PortBinding` model exposed container ports and host mappings using keys like `80/tcp`.
- `MountType`, `MountPoint`, and `Mount` cover runtime mount reporting and requested mounts. They include bind, cluster, image, npipe, tmpfs, and volume modes, plus detailed bind options, tmpfs options, image/volume subpaths, SELinux and propagation notes, and read-only recursion controls added around v1.44.
- `DeviceMapping`, `DeviceRequest`, `ThrottleDevice`, and `DeviceInfo` model host devices, GPU/CDI-style devices, and throttling inputs.
- `RestartPolicy`, `Resources`, `Limit`, `ResourceObject`, and `GenericResources` model both container runtime limits and swarm resource scheduling.

`Resources` is a broad cgroups/runtime contract. It includes CPU shares/period/quota/realtime, cpusets, block IO, memory/swap/swappiness, OOM behavior, init, PID limits, ulimits, device cgroup rules, GPU/device requests, and Windows-only CPU/IO controls. Several fields are platform-dependent or deprecated, especially `KernelMemoryTCP`, which is called out as deprecated because newer kernels removed the underlying cgroup v1 memory TCP accounting.

`HealthConfig`, `Health`, and `HealthcheckResult` define probe configuration and result state. Probe timing is in nanoseconds with zero meaning inherit, and the status enum is `none`, `starting`, `healthy`, or `unhealthy`. Exit code semantics are documented directly in the schema. Health check commands are expected to be side-effect free, which is a behavioral contract beyond mere typing.

`HostConfig` composes `Resources` and host-specific settings for container creation and update: bind strings, logging driver config, network mode, port bindings, restart policy, auto-remove, volume driver, inherited volumes, structured mounts, console size, runtime annotations, Linux namespace/security/cgroup options, DNS/hosts, tmpfs/sysctls/runtime, Windows isolation, and masked/read-only paths. This is one of the most central definitions because container create/update endpoints and inspect responses depend on it.

`ContainerConfig` and `ImageConfig` model portable config defaults: user, environment, command, healthcheck, entrypoint, labels, working directory, stop signal, shell, volumes, and exposed ports. `ContainerConfig` has container-specific attachment and networking fields. It also carries deprecation on container-level `MacAddress`, directing users to `EndpointSettings.MacAddress`.

### Container Runtime Responses And Stats

The response-side container models appear later:

- `ContainerInspectResponse` combines ID, timestamps, command path/args, state, image ID, daemon-managed host file paths, log path, name, restart count, driver/platform, optional `ImageManifestDescriptor`, labels/security profile fields, exec IDs, `HostConfig`, storage driver data, size fields, mounts, portable config, and `NetworkSettings`.
- `ContainerSummary` is the list/df-style summary shape: names, image reference, image ID, optional image manifest descriptor, command, created timestamp, ports, optional sizes, labels, state/status, reduced host config, per-network settings, and mounts.
- `ContainerState` captures current state booleans and timestamps, but warns that `Running` and `Paused` can both be true on Linux because pause uses the freezer cgroup. Consumers should prefer `Status`.
- `ContainerCreateResponse`, `ContainerUpdateResponse`, `ContainerTopResponse`, `ContainerWaitResponse`, and `ContainerWaitExitError` are focused operation responses.
- `ContainerStatsResponse` and its nested stats definitions model streaming or one-shot stats for CPU, memory, block IO, network, PIDs, and Windows storage.

The stats definitions have many platform and cgroup-version conditions. `ContainerBlkioStats` states that cgroups v2 only reliably has `io_service_bytes_recursive` and many v1 fields are omitted or null. `ContainerCPUUsage.percpu_usage`, `ContainerMemoryStats.max_usage`, `failcnt`, and several memory stat names vary by cgroups v1/v2 and Windows. These are high-risk for generated clients that treat numeric fields as always present.

### Images, Build, OCI, And Distribution

Image definitions cover history, inspection, summaries, build output, push/pull progress, deletion, OCI descriptors, and manifest summaries:

- `ImageHistoryResponseItem` models layer history rows.
- `ImageInspect` includes IDs, descriptors, manifests, tags/digests, deprecated parent and Docker version fields, author/config/platform/size, graph driver details, rootfs layer IDs, and metadata such as last tag time.
- `ImageSummary` is list-oriented and requires many fields including IDs, tag/digest arrays, timestamps, size/shared size, labels, and container count. It also exposes experimental `Manifests` and optional `Descriptor` for multi-platform image stores.
- `BuildInfo`, `CreateImageInfo`, and `PushImageInfo` describe JSON progress streams with deprecated `error` and `progress` fields and preferred `errorDetail`/`progressDetail`.
- `BuildCache` mirrors BuildKit cache records: ID, parents, cache type enum, description, in-use/shared flags, size, creation/last-use timestamps, and usage count.
- `ImageDeleteResponseItem`, `ImageID`, `ErrorDetail`, and `ProgressDetail` are small supporting records.
- `OCIDescriptor`, `OCIPlatform`, `DistributionInspect`, and `ImageManifestSummary` provide the multi-platform and content-store schema. Descriptors include media type, digest, size, URLs, annotations, embedded data, platform, and artifact type. Manifest summary distinguishes image, attestation, and unknown kinds, with separate `ImageData` and `AttestationData`.

Experimental and availability language is concentrated here. The multi-platform image store fields are documented as experimental and may change without backward compatibility. Tests and clients should gate assumptions about `Descriptor`, `Manifests`, and `ImageManifestSummary` by daemon capabilities and request parameters.

### Networking

Networking definitions include both creation-time config and inspect/list output:

- `NetworkingConfig` maps network names to endpoint settings for `docker create` and network connect flows.
- `NetworkSettings` is inspect-time operational data. It contains deprecated default bridge fields that should be replaced by entries in the `Networks` map.
- `EndpointSettings` combines requested endpoint configuration (`IPAMConfig`, links, MAC address, aliases, driver options, gateway priority) and operational output fields (`NetworkID`, `EndpointID`, gateway/IP data, DNS names).
- `EndpointIPAMConfig`, `Address`, `PortMap`, `PortBinding`, `Network`, `ConfigReference`, `IPAM`, `IPAMConfig`, `NetworkContainer`, `PeerInfo`, and `NetworkCreateResponse` support network create/list/inspect/connect APIs.

There are several compatibility traps: `NetworkSettings` still exposes old bridge fields for backward compatibility, `Network.Peers` is present only for overlay networks, and `EndpointSettings.DNSNames` has unquoted `type: array`/`type: string` values while most surrounding scalar type names are quoted. YAML accepts both, but generators that expect consistent style should be tested.

### Volumes And Cluster Volumes

Local volume schemas include:

- `Volume`, with name, driver, mountpoint, creation time, status, labels, scope, options, usage data, and optional cluster volume data.
- `VolumeCreateOptions` and `VolumeListResponse`.

The later `ClusterVolume`, `ClusterVolumeSpec`, and `Topology` definitions model Swarm CSI cluster volumes. They add swarm object identity/versioning, global volume info, controller publish state, capacity, accessibility topology, secrets passed to the CSI plugin, access mode scope/sharing, mount/block volume options, capacity range, and volume availability. This introduces scheduling semantics: volume group, access scope, sharing mode, and topology can affect where services are placed.

There is a structural risk in `ClusterVolumeSpec.AccessMode.MountVolume`: the nested `properties:` indentation in the source appears unusual, with `properties` visually indented under the description block area. YAML parsing should be validated by the repository's normal swagger tooling because a minor indentation regression here could silently move `MountVolume`/`BlockVolume` shape information.

### Plugins

Plugin definitions model both user-facing plugin resources and privilege prompts:

- `PluginMount`, `PluginDevice`, `PluginEnv`, `PluginInterfaceType`, and `PluginPrivilege` are reusable plugin configuration and install-approval objects.
- `Plugin` includes ID/name/enabled state, mutable settings, remote reference, and full plugin config.
- Plugin config includes interface type/socket/protocol scheme, entrypoint, workdir, user UID/GID, network, Linux capabilities/devices, propagated mount, host IPC/PID flags, mounts, env, args, and rootfs layer IDs.

Many plugin fields are marked non-nullable and required. The deprecated plugin `DockerVersion` field is marked `x-omitempty`, showing that generated clients must distinguish legacy information from stable config.

### Swarm, Nodes, Services, Tasks, Secrets, And Configs

Swarm definitions are extensive and form a stateful API contract:

- `ObjectVersion` is the concurrency control mechanism for swarm objects. Update operations must send the version read earlier; concurrent writers based on the same version cannot both succeed. This is the key state-consistency model in the chunk.
- `NodeSpec`, `Node`, `NodeDescription`, `Platform`, `EngineDescription`, `TLSInfo`, `NodeStatus`, `NodeState`, `ManagerStatus`, and `Reachability` describe swarm nodes and manager reachability.
- `SwarmSpec`, `ClusterInfo`, `JoinTokens`, and `Swarm` describe cluster configuration, raft timings, dispatcher heartbeat, CA config, encryption/autolock settings, task defaults, and join token output. `ForceRotate` is present for CA rotation.
- `TaskSpec` is the service task template. It includes container spec, plugin spec, resources, restart policy, placement constraints/preferences/platform filters, force update, runtime, networks, and log driver.
- `TaskState`, `ContainerStatus`, `PortStatus`, `TaskStatus`, and `Task` model scheduling/running state, including desired state and job iteration.
- `ServiceSpec`, `EndpointPortConfig`, `EndpointSpec`, `Service`, `ServiceCreateResponse`, and `ServiceUpdateResponse` cover service creation/update/list/inspect. They support replicated/global services plus replicated and global jobs, update and rollback behavior, endpoint modes, published ports, service status, and job status.
- `SecretSpec`/`Secret` and `ConfigSpec`/`Config` model swarm secrets and configs with versioned objects, labels, base64 payloads, templating drivers, and optional external secret drivers.

The stateful control flow for swarm clients is read-modify-write: inspect/list to obtain `ObjectVersion`, mutate the `Spec`, then update with the version. Tests should cover update conflicts and version-required endpoints. Secrets and configs include size limits documented by links to swarmkit constants; the schema itself does not enforce those byte limits, so server-side validation remains required.

### System, Runtime, Registry, And Events

System definitions describe daemon capabilities and operational state:

- `SystemVersion` is the `/version` response with component versions, daemon version/API range, Git commit, Go version, OS/arch/kernel/build time, and experimental flag.
- `SystemInfo` is a large `/info` response spanning container/image counts, storage driver, Docker root dir, plugins, cgroup and kernel capabilities, debug counters, OS/architecture, CPU/memory, proxy settings, registry config, generic resources, daemon labels, runtimes, swarm info, live restore, default isolation, init binary, component commits, security options, product license, address pools, firewall backend, discovered CDI devices, warnings, CDI spec dirs, and containerd connection info.
- `ContainerdInfo`, `FirewallInfo`, `PluginsInfo`, `RegistryServiceConfig`, `IndexInfo`, `Runtime`, `Commit`, `SwarmInfo`, `LocalNodeState`, and `PeerNode` support `SystemInfo`.
- `EventActor` and `EventMessage` model the event stream with object type, action, actor attributes, scope, and second/nanosecond timestamps.

Much of this schema is informational and intentionally unstable in formatting. `DriverStatus`, runtime `status`, firewall `Info`, proxy masking, registry insecure flags, debug-only counters, experimental flags, and CDI fields all need tolerant client handling. The schema documents that some fields are omitted on unsupported platforms or when empty.

## Control Flow And Integration Points

Although the chunk has no runtime functions, it encodes API control flow:

- Container creation is a composed request flow using `ContainerConfig`, `HostConfig`, and `NetworkingConfig`, followed by lifecycle endpoints in later chunks. Runtime state is later reported by `ContainerInspectResponse`, `ContainerSummary`, `ContainerState`, and stats/top/wait responses.
- Image flows use local cache models (`ImageInspect`, `ImageSummary`) plus streaming progress records for build/pull/push and OCI descriptor models for content-store and registry integration.
- Swarm update flows depend on optimistic concurrency via `ObjectVersion`; service/node/swarm/secret/config updates should read current object version before submitting mutations.
- Volume scheduling flows are split between local volumes and Swarm CSI cluster volumes. Cluster volumes carry swarm object versions, topology, access mode, capacity, and publish state.
- System observability flows use `/version`, `/info`, `/events`, and stats schemas to expose daemon state without guaranteeing all platform-specific fields.

Primary dependencies and integrations encoded in the text include Docker Engine, containerd, OCI runtimes such as runc, OCI image-spec descriptors and platforms, BuildKit cache/progress concepts, swarmkit object/version/control API concepts, CSI storage plugins, CDI device specifications, registry authentication/configuration, cgroups v1/v2, Linux namespaces/SELinux/AppArmor/seccomp, Windows container isolation, and ReDoc/GitHub-flavored Markdown rendering.

The first `paths:` entry begins at line 7719 with `/containers/json` and `GET` summary/description for listing containers. The operation id, query parameters, responses, tags, and schema references are outside this chunk, so this chunk can only establish that the endpoint section starts here and that the list response is intended to align with the inspect endpoint format.

## State And Persistence Behavior

The schema identifies several persistence boundaries:

- Docker root state lives under `DockerRootDir` such as `/var/lib/docker` on Linux or `C:\ProgramData\docker` on Windows.
- Daemon-managed per-container files such as `resolv.conf`, `hostname`, `hosts`, and json log files are exposed in inspect output but documented as managed by Docker and not for external modification.
- Volumes are persistent storage. Mounts of type `volume` are explicitly not removed when a container is removed. `MountPoint.Source` can reveal host-side volume or bind locations.
- Image metadata distinguishes content-addressable image IDs, manifest digests, rootfs layers, tags, local metadata, and content-store availability.
- Swarm state is versioned with `ObjectVersion`; raft snapshot and log retention settings are part of `SwarmSpec`.
- Secrets/configs persist swarm data but create-only payload fields are not returned by normal inspect/list endpoints.
- Cluster volume state persists through swarm object versions, CSI plugin volume IDs, capacity, topology, and publish status.

The document also distinguishes local daemon state from externally managed or informational state: registry configs can be insecure or mirrored; runtime status and storage-driver metadata are explicitly informational; containerd namespace information is for debugging and warns against tampering.

## Risks And Edge Cases

- The v1.51 file introduction appears to contain a stale parenthetical reference to v1.50 in the "omit version-prefix" paragraph. This should be checked against generated docs.
- Swagger 2.0 plus custom vendor extensions means generators must preserve `x-go-name`, nullability, omitempty, and `allOf` semantics. Dropping these extensions can change Go type names, pointer-ness, JSON omission behavior, or embedded resource fields.
- Many fields are platform-specific, cgroup-version-specific, experimental, deprecated, omitted when empty, or informational-only. Clients must tolerate missing fields and unknown extra fields.
- Numeric examples sometimes appear as quoted strings even when the schema type is integer, for example size and timestamp examples. This is usually harmless for documentation but can trip strict example validators.
- Multi-platform image store fields are explicitly experimental and can change without backward compatibility. Tests should not assume stable presence or complete manifest details on all daemons.
- Swarm update APIs rely on `ObjectVersion`; stale version handling is a core correctness requirement not enforceable by the schema alone.
- Secret and config size limits are documented by prose/links, not represented as schema max-length constraints.
- The cluster volume schema has complex nested indentation and should be parsed by tooling whenever edited.
- The first path operation is truncated in this chunk, so any endpoint-level conclusion for `/containers/json` must be reconciled with the next chunk.

## Test Signals

Useful validation signals for this chunk:

- Run the repository's Swagger/OpenAPI validation or generation pipeline against `api/docs/v1.51.yaml` to catch YAML syntax, `$ref`, enum, and vendor-extension regressions.
- Generate API docs and clients/server types, then check that named Go mappings such as `InspectResponse`, `StatsResponse`, `CreateResponse`, `IDResponse`, `Descriptor`, and `ManifestSummary` remain stable.
- Validate that all `$ref` targets within this chunk resolve, especially high-use references like `HostConfig`, `ContainerConfig`, `EndpointSettings`, `ObjectVersion`, `OCIDescriptor`, and `ImageManifestSummary`.
- Exercise fixture responses for Linux cgroups v1, Linux cgroups v2, Windows containers, multi-platform image store enabled/disabled, experimental CDI enabled/disabled, swarm enabled/disabled, and rootless/security-option variants.
- Add or keep compatibility tests ensuring clients ignore extra response properties and tolerate omitted nullable/platform-specific fields.
- For swarm update endpoints in later chunks, test stale `ObjectVersion` conflict behavior and successful read-modify-write flows.
- For docs rendering, inspect ReDoc tag order and markdown blocks for API introduction, deprecation notes, warnings, and tables.
- For the chunk boundary, verify that the next chunk completes `/containers/json` and links it to the container summary/list response schema.
