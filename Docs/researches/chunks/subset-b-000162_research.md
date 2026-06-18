# sources/cloud-native/moby/api/swagger.yaml lines 1-7937

## Scope And Purpose

This chunk covers the opening metadata and most of the `definitions` section of the Docker Engine API Swagger 2.0 contract for API version `1.55`. The `paths:` block begins after this chunk, so this research is about the public type model, documentation taxonomy, compatibility rules, and generated client/server schema inputs rather than individual HTTP operations.

The file is used for Engine API documentation and generated API types. It declares the `http` and `https` schemes, JSON and plain-text media types, `basePath: "/v1.55"`, the Docker Engine API title/version, ReDoc tag ordering, registry authentication conventions, and the open-schema compatibility rule: servers may add response fields and ignore extra request fields, so clients must tolerate unknown properties.

The definitions in this span model nearly every Docker Engine state domain: containers, images, build cache, volumes, networks, plugins, Swarm nodes/services/tasks/secrets/configs, system information, events, OCI descriptors/platforms, distribution metadata, and the beginning of CSI-backed cluster volume state.

## Document Structure And Generation Semantics

The header comments are part of the engineering contract. They state that the file is not only documentation but an input for generated client/server types, and they define style rules such as ReDoc Markdown descriptions and singular-noun `operationId` naming. The ordered tags establish public navigation and grouping for `Container`, `Image`, `Network`, `Volume`, `Exec`, Swarm-related objects, `Plugin`, and `System`.

Swagger features used heavily in this chunk include `$ref`, `allOf`, maps through `additionalProperties`, enums, numeric formats, examples, required-field lists, and vendor extensions. The Docker-specific extensions are important integration points: `x-go-name`, `x-go-package`, `x-go-type`, `x-nullable`, and `x-omitempty` influence generated Go type names, packages, nullability, omission behavior, and specialized net/time/container types.

The API-level description defines error bodies as `{"message": "..."}` through `ErrorResponse`, describes URL version-prefix behavior, and documents registry authentication headers. Registry-facing endpoints later in the file use base64url-encoded JSON in `X-Registry-Auth`; `/auth` can return an identity token represented by `AuthResponse`.

## Container, Runtime, And Host Schemas

The container model starts with reusable primitives: `PortSummary`, `PortMap`, `PortBinding`, `MountType`, `MountPoint`, `Mount`, `DeviceMapping`, `DeviceRequest`, `ThrottleDevice`, `RestartPolicy`, `Resources`, `HealthConfig`, `Health`, and `HealthcheckResult`.

`Resources` is the core cgroup/resource contract. It covers portable and platform-specific controls such as CPU shares/period/quota/realtime settings, cpusets, memory limits/reservation/swap/swappiness, OOM behavior, PID limits, blkio throttles, device rules and device requests, ulimits, and Windows-only CPU/IO controls. `HostConfig` composes `Resources` with host-specific container settings: binds, log driver config, network mode, port bindings, restart behavior, volume inheritance, mounts, console size, annotations, capabilities, namespace modes, DNS, extra hosts, groups, IPC/cgroup/PID/user namespace settings, privileged mode, port publishing, read-only rootfs, security options, tmpfs, sysctls, runtime choice, Windows isolation, masked paths, and read-only paths.

`ContainerConfig` and `ImageConfig` describe portable image/container settings such as hostname/domain/user, stream attachment, TTY/stdin behavior, exposed ports, env, command, healthcheck, image reference, volumes, working directory, entrypoint, labels, stop signal/timeout, shell, and Windows argument escaping. The split matters because `ContainerConfig` is an input and inspect artifact for a concrete container, while `ImageConfig` provides defaults stored in an image.

`ContainerInspectResponse`, `ContainerSummary`, `ContainerState`, `ContainerCreateResponse`, `ContainerUpdateResponse`, `ContainerTopResponse`, and `ContainerWaitResponse` define the main response bodies for later container endpoints. Inspect exposes daemon-managed paths under the container store (`resolv.conf`, `hostname`, `hosts`, log path), graph-driver data, rootfs storage/snapshotter data, image manifest descriptor, mount labels, AppArmor profile, exec IDs, host config, mounts, config, and network settings. `ContainerState` explicitly warns that `Running` and `Paused` can both be true on Linux; `Status` is the reliable discriminator.

