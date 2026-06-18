# Research: sources/cloud-native/moby/api/swagger.yaml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-000162`: lines 1-7937, `Docs/researches/chunks/subset-b-000162_research.md`
- `subset-b-000163`: lines 7938-13998, `Docs/researches/chunks/subset-b-000163_research.md`

## Chunk Research

### subset-b-000162: lines 1-7937

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

### subset-b-000163: lines 7938-13998

# sources/cloud-native/moby/api/swagger.yaml lines 7938-13998

## Scope And Purpose

This chunk is the tail of the Docker Engine API Swagger 2.0 definition's `definitions` section followed by the main `paths` section for core daemon APIs. It starts inside the `ClusterVolume` schema's CSI plugin status fields, defines cluster-volume specs, topology, image attestation statements, and image manifest summaries, then enumerates HTTP operations for containers, images/builds, system metadata, exec sessions, volumes, networks, plugins, Swarm, nodes, services, tasks, secrets, configs, registry distribution inspection, and the deprecated interactive session endpoint.

The file is an API contract and documentation source, not executable daemon code. Its purpose is to lock down the externally visible Docker Engine HTTP surface: paths, methods, operation IDs, request parameters, body schemas, response schemas, response codes, media types, examples, enum values, and compatibility notes used by generated clients, server routing validation, and rendered API documentation.

## Important APIs, Types, And Operation Groups

The visible schema definitions extend Docker's cluster-storage and image metadata models. The partial `ClusterVolume` tail records CSI plugin output such as `VolumeContext`, plugin `VolumeID`, accessible topology, and per-node publish status. `ClusterVolumeSpec` describes Swarm CSI cluster-volume intent: volume grouping for scheduler interchangeability, access scope and sharing modes, mount or block volume options, CSI secrets, topology requirements, capacity limits, and `Availability` values of `active`, `pause`, or `drain`. `Topology` is a map of topology segments. `AttestationStatement` represents an in-toto statement attached to an image, optionally including the verbatim statement body. `ImageManifestSummary` summarizes an image or attestation manifest with an OCI descriptor, local availability, content/total size accounting, kind-specific image data, platform identity, container consumers, unpacked size, and attestation target digest.

Container APIs include listing and creation, inspect/top/logs/changes/export/stats/resize, lifecycle operations start/stop/restart/kill/update/rename/pause/unpause, attach via hijacked HTTP or websocket, wait, delete, archive metadata/download/upload, and stopped-container prune. These operations expose container identifiers as names or IDs, JSON filter maps, runtime sizing and resource update inputs, raw or multiplexed log/attach streams, tar archive bodies, and delete/prune force or volume cleanup controls.

Image and build APIs include `ImageList`, `ImageBuild`, `BuildPrune`, `ImageCreate`, `ImageInspect`, `ImageAttestations`, `ImageHistory`, `ImagePush`, `ImageTag`, `ImageDelete`, `ImageSearch`, `ImagePrune`, `ImageCommit`, `ImageGet`, `ImageGetAll`, and `ImageLoad`. The build endpoint accepts compressed tar contexts or remote contexts, Dockerfile selection, multiple tags, cache inputs, build args, resource limits, labels, network mode, registry config headers, platform, target, BuildKit output configuration, and builder backend selector `1` or `2`. Image inspect/list support manifest and identity metadata. Image attestations read in-toto statements for a platform and can filter by predicate type or include statement JSON only when requested.

System APIs include registry auth validation, daemon info and version, `GET`/`HEAD` ping with daemon capability headers, real-time event streaming, and disk usage accounting. Exec APIs create, start, resize, and inspect an exec instance, using attach flags, TTY and console size settings, detach keys, env, command, user, working directory, stream transport, and process state fields such as `Running`, `ExitCode`, open streams, container ID, and host PID.

Volume APIs list, create, inspect, update, delete, and prune volumes. `VolumeUpdate` is explicitly valid only for Swarm cluster volumes; it wraps `ClusterVolumeSpec` in a body object, currently allows only `Availability` changes, and requires the current volume version from the `ClusterVolume` field. Network APIs list, inspect, delete, create, connect, disconnect, and prune networks with driver, scope, internal/attachable/ingress, config-only/config-from, IPAM, IPv4/IPv6, options, labels, and swarm-scoped operation restrictions.

Plugin APIs cover listing, privilege inspection, pull/install, inspect, delete, enable, disable, upgrade, local tar creation, push, and set/configure. Pull and upgrade use registry auth and accepted privilege arrays. Enable/disable/delete include timeout or force behavior. Local plugin creation consumes an `application/x-tar` plugin rootfs/manifest bundle.

Swarm, node, service, task, secret, and config APIs expose cluster control-plane state. Node operations list, inspect, delete, and update nodes. Swarm operations inspect, init, join, leave, update, get unlock key, and unlock a locked manager. Service operations list, create, inspect, delete, update, and stream logs. Task operations list, inspect, and stream logs. Secret and config operations list, create, inspect, delete, and update versioned Swarm objects, with update prose limiting mutable fields to labels.

