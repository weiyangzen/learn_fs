# sources/cloud-native/moby/api/docs/v1.33.yaml lines 1-7569

## Chunk Scope

This chunk covers the opening 7,569 lines of the Docker Engine API v1.33 Swagger 2.0 document. It includes the file header, global OpenAPI metadata, tag taxonomy, all schema definitions from `ImageHistoryResponseItem` through `PeerNode`, and the beginning of the `paths` table from `/containers/json` through the first part of `/volumes/{name}`. The chunk ends while defining the `name` path parameter for `VolumeInspect`; later chunk research must complete the rest of that endpoint and the remaining paths.

The file states that it is used to generate API documentation and the client/server types. The schemas and `operationId` values are therefore not just static documentation: they are part of the contract for generated Go-facing API types, generated clients, ReDoc output, and compatibility expectations for Docker Engine API version `1.33`.

## Purpose and Structure

The document defines the versioned Docker Engine HTTP API under `basePath: /v1.33`, with `http` and `https` schemes and default JSON/text media types. Its top-level `info.description` explains the major compatibility rule: clients should prefix requests with a version, tolerate additional response fields, and avoid depending on unversioned API access. Registry authentication is specified as a client-supplied `X-Registry-Auth` header containing base64-encoded JSON credentials or an identity token.

The `tags` section defines ReDoc menu groupings and the logical API domains visible in this chunk: `Container`, `Image`, `Network`, `Volume`, `Exec`, `Swarm`, `Node`, `Service`, `Task`, `Secret`, `Config`, `Plugin`, and `System`. The tag comments are an important maintenance signal because incorrect tagging affects documentation navigation even if the API machinery still parses the file.

The `definitions` section provides reusable object and enum schemas. The later `paths` section references those definitions through `$ref`, inline composition with `allOf`, and request/response bodies. Docker-specific vendor extensions appear throughout, especially `x-go-name` and `x-nullable`, indicating that generated Go types and nullability behavior depend on this YAML, not only the public docs.

## Important Definitions and Data Contracts

Container and host configuration are the central model area in this chunk. `ContainerConfig` describes portable container configuration such as hostname, user, attached streams, TTY/stdin behavior, environment, command, entrypoint, healthcheck, image, labels, stop signal, stop timeout, shell, exposed ports, volumes, and working directory. `HostConfig` composes `Resources` and adds host-specific behavior: bind mounts, container ID file, logging driver config, network mode, port bindings, restart policy, auto-remove, volume inheritance, `Mounts`, Linux capabilities, DNS, extra hosts, IPC/PID/user namespace settings, privilege flags, read-only rootfs, security options, storage options, tmpfs, sysctls, runtime, Windows console size, and Windows isolation.

Resource schemas include `Resources`, `ResourceObject`, `ThrottleDevice`, `DeviceMapping`, and `GenericResources`. They model cgroup-style CPU, memory, blkio, device, pids, ulimit, and generic scheduling resources. This makes the API contract sensitive to platform differences: many fields are Unix-specific, some are Windows-only, and some are only meaningful if the daemon reports host support in `/info`.

Mount and volume schemas include `MountType`, `Mount`, `MountPoint`, and `Volume`. `Mount` is the create-time request object for bind, npipe, tmpfs, and named volume mounts, with nested bind, volume, and tmpfs options. `MountPoint` is the runtime/reporting view returned by container inspection and list endpoints. `Volume` models persistent storage with driver, mountpoint, labels, scope, options, and optional `UsageData` used by `/system/df`.

Image schemas include `ImageHistoryResponseItem`, `Image`, `ImageSummary`, `ImageDeleteResponseItem`, `BuildInfo`, `CreateImageInfo`, `PushImageInfo`, `GraphDriverData`, and `Commit`. These distinguish summary list data from full image inspection data, layer history, graph driver metadata, root filesystem layers, delete results, and streaming build/pull/push progress messages.

Networking schemas include `NetworkSettings`, `EndpointSettings`, `EndpointIPAMConfig`, `Address`, `PortMap`, `PortBinding`, `Network`, `IPAM`, and `NetworkContainer`. Important compatibility details include deprecated default-bridge fields in `NetworkSettings`, nullable endpoint driver options, port map keys in `<port>/<protocol>` format, and bridge/network summary fields that can vary by driver.