Container metrics are deeply modeled through `ContainerStatsResponse`, `ContainerCPUStats`, `ContainerCPUUsage`, `ContainerMemoryStats`, `ContainerBlkioStats`, `ContainerPidsStats`, `ContainerNetworkStats`, and `ContainerStorageStats`. These schemas encode major platform differences: Linux cgroups v1 exposes many blkio and memory fields that cgroups v2 omits, Windows uses commit/private-working-set and storage stats, Hyper-V isolation can omit CPU mode values, and `preread` can be absent or zeroed for one-shot stats.

## Image, Build, Registry, And OCI Schemas

Image definitions include `ImageHistoryResponseItem`, `ImageInspect`, `ImageSummary`, `ImagesDiskUsage`, `ImageDeleteResponseItem`, `ImageID`, `CreateImageInfo`, `PushImageInfo`, `BuildInfo`, `BuildCache`, and `BuildCacheDiskUsage`. The schemas distinguish local image configuration and tags from registry manifest digests and OCI descriptors. `ImageInspect` and `ImageSummary` include experimental multi-platform fields such as `Descriptor` and `Manifests`; clients should treat these as optional and unstable.

The v1.55 schema includes a richer image provenance and trust model through `Identity`, `BuildIdentity`, `PullIdentity`, `SignatureIdentity`, `SignatureTimestamp`, `SignatureTimestampType`, `SignatureType`, `KnownSignerIdentity`, and `SignerIdentity`. These describe verified signatures, signed timestamps, known signer identities, signer certificate/OIDC/source repository fields, build references, and pull origins. The contract states that image identity is trusted daemon-verified information and cannot be changed merely by retagging an image.

Build and image progress schemas (`BuildInfo`, `CreateImageInfo`, `PushImageInfo`, `ErrorDetail`, `ProgressDetail`) represent streamed JSON progress from long-running operations. Build cache records include IDs, parents, type enums such as `regular`, `frontend`, `source.local`, and `exec.cachemount`, usage/sharing status, size, timestamps, and use counts. Disk usage wrapper types aggregate active/total/reclaimable/size counters and item arrays for images, containers, volumes, and build cache.

OCI and registry integration is represented by `OCIDescriptor`, `OCIPlatform`, and `DistributionInspect`. `OCIDescriptor` follows OCI content descriptor concepts: media type, digest, size, optional URLs, annotations, embedded base64 data, platform, and artifact type. `OCIPlatform` carries architecture, OS, OS version/features, and variant. `DistributionInspect` is registry-derived metadata with a descriptor and all supported platforms.

`AuthConfig`, `AuthResponse`, `RegistryServiceConfig`, and `IndexInfo` define registry authentication and daemon registry policy. Registry config includes insecure CIDR ranges, per-index mirrors/security/official status, and Docker Hub mirrors. The descriptions warn that insecure registries should be limited to testing because they allow unencrypted or untrusted TLS communication.

## Volumes, Networks, Plugins, And Devices

Volume schemas include `Volume`, `VolumesDiskUsage`, `VolumeCreateRequest`, `VolumeListResponse`, and the opening portion of `ClusterVolume`. Local volumes carry names, drivers, host mountpoints, labels, scope, driver options, status maps, and optional usage data for `/system/df`. `VolumeCreateRequest` supports a normal volume driver path and `ClusterVolumeSpec` for swarm CSI volumes. This chunk reaches `ClusterVolume.Info.CapacityBytes` and `VolumeContext`; the rest of cluster-volume specification continues after line 7937.

Network schemas include `Network`, `NetworkSummary`, `NetworkInspect`, `NetworkStatus`, `ServiceInfo`, `NetworkTaskInfo`, `ConfigReference`, `IPAM`, `IPAMConfig`, `IPAMStatus`, `SubnetStatus`, `EndpointResource`, `PeerInfo`, `NetworkCreateResponse`, `NetworkConnectRequest`, `NetworkDisconnectRequest`, `EndpointSettings`, `EndpointIPAMConfig`, and `NetworkAttachmentConfig`. They model bridge/overlay and swarm-scoped networks, IPv4/IPv6 enablement, IPAM pools and runtime subnet availability, config-only networks, attached containers/services/tasks, endpoint DNS names, endpoint driver options, static IP/MAC data, and `GwPriority` selection of a container default gateway.

Device and runtime-adjacent additions include `DeviceRequest` for driver/capability-selected devices, `DeviceInfo` for devices visible to containers with CDI-style IDs, and `NRIInfo` for Node Resource Interface status when enabled. These are intentionally flexible and driver-specific, which makes generated clients responsible for preserving unknown labels and values.

