# sources/cloud-native/moby/api/docs/v1.54.yaml lines 1-7937

## Chunk Scope

This chunk covers the opening 7,937 lines of the Docker Engine API v1.54 Swagger 2.0 document. It includes the file header, top-level OpenAPI metadata, ReDoc tag taxonomy, and most of the `definitions` table from `ImageHistoryResponseItem` through the beginning of `ClusterVolume`. The chunk stops at line 7937 inside `ClusterVolume.Info.VolumeContext`; the rest of the cluster-volume schemas and all later path operations are in later chunks.

The file states that it is used to generate API documentation and the client/server types. The schemas, vendor extensions, examples, and markdown descriptions in this chunk are therefore part of the public Engine API contract for generated Go-facing API packages, generated clients, and documentation for `basePath: /v1.54`.

## Purpose And Structure

The document defines the versioned Docker Engine HTTP API as Swagger 2.0, with `http` and `https` schemes, JSON/text media defaults, and `/v1.54` as the base path. The opening description documents the daemon API model: clients should prefix calls with an API version, tolerate additional response fields, and ignore extra query/body fields added by newer daemons. Registry authentication is described as client-side and passed to registry-touching endpoints through `X-Registry-Auth`, containing base64url-encoded JSON credentials or an identity token.

The tag list establishes the documentation and operation grouping model: `Container`, `Image`, `Network`, `Volume`, `Exec`, `Swarm`, `Node`, `Service`, `Task`, `Secret`, `Config`, `Plugin`, and `System`. Comments around the tags are maintenance guidance for ReDoc navigation, so tag order and naming are a documentation integration contract even though they do not affect daemon runtime behavior directly.

The `definitions` section is the main content in this chunk. It defines reusable request and response object schemas with `$ref`, `allOf`, maps via `additionalProperties`, enums, examples, and Docker-specific vendor extensions such as `x-go-name`, `x-go-package`, `x-go-type`, `x-nullable`, and `x-omitempty`. Those extensions matter for generated Go names, package placement, nullability, pointer/omitempty behavior, and custom types such as `net/netip.Addr`, `time.Time`, `netip.Prefix`, and hardware addresses.

## Important Definitions And API Types

Container creation and inspection are centered on `ContainerConfig`, `HostConfig`, `Resources`, `RestartPolicy`, `HealthConfig`, `Health`, `ContainerState`, `ContainerInspectResponse`, `ContainerSummary`, `ContainerCreateResponse`, `ContainerUpdateResponse`, `ContainerTopResponse`, and `ContainerWaitResponse`. `ContainerConfig` carries portable image/container defaults such as user, env, command, healthcheck, entrypoint, labels, stop signal, shell, volumes, and working directory. `HostConfig` composes `Resources` and adds host-specific runtime settings: bind mounts, log driver config, network mode, port bindings, restart policy, auto-remove, volume inheritance, mount specs, console size, runtime annotations, Linux capabilities and namespaces, DNS, extra hosts, privilege/security options, sysctls, masked/read-only paths, Windows isolation, and runtime selection.

Resource and device schemas include `Resources`, `Limit`, `ResourceObject`, `GenericResources`, `DeviceMapping`, `DeviceRequest`, and `ThrottleDevice`. They model cgroup CPU, memory, blkio, device rules, CDI/vendor device requests, Windows CPU/IO controls, pids, ulimits, and swarm scheduler resources. Many fields are platform-specific, and the spec relies on descriptions plus daemon `/info` capabilities rather than schema-level validation to indicate availability.

Mount and storage schemas include `MountType`, `Mount`, `MountPoint`, `Storage`, `RootFSStorage`, `RootFSStorageSnapshot`, `DriverData`, `FilesystemChange`, and `ChangeType`. `Mount` is the create-time mount contract for bind, cluster, image, npipe, tmpfs, and volume mounts, with nested `BindOptions`, `VolumeOptions`, `ImageOptions`, and `TmpfsOptions`. `MountPoint` is the runtime reporting shape for container inspect/list responses. Storage reporting covers graph-driver data, container rootfs snapshot metadata, and filesystem diff entries.

