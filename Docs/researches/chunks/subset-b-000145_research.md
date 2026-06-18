# sources/cloud-native/moby/api/docs/v1.48.yaml

## Chunk Scope
Research for `subset-b-000145`, covering `sources/cloud-native/moby/api/docs/v1.48.yaml` lines 1-7758. This chunk contains the OpenAPI/Swagger 2.0 document header, tag taxonomy, and the bulk of the `definitions` section through `ImageManifestSummary`.

## Purpose
This file is the Docker Engine API v1.48 contract used to generate API documentation and client/server types. The header declares Swagger 2.0, `/v1.48` as the versioned base path, JSON/text media types, the ReDoc-facing description, registry authentication header semantics, and the tag menu order for primary objects, Swarm objects, plugins, and system APIs.

Within this chunk, the main purpose is schema definition. It models Docker Engine resources and response bodies for containers, images, volumes, networks, plugins, Swarm nodes/services/tasks/secrets/configs, runtime/system information, registry configuration, events, OCI descriptors/platforms, distribution inspect results, and Swarm CSI cluster volumes.

## Important APIs, Types, And Schemas
- Document metadata and tags define the public API surface grouping: `Container`, `Image`, `Network`, `Volume`, `Exec`, `Swarm`, `Node`, `Service`, `Task`, `Secret`, `Config`, `Plugin`, and `System`.
- Container creation and inspection are built from `ContainerConfig`, `HostConfig`, `Resources`, `Mount`, `MountPoint`, `RestartPolicy`, `HealthConfig`, `Health`, `ContainerState`, `ContainerInspectResponse`, `ContainerSummary`, `ContainerCreateResponse`, `ContainerUpdateResponse`, `ContainerStatsResponse`, `ContainerTopResponse`, and `ContainerWaitResponse`.
- Image schemas include `ImageHistoryResponseItem`, `ImageConfig`, `ImageInspect`, `ImageSummary`, `ImageDeleteResponseItem`, `ImageID`, `CreateImageInfo`, `PushImageInfo`, `BuildInfo`, `BuildCache`, `OCIDescriptor`, `OCIPlatform`, and `DistributionInspect`. The image manifest summary schema begins at the chunk boundary.
- Network and endpoint types include `NetworkingConfig`, `NetworkSettings`, `Network`, `ConfigReference`, `IPAM`, `IPAMConfig`, `NetworkContainer`, `PeerInfo`, `EndpointSettings`, `EndpointIPAMConfig`, `NetworkCreateResponse`, `Port`, `PortMap`, `PortBinding`, `Address`, `DriverData`, and `NetworkAttachmentConfig`.
- Volume and storage schemas include `Volume`, `VolumeCreateOptions`, `VolumeListResponse`, `ClusterVolume`, `ClusterVolumeSpec`, and `Topology`. The cluster-volume model captures Swarm CSI identity, capacity, topology, publish state, access mode, sharing, secrets, and availability.
- Plugin schemas include `PluginMount`, `PluginDevice`, `PluginEnv`, `PluginInterfaceType`, `PluginPrivilege`, and `Plugin`, including plugin settings, config, interface, Linux device/capability needs, rootfs metadata, and user-settable fields.
- Swarm schemas include `ObjectVersion`, `NodeSpec`, `Node`, `NodeDescription`, `Platform`, `EngineDescription`, `TLSInfo`, `NodeStatus`, `ManagerStatus`, `SwarmSpec`, `ClusterInfo`, `JoinTokens`, `Swarm`, `TaskSpec`, `TaskState`, `TaskStatus`, `Task`, `ServiceSpec`, `EndpointPortConfig`, `EndpointSpec`, `Service`, `ServiceCreateResponse`, `ServiceUpdateResponse`, `SecretSpec`, `Secret`, `ConfigSpec`, `Config`, `SwarmInfo`, `LocalNodeState`, and `PeerNode`.
- System schemas include `SystemVersion`, `SystemInfo`, `ContainerdInfo`, `PluginsInfo`, `RegistryServiceConfig`, `IndexInfo`, `Runtime`, `Commit`, `EventActor`, and `EventMessage`.
- Generic response and stream helper schemas include `ErrorResponse`, `IDResponse`, `ErrorDetail`, and `ProgressDetail`.

