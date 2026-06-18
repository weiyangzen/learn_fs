# sources/cloud-native/moby/api/docs/v1.54.yaml - subset-b-000158 Research

Source chunk: `sources/cloud-native/moby/api/docs/v1.54.yaml` lines 7938-13891.

## Purpose

This chunk transitions from the tail of reusable OpenAPI definitions into the main Docker Engine API `paths` section. It documents a large portion of the v1.54 HTTP API surface: container lifecycle and filesystem operations, image build/pull/push/import/export, daemon/system inspection, exec sessions, volumes, networks, plugins, Swarm nodes and cluster control, services, tasks, secrets, configs, registry distribution inspection, and the deprecated interactive session transport.

The content is declarative Swagger/OpenAPI 2.0 YAML rather than executable code. Its practical role is to define the daemon/client contract for generated clients, API reference rendering, compatibility checks, and request/response validation. The `operationId` values are especially important integration points because they map stable HTTP operations to client method names and documentation anchors.

## Important APIs, Types, and Schemas

The chunk starts inside definitions for Swarm/CSI-oriented volumes and image manifest summaries:

- `ClusterVolumeSpec` defines cluster-specific volume scheduling and CSI provisioning options. Important fields include `Group`, `AccessMode`, `Secrets`, `AccessibilityRequirements`, `CapacityRange`, and `Availability`.
- `Topology` models CSI topology as `Segments`, a string-to-string map.
- `ImageManifestSummary` (`x-go-name: ManifestSummary`) summarizes per-manifest image data, including OCI `Descriptor`, `Available`, `Size`, `Kind`, image-specific `ImageData`, and attestation-specific `AttestationData`.

The path operations visible in this chunk are grouped by Docker object domain:

- Container APIs: `ContainerList`, `ContainerCreate`, `ContainerInspect`, `ContainerTop`, `ContainerLogs`, `ContainerChanges`, `ContainerExport`, `ContainerStats`, `ContainerResize`, `ContainerStart`, `ContainerStop`, `ContainerRestart`, `ContainerKill`, `ContainerUpdate`, `ContainerRename`, `ContainerPause`, `ContainerUnpause`, `ContainerAttach`, `ContainerAttachWebsocket`, `ContainerWait`, `ContainerDelete`, `ContainerArchiveInfo`, `ContainerArchive`, `PutContainerArchive`, and `ContainerPrune`.
- Image/build APIs: `ImageList`, `ImageBuild`, `BuildPrune`, `ImageCreate`, `ImageInspect`, `ImageHistory`, `ImagePush`, `ImageTag`, `ImageDelete`, `ImageSearch`, `ImagePrune`, `ImageCommit`, `ImageGet`, `ImageGetAll`, and `ImageLoad`.
- System APIs: `SystemAuth`, `SystemInfo`, `SystemVersion`, `SystemPing`, `SystemPingHead`, `SystemEvents`, and `SystemDataUsage`.
- Exec APIs: `ContainerExec`, `ExecStart`, `ExecResize`, and `ExecInspect`.
- Volume APIs: `VolumeList`, `VolumeCreate`, `VolumeInspect`, `VolumeUpdate`, `VolumeDelete`, and `VolumePrune`.
- Network APIs: `NetworkList`, `NetworkInspect`, `NetworkDelete`, `NetworkCreate`, `NetworkConnect`, `NetworkDisconnect`, and `NetworkPrune`.
- Plugin APIs: `PluginList`, `GetPluginPrivileges`, `PluginPull`, `PluginInspect`, `PluginDelete`, `PluginEnable`, `PluginDisable`, `PluginUpgrade`, `PluginCreate`, `PluginPush`, and `PluginSet`.
- Swarm/node/service/task APIs: `NodeList`, `NodeInspect`, `NodeDelete`, `NodeUpdate`, `SwarmInspect`, `SwarmInit`, `SwarmJoin`, `SwarmLeave`, `SwarmUpdate`, `SwarmUnlockkey`, `SwarmUnlock`, `ServiceList`, `ServiceCreate`, `ServiceInspect`, `ServiceDelete`, `ServiceUpdate`, `ServiceLogs`, `TaskList`, `TaskInspect`, and `TaskLogs`.
- Secret/config APIs: `SecretList`, `SecretCreate`, `SecretInspect`, `SecretDelete`, `SecretUpdate`, `ConfigList`, `ConfigCreate`, `ConfigInspect`, `ConfigDelete`, and `ConfigUpdate`.
- Registry/session APIs: `DistributionInspect` and `Session`.