Plugin schemas (`PluginMount`, `PluginDevice`, `PluginEnv`, `PluginPrivilege`, `Plugin`) cover managed Engine plugins. They expose enabled state, registry reference, user-settable settings, mounts, env, args, devices, plugin interface types/sockets/protocol scheme, entrypoint/workdir/user, network mode, Linux capabilities, allow-all-devices, propagated mount, host IPC/PID flags, and rootfs layer metadata. This is a security-sensitive type surface because accepting plugin privileges can grant host mounts, devices, capabilities, and host namespace access.

## Swarm And Orchestration Schemas

Swarm objects use `ObjectVersion` for optimistic concurrency. Its description is explicit: clients must send the current version with update requests so concurrent writes do not silently overwrite each other. This pattern appears across nodes, swarm cluster state, services, tasks, secrets, configs, and cluster volumes.

Node and cluster definitions include `NodeSpec`, `Node`, `NodeDescription`, `Platform`, `EngineDescription`, `TLSInfo`, `NodeStatus`, `NodeState`, `ManagerStatus`, `Reachability`, `SwarmSpec`, `ClusterInfo`, `JoinTokens`, `Swarm`, `SwarmInfo`, `LocalNodeState`, and `PeerNode`. `SwarmSpec` covers orchestration history retention, Raft snapshots/election/heartbeat settings, dispatcher heartbeat, CA/external CA configuration, CA rotation, manager autolock, and default task log driver. `ClusterInfo` exposes root rotation, data path port, default address pool, and subnet size; `Swarm` adds worker and manager join tokens.

`TaskSpec`, `TaskState`, `ContainerStatus`, `PortStatus`, `TaskStatus`, `Task`, `ServiceSpec`, `EndpointPortConfig`, `EndpointSpec`, `Service`, `ServiceCreateResponse`, and `ServiceUpdateResponse` model swarm scheduling. `TaskSpec` supports mutually exclusive `ContainerSpec`, `PluginSpec`, and `NetworkAttachmentSpec`; container tasks include image, command, env, user/groups, mounts, stop grace period, DNS, hosts, secrets, configs, isolation, init, sysctls, capabilities, ulimits, and resource requirements. Placement supports constraints, ordered spread preferences, per-node replica caps, and platform filters.

`ServiceSpec` defines service naming, labels, task template, replicated/global and replicated-job/global-job modes, update and rollback strategies, network attachment, and endpoint configuration. `Service` adds endpoint VIPs/ports, update status, service task counts, and job status. Job mode uses a separate `JobIteration` version value to identify executions without using it as an update precondition.

`SecretSpec`, `Secret`, `ConfigSpec`, `Config`, and `Driver` represent swarm-managed sensitive data and configs. Secret data is base64 encoded, create-only, omitted from reads, and limited to 500KB. Config data is base64 encoded and limited to 1000KB. Both can carry labels, timestamps, versions, and optional templating driver metadata.

## System, Events, And Host Capability Schemas

`SystemVersion` models `/version` output with component versions, daemon version, API and minimum API version, Git commit, Go version, OS/arch, kernel, experimental flag, and build time. `SystemInfo` is a broad daemon snapshot: counts of containers/images, storage driver and driver status, Docker root dir, plugin availability, memory/swap/CPU/PID/cgroup feature support, IPv4 forwarding, debug counters, event listener count, host OS/kernel/architecture/CPU/memory, registry config, generic resources, masked proxy settings, daemon labels, runtime list/default runtime, swarm info, live restore, isolation, init binary, containerd info, warnings, CDISpecDirs, NRI info, and firewall info.

`ContainerdInfo`, `FirewallInfo`, `PluginsInfo`, `Runtime`, and `Commit` are supporting system types. `ContainerdInfo` documents default containerd namespaces for containers and plugins, warning that changing them can cause unexpected behavior because the daemon treats the namespaces as exclusive. `FirewallInfo` is Linux-only and intentionally unstable in formatting. `Runtime` points at OCI runtime binaries and optional status maps, including possible OCI runtime-spec feature data encoded as JSON strings.

`EventActor` and `EventMessage` define event stream payloads for builder, config, container, daemon, image, network, node, plugin, secret, service, and volume events. Events include action, actor attributes, local/swarm scope, seconds timestamp, and nanosecond timestamp.

## Control Flow And State Behavior

The YAML has no executable control flow, but it encodes daemon control flow through object relationships and response shapes. Container creation combines `ContainerConfig`, `HostConfig`, and `NetworkingConfig`; inspect returns the persisted input metadata plus current runtime state, daemon-managed files, graph/snapshot data, mounts, and endpoint state. Container lifecycle states move through created, running, paused, restarting, removing, exited, and dead, with healthcheck state nested under runtime state.