Swarm and orchestration schemas include `ObjectVersion`, `NodeSpec`, `Node`, `NodeDescription`, `Platform`, `EngineDescription`, `TLSInfo`, `NodeStatus`, `NodeState`, `ManagerStatus`, `Reachability`, `SwarmSpec`, `ClusterInfo`, `JoinTokens`, `Swarm`, `TaskSpec`, `TaskState`, `Task`, `ServiceSpec`, `EndpointPortConfig`, `EndpointSpec`, `Service`, `ServiceUpdateResponse`, `SecretSpec`, `Secret`, `ConfigSpec`, and `Config`. These models embed swarmkit concepts: optimistic concurrency with version indexes, manager reachability, raft/CA/dispatcher settings, service update and rollback policies, task templates, secrets/config references, placement constraints, platform filters, and endpoint publishing.

System and daemon schemas include `SystemInfo`, `PluginsInfo`, `RegistryServiceConfig`, `IndexInfo`, `Runtime`, `SwarmInfo`, `LocalNodeState`, and `PeerNode`. `SystemInfo` is broad and includes host/container/image counts, storage driver data, Docker root directory, legacy standalone Swarm status, plugin lists, cgroup feature flags, debug-only daemon metrics, daemon proxy settings, labels, runtimes, live-restore, default runtime, security options, and commit IDs for containerd/runc/init. `RegistryServiceConfig` carries insecure registry, mirror, and index configuration, with explicit warnings around insecure registry use.

Plugin schemas include `Plugin`, `PluginMount`, `PluginDevice`, `PluginEnv`, and `PluginInterfaceType`. They model managed plugin settings, capabilities, Linux device access, network mode, propagated mounts, rootfs layers, and settable user-controlled plugin configuration.

Common utility schemas include `AuthConfig`, `ProcessConfig`, `ErrorDetail`, `ProgressDetail`, `ErrorResponse`, and `IdResponse`. Most error responses across paths reference `ErrorResponse`, giving clients a stable `message` field for failures.

## API Operations in This Chunk

Container operations dominate the first path block. `ContainerList` (`GET /containers/json`) lists containers with `all`, `limit`, `size`, and JSON-encoded `filters`. `ContainerCreate` (`POST /containers/create`) accepts a body that combines `ContainerConfig`, `HostConfig`, and `NetworkingConfig`; it can return image-not-found, conflict, bad-parameter, and server errors. `ContainerInspect` returns detailed container state, host config, graph driver data, mount points, config, and network settings, with an optional `size` query. `ContainerTop`, `ContainerLogs`, `ContainerChanges`, `ContainerExport`, `ContainerStats`, and `ContainerArchive` expose process lists, logs, filesystem diffs, tar exports, live stats, and path-level archive operations.

Container lifecycle mutations include `ContainerStart`, `ContainerStop`, `ContainerRestart`, `ContainerKill`, `ContainerUpdate`, `ContainerRename`, `ContainerPause`, `ContainerUnpause`, `ContainerWait`, `ContainerDelete`, and `ContainerPrune`. These endpoints encode state-machine expectations through HTTP statuses: `204` for successful no-body lifecycle changes, `304` for already-started/already-stopped, `404` for missing containers, `409` for conflicts such as removing a running container or name collisions, and `500` for daemon failures. `ContainerWait` adds `condition` values `not-running`, `next-exit`, and `removed`.

Interactive stream operations are a key special case. `ContainerLogs` can return either a plain response or a hijacked stream when `follow` is enabled. `ContainerAttach` uses `application/vnd.docker.raw-stream`, optional HTTP upgrade, and a multiplexed frame format when TTY is disabled. `ContainerAttachWebsocket` exposes a websocket-oriented attach variant. `ExecStart` uses the same raw-stream media type for interactive exec sessions. Client and proxy implementations must treat `101` upgrade responses, raw TCP hijacking, websocket attachment, TTY-vs-non-TTY multiplexing, and detach key handling as protocol behavior rather than ordinary JSON REST responses.