Image schemas include `ImageHistoryResponseItem`, `ImageConfig`, `ImageInspect`, `ImageSummary`, `ImageDeleteResponseItem`, `ImagesDiskUsage`, `ImageID`, `BuildInfo`, `BuildCache`, `BuildCacheDiskUsage`, `CreateImageInfo`, `PushImageInfo`, `Identity`, `BuildIdentity`, `PullIdentity`, `SignatureIdentity`, `SignatureTimestamp`, `SignatureType`, `KnownSignerIdentity`, and `SignerIdentity`. The v1.54 model includes multi-platform image-store data through `OCIDescriptor`, `OCIPlatform`, image manifests, and descriptor fields, as well as trusted identity/signature metadata for pull, build, and verified signatures. Build cache records expose BuildKit cache IDs, parent relationships, cache type enums, size, usage count, creation time, last-used time, and reclaim accounting.

Volume schemas include `Volume`, `VolumesDiskUsage`, `VolumeCreateRequest`, and `VolumeListResponse`, plus the start of `ClusterVolume`. Regular volumes carry name, driver, mountpoint, labels, scope, options, optional driver status, optional usage data, and optional cluster-volume metadata. `ClusterVolume` begins the Swarm CSI cluster volume object with ID, optimistic version, timestamps, spec reference, and global status information. This chunk cuts off before the full cluster-volume contract is visible.

Networking schemas include `NetworkingConfig`, `NetworkSettings`, `Address`, `PortMap`, `PortBinding`, `Network`, `NetworkSummary`, `NetworkInspect`, `NetworkStatus`, `ServiceInfo`, `NetworkTaskInfo`, `ConfigReference`, `IPAM`, `IPAMConfig`, `IPAMStatus`, `SubnetStatus`, `EndpointResource`, `PeerInfo`, `NetworkCreateResponse`, `NetworkConnectRequest`, `NetworkDisconnectRequest`, `EndpointSettings`, `EndpointIPAMConfig`, and `NetworkAttachmentConfig`. They describe per-container endpoint configuration, operational endpoint data, network summary/inspect responses, IPAM status including address capacity, service task backends on swarm networks, driver options, DNS aliases, gateway priority, and port maps keyed as `<port>/<protocol>`.

Plugin schemas include `Plugin`, `PluginMount`, `PluginDevice`, `PluginEnv`, and `PluginPrivilege`. They model managed plugin identity, enabled state, user-configurable settings, remote reference, interface capabilities and socket, protocol scheme, entrypoint, workdir, user IDs, network mode, Linux capabilities/devices, propagated mounts, host IPC/PID settings, environment, args, and plugin rootfs layer metadata.

Swarm object schemas include `ObjectVersion`, `NodeSpec`, `Node`, `NodeDescription`, `Platform`, `EngineDescription`, `TLSInfo`, `NodeStatus`, `NodeState`, `ManagerStatus`, `Reachability`, `SwarmSpec`, `ClusterInfo`, `JoinTokens`, `Swarm`, `TaskSpec`, `TaskState`, `ContainerStatus`, `PortStatus`, `TaskStatus`, `Task`, `ServiceSpec`, `EndpointPortConfig`, `EndpointSpec`, `Service`, `ServiceCreateResponse`, and `ServiceUpdateResponse`. These expose swarmkit concepts: version-index optimistic concurrency, node role/availability, resource advertisement, manager reachability, raft/dispatcher/CA configuration, encryption-at-rest, service task templates, plugin/container/attachment runtime exclusivity, secrets/config references, credential specs, SELinux/seccomp/AppArmor/no-new-privileges, resource limits and reservations, placement constraints/preferences, update and rollback policies, job service modes, endpoint publishing, and task state transitions.

Secret and config schemas include `Driver`, `SecretSpec`, `Secret`, `ConfigSpec`, and `Config`. They model swarm secrets/configs as versioned objects with names, labels, base64-encoded data, optional external drivers, optional templating drivers, and file/runtime references when mounted into service tasks. The descriptions explicitly state size limits and that secret data is create-only and not returned by other endpoints.

Stats and daemon/system schemas include `ContainerStatsResponse`, `ContainerBlkioStats`, `ContainerBlkioStatEntry`, `ContainerCPUStats`, `ContainerCPUUsage`, `ContainerPidsStats`, `ContainerThrottlingData`, `ContainerMemoryStats`, `ContainerNetworkStats`, `ContainerStorageStats`, `SystemVersion`, `SystemInfo`, `ContainerdInfo`, `FirewallInfo`, `PluginsInfo`, `RegistryServiceConfig`, `IndexInfo`, `Runtime`, `Commit`, `SwarmInfo`, `LocalNodeState`, `PeerNode`, `EventActor`, and `EventMessage`. These definitions expose container live stats, cgroups v1/v2 differences, Windows-specific storage/network/memory fields, daemon version/build metadata, host feature flags, storage and firewall backends, registry mirrors/insecure registries, configured OCI runtimes, containerd namespaces, security options, CDI spec directories, NRI status, live-restore, swarm membership, and event payloads.