The final operations are `DistributionInspect`, which contacts a registry for image descriptor and platform metadata, and `Session`, a deprecated h2c connection-hijack endpoint that lets the daemon call back to client-exposed gRPC services.

## Control Flow

Control flow is encoded by REST method, path shape, operation ID, status code, and transport semantics. `GET` operations read or stream daemon state, registry metadata, logs, events, tar exports, and object inspections. `POST` operations create resources, mutate lifecycle state, run prune jobs, validate credentials, perform Swarm membership/control changes, start exec sessions, and establish interactive sessions. `PUT` is used for container archive extraction and cluster-volume update. `DELETE` removes resources. `HEAD` on container archive metadata and ping returns headers without a JSON body.

Several operations require multi-step client workflows. Container create precedes start, attach, logs, wait, exec, archive, update, and delete. Attach requires at least `logs` or `stream`, then the client must handle either a `200` hijacked connection or a `101` upgraded connection. Non-TTY attach streams use Docker's 8-byte multiplex header to separate stdout and stderr; TTY attach streams are raw PTY bytes.

Exec follows create/start/resize/inspect sequencing. `ContainerExec` records the command setup against a running container. `ExecStart` either detaches immediately or attaches to raw/multiplexed output. `ExecResize` only makes sense for a TTY exec session, and `ExecInspect` reports final process state and exit code.

Image build, pull/import, push, save/load, and attestation flows cross local and remote storage boundaries. Builds stream progress and are canceled when the client connection drops. Pull/import semantics depend on `fromImage`, `fromSrc`, tag, digest, repository, changes, platform, and registry auth headers. Attestation lookup first selects an image platform, locates attestation manifests that refer to the selected image manifest, and reads statement layers only when the `statement` query opts in.

Versioned Swarm updates use optimistic concurrency. Node, swarm, service, secret, config, and cluster-volume updates all require a `version` query parameter taken from a prior inspect/list result. Service update additionally supports registry auth selection through `registryAuthFrom` and server-side rollback via `rollback=previous`, in which case the supplied spec is ignored.

Prune operations consistently turn JSON-encoded filter maps into destructive cleanup jobs and return deleted object identifiers and reclaimed space where applicable. Filters such as `until`, labels, dangling state, build cache state, and `all` materially control the deletion scope.

## State And Persistence Behavior

The YAML itself persists no runtime state, but it specifies persistent and transient daemon state transitions. Container operations affect process state, cgroup freezer state, restart/stop/kill behavior, resource limits, container names, root filesystems, attached streams, anonymous volumes, logs, and archive extraction. Container archive upload can mutate the container filesystem and must honor read-only rootfs and volume permissions.

Image and build operations mutate local image content, tags, manifests, BuildKit/classic builder cache, import/export tar streams, and registry references. `ImageCommit` snapshots a container into a new image and can pause the container during capture. `ImageDelete`, `ImagePrune`, and `BuildPrune` reclaim storage and alter reference graphs. Manifest summaries and attestations introduce state that depends on OCI indexes, content-store availability, unpacked snapshots, and backend support.

Volumes and networks are driver-managed persistent resources. Cluster volumes are Swarm objects with versions, CSI plugin context, external plugin volume IDs, topology, publish states, and scheduler availability. Network operations mutate IPAM state, endpoint attachments, overlay/local driver state, and container membership. Some network operations are forbidden for builtin or swarm-scoped resources.

Plugins persist installed plugin content, accepted privileges, enabled/disabled state, configuration strings, and registry-pulled versions. Force removal or force disable can disrupt containers or networks that depend on the plugin.

Swarm resources are Raft-backed cluster state. Init, join, leave, unlock, token rotation, node update/delete, service create/update/delete, task scheduling, secrets, and configs all affect manager/worker membership or desired cluster state. Services persist desired state, while tasks expose scheduler and runtime observations. Secrets and configs carry sensitive or configuration data at creation time, but this contract restricts later updates to labels.

System info, ping, version, events, disk usage, distribution inspection, logs, and sessions mostly read live state or establish transports. They still expose sensitive operational details, can hold long-lived connections, and may cross daemon boundaries to registries or callback services.

## Dependencies And Integration Points

This chunk depends on shared definitions declared elsewhere in `sources/cloud-native/moby/api/swagger.yaml`, including `ErrorResponse`, `ContainerConfig`, `HostConfig`, `NetworkingConfig`, `ContainerSummary`, `ContainerInspectResponse`, `ContainerStatsResponse`, `FilesystemChange`, `ImageSummary`, `ImageInspect`, `ImageHistoryResponseItem`, `ImageDeleteResponseItem`, `AuthConfig`, `AuthResponse`, `SystemInfo`, `SystemVersion`, `EventMessage`, disk usage types, `IDResponse`, `Volume`, `VolumeCreateRequest`, `VolumeListResponse`, `NetworkSummary`, `Network`, `NetworkCreateResponse`, `NetworkConnectRequest`, `NetworkDisconnectRequest`, `Plugin`, `PluginPrivilege`, `Node`, `NodeSpec`, `Swarm`, `SwarmSpec`, `Service`, `ServiceSpec`, `ServiceCreateResponse`, `ServiceUpdateResponse`, `Task`, `Secret`, `SecretSpec`, `Config`, `ConfigSpec`, `DistributionInspect`, `OCIDescriptor`, `OCIPlatform`, `Identity`, and `ObjectVersion`.

