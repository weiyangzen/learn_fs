# sources/cloud-native/moby/api/docs/v1.55.yaml lines 7938-13998

## Scope

This chunk covers the transition from late schema definitions into the main Docker Engine API v1.55 Swagger path table. It starts with cluster-volume/CSI and image-manifest schema fragments, then defines HTTP operations for containers, images/builds, system endpoints, exec sessions, volumes, networks, plugins, swarm nodes and cluster management, services, tasks, secrets, configs, registry distribution inspection, and the deprecated interactive session endpoint.

The file is declarative OpenAPI/Swagger YAML rather than executable code. Its purpose is to define the wire contract used by API documentation, generated clients, compatibility validation, and daemon route/schema tests. Behavior described here must align with daemon implementations elsewhere in Moby.

## Local Schema Definitions

The opening lines complete cluster volume status/spec definitions:

- Cluster volume status includes plugin return data such as `VolumeContext`, CSI `VolumeID`, `AccessibleTopology`, and per-node `PublishStatus`.
- `PublishStatus` records Swarm node ID, publish state, and CSI `PublishContext`. Its state machine includes `pending-publish`, `published`, `pending-node-unpublish`, and `pending-controller-unpublish`.
- `ClusterVolumeSpec` contains volume `Group`, `AccessMode`, `Secrets`, `AccessibilityRequirements`, `CapacityRange`, and `Availability`.
- `AccessMode` controls scheduling and attachment semantics through `Scope` (`single` or `multi`), `Sharing` (`none`, `readonly`, `onewriter`, `all`), mount-vs-block options, CSI secret mappings, topology requirements, and capacity bounds.
- `Topology` is a map of CSI topology segments.

This chunk also defines image attestation and manifest-summary structures:

- `AttestationStatement` includes an OCI descriptor, an in-toto predicate type URI, and optional verbatim statement JSON gated by the `statement=true` query parameter.
- `ImageManifestSummary` describes an image manifest by ID/digest, `OCIDescriptor`, local availability, size accounting, kind (`image`, `attestation`, or `unknown`), optional image data, and optional attestation data.
- Image manifest image data includes platform, identity, container users of the image, and unpacked size. Attestation data identifies the image manifest digest it applies to.

These schemas are shared by later volume and image endpoints. They are also integration-sensitive because CSI topology/status and OCI attestation metadata are surfaced directly to clients.

## Container Operations

The container path table covers the main container lifecycle:

- `ContainerList` (`GET /containers/json`) returns `ContainerSummary` arrays and supports `all`, `limit`, `size`, and JSON-encoded filters for ancestor, before/since, ports, exit code, health, id, isolation, task status, labels, name, network, status, and volume.
- `ContainerCreate` (`POST /containers/create`) accepts `ContainerConfig` plus `HostConfig` and `NetworkingConfig`, with optional name and platform query parameters. The platform text documents local-image lookup behavior and warning generation when a cached image platform mismatches the host.
- `ContainerInspect`, `ContainerTop`, `ContainerLogs`, `ContainerChanges`, `ContainerExport`, and `ContainerStats` provide inspection, process listing, log streaming, filesystem diff, tar export, and resource usage stats.
- `ContainerResize`, `ContainerStart`, `ContainerStop`, `ContainerRestart`, `ContainerKill`, `ContainerUpdate`, `ContainerRename`, `ContainerPause`, and `ContainerUnpause` mutate runtime or metadata state.
- `ContainerAttach` and `ContainerAttachWebsocket` attach to stdio over hijacked HTTP or websocket transports. The spec defines raw vs multiplexed stream framing and TTY behavior.
- `ContainerWait` blocks until `not-running`, `next-exit`, or `removed`.
- `ContainerDelete` removes containers with optional anonymous volume removal, force kill, or legacy link removal.
- `ContainerArchiveInfo`, `ContainerArchive`, and `PutContainerArchive` stat, download, or upload tar archives against a container filesystem.
- `ContainerPrune` deletes stopped containers with `until` and label filters.