Most operations reference common definitions outside this chunk, including `ErrorResponse`, `ContainerSummary`, `ContainerConfig`, `HostConfig`, `NetworkingConfig`, `ContainerInspectResponse`, `ContainerStatsResponse`, `FilesystemChange`, `ImageSummary`, `ImageInspect`, `ImageHistoryResponseItem`, `ImageDeleteResponseItem`, `AuthConfig`, `AuthResponse`, `SystemInfo`, `SystemVersion`, `EventMessage`, `IDResponse`, `Volume`, `VolumeCreateRequest`, `NetworkSummary`, `NetworkInspect`, `NetworkConnectRequest`, `NetworkDisconnectRequest`, `Plugin`, `PluginPrivilege`, `Node`, `NodeSpec`, `Swarm`, `SwarmSpec`, `Service`, `ServiceSpec`, `Task`, `Secret`, `SecretSpec`, `Config`, `ConfigSpec`, and `DistributionInspect`.

## Control Flow and Protocol Behavior

The OpenAPI file does not implement daemon control flow, but it documents expected request-response flow and several long-lived transports:

- Container lifecycle flow is represented as create -> inspect/start/stop/restart/kill/update/rename/pause/unpause/wait/delete, with `id` path parameters accepting container ID or name. `ContainerStart` returns `204` on success and `304` when already started; `ContainerStop` returns `304` when already stopped; `ContainerKill` returns `409` when the target is not running.
- Container attach and exec start can hijack or stream the HTTP connection. `ContainerAttach` documents raw stream vs multiplexed stream behavior, the eight-byte multiplex header layout, upgrade responses (`101`) vs plain `200`, and TTY mode behavior where stdout/stderr are not framed separately. `ExecStart` uses the same raw/multiplexed media types.
- Logs endpoints (`ContainerLogs`, `ServiceLogs`, `TaskLogs`) return binary stream payloads and rely on query switches (`follow`, `stdout`, `stderr`, `since`, `timestamps`, `tail`, and service/task `details`). They are constrained by configured log drivers.
- Archive flow has `HEAD /containers/{id}/archive` for stat metadata via `X-Docker-Container-Path-Stat`, `GET` for tar export, and `PUT` for extracting tar content into a container path.
- Image workflows include pull/import via `ImageCreate`, build via `ImageBuild`, tag/push/delete/prune, save/load tar streams, history/inspect, and commit-from-container. Build and push operations are explicitly cancellable when the client connection closes.
- Swarm update-style operations (`NodeUpdate`, `SwarmUpdate`, `ServiceUpdate`, `SecretUpdate`, `ConfigUpdate`, `VolumeUpdate`) require object `version` query parameters to avoid conflicting writes. Service update also supports registry auth source selection and server-side rollback.
- Swarm initialization/joining models the cluster bootstrap path with manager/listen/advertise/data-path addresses, default address pools, join tokens, and optional forced new cluster creation.
- `SystemEvents` is a streaming endpoint with time bounds and filters across object types. It produces JSON lines, ndjson, or JSON sequence formats.
- `Session` is a deprecated HTTP hijack into h2c transport for client callback capabilities, primarily relevant to advanced build/session integrations.

## State and Persistence Behavior

The chunk documents persistent daemon state transitions rather than implementing storage:

- Containers are persistent objects created from `ContainerConfig`, `HostConfig`, and `NetworkingConfig`; state changes are exposed through lifecycle endpoints and inspected through `ContainerInspect`.
- Container filesystem deltas and archive endpoints expose the writable layer and mounted filesystem view. `ContainerDelete` optionally removes anonymous volumes, and `ContainerPrune` deletes stopped containers with filter support.
- Images and manifests live in the image/content store. Multi-platform behavior appears repeatedly through `platform`, `platforms`, `manifests`, and `identity` parameters. Image delete can remove selected platform content; save/load can filter platform variants.
- Build cache is persistent daemon state exposed through `BuildPrune` with disk-goal parameters (`reserved-space`, `max-used-space`, `min-free-space`) and cache filters.
- Volumes are persistent storage objects, with local and Swarm cluster volume semantics. `VolumeUpdate` is restricted to Swarm cluster volumes and currently only allows changing `Availability`; `version` is required.
- Networks are persistent daemon or Swarm-scoped objects; create supports driver selection, IPAM, attachability, ingress, config-only/config-from behavior, labels, options, and IPv4/IPv6 toggles.
- Plugins are installed, enabled/disabled, configured, upgraded, pushed, or removed as daemon-managed extension state. Pull/upgrade accept privilege lists and registry auth.
- Swarm objects are Raft/versioned state: nodes, services, tasks, secrets, configs, and cluster spec all expose versioned update patterns and return `503` when the daemon is not in an appropriate Swarm state.
- Secrets and configs expose create/inspect/delete/update, but update descriptions restrict mutable fields to labels while data and other spec fields must remain unchanged.

## Dependencies and Integration Points

The API surface depends on several external or cross-component contracts:

- OCI image descriptors, OCI platforms, and OCI image layout are used by image manifest summaries and image save/load/export behavior.
- Registry authentication is passed through `X-Registry-Auth` or `X-Registry-Config`, both base64/base64url-encoded JSON auth objects. These headers integrate image and plugin pull/push/build workflows with registries.
- BuildKit is exposed through the `ImageBuild` `version=2` option and `outputs` BuildKit output configuration, while `version=1` retains the classic builder. `/_ping` advertises the daemon's recommended builder via `Builder-Version`.
- Linux/container runtime primitives are visible through cgroups (`ContainerStats`, pause/freezer behavior), POSIX signals (`ContainerKill`, stop/restart signal parameters), TTY resizing, process listing through `ps`, and tar archive extraction.
- Logging driver capabilities constrain `ContainerLogs`, `ServiceLogs`, and `TaskLogs`; client code must not assume logs are available for every configured driver.
- Swarm integration spans nodes, services, tasks, secrets, configs, overlay networks, join tokens, manager unlock keys, routing mesh ingress networks, and versioned object updates.
- CSI concepts are integrated through `ClusterVolumeSpec`, `Topology`, capacity ranges, access modes, publishing status, and storage plugin-returned metadata.
- The deprecated `/session` endpoint integrates with gRPC-over-h2c callback sessions and should be treated as compatibility surface rather than preferred new behavior.

## Risks and Edge Cases

- Streaming and hijacked endpoints are easy for clients, proxies, and generated SDKs to mishandle. `ContainerAttach`, `ContainerAttachWebsocket`, `ExecStart`, `ContainerLogs`, `ServiceLogs`, `TaskLogs`, `SystemEvents`, and `Session` need tests beyond ordinary JSON request/response handling.
- Multiplexed stream framing changes when TTY is enabled. Clients must branch on container/exec TTY settings and media type instead of always trying to parse Docker's eight-byte frame header.
- Many filters are JSON-encoded `map[string][]string` query parameters. Incorrect URL encoding or type handling can silently change behavior for list/prune/event APIs.
- Multi-platform image parameters are inconsistent by transport shape: some are strings containing JSON-encoded platforms, while save/load/delete use arrays or repeated query values. Swagger 2.0 limitations are explicitly called out for query arrays that cannot `$ref` `OCIPlatform`.
- `ImageCreate` changes behavior depending on whether `fromImage`, `fromSrc`, `tag`, and digest inputs are present. Pull-by-digest ignores `tag`, while a missing tag/digest can pull all tags.
- Several destructive operations have force flags (`ContainerDelete`, `VolumeDelete`, `PluginDelete`, `PluginDisable`, `NodeDelete`, `SwarmLeave`, `ImageDelete`) that can break running workloads, remove references, or disrupt cluster membership.
- Versioned update APIs must be guarded by a fresh inspect/list read. Stale `version` values should produce conflict or bad-parameter behavior, and callers must preserve immutable fields for secrets/configs/cluster volumes.
- Swarm-only endpoints frequently return `503` if the node is not part of a swarm or is already in an incompatible swarm state. Tests should cover standalone daemon behavior, manager behavior, and worker behavior separately.
- `ContainerStats` documents cgroup v1/v2 differences and compatibility fallbacks for CPU counts. Consumers that compute Docker CLI-like percentages need separate cases for cgroup version and missing fields.
- The `ClusterVolumeSpec.AccessMode.MountVolume` section appears with unusual indentation in this chunk. Because this file is a generated/maintained API spec, validation should catch whether the YAML parser treats `MountVolume`, `BlockVolume`, and nested `properties` as intended.
- Examples include complex maps and generated IDs; schema-driven tests should validate examples because examples are often copied into docs, SDK samples, and client fixtures.

## Test Signals

Useful validation signals for this chunk include:

- Parse `v1.54.yaml` as Swagger/OpenAPI 2.0 and validate that every `$ref` used in this chunk resolves to a definition.
- Check uniqueness and stability of `operationId` values listed above, because generated clients and documentation anchors rely on them.
- Verify that required path parameters (`id`, `name`) are marked `required: true` and match their containing path templates.
- Exercise query parameter encoding for JSON filters, repeated array values, boolean defaults, and JSON-encoded OCI platform selectors.
- Contract-test success and documented error responses for representative operations in each tag group: Container, Image, System, Exec, Volume, Network, Plugin, Node, Swarm, Service, Task, Secret, Config, Distribution, and Session.
- Include streaming tests for raw stream, multiplexed stream, websocket attach, event streams, and HTTP connection hijack/upgrade behavior.
- Include state-transition tests around lifecycle idempotence (`304` already started/stopped), conflicts (`409` running container remove, stopped container kill, service name conflict), and Swarm `503` mode errors.
- Validate destructive prune/delete endpoints against filter handling and `SpaceReclaimed`/deleted-ID response schemas.
- Validate versioned update APIs with both current and stale versions, and confirm immutable-field restrictions for secrets, configs, and cluster volumes.