OCI and registry-inspection schemas include `OCIDescriptor`, `OCIPlatform`, and `DistributionInspect`. They mirror OCI image-spec descriptor/platform concepts, including media type, digest, size, URLs, annotations, embedded base64 content, platform, artifact type, and registry-supported platform lists.

Common utility schemas include `AuthConfig`, `AuthResponse`, `ProcessConfig`, `ErrorDetail`, `ProgressDetail`, `ErrorResponse`, and `IDResponse`. These provide shared registry login shapes, process metadata, progress/error messages for streaming operations, and stable `message` or `Id` fields used by many path operations in later chunks.

## Control Flow And Implied API Workflows

This chunk contains data contracts rather than path/method definitions, so it does not implement executable control flow. It does, however, encode the object flow expected by later API operations.

Container lifecycle flows use `ContainerConfig`, `HostConfig`, `NetworkingConfig`, and `EndpointSettings` at create/connect time, then expose runtime results through `ContainerInspectResponse`, `ContainerState`, `MountPoint`, `NetworkSettings`, `Health`, stats objects, top/process responses, wait responses, and filesystem change entries. The schema separates desired/persisted configuration from operational state: create-time mount and network requests are not identical to inspect-time mount points and endpoint state.

Image workflows use build/create/push progress messages, image summaries, image inspection data, image history records, build cache disk-usage records, and OCI descriptors. A client can infer a flow of build or pull progress, local image summary/inspect visibility, multi-platform descriptor inspection, and eventual disk-usage accounting.

Swarm workflows use spec/status object pairs. `SwarmSpec`, `NodeSpec`, `ServiceSpec`, `TaskSpec`, `SecretSpec`, and `ConfigSpec` represent desired or user-modifiable state, while `Node`, `Service`, `Task`, `Secret`, `Config`, `ClusterInfo`, and status subobjects report persisted cluster state. `ObjectVersion.Index` is the explicit concurrency token that later update endpoints must use to avoid accidental overwrites.

System and runtime workflows expose a capability-discovery phase. Clients should query `/version` and `/info` contracts represented by `SystemVersion` and `SystemInfo` before assuming support for cgroups, runtime names, CDI/NRI, containerd namespaces, firewall backend, storage features, swarm availability, registry configuration, or platform-specific stats fields.

## State And Persistence Behavior

The YAML itself is static source, but the schemas describe daemon-owned persistent and runtime state. Containers persist config, host config, restart policy, labels, mounts, network attachments, logs, exec IDs, image references, rootfs changes, health state, and lifecycle timestamps. Volumes persist driver-managed storage, labels, options, usage accounting, and for cluster volumes a swarm object identity and CSI/global status. Images persist layer content, tags, digests, descriptors, local metadata, signatures/identity, build cache records, and usage/reclaim accounting.

Swarm objects persist versioned raft-backed cluster state: nodes, services, tasks, secrets, configs, swarm spec, CA material, join tokens, manager state, and cluster volumes. The schema emphasizes optimistic concurrency via `ObjectVersion.Index`; any generated client or handler layer that ignores this field risks lost updates.

System state is mostly observed, not mutated, through these definitions. `SystemInfo` reports daemon process state, host resources, storage driver status, configured runtimes, proxy settings, daemon root directory, registry configuration, security features, CDI directories, NRI information, containerd socket/namespaces, and warning messages. Some fields are explicitly unstable informational data, especially driver status, runtime status, firewall info, OS version formatting, daemon ID format, and NRI info.

Stats state is sampled. `ContainerStatsResponse` carries current and previous CPU samples, memory stats, network counters, blkio counters, storage stats, and pids stats. The schema documents cgroups v1/v2 and Linux/Windows omissions, so clients must treat absent/null values as normal rather than as parse failures.

## Dependencies And Integration Points

The immediate tooling dependency is Swagger/OpenAPI 2.0 plus Docker's generator extensions. Consumers must preserve `$ref`, `allOf`, enum values, examples, markdown descriptions, nullable markers, custom Go type mappings, package/name overrides, and map-valued `additionalProperties`.