Important response codes distinguish normal lifecycle no-ops from errors: start/stop can return 304, kill can return 409 when not running, delete can return 409 for running containers, and many operations return 404 for unknown IDs or names. Streaming/log endpoints use raw or multiplexed binary content rather than ordinary JSON.

## Image and Build Operations

Image APIs cover inventory, build, registry transfer, content archival, attestations, and cleanup:

- `ImageList` (`GET /images/json`) returns `ImageSummary` and supports `all`, JSON filters, `shared-size`, `digests`, `manifests`, and `identity`. The `identity` flag requires manifest summaries.
- `ImageBuild` (`POST /build`) consumes a build-context tar stream and exposes classic and BuildKit controls: Dockerfile path, tags, remote context, quiet/no-cache/cache-from/pull flags, intermediate cleanup, resource controls, build args, shm size, squash, labels, build network mode, content type, registry config, platform, target, BuildKit output JSON, and builder `version` (`1` classic or `2` BuildKit).
- `BuildPrune` deletes build cache with `reserved-space`, `max-used-space`, `min-free-space`, `all`, and detailed filters.
- `ImageCreate` pulls or imports images, using `fromImage`, `fromSrc`, `repo`, `tag`, import body, registry auth, Dockerfile-style `changes`, and platform selection.
- `ImageInspect`, `ImageHistory`, `ImagePush`, `ImageTag`, `ImageDelete`, `ImageSearch`, and `ImagePrune` provide standard image lifecycle operations.
- `ImageAttestations` returns in-toto statements for an image/platform, optionally filtered by predicate type and optionally including full statement JSON. It can return 501 when the backend cannot preserve OCI image indexes.
- `ImageCommit` creates a new image from a container with repo/tag/comment/author, pause behavior, change instructions, and optional container config override.
- `ImageGet`, `ImageGetAll`, and `ImageLoad` save/load image tarballs and document the OCI image layout plus backwards-compatible Docker save metadata.

Platform handling is a repeated integration point. Inspect, history, push, delete, save, and load support platform selection in different query shapes, often as JSON-encoded OCI platform strings. Client generators need to preserve array serialization (`collectionFormat: multi`) where declared.

## System APIs

System endpoints in this chunk are:

- `SystemAuth` validates registry credentials and may return an identity token.
- `SystemInfo` returns daemon/system information.
- `SystemVersion` returns Docker version and system version metadata.
- `SystemPing` and `SystemPingHead` provide lightweight daemon reachability checks. Response headers include `Api-Version`, `Builder-Version`, `Docker-Experimental`, `Swarm`, and cache-control headers.
- `SystemEvents` streams events as JSONL/NDJSON/JSON sequence and supports `since`, `until`, and JSON filters across container, image, volume, network, daemon, plugin, node, service, secret, config, and builder objects.
- `SystemDataUsage` (`GET /system/df`) returns image/container/volume/build-cache usage and supports repeated `type` filters plus `verbose`.

The system event stream is state-observability glue across the whole daemon. It must remain consistent with event names emitted by container, image, volume, network, swarm, and builder implementations.

## Exec APIs

Exec is a two-phase API:

- `ContainerExec` creates an exec instance inside a running container and accepts stdio attach flags, console size, detach keys, TTY, environment, command, privileged flag, user, and working directory.
- `ExecStart` starts the created exec instance and either detaches or returns an interactive raw/multiplexed stream.
- `ExecResize` adjusts TTY dimensions with required `h` and `w`.
- `ExecInspect` returns running state, exit code, process config, open stream flags, container ID, and host PID.

State is transient but important: create allocates an exec ID, start changes runtime state and may hijack the connection, inspect observes completion, and resize is meaningful only for TTY-backed sessions. Expected failures include 404 for missing exec IDs and 409 for stopped or paused containers.

## Volume Operations

Volume endpoints include `VolumeList`, `VolumeCreate`, `VolumeInspect`, `VolumeUpdate`, `VolumeDelete`, and `VolumePrune`.