Image operations include `ImageList`, `ImageBuild`, `BuildPrune`, `ImageCreate`, `ImageInspect`, `ImageHistory`, `ImagePush`, `ImageTag`, `ImageDelete`, `ImageSearch`, `ImagePrune`, `ImageCommit`, `ImageGet`, `ImageGetAll`, and `ImageLoad`. These operations cover local image metadata, build contexts, registry pulls/imports, inspection, layer history, push, tagging, deletion, Docker Hub-style search, pruning, commit-from-container, and tarball import/export. Several operations stream progress or tar data rather than returning typed JSON schemas, so generated clients need separate code paths for binary bodies and line-oriented JSON progress.

System operations include `SystemAuth`, `SystemInfo`, `SystemVersion`, `SystemPing`, `SystemEvents`, and `SystemDataUsage`. `SystemAuth` validates registry credentials through the `AuthConfig` body and may return either a JSON status/identity token response or `204`. `/events` is a streaming monitor with `since`, `until`, and JSON `filters`, covering objects such as containers, images, volumes, networks, daemon, plugins, nodes, services, secrets, and configs. `/system/df` returns cross-object storage usage for layers, images, containers, and volumes.

Exec operations include `ContainerExec`, `ExecStart`, `ExecResize`, and `ExecInspect`. The flow is two-step: create an exec instance inside a container, then start it. The create body controls attached streams, TTY, env, command, privilege, detach keys, and user. Start decides detach vs interactive behavior. Resize only applies when a TTY was allocated, and inspect returns process config, running state, exit code, stdin/stdout/stderr flags, container ID, and host PID.

Volume operations begin with `VolumeList`, `VolumeCreate`, and the start of `VolumeInspect`. Listing accepts JSON filters for dangling state, driver, label, and name, and returns both volume entries and warnings. Creation accepts name, driver, driver options, and labels. The `VolumeInspect` definition is incomplete in this chunk because line 7,569 cuts off inside the path parameter block.

## Control Flow and State Behavior

This YAML expresses the Docker client-to-daemon control flow as independent HTTP operations, but many endpoint groups are designed to be sequenced. Running a container typically requires `ContainerCreate`, `ContainerStart`, optionally `ContainerAttach` or `ContainerLogs`, then `ContainerWait`, `ContainerStop`, and `ContainerDelete`. Running an exec command requires `ContainerExec`, `ExecStart`, optionally `ExecResize`, and `ExecInspect`. Building or importing images involves streaming input to `/build`, `/images/create`, or `/images/load`, then observing resulting image state through list/inspect/history/export endpoints.

The persistent state controlled by these APIs lives in the daemon and host, not in the YAML. Containers persist configuration, runtime state, logs, root filesystem changes, network endpoints, mounts, and restart policy. Images persist layers, tags, digests, graph driver data, rootfs metadata, and build/import/export content. Volumes persist driver-created storage and optional usage accounting. Swarm objects persist versioned cluster state through raft-backed manager state, including nodes, services, tasks, secrets, configs, CA material, and join tokens. System endpoints expose daemon process, host, registry, runtime, plugin, and storage-driver state.

The schema repeatedly distinguishes create-time configuration from inspect-time operational state. For example, `ContainerConfig` and `HostConfig` are inputs and persisted desired configuration, while `ContainerInspect` returns `State`, `GraphDriver`, `Mounts`, and `NetworkSettings` that reflect runtime results. Likewise `ServiceSpec` is desired service configuration, while `Service` includes `Endpoint` and `UpdateStatus`.

Optimistic concurrency is explicitly modeled for swarm objects through `ObjectVersion.Index`; update endpoints outside this chunk are expected to require the version number so simultaneous writes do not silently overwrite each other. This is one of the strongest state-safety contracts visible in the definitions section.

## Dependencies and Integration Points

The immediate format dependency is Swagger/OpenAPI 2.0. Tooling must understand `$ref`, `allOf`, object maps through `additionalProperties`, vendor extensions such as `x-go-name` and `x-nullable`, nullable arrays/objects, examples, markdown descriptions, response headers, binary string formats, and non-JSON media types.

Runtime dependencies exposed by the API include the Docker daemon, containerd, OCI runtimes such as runc, Linux cgroups and namespaces, SELinux/AppArmor/seccomp/userns features, Windows isolation and credential specs, storage graph drivers, logging drivers, network drivers, volume drivers, managed and legacy plugins, registries, registry mirrors, external CAs, and swarmkit/raft. Registry operations integrate through `X-Registry-Auth` and `X-Registry-Config` headers, and build operations can fetch remote Git/HTTP contexts.