Runtime integration points exposed by the schema include Docker Engine, containerd, OCI runtimes such as runc, Linux cgroups/namespaces/seccomp/AppArmor/SELinux/userns/rootless support, Windows isolation and credential specs, storage graph drivers, BuildKit cache/image-store concepts, registry services and mirrors, swarmkit/raft/CA, volume/network/logging/authorization plugins, CDI device injection, NRI, firewall backends, and OCI image/distribution specifications.

Documentation integration depends on ReDoc behavior, tag ordering, markdown tables, notes, warnings, and embedded links to Docker docs, Go docs, OCI specs, kernel docs, RFCs, and swarmkit constants. Generated-client integration depends on stable schema names and generator hints such as `x-go-name: DiskUsage`, `x-go-package`, and custom `net/netip` types.

## Risks And Edge Cases

Schema drift is the primary risk. Because this YAML is used for docs and generated types, incorrect required fields, nullability, enum members, integer formats, or custom Go types can break clients even if daemon handlers still behave correctly.

The chunk contains several compatibility-sensitive platform distinctions. Linux cgroups v1/v2 stats differ, Windows has separate CPU, memory, storage, networking, isolation, and credential-spec behavior, and many daemon `/info` values appear only when debug, experimental, rootless, CDI, NRI, swarm, firewall, or containerd-image-store conditions are met. Clients must tolerate missing, null, empty, or informational-only fields.

Security-sensitive surface area is broad. The schemas expose privileged containers, host namespaces, capabilities, device mappings and requests, bind mounts, sysctls, security options, insecure registries, registry auth, plugin device/mount permissions, swarm CA signing keys, secrets/config data, credential specs, CDI injection, and runtime arguments. Shape validation in the schema is not sufficient for path safety, secret redaction, registry trust, privilege boundaries, or runtime policy enforcement.

Streaming and non-JSON endpoints are not visible as paths in this chunk, but their shared progress/error schemas are. Build, pull, push, stats, logs, attach, exec, events, archive, export, and import operations in later chunks must not be treated as ordinary request/JSON-response RPCs just because they reuse definitions from here.

Open schema compatibility can conflict with strict code generation. The file-level description says servers may add response properties and ignore extra request properties. Generated clients and tests should allow unknown fields even where generated structs have a fixed field list.

Version text should be reviewed carefully. The file is `v1.54` with `basePath: /v1.54`, but the top description still mentions the current API and examples with older version numbers. That may be intentional copied compatibility prose, but it is a documentation drift signal for the merge lane to validate against surrounding v1.54 docs.

This chunk ends mid-definition. Any merger must avoid treating `ClusterVolume` or later `ClusterVolumeSpec` references as complete from this artifact alone.

## Test Signals

Useful static validation is full-file Swagger parsing with this chunk reconciled against later chunks: all `$ref` targets should resolve, vendor extensions should be accepted, schema names should remain unique, and generated Go names/packages should match the intended API packages.

Generated-type tests should cover `x-nullable`, `x-omitempty`, `x-go-name`, `x-go-package`, `x-go-type`, `allOf` composition, map fields through `additionalProperties`, nullable arrays, integer formats such as `uint64`, `uint32`, and `int64`, enum generation, date-time strings, OCI descriptor/platform structs, and custom network address types.

Contract tests should exercise representative create/inspect/list/update flows for containers, images, networks, volumes, plugins, swarm nodes/services/tasks/secrets/configs, and system info. State tests should verify that created or mutated objects appear in later inspect/list/system-df responses and that swarm updates preserve `ObjectVersion.Index` concurrency behavior.

Platform tests should assert Linux cgroups v1/v2 stats omissions, Windows-specific stats and isolation fields, CDI/NRI experimental behavior, rootless/userns changes to containerd namespaces, debug-only daemon metrics, and optional multi-platform image descriptor fields.

Security and compatibility tests should cover unknown-field tolerance, invalid enum/format rejection where handlers enforce it, insecure registry warnings, secret/config data redaction, privilege-related host config validation, bind/tmpfs/image/cluster mount constraints, endpoint IPAM validation, credential spec exclusivity, and plugin privilege prompts.

Documentation tests or review checks should confirm ReDoc tag placement, markdown rendering, warnings/notes, examples, and version prose so generated docs for API v1.54 do not mislead clients.