`VolumeList` supports JSON filters for dangling state, driver, label, and name. `VolumeCreate` returns a `Volume` from `VolumeCreateRequest`. `VolumeUpdate` is restricted to Swarm cluster volumes, wraps `ClusterVolumeSpec` as `Spec`, requires a `version` query parameter for optimistic concurrency, and currently permits only `Availability` to change. `VolumeDelete` can force removal but still advertises conflict behavior for in-use volumes. `VolumePrune` supports label filters and an `all=true` filter to include all local volumes rather than only anonymous volumes.

These endpoints mutate durable volume metadata and may delegate work to local volume drivers or CSI-backed cluster volume plugins. CSI fields from the opening schema fragment are therefore not merely descriptive; they are part of volume scheduling, publish/unpublish, and plugin reconciliation state.

## Network Operations

Network endpoints include:

- `NetworkList` with filters for dangling, driver, id, label, name, scope, and built-in/custom type.
- `NetworkInspect` with `verbose` and `scope`.
- `NetworkDelete`, including 403 for predefined networks.
- `NetworkCreate`, whose request contains name, driver, scope, internal/attachable/ingress/config-only flags, `ConfigFrom`, `IPAM`, `EnableIPv4`, `EnableIPv6`, driver options, and labels.
- `NetworkConnect` and `NetworkDisconnect` for container endpoint membership.
- `NetworkPrune` with `until` and label filters.

Integration points are libnetwork drivers, swarm overlay networking, IPAM configuration, predefined network protection, and endpoint settings shared with container creation. The `EnableIPv4`/`EnableIPv6` fields make address-family configuration part of the API contract.

## Plugin Operations

Plugin APIs include `PluginList`, `GetPluginPrivileges`, `PluginPull`, `PluginInspect`, `PluginDelete`, `PluginEnable`, `PluginDisable`, `PluginUpgrade`, `PluginCreate`, `PluginPush`, and `PluginSet`.

Plugin pull and upgrade accept registry auth and a body of `PluginPrivilege` grants. Plugin create consumes a tar archive containing plugin rootfs and manifest. Enable/disable/delete expose force or timeout controls, while set accepts string settings such as `DEBUG=1`.

Security risk is high relative to ordinary metadata APIs because plugin privileges can grant host network, mounts, and devices. Tests and clients need to preserve auth headers and privilege-body shape exactly, and server-side implementation must keep force-disable/delete semantics clear when plugins are in active use.

## Swarm Nodes and Cluster

Swarm node endpoints include `NodeList`, `NodeInspect`, `NodeDelete`, and `NodeUpdate`. Node list filters include id, engine label, membership, name, node label, and role. Node updates require the current version number to avoid conflicting writes.

Cluster-level endpoints include:

- `SwarmInspect`.
- `SwarmInit`, with listen/advertise/data-path addresses, data path port, default address pools, subnet size, force-new-cluster, and `SwarmSpec`.
- `SwarmJoin`, requiring `ListenAddr`, `RemoteAddrs`, and `JoinToken`.
- `SwarmLeave`, with a force option for risky departures.
- `SwarmUpdate`, requiring a versioned `SwarmSpec` and optional worker token, manager token, and manager unlock-key rotation.
- `SwarmUnlockkey` and `SwarmUnlock` for manager autolock workflows.

Most swarm APIs return 503 when the daemon is not in the required swarm state. Mutations persist into cluster/Raft state and affect membership, networking defaults, tokens, manager lock state, and scheduling behavior.

## Services and Tasks

Service endpoints include `ServiceList`, `ServiceCreate`, `ServiceInspect`, `ServiceDelete`, `ServiceUpdate`, and `ServiceLogs`.

Service create/update bodies are `ServiceSpec` values. Examples exercise container image, mounts, hosts, user, DNS, secrets, OOM score, log driver, resources, restart policy, placement, replicated mode, update/rollback config, endpoint ports, and labels. Create accepts `X-Registry-Auth`. Update requires the current service version, can source registry auth from `spec` or `previous-spec`, supports `rollback=previous`, and also accepts `X-Registry-Auth`.