## Control Flow And API Semantics
The file is declarative, so runtime control flow is encoded as relationships among schemas and endpoint contracts rather than executable branches. The OpenAPI document establishes how clients and generators traverse `$ref` links to compose request and response shapes.

Key flows represented by this chunk:
- Container creation combines portable `ContainerConfig`, host-specific `HostConfig`, and per-endpoint `NetworkingConfig`; inspection returns those inputs plus runtime state, graph-driver data, mounts, generated host files, exec IDs, size fields, and network operational data.
- Mount handling distinguishes reporting (`MountPoint`) from create/update inputs (`Mount`). `Mount.Type` drives which option object is meaningful: bind, volume, image, tmpfs, npipe, or cluster volume.
- Healthcheck flow is represented by `HealthConfig` inputs and `Health`/`HealthcheckResult` outputs. Probe exit code meanings and timing thresholds are part of the API contract.
- Image operations stream progress through `BuildInfo`, `CreateImageInfo`, and `PushImageInfo`; modern consumers should prefer structured `errorDetail` and `progressDetail` over deprecated string fields.
- Swarm update flow uses `ObjectVersion.Index` for optimistic concurrency. Nodes, services, tasks, secrets, configs, and swarm cluster state carry versions so update requests can fail instead of silently overwriting concurrent changes.
- Service orchestration is modeled through `ServiceSpec.TaskTemplate`, `Mode`, `UpdateConfig`, `RollbackConfig`, `EndpointSpec`, and `TaskSpec`. `TaskSpec` supports container tasks, plugin tasks, and read-only network attachment tasks, with mutual-exclusion constraints documented in descriptions.
- Task lifecycle is captured by `TaskState` from `new` through scheduling, running, terminal, removal, and orphan states. `TaskStatus` embeds container and published-port status.
- System/version/info endpoints expose daemon build metadata, feature support, storage/network/security/runtime configuration, Swarm status, proxy settings, warnings, and containerd namespace details.

## State And Persistence Behavior
The schemas describe several persistent state domains:
- Docker daemon state under `DockerRootDir`, including containers, images, volumes, graph-driver data, logs, generated container files, and local metadata such as image `LastTagTime`.
- Runtime container state in `ContainerState`, including status, PID, exit code, OOM information, start/finish timestamps, restart count, health, and paused/running semantics. The API explicitly warns that `Running` and `Paused` can both be true, so `Status` is the reliable state discriminator.
- Resource and cgroup state in `Resources`, `ContainerStatsResponse`, and nested CPU, memory, blkio, PID, network, and storage stats. Many fields are platform-specific and differ between Linux cgroups v1, Linux cgroups v2, and Windows.
- Swarm Raft state in `SwarmSpec`, `ClusterInfo`, `JoinTokens`, `ObjectVersion`, and related node/service/task objects. Settings cover task-history retention, snapshots, election/heartbeat ticks, external CA configuration, manager auto-lock, and task defaults.
- Secrets and configs persist as Swarm objects with versions and timestamps. `SecretSpec.Data` is create-only, base64-encoded, omitted from read endpoints, and limited to 500KB; `ConfigSpec.Data` is base64-encoded and limited to 1000KB.
- Volume state includes local/global scope, driver options, low-level driver status, usage data used by `/system/df`, and CSI cluster volume creation/publish/accessibility status.
- Registry and runtime state is represented by `RegistryServiceConfig`, `IndexInfo`, `Runtime`, `Commit`, and `ContainerdInfo`, including insecure registry policy, mirrors, OCI runtime paths/args/status, external component commits, and containerd namespaces used by the daemon.

