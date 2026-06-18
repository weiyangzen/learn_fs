# sources/cloud-native/moby/api/docs/v1.53.yaml lines 1-7937

## Scope And Purpose

This chunk covers the beginning of the Docker Engine API v1.53 Swagger/OpenAPI 2.0 document through line 7937. It includes the file header, global API metadata, ReDoc tag ordering, the complete pre-`paths` schema surface up to `DistributionInspect`, and the beginning of the new `ClusterVolume` definition. The chunk ends before `paths:` starts at line 8257, so no HTTP endpoint operation is fully in scope here.

The file is not daemon implementation code. It is a contract source used to generate API documentation and client/server API types. Edits to this range affect generated Go names/packages, nullability, SDK models, public documentation, and route conformance expectations for later path operations that reference these definitions.

The global metadata declares Swagger 2.0 over HTTP/HTTPS, JSON and plain-text media types, and `basePath: "/v1.53"`. The top-level description documents Engine API errors, version-prefix behavior, open-schema compatibility, and registry authentication through `X-Registry-Auth`. The tag list defines documentation groups for containers, images, networks, volumes, exec, swarm resources, plugins, and system resources.

## API Contract Structure

The document uses Docker-specific Swagger extensions extensively. `x-go-name`, `x-go-package`, and `x-go-type` steer generated Go bindings; `x-nullable` and `x-omitempty` encode wire compatibility details that are not always expressible in plain Swagger 2.0. Many schemas also carry concrete examples that become public documentation and useful test fixtures.

Definitions in this chunk are shared across the route table that appears later in the file. The main schema families are:

- container create, inspect, summary, lifecycle result, and stats models;
- image inspect/list/build/pull/push/delete/distribution models, including multi-platform image store and image identity/signature metadata;
- storage and volume models, including local volume disk usage and the first part of swarm CSI cluster-volume state;
- network, IPAM, endpoint, service attachment, and network status models;
- plugin install/runtime configuration and privilege models;
- swarm node, task, service, secret, config, and event models;
- daemon system, version, registry, runtime, containerd, NRI, firewall, and plugin capability models.

Because the chunk stops inside `ClusterVolume.Info.VolumeContext`, the chunk is not standalone YAML. It must be validated as part of the full `v1.53.yaml`, and the remainder of the cluster-volume definitions plus all path operations belong to later chunk `subset-b-000156`.

## Important Schemas And Types

Container runtime configuration is centered on `ContainerConfig`, `HostConfig`, `Resources`, `Mount`, `RestartPolicy`, `HealthConfig`, `NetworkingConfig`, and `EndpointSettings`. `ContainerConfig` captures portable image/runtime settings such as user, environment, command, healthcheck, TTY/stdin behavior, image reference, volumes, labels, stop signal/timeout, and shell. `HostConfig` composes `Resources` with host-specific settings: legacy bind strings, structured mounts, log driver, network mode, port bindings, restart policy, automatic removal, annotations passed to the runtime, Linux capability and namespace controls, DNS/hosts settings, privileged/rootfs/security/storage/sysctl/runtime settings, Windows isolation, and masked/read-only paths.

`Resources` models cgroup and platform resource controls for create/update flows. It includes CPU shares/quota/period/realtime, cpuset strings, block IO weights and throttles, device mappings, cgroup device rules, `DeviceRequest` accelerator requests, memory/swap/swappiness/OOM/PIDs controls, `Init`, ulimits, and Windows CPU/IO controls. `RestartPolicy` records daemon restart behavior and retry count. `HealthConfig`, `Health`, and `HealthcheckResult` define probe commands, timing, start intervals, exit-code handling, rolling logs, status, failing streak, and output.

Storage definitions include `MountType`, `MountPoint`, `Mount`, `DeviceMapping`, `ThrottleDevice`, `Volume`, `VolumeCreateRequest`, `VolumeListResponse`, `VolumesDiskUsage`, and the start of `ClusterVolume`. v1.53 mount types include `bind`, `cluster`, `image`, `npipe`, `tmpfs`, and `volume`. Structured mount options include bind propagation and recursive read-only controls, host mountpoint creation, volume driver config and subpaths, image subpaths, and tmpfs size/mode/options. `Volume` now references `ClusterVolume`, and `VolumeCreateRequest` can carry `ClusterVolumeSpec`, linking ordinary volume APIs with swarm CSI volume state.