Task endpoints include `TaskList`, `TaskInspect`, and `TaskLogs`. Task list filters include desired state, id, label, name, node, and service. Examples expose scheduler-created state such as service ID, slot, node ID, status, desired state, container status, and network attachments.

Services are desired-state resources, while tasks are scheduler materializations of those specs. Logs for services and tasks mirror container log flags (`details`, `follow`, `stdout`, `stderr`, `since`, `timestamps`, `tail`) and are documented as available only with supported logging drivers such as `local`, `json-file`, or `journald`.

## Secrets and Configs

Secrets and configs have parallel swarm-scoped APIs:

- Secrets: `SecretList`, `SecretCreate`, `SecretInspect`, `SecretDelete`, `SecretUpdate`.
- Configs: `ConfigList`, `ConfigCreate`, `ConfigInspect`, `ConfigDelete`, `ConfigUpdate`.

List operations support JSON filters by id, label, name, and names. Create operations return `IDResponse` and can conflict on duplicate names. Inspect returns the corresponding `Secret` or `Config`. Delete returns 204 on success. Update requires a `version` query parameter and is explicitly limited to label updates; all other fields must match the inspected object.

Persistent state is swarm cluster state. Secret data examples are base64 encoded, and generated code/logging should avoid accidentally exposing secret payloads. Update tests should verify immutable fields are rejected or ignored according to daemon behavior.

## Distribution and Session

`DistributionInspect` (`GET /distribution/{name}/json`) contacts a registry to return digest and platform information. It can return 401 for authentication failure or missing images and depends on registry naming/auth behavior rather than only local daemon state.

`Session` (`POST /session`) initializes an interactive h2c session by hijacking the HTTP connection. It is marked deprecated in favor of gRPC directly on the listening socket. Successful upgrade returns 101 and uses `application/vnd.docker.raw-stream`; errors use `ErrorResponse`.

## Shared Dependencies

This chunk relies heavily on definitions elsewhere in the same YAML file. Important referenced schemas include:

- Error and simple response wrappers: `ErrorResponse`, `IDResponse`, `AuthResponse`.
- Container/runtime types: `ContainerSummary`, `ContainerConfig`, `HostConfig`, `NetworkingConfig`, `ContainerInspectResponse`, `ContainerTopResponse`, `FilesystemChange`, `ContainerStatsResponse`, `ContainerUpdateResponse`, `ContainerWaitResponse`, `Resources`, `RestartPolicy`, `ProcessConfig`.
- Image/build/distribution types: `ImageSummary`, `ImageInspect`, `ImageHistoryResponseItem`, `ImageDeleteResponseItem`, `ImagesDiskUsage`, `BuildCacheDiskUsage`, `DistributionInspect`, `OCIDescriptor`, `OCIPlatform`, `Identity`.
- Storage/network types: `Volume`, `VolumeListResponse`, `VolumeCreateRequest`, `ClusterVolumeSpec`, `Topology`, `NetworkSummary`, `NetworkInspect`, `NetworkCreateResponse`, `NetworkConnectRequest`, `NetworkDisconnectRequest`, `IPAM`, `ConfigReference`.
- Plugin and swarm types: `Plugin`, `PluginPrivilege`, `Node`, `NodeSpec`, `Swarm`, `SwarmSpec`, `Service`, `ServiceSpec`, `ServiceCreateResponse`, `ServiceUpdateResponse`, `Task`, `Secret`, `SecretSpec`, `Config`, `ConfigSpec`.

Broken `$ref` names or incompatible schema changes here would affect documentation and generated clients across many endpoint families.

## Control Flow Patterns

Recurring API patterns visible in this chunk:

- Synchronous CRUD/lifecycle operations return 200, 201, 204, or `ErrorResponse`.
- Long-lived reads and bidirectional operations use raw streams, multiplexed streams, websockets, HTTP hijacking, or h2c upgrade rather than JSON responses.
- Many list/prune endpoints accept JSON-encoded `map[string][]string` filters in query strings.
- Import/export/build operations use tar or binary bodies.
- Registry operations use `X-Registry-Auth` or `X-Registry-Config` headers.
- Swarm object updates require version query parameters for optimistic concurrency.
- Swarm-only resources consistently expose 503 for non-swarm daemons.
- Platform selection appears as plain strings, JSON-encoded strings, and repeated arrays depending on the endpoint.