Runtime integrations implied by the contract include Docker daemon HTTP routing, request validation, container runtime and cgroups, PTY handling, stream multiplexing, websocket upgrades, logging drivers, filesystem tar/archive handling, local image/content stores, registry resolvers, BuildKit and classic builder backends, build cache accounting, volume drivers and CSI plugins, network drivers and IPAM, plugin management, swarmkit managers/agents, Raft persistence, scheduler/orchestrator state, secret/config storage, event broadcasting, and h2c/gRPC session transport.

Client integrations are broad. The Docker CLI and generated SDKs must handle JSON bodies, repeated query parameters, JSON-encoded filter maps, names or IDs in path parameters, base64/base64url auth headers, binary tar request and response bodies, raw-stream and multiplexed-stream media types, HTTP connection hijacking, websocket attach, long-lived event/log/build streams, optimistic update versions, and open-ended driver option/label maps.

## Risks And Edge Cases

Public API compatibility is the dominant risk. Changing operation IDs, route names, method choices, required flags, enum values, parameter names, query collection formats, response status codes, media types, referenced schemas, or examples can break generated clients, Docker CLI expectations, and third-party integrations.

The source slice exposes several high-risk transports. Attach, websocket attach, exec start, container logs, service logs, task logs, events, image build, push/pull progress, tar export/import, container archive transfer, and session h2c upgrades do not behave like ordinary short JSON requests. Proxies, clients, and generated SDKs must preserve connection lifetime, binary framing, content type, upgrade behavior, cancellation, and TTY versus non-TTY stream differences.

Destructive APIs need strict validation. Container/image/build/volume/network prune can remove broad resource sets when filters are missing or parsed incorrectly. Image delete and tag mutation can alter shared references. Volume/network/plugin force operations can break active consumers. Archive extraction can overwrite paths or cross read-only boundaries if flags such as `noOverwriteDirNonDir` and `copyUIDGID` are mishandled.

Concurrency-sensitive Swarm updates can lose writes if version checks are skipped or stale versions are accepted. Secret/config and cluster-volume updates are especially easy to implement incorrectly because their schemas accept rich specs while prose currently permits only labels or volume availability to change.

Security-sensitive paths include registry auth headers, build registry config headers, secret/config creation bodies, plugin privilege approval, plugin rootfs tar upload, swarm join tokens, manager unlock keys, session callback transport, and distribution inspection. Implementations and tests should ensure credentials and secret data are not logged, echoed, cached, or exposed through examples or errors.

Compatibility edges include name-or-ID ambiguity, platform selection for multi-platform images, attestation support returning `501` on legacy graphdriver stores, cgroup v1/v2 stats differences, logging-driver limitations for log endpoints, Windows unsupported behavior for container top, Swarm `503` behavior when not in a cluster, and registry `401` versus missing-image errors.

## Test Signals

Static tests should parse the Swagger YAML, resolve every `$ref`, validate Swagger 2.0 shape, ensure operation IDs are unique, verify all path parameters are declared and required, check enum/default compatibility, and regenerate docs/clients without schema or rendering failures.

API conformance tests should cover success and documented error status codes: `200`, `201`, `204`, and `101` success paths; `400` bad parameters; `401` registry authentication or missing registry image; `403` forbidden network/archive cases; `404` missing objects; `409` conflicts such as running containers, paused containers, or name collisions; `500` daemon failures; `501` unsupported attestation backend; and `503` Swarm state mismatches.

Stateful integration tests should exercise representative flows for each operation family: container create/start/logs/stats/attach/wait/archive/update/delete/prune; image build/create/inspect/attestations/history/push/tag/delete/search/prune/commit/export/load; build cache prune; exec create/start/resize/inspect; volume create/cluster-update/delete/prune; network create/connect/disconnect/delete/prune; plugin pull/create/privileges/enable/disable/set/upgrade/push/delete; swarm init/join/leave/update/unlock; node update/delete; service create/update/rollback/logs/delete; task list/inspect/logs; and secret/config create/update/delete.

Transport tests should verify raw and multiplexed stream framing, TTY and non-TTY attach behavior, websocket attach, service/task/container log filters, event stream `since`/`until` handling, build cancellation on client disconnect, binary tar import/export, base64 `X-Docker-Container-Path-Stat` archive headers, archive extraction flags, image attestation filtering and statement opt-in, and deprecated `/session` h2c hijacking.

Compatibility tests should verify JSON filter encoding as `map[string][]string`, repeated array query encoding for platform/type and disk-usage selectors, preservation of `X-Registry-Auth` and `X-Registry-Config` headers, correct optimistic concurrency failures for stale versions, label-only mutation restrictions for secrets/configs, availability-only mutation for cluster volumes, and stable behavior when object identifiers can be names, IDs, or partial IDs.