Networking definitions include `Network`, `NetworkSummary`, `NetworkInspect`, `NetworkStatus`, `ServiceInfo`, `NetworkTaskInfo`, `IPAM`, `IPAMConfig`, `IPAMStatus`, `SubnetStatus`, `EndpointResource`, `EndpointSettings`, `EndpointIPAMConfig`, `NetworkConnectRequest`, `NetworkDisconnectRequest`, and `NetworkAttachmentConfig`. They model IPv4/IPv6 enablement, config-only networks, swarm ingress/attachable properties, driver options, peers, allocated IP status, containers and services on a network, static endpoint addressing, aliases, MAC addresses, DNS names, driver options, and gateway priority.

Image definitions are broader than earlier API versions. `ImageInspect` includes content-addressed image ID, repo tags/digests, image config, architecture/platform fields, graph driver and rootfs metadata, local cache metadata, experimental multi-platform `Descriptor` and `Manifests`, and trusted `Identity` data. The identity tree includes `BuildIdentity`, `PullIdentity`, `SignatureIdentity`, `SignatureTimestamp`, `KnownSignerIdentity`, `SignerIdentity`, and `SignatureType`; these expose verified signature state, signer certificate and OIDC/source repository provenance, timestamp sources, warning/error details, and build/pull origin references. `ImageSummary`, `ImagesDiskUsage`, `ImageManifestSummary` references, `OCIDescriptor`, `OCIPlatform`, and `DistributionInspect` support local image listing, multi-platform descriptors, registry distribution inspection, attestations/artifacts, and system disk usage.

Build and registry progress schemas include `BuildInfo`, `BuildCache`, `BuildCacheDiskUsage`, `ImageID`, `CreateImageInfo`, `PushImageInfo`, `ErrorDetail`, and `ProgressDetail`. These are used by streaming build/pull/push/prune surfaces later in the file, and they intentionally contain loosely typed progress and aux payloads.

Daemon/system schemas include `SystemVersion`, `SystemInfo`, `ContainerdInfo`, `FirewallInfo`, `PluginsInfo`, `RegistryServiceConfig`, `IndexInfo`, `Runtime`, `Commit`, `SwarmInfo`, `LocalNodeState`, `PeerNode`, `DeviceInfo`, and `NRIInfo`. They expose API and daemon version bounds, component commit IDs, OS/kernel/architecture, storage driver status, cgroup driver/version, CPUs/memory, runtime inventory and default runtime, CDI devices, NRI status, firewall backend, registry mirrors/insecure registry configuration, proxy settings, warnings, and swarm status.

Plugin schemas include `PluginMount`, `PluginDevice`, `PluginEnv`, `PluginPrivilege`, and `Plugin`. The plugin model captures installed/enabled state, remote references, mutable settings, declared interface/socket/protocol, entrypoint/workdir/user, host/network/pid/ipc requirements, Linux capabilities/devices, propagated mounts, rootfs layers, environment, args, and privilege prompts.

Swarm schemas include `ObjectVersion`, `NodeSpec`, `Node`, `NodeDescription`, `EngineDescription`, `TLSInfo`, `NodeStatus`, `ManagerStatus`, `SwarmSpec`, `ClusterInfo`, `JoinTokens`, `Swarm`, `TaskSpec`, `TaskState`, `ContainerStatus`, `PortStatus`, `TaskStatus`, `Task`, `ServiceSpec`, `EndpointPortConfig`, `EndpointSpec`, `Service`, `ServiceCreateResponse`, `ServiceUpdateResponse`, `SecretSpec`, `Secret`, `ConfigSpec`, and `Config`. They describe raft object versioning, manager/node state, swarm CA and dispatcher/orchestration/raft/encryption settings, service task templates, job modes, update/rollback policy, task status, network attachments, secrets, configs, templating, and service endpoint publication.