Image and build flows persist content-addressed image records, local tags, manifest descriptors, build cache records, and provenance/signature data. Progress types are designed for streamed operations rather than one-shot JSON responses. Disk-usage types aggregate persistent stores and mark unknown or unavailable values with sentinel values such as `-1`.

Swarm flow is versioned and Raft-backed. Node, service, swarm, secret, config, task, and volume objects carry versions and timestamps. Updates require matching versions, while task and job state reflect scheduler progress from allocation through running and terminal states. Secrets and configs persist in swarm state, but secret payloads are deliberately omitted from read responses.

Network and volume state is both local and cluster-aware. Network endpoints mix desired configuration and operational data such as IDs, gateways, IPs, DNS names, and task backends. Volumes can be local driver resources or swarm CSI cluster volumes, with usage data only available in specific contexts such as system data usage.

## Dependencies And Integration Points

This chunk depends on Swagger 2.0 tooling, ReDoc rendering, Docker's API generation pipeline, Go code-generation extensions, Docker CLI/API conventions, OCI image and runtime specifications, containerd, runC/OCI runtimes, BuildKit cache concepts, registry authentication, libnetwork/IPAM, SwarmKit orchestration, and CSI-style cluster volumes.

Important external integration points include RFC 3339 timestamps, RFC 4648 base64/base64url data, registry mirrors and insecure registry policy, netip-based Go IP types, time-based Go types, cgroups v1/v2, Windows process/Hyper-V isolation, SELinux/AppArmor/seccomp/capabilities/user namespaces, containerd namespaces, CDI device identifiers, NRI plugin status, OCI descriptors/platforms, and swarm TLS/CA material.

## Risks And Edge Cases

Strict schema clients are a compatibility risk because the file explicitly uses an open schema model. Clients must accept extra response fields, omitted optional fields, nullable fields, and platform-specific omissions.

Generated type correctness is high risk around `x-nullable`, `x-omitempty`, `allOf`, custom `x-go-type` mappings, map values, nested anonymous objects, and fields with dotted JSON names such as `OCIPlatform.os.version` and `os.features`.

Security-sensitive fields include registry credentials and identity tokens, insecure registry configuration, bind mounts, devices, device requests, privileged mode, capabilities, sysctls, namespace sharing, plugin privileges, swarm signing CA certificates/keys, join tokens, unlock/autolock material, secret/config payloads, credential specs, proxy URLs, and runtime paths/args.

Several fields are intentionally unstable or experimental: multi-platform image descriptors/manifests, image identity/signature details, daemon IDs, driver status formatting, OS version formatting, runtime status maps, NRI info, firewall info, and some plugin/runtime metadata. Clients should treat these as informational unless a later endpoint contract makes stronger guarantees.

Platform differences are pervasive. Linux cgroups v1, Linux cgroups v2, Windows process isolation, Windows Hyper-V isolation, rootless/userns, swarm active/inactive states, containerd image-store availability, and daemon experimental flags all change field presence or interpretation.

The chunk ends inside `ClusterVolume`, so any final per-file summary must merge this document with the following chunk before making complete claims about cluster volume specs, topology, access modes, secrets, and publish status.

## Test Signals

Strong validation signals include parsing this YAML as Swagger 2.0, resolving every `$ref` that appears in lines 1-7937, preserving Docker vendor extensions, and ensuring generated Go client/server types compile with the intended names, packages, nullability, omitempty behavior, and custom IP/time/runtime mappings.

Documentation tests should render ReDoc output for Markdown descriptions, tables, warnings, deprecation notes, enum lists, examples, and tag ordering. Schema regression tests should compare generated type diffs for sensitive definitions such as `HostConfig`, `ContainerInspectResponse`, `ImageInspect`, `ImageSummary`, `EndpointSettings`, `Plugin`, `SwarmSpec`, `TaskSpec`, `ServiceSpec`, `SystemInfo`, and `OCIDescriptor`.

Behavioral conformance tests downstream of these definitions should cover container create/inspect/update/stats/wait/top, image inspect/list/progress/identity/multi-platform fields, volume list/create/df usage, network create/connect/inspect with IPAM and gateway priority, plugin privilege/config handling, swarm node/service/task update version conflicts, secret data omission on reads, config size/templating behavior, system info/version output, event stream payloads, registry auth/insecure registry handling, and OCI distribution inspection.

Platform matrix tests are especially important for stats and system schemas: Linux cgroups v1 versus v2, Windows process versus Hyper-V isolation, rootless/userns, containerd image store on/off, NRI enabled/disabled, CDI devices present/absent, swarm inactive/active/locked, and experimental multi-platform image support enabled/disabled.