Documentation integration depends on ReDoc-specific behavior and the tag ordering comments. Generated code integration depends on stable `operationId` names such as `ContainerCreate`, `ImageBuild`, `SystemInfo`, and `ExecStart`. Test suites and generated clients should treat those names as public generator inputs.

## Risks and Edge Cases

The largest compatibility risk is schema drift between this YAML and Docker Engine handlers/types. Since the file is used for documentation and generated client/server types, incorrect nullability, required fields, enum values, or response codes can produce broken clients even if the daemon behavior is correct.

Streaming and hijacked-connection endpoints are high-risk for generic OpenAPI tooling. `ContainerAttach`, `ContainerLogs` with follow, `ExecStart`, `SystemEvents`, image build/pull/push progress, tar export/import, and archive operations cannot be tested as ordinary request/JSON-response calls. Clients must handle raw streams, upgrade responses, binary tar bodies, websocket attachment, cancellation on client disconnect, and Docker multiplex framing.

Security-sensitive fields are widely exposed. `Privileged`, device mappings, capabilities, host namespaces, bind mounts, `SecurityOpt`, insecure registries, registry auth headers, swarm CA signing material, secrets/config data, plugin device/mount permissions, and build remote contexts all require careful server-side validation outside this schema. The schema documents shape and some constraints, but it does not enforce path safety, privilege boundaries, secret redaction, registry trust, tar extraction safety, or command execution policy by itself.

Platform-specific fields can be misleading if clients assume all properties apply everywhere. The chunk mixes Linux-only cgroup/freezer/namespace behavior, Windows isolation and credential specs, debug-only daemon metrics, standalone Swarm legacy fields, built-in swarm mode fields, and deprecated bridge network fields. Code generators should preserve optionality and clients should tolerate absent or empty values.

Some schema details warrant validation scrutiny. `ProgressDetail.message` is typed as integer even though the name suggests text. `ContainerInspect.ExecIDs` is typed as string, while engine behavior in nearby API versions often represents exec IDs as a list or null. `ContainerConfig.Volumes` nests `additionalProperties` under `properties`, which is unusual for a map-shaped object. `IPAM.Options` is modeled as an array of maps, while many Docker APIs use a map. `buildargs` on `/build` is typed as integer despite being described as a JSON map of strings. These may be intentional historical API quirks or spec defects; generated-code and conformance tests should make the expected behavior explicit.

The chunk ends in the middle of `VolumeInspect`, so a merger must avoid treating `/volumes/{name}` as complete based only on this artifact.

## Test Signals

Useful validation starts with OpenAPI parsing of lines 1-7569 in the context of the full file: verify valid Swagger 2.0, resolvable `$ref` targets, accepted vendor extensions, stable tag and `operationId` uniqueness, and no duplicate path/method definitions. Generated Go type tests should cover `x-nullable`, `x-go-name`, `allOf` composition, `additionalProperties` maps, arrays, enum generation, integer formats such as `uint64`/`int64`, and binary string bodies.

Endpoint conformance tests should exercise representative success and failure statuses for container lifecycle operations, image build/pull/push/import/export operations, system info/version/ping/auth/events/data-usage endpoints, exec create/start/resize/inspect, and volume list/create/inspect. Negative tests should cover missing resources, bad parameters, conflicts, read-only filesystem/archive errors, paused/stopped container exec errors, and registry auth failures.

Protocol-level tests are especially important for attach/logs/exec/events/build streams. They should assert HTTP `101` upgrade behavior, non-upgrade `200` raw-stream behavior, Docker multiplex frame parsing when TTY is disabled, raw PTY stream behavior when TTY is enabled, websocket attach behavior, event filtering, stream cancellation on client disconnect, tar upload/download media types, and large body handling.

State and persistence tests should verify that create/update/delete operations are visible through subsequent inspect/list/system-df endpoints; that image and volume prune reclaim accounting is plausible; that container size fields appear only when requested; that volume `UsageData` appears in `/system/df`; and that swarm object definitions preserve version indexes for safe updates in later endpoint chunks.