Container response schemas in this chunk are detailed. `ContainerInspectResponse` records ID validation, creation timestamp, command path/args, `ContainerState`, source image digest, daemon-managed resolver/hostname/hosts/log paths, name, restart count, storage driver, platform, image manifest descriptor, security labels, active exec IDs, host config, graph driver/storage metadata, size fields, mounts, portable config, and network settings. `ContainerSummary` is a smaller list/df shape with names, image reference, image ID, optional image manifest descriptor, command, created time, ports, sizes, labels, state/status, reduced host config, network summaries, mounts, and v1.52+ health summary.

Stats schemas are now strongly modeled instead of an undifferentiated object. `ContainerStatsResponse` references CPU, memory, network, blkio, pids, and storage stats. `ContainerBlkioStats`, `ContainerCPUStats`, `ContainerCPUUsage`, `ContainerPidsStats`, `ContainerThrottlingData`, `ContainerMemoryStats`, `ContainerNetworkStats`, and `ContainerStorageStats` document cgroup v1/v2 differences, Linux-only and Windows-only fields, Hyper-V omissions, nullable values, and timestamp behavior for one-shot stats. `ContainerTopResponse` and `ContainerWaitResponse`/`ContainerWaitExitError` cover process-list and wait-result shapes.

## Control Flow And Protocol Behavior

There is no executable control flow and no route body in this chunk. The control flow represented here is schema composition: later endpoints reference these shared models to define request bodies, response bodies, and generated SDK types. The core daemon workflow implied by the models is create a container from `ContainerConfig` plus `HostConfig` plus `NetworkingConfig`, then inspect/list it through `ContainerInspectResponse` and `ContainerSummary`, observe runtime state through `ContainerState` and stats models, mutate resources through `Resources` plus restart policy, and associate it with images, mounts, networks, logs, exec instances, and daemon-managed files.

Container and service models separate desired state from observed state. Desired state appears in `ContainerConfig`, `HostConfig`, `TaskSpec`, `ServiceSpec`, `NetworkAttachmentConfig`, `SecretSpec`, `ConfigSpec`, and `ClusterVolumeSpec` references. Observed state appears in `ContainerState`, `ContainerInspectResponse`, `ContainerSummary`, `TaskStatus`, `Service.ServiceStatus`, `Service.JobStatus`, `NodeStatus`, `ManagerStatus`, `SwarmInfo`, `NetworkStatus`, `Volume.UsageData`, and the beginning of `ClusterVolume.Info`.

Swarm update flow is modeled through `ObjectVersion`. Nodes, services, secrets, configs, cluster info, and cluster volumes carry version objects so path operations later can require current version indexes for optimistic concurrency. Service job mode has a second version-like `JobIteration` counter that identifies service job executions but does not behave like the service update version.

Streaming protocol behavior is represented indirectly by progress and stats models. Build, pull, push, and image-create operations use status/progress/error shapes. Container stats now has explicit nested fields for streamed or one-shot samples, including `read`, `preread`, `precpu_stats`, per-network stats, and platform-specific storage/memory/blkio differences. Raw attach/log/exec transport details are outside this chunk's path table, but the schemas here provide the typed payloads and state inputs those endpoints use.

## State And Persistence Behavior

The YAML itself persists no runtime state, but it documents durable and transient Docker daemon state. Container configuration, host configuration, network attachments, mount specs, restart policy, labels, annotations, security settings, and created image references are persisted in the daemon's container metadata and exposed through inspect/list schemas. Runtime-only fields include PID, running/paused/restarting/removing/dead flags, exit code, health status, OOM flag, timestamps, live stats, active exec IDs, and process-list results.

Image state is represented as content-addressed data plus mutable local references. `ImageInspect` and `ImageSummary` distinguish image config digests from repo manifest digests, tags, local metadata, rootfs layers, graph driver data, and multi-platform descriptors. Identity and signature fields are described as trusted information verified by the daemon and not changed merely by retagging. This makes identity metadata a higher-integrity API surface than repo tag strings.