## Dependencies And Integration Points
- The file depends on Swagger 2.0/OpenAPI tooling, ReDoc Markdown rendering, and Docker's API generation pipeline referenced in the file header.
- It integrates with Docker CLI behavior: the description maps CLI commands to Engine endpoints, and many schema fields mirror CLI concepts such as `docker ps`, `docker inspect`, `docker exec`, `docker info`, `docker system df`, and Swarm service updates.
- Registry authentication depends on clients sending `X-Registry-Auth` as base64url-encoded JSON credentials or an identity token from `/auth`.
- Runtime and platform schemas integrate with OCI runtime spec, OCI image descriptor/index/platform semantics, containerd, runC, and multi-platform image stores.
- Networking schemas integrate with libnetwork concepts: network drivers, IPAM, endpoint settings, DNS names, gateway priority, overlay peers, ingress routing mesh, attachable networks, and config-only networks.
- Swarm schemas integrate with swarmkit concepts: Raft versions, node roles/availability, manager reachability, join tokens, external CAs, task scheduling constraints/preferences, secrets/config references, service update/rollback state, and job-mode services.
- Storage schemas integrate with graph drivers/snapshotters, volume drivers, BuildKit build cache metadata, CDI device spec directories, and CSI-style cluster volumes.
- Security-related integration points include SELinux labels, AppArmor, seccomp, no-new-privileges, user namespaces, capabilities, credential specs on Windows, insecure registry policy, TLS CA info, and plugin privileges.

## Risks And Edge Cases
- The API uses an open schema model: servers may add response fields and ignore extra request fields. Strict clients that reject unknown properties are compatibility risks.
- Many fields are nullable, optional, platform-specific, or endpoint-specific. Codegen and clients must distinguish absent, `null`, zero values, and sentinel values such as `-1` for unknown sizes/refcounts.
- Deprecations are significant in this chunk: many `ImageConfig` fields are no longer part of the image specification and are scheduled for removal in API v1.50; `ContainerConfig.MacAddress` is deprecated in favor of endpoint settings; nondistributable artifact registry allow-lists are scheduled for removal in API v1.49; `Commit.Expected` is deprecated; several build/push progress string fields are deprecated in favor of structured detail objects.
- Experimental multi-platform image fields such as image `Descriptor` and `Manifests` warn that they may change without backward compatibility.
- Security-sensitive fields include registry credentials, secrets/config data, insecure registry settings, external CA material, credential specs, plugin privileges, host namespace modes, privileged containers, device access, capabilities, sysctls, and bind mounts.
- Some descriptions encode validation rules that are not fully machine-enforced by Swagger, such as mutual exclusivity among `TaskSpec.ContainerSpec`, `PluginSpec`, and `NetworkAttachmentSpec`, credential-spec sources, config file/runtime targets, mount option combinations, and service endpoint mode restrictions.
- Generated clients need care around non-standard extension fields such as `x-go-name`, `x-nullable`, and `x-omitempty`; these affect Go type generation and JSON omission behavior but are not generic Swagger keywords.
- Long examples and rich Markdown are part of the documentation contract. Formatting regressions can affect rendered docs even when schema validation passes.

## Test Signals
- OpenAPI/Swagger validation should parse the document, resolve all `$ref` entries in this chunk, and preserve vendor extensions used by Docker's generators.
- Generated Go types and client/server stubs should compile after any schema change, especially around `allOf` composition (`HostConfig`, `Swarm`) and nullable/omitempty fields.
- Documentation rendering in ReDoc should be checked for tag ordering, Markdown tables/lists, deprecation notes, warnings, and examples.
- API compatibility tests should cover old clients reading newer daemon responses with additional properties, and newer clients tolerating omitted fields from older or platform-limited daemons.
- Behavioral tests should exercise container create/inspect/update/stats/wait/top, image inspect/list/pull/push/build progress, network create/connect/inspect, volume create/list/df usage, Swarm node/service/task update flows with version conflicts, secret/config create/read redaction, `/version`, `/info`, `/events`, and distribution inspect.
- Platform matrix signals matter: Linux cgroups v1, Linux cgroups v2, Windows process isolation, Windows Hyper-V isolation, rootless/userns, containerd image store enabled/disabled, Swarm active/inactive, and experimental feature enabled/disabled.
- Security test signals should include insecure registry handling, registry auth header parsing, secret data omission on read, plugin privilege prompts/config, privileged/device/capability/sysctl validation, and external CA/TLS fields.