Generated clients need special handling for query JSON, repeated query arrays, binary request/response bodies, connection upgrade semantics, and status codes that represent non-error lifecycle outcomes.

## State and Persistence Behavior

The chunk describes operations that mutate multiple persistent or semi-persistent stores:

- Container metadata/runtime state: create, start/stop/restart/kill, update, rename, pause/unpause, archive extraction, delete, exec allocation.
- Image/content/build-cache state: build, pull/import, commit, tag, delete, prune, save/load, attestation reads.
- Volume and cluster-volume state: create, update availability, publish/unpublish status, delete, prune.
- Network state: create, connect/disconnect endpoints, delete, prune.
- Plugin installation/configuration state: pull, create, enable/disable, upgrade, set, push, delete.
- Swarm cluster/Raft state: nodes, swarm init/join/leave/update/unlock, services, tasks, secrets, configs, join tokens, manager unlock keys.
- Registry-observed state: distribution inspect, image push/pull/plugin pull.

The chunk also exposes transient state streams: logs, stats, events, attach/exec streams, wait conditions, service/task logs, and sessions. Tests should separate durable mutations from streaming observers.

## Risks and Compatibility Notes

- Streaming/hijack endpoints are fragile for proxies, generated clients, and HTTP libraries that assume request/response JSON.
- Several endpoint parameters are JSON-encoded strings in query positions, which is easy to serialize incorrectly.
- The same concept, especially platform selection, uses different Swagger shapes across endpoints.
- Optimistic concurrency depends on clients sending current `version` values for swarm resources; stale updates should not silently overwrite cluster state.
- Plugin privilege grants and registry auth headers are sensitive and must not be logged or transformed unsafely.
- Secret data is represented as base64 payloads and should not leak through examples, debug output, or generated client tracing.
- CSI cluster volume fields connect Docker scheduling to external storage-plugin state; inconsistent publish/status handling can strand volumes.
- Attestation support depends on an OCI-index-preserving image backend, so the 501 response is part of the compatibility contract.
- Prune/delete endpoints reclaim disk and remove state; filters such as `until`, `label`, `all`, and storage-budget parameters need strict parsing.
- YAML indentation and Swagger 2.0 limitations are visible in comments and query array workarounds, so schema validation should be part of change review.

## Test Signals

Useful validation for this chunk includes:

- Swagger/OpenAPI validation for all paths, methods, operation IDs, `$ref` targets, response schemas, content types, and query parameter shapes.
- Generated-client tests for JSON-encoded filters, repeated query arrays, required path/body/query parameters, auth headers, and binary tar streams.
- Container lifecycle tests for platform warning behavior, 304 start/stop cases, 409 kill/delete conflicts, archive put/get/stat behavior, stats formulas, and attach/log multiplexed framing.
- Image tests for build backend selection, BuildKit outputs, build-cache pruning storage bounds, pull/import platform behavior, manifest summary/identity inclusion, attestations with and without statement bodies, and platform-specific save/load/delete/push.
- System tests for ping headers, event stream filtering, and `system/df` type filtering.
- Exec tests for create/start/inspect/resize sequencing, TTY vs non-TTY streams, paused/stopped container errors, and exit-code observation.
- Volume/network tests for filter handling, cluster volume versioned updates, CSI topology/status fields, in-use delete conflicts, IPv4/IPv6 network creation, predefined network protection, and swarm overlay restrictions.
- Plugin tests for privilege negotiation, registry auth propagation, force disable/delete semantics, tar-based create, and settings update.
- Swarm tests for non-swarm 503 responses, init/join/leave state transitions, versioned node/swarm/service/secret/config updates, token rotation, unlock flows, service rollback, task filtering, and supported log drivers.
- Security-focused tests for registry auth, plugin privileges, secret payload handling, and session/attach connection upgrade boundaries.