Volume state spans local and swarm-scoped resources. Ordinary `Volume` includes name, driver, mountpoint, labels, scope, driver options, optional driver status, optional usage data, and an optional `ClusterVolume` object for CSI-backed swarm volumes. The chunk captures cluster volume ID, raft version, timestamps, spec reference, capacity, and the start of plugin-returned volume context. Named volumes are not removed with containers by default; cluster volumes introduce raft object state and CSI plugin status into the volume schema.

Network state includes static configuration and runtime allocation. `Network` records driver/IPAM/config-only/ingress/attachable/options/labels/peers; `NetworkInspect` adds attached containers and swarm services; `NetworkStatus` and IPAM status track allocated subnets and addresses; `EndpointSettings` exposes per-container endpoint IDs, IPs, gateways, aliases, DNS names, MAC addresses, and driver options.

Swarm state is raft-backed. `SwarmSpec`, `Node`, `Task`, `Service`, `Secret`, `Config`, and the visible cluster-volume fields all carry timestamps, object versions, specs, and status. Secrets and configs separate create-only payload data from inspect/update metadata. Service job state tracks completed tasks and job iterations. Swarm info also exposes local manager availability and remote manager addresses.

System state is an aggregate of multiple subsystems: storage and snapshotters, containerd namespaces/address, cgroups, runtimes, plugins, registry configuration, security options, CDI devices, NRI configuration, firewall backend, swarm state, warnings, proxy settings, and version/component commits. Many fields are optional or platform/capability dependent, so absence is part of the contract.

## Dependencies And Integration Points

This document depends on Swagger/OpenAPI 2.0 parsing, ReDoc rendering, Docker's API generation pipeline, and full-file `$ref` resolution. Go generation depends on extensions such as `x-go-name`, `x-go-package`, `x-go-type`, `x-nullable`, and `x-omitempty`. For example, network IP fields use `net/netip`-oriented generated types, many disk-usage definitions map into package-specific Go API packages, and OCI descriptor/platform schemas map to image distribution types.

Runtime dependencies described by the schemas include containerd, OCI runtimes, Linux cgroups v1/v2, Windows container isolation, storage graph drivers and snapshotters, volume drivers and CSI plugins, BuildKit build cache/history, registries and mirrors, OCI image descriptors/indexes/artifacts, Docker plugin interfaces, swarmkit raft/object models, network drivers/IPAM, CDI device discovery, NRI, firewall backends, logging drivers, SELinux/AppArmor/seccomp, and Windows credential specs.

Integration points are broad because this chunk defines shared models rather than one endpoint. Docker CLI workflows such as `docker create`, `docker inspect`, `docker ps`, `docker stats`, `docker system df`, `docker image inspect`, `docker build`, `docker pull`, `docker push`, `docker network inspect`, `docker volume inspect`, `docker plugin inspect`, `docker node/service/task/secret/config inspect`, and daemon `/info` and `/version` all depend on these schemas through later path operations.

The image identity and OCI descriptor additions integrate Docker Engine with registry distribution, multi-platform image stores, BuildKit history/provenance, signatures, and attestations. The cluster-volume fields integrate volume APIs with swarm CSI storage plugins. The typed stats definitions integrate Engine API clients with platform-specific cgroup and Windows metrics.

## Risks And Edge Cases

The highest general risk is generated-client drift. A mistaken required field, nullability marker, enum, object/array type, `$ref`, or Go extension in this chunk can break public SDKs and daemon/client compatibility even though no route implementation is present here. Strict clients must follow the top-level open-schema rule and ignore unknown response properties.

The line range ends inside `ClusterVolume`, so conclusions about cluster-volume behavior are partial. The visible fields show swarm CSI volume ID/version/spec/status intent, but the complete publish status, spec, topology, and path operations are outside this chunk. Validators and merge reports must treat this chunk as an ordered fragment of the full file.

Several schemas intentionally expose unstable or opaque data. `Runtime.status`, `NRIInfo.Info`, volume `Status`, graph/storage driver data, network driver options, registry/index maps, plugin settings, event attributes, memory `stats`, OCI descriptor annotations/data, and progress records are extension points. Generated clients should preserve these as flexible maps/arrays instead of imposing narrow enums.

Platform differences are central. Many resource, stats, namespace, credential, storage, and isolation fields are Linux-only or Windows-only. cgroup v2 omits or changes many blkio/memory/per-CPU stats compared with cgroup v1. Windows Hyper-V isolation omits some CPU usage fields. `ContainerTopResponse` is Unix-shaped, while `ContainerStorageStats` is Windows-specific.

Security-sensitive fields are numerous. HostConfig can grant privileged mode, host namespaces, capabilities, devices, sysctls, runtime annotations, bind mounts, masked/read-only path overrides, and insecure registry access. Plugin privileges, plugin Linux devices/capabilities, swarm secrets/configs, registry credentials, signed image identity, and Windows credential specs need careful documentation and tests because type changes can hide or misrepresent security behavior.

Some models include experimental or version-sensitive behavior. Image multi-platform descriptors and manifest summaries are documented as experimental. Container summary health was added in v1.52. Bind recursive read-only options have compatibility behavior for clients before v1.44. Job-mode services and `JobIteration` require special interpretation. `Descriptor`, `ImageManifestDescriptor`, and `Manifests` can be absent unless the daemon provides a multi-platform image store.

There are schema sharp edges for tooling. Some example values are strings even when the declared schema is integer-like, several maps use object values whose concrete shapes are driver-defined, some property names include lowercase or dotted names such as OCI `os.version`, and some enums allow empty string for backward compatibility. Generic Swagger clients may produce awkward or lossy types unless Docker's custom extensions are honored.

## Test Signals

Validation should parse the complete `sources/cloud-native/moby/api/docs/v1.53.yaml` as Swagger 2.0 and verify that every `$ref` introduced in lines 1-7937 resolves in the full file. The chunk alone should not be treated as a standalone YAML document because it cuts off inside `ClusterVolume`.

Schema tests should check generated Go names/packages/types for major definitions: container inspect/summary/stats, image inspect/summary/identity, volume/cluster-volume references, network endpoint/IPAM, plugin, swarm objects, system info/version, OCI descriptor/platform, and disk-usage summaries. Nullability and omit-empty behavior should be asserted for optional platform/capability fields.

Compatibility tests should decode representative JSON for Linux cgroup v1, Linux cgroup v2, and Windows container stats. They should cover absent blkio/percpu/memory fields, nullable arrays, one-shot `preread` behavior, Windows storage stats, network stats with Windows endpoint IDs, and very large unsigned integer values.

Contract tests should cover image inspect/list responses with and without multi-platform descriptors, manifest summaries, image identity, signed identity warnings/errors, pull/build identity records, and OCI descriptor annotations/data/artifact type. Clients should tolerate missing experimental fields and preserve unknown descriptor annotations.

Container model tests should cover create/inspect/list payloads with structured mounts for `bind`, `volume`, `tmpfs`, `image`, and `cluster`, runtime annotations, DNS names, gateway priority, image manifest descriptors, health summary, 64-character container ID validation, and host config security/resource options.

Swarm and storage tests should verify `ObjectVersion` handling, service job mode and `JobIteration`, secret/config create-only data semantics, cluster-volume references from `Volume` and `VolumeCreateRequest`, and partial/absent cluster-volume status for non-cluster volumes.

System-info tests should exercise daemon responses with containerd info, CDI devices, NRI enabled/disabled, firewall backend values, registry mirror/insecure registry config including IPv6 host formatting, multiple runtimes with unstable runtime status maps, and platform-specific omissions.

Documentation/rendering tests should ensure ReDoc can render the tag order, Markdown descriptions, warnings/notes, examples, custom extensions, and nested schemas without losing Docker-specific notes about open schema compatibility, registry auth, insecure registries, experimental fields, and platform-specific behavior.
