# sources/cloud-native/moby/api/docs/v1.30.yaml lines 1-7610

## Scope And Purpose

This chunk is the first 7,610 lines of the Docker Engine API v1.30 Swagger/OpenAPI 2.0 specification. The file is not runtime code, but it is a source-of-truth contract used to generate Engine API documentation and client/server API types. It declares global protocol metadata for API version `/v1.30`, common request/response content types, ReDoc tag organization, schema definitions, and the beginning of the `paths` table.

The in-scope path surface covers container, image, system, exec, volume, network, plugin, node, and early swarm APIs through the beginning of `POST /swarm/join`. Later endpoints in the same source file, including the rest of swarm operations and service/task/secret/config/distribution paths, start after this chunk and are intentionally not summarized here except where their shared definitions are present in lines 1-7610.

## API Contract Structure

The spec declares `swagger: "2.0"`, `http`/`https` schemes, JSON and plain-text global produces/consumes, and `basePath: "/v1.30"`. The `info` block describes Docker Engine as an HTTP API used by the Docker CLI, explains standard JSON error bodies of the form `{ "message": "..." }`, and documents version negotiation expectations. The versioning text is important for client compatibility: clients should prefix requests with `/v1.30`, should tolerate extra response properties, and should expect the daemon to ignore unknown query/body fields.

The top-level tags define ReDoc navigation and API grouping: `Container`, `Image`, `Network`, `Volume`, `Exec`, swarm-related `Swarm`, `Node`, `Service`, `Task`, `Secret`, and system-related `Plugin` and `System`. In this chunk, path operations use all of these except the later service/task/secret/config path groups, while the corresponding schema definitions are already present.

## Important Schemas And Types

Container configuration is split between portable container settings and host-specific settings. `ContainerConfig` describes image/runtime command data such as `Hostname`, `User`, attach flags, `Env`, `Cmd`, `Healthcheck`, `Image`, `Volumes`, `Entrypoint`, labels, stop signal/timeout, and shell. `HostConfig` composes `Resources` and host integration options including bind mounts, logging driver, network mode, port bindings, restart policy, auto-remove, volumes-from, named `Mounts`, Linux capabilities/namespaces/security options/sysctls/runtime, and Windows console/isolation settings. `Resources` centralizes cgroup and platform resource controls: CPU shares/quota/period/realtime, cpusets, block IO throttling, memory/swap/swappiness/OOM/PIDs, device mappings, ulimits, and Windows CPU/IO limits.

Storage and mount schemas include `MountType`, `MountPoint`, `Mount`, `DeviceMapping`, `ThrottleDevice`, and `Volume`. `Mount` models create-time bind/tmpfs/volume mounts with typed option subdocuments; `MountPoint` models inspect/list output for mounts already attached to a container. `Volume` represents persistent host-managed storage, with driver, mountpoint, labels, scope, driver options, optional low-level status, and optional `UsageData` used by `GET /system/df`.

Image schemas include `Image`, `ImageSummary`, `ImageHistoryResponseItem`, `ImageDeleteResponseItem`, `BuildInfo`, `CreateImageInfo`, and `PushImageInfo`. The full `Image` response records identifiers, tags/digests, parent, created time, Docker version, architecture/OS, size/virtual size, `GraphDriverData`, rootfs layers, and the image's `ContainerConfig`/`Config`. `ImageSummary` is the smaller list/df representation with required repo tags/digests, size fields, labels, and container reference count.

Networking schemas include `Network`, `IPAM`, `NetworkContainer`, `EndpointSettings`, and `NetworkConfig`. They capture local and swarm-scoped network identity, driver, scope, IPv6, internal/attachable/ingress flags, IPAM driver/config/options, labels/options, connected container endpoints, and per-container endpoint overrides such as static IPv4/IPv6 addresses, aliases, links, gateways, and MAC addresses.

Exec and process schemas include `ProcessConfig`, plus inline schemas on `POST /containers/{id}/exec`, `POST /exec/{id}/start`, and `GET /exec/{id}/json`. Exec creation captures stream attachment, detach keys, TTY, environment, command, privilege, and user. Exec inspect reports run state, exit code, attached stream flags, container ID, PID, and process configuration.

Plugin schemas include `Plugin`, `PluginMount`, `PluginDevice`, `PluginEnv`, and `PluginInterfaceType`. They model installed plugin state (`Enabled`, `Name`, `Id`, remote reference), mutable settings, declared privileges/devices/mounts/env, plugin interface socket/types, rootfs layers, entrypoint/workdir/user, network mode, Linux capabilities/devices, propagated mount, and host namespace requirements.

Swarm object schemas are defined before all of their paths. `ObjectVersion` provides optimistic concurrency via an `Index` supplied on updates. `NodeSpec` and `Node` define node identity, role, availability, engine/platform/resources/plugins, status, manager status, and TLS info. `SwarmSpec` covers cluster name/labels, orchestration task-history retention, Raft snapshot/election/heartbeat settings, dispatcher heartbeat, CA configuration and external CAs, manager encryption-at-rest autolock, and task default log driver. `ClusterInfo` is the `/info` and `/swarm` cluster representation without join tokens. `TaskSpec`, `TaskState`, `Task`, `ServiceSpec`, `EndpointPortConfig`, `EndpointSpec`, `Service`, `ServiceUpdateResponse`, `SecretSpec`, `Secret`, `ConfigSpec`, and `Config` are present for swarm workloads even though most related paths are after this chunk.

Common responses are `ErrorResponse` and `IdResponse`. The spec consistently uses `ErrorResponse` for 4xx/5xx errors and `IdResponse` for object creation APIs that return only an ID.

## In-Scope Path Surface

Container APIs include `ContainerList`, `ContainerCreate`, `ContainerInspect`, process listing, logs, filesystem changes/export/archive copy, live stats, TTY resize, lifecycle transitions (`start`, `stop`, `restart`, `kill`, `pause`, `unpause`), update/rename/delete, attach over raw hijacked HTTP or websocket, wait, and prune. The create body combines `ContainerConfig`, `HostConfig`, and `NetworkingConfig`. Several endpoints use special transports: logs and attach can upgrade/hijack the connection, archive endpoints exchange tar streams, export returns an octet-stream tarball, and stats can stream resource samples.

Image APIs include list, build, create/pull/import, inspect, history, push, tag, delete, search, prune, commit, export single or multiple images, and load. Build accepts a tar build context with many query controls for Dockerfile path, tags, cache, remote contexts, resource limits, build args, squash, labels, network mode, and registry auth. Registry-interacting calls use `X-Registry-Auth` or `X-Registry-Config` base64 JSON headers. Export/load endpoints use `application/x-tar` and document the legacy image tarball layout.

System APIs include `SystemAuth`, `SystemInfo`, `SystemVersion`, `SystemPing`, `SystemEvents`, and `SystemDataUsage`. These expose registry credential validation/token acquisition, daemon capability and environment inventory, API/server version metadata, a lightweight health/ping endpoint with version and experimental headers, event streaming across Docker object types, and disk usage by layers/images/containers/volumes.

Volume APIs include list, create, inspect, delete, and prune. Filtering is encoded as JSON string maps in query parameters. Create passes driver-specific options directly to the selected volume driver, while delete supports a `force` query flag but may still return conflict when a volume is in use.

Network APIs include list, inspect, delete, create, connect, disconnect, and prune. Create accepts driver, duplicate checking, internal/attachable/ingress flags, IPAM, IPv6, options, and labels. Connect/disconnect bind containers to networks with optional endpoint configuration, and explicitly reject unsupported operations on swarm-scoped networks.

Plugin APIs include list, privilege discovery, pull/install, inspect, delete, enable, disable, upgrade, create from tar, push, and set configuration. Pull and upgrade require the user-accepted privileges body and may use registry auth. Enable/disable/delete all have in-use or missing-plugin failure modes; forced disable/delete can disrupt containers using the plugin.

Node and early swarm APIs include node list/inspect/delete/update, swarm inspect, swarm init, and the start of swarm join. Node update requires a `version` query parameter to enforce `ObjectVersion` optimistic concurrency. Swarm inspect returns `ClusterInfo` plus worker/manager join tokens. Swarm init accepts listen/advertise/data-path addresses, `ForceNewCluster`, and a `SwarmSpec`; swarm join begins with listen/advertise/data-path address fields but this chunk ends before the join schema is complete.

## Control Flow And Protocol Behavior

The contract models Docker CLI workflows as multiple HTTP calls. Running a container is not a single operation: a client creates a container, may attach/log or configure networking/volumes, starts it, optionally waits, inspects state, streams stats/logs, then stops/removes it. Exec similarly has a two-phase flow: create an exec instance inside a running container, then start it, with resize and inspect as side operations.

Long-running and streaming operations are a major control-flow concern. Attach uses HTTP connection hijacking or websocket upgrade, with raw bidirectional I/O after headers. When TTY is disabled, stdout/stderr are multiplexed into 8-byte framed messages; when TTY is enabled, the stream is raw PTY data. Logs can return a plain body or a `101` upgraded stream when `follow` is true. Events and stats are streaming JSON flows, while build, pull, push, create image, load, and plugin pull/upgrade can produce progress/error objects over time rather than a single detailed schema.

State-changing operations generally communicate success with `201`, `204`, or `200`, and use HTTP status distinctions for idempotency or conflict: container start/stop use `304` for already-started/stopped, deletes can return `409` for conflicts, and swarm/node APIs return `503` when the daemon is not in the required swarm state.

Filters are repeatedly represented as JSON-encoded query strings with `map[string][]string` semantics. This pattern appears on container/image/volume/network/plugin/node/event/prune listing APIs and is an integration hotspot for clients because the OpenAPI type is only `string`, while the semantic value is structured JSON.

## State And Persistence Behavior

The API exposes several daemon persistence domains. Containers persist config, host config, runtime state, logs, graph driver data, filesystem diffs, mounts, network attachments, restart counts, and names until removed. Container archive and changes APIs operate on the writable container filesystem, and commit can persist that filesystem/config as a new image.

Images persist local content-addressed rootfs layers, repository tags/digests, history, graph-driver metadata, and config. Build and import/create/load mutate the local image store; push/search/auth integrate with remote registries. Delete/prune operations can reclaim local layer storage but are constrained by descendants, tags, containers, and build usage.

Volumes persist outside container lifecycles unless explicitly pruned or removed. `Mount` documentation emphasizes named volumes are not removed when a container is removed; `Volume.UsageData` is only populated for data-usage reporting and may be unavailable for non-local drivers.

Networks persist driver/IPAM configuration and endpoint attachments. Built-in networks have special protection; swarm-scoped networks restrict direct connect/disconnect operations. Endpoint settings link container state to network state and can include static addressing.

Plugins persist installed package metadata, accepted privileges, enabled/running state, rootfs and settings. Plugin operations can affect daemon capabilities because volume/network/log drivers are plugin extension points.

Swarm state is versioned and cluster-replicated. `ObjectVersion` and required update-version query parameters guard concurrent writes to nodes and other swarm objects. `SwarmSpec` documents Raft snapshots, elections, dispatcher heartbeat, CA material, join tokens, manager autolock, and task defaults, all of which are persisted in swarm manager state.

## Dependencies And Integration Points

The spec depends on Swagger/OpenAPI 2.0 tooling, ReDoc rendering conventions, and Docker's code-generation pipeline for API documentation and Go types. Vendor extensions such as `x-go-name` and `x-nullable` are generation hints, so edits to schemas can affect generated Go names, pointer/nullability behavior, and documentation rendering.

Docker Engine subsystems represented here include container runtime execution, cgroups/resource controls, graph/storage drivers, logging drivers, registry authentication and distribution, build, volume drivers, network drivers/IPAM, plugin management, event publishing, and swarmkit orchestration. The spec also encodes platform-specific contracts for Linux namespaces/cgroups/SELinux/AppArmor and Windows isolation, CPU controls, credential specs, and registry credential storage.

External integrations include registries via `X-Registry-Auth` and `X-Registry-Config`, Docker Hub search, plugin registries, volume/network/log plugin drivers, external swarm certificate authorities using the `cfssl` protocol, and clients/proxies that must handle connection upgrades and raw stream framing.

## Risks And Edge Cases

Because this OpenAPI document feeds generated clients/types and documentation, schema mistakes can become compatibility defects. Notable risks in this chunk include loose `type: "object"` response schemas for complex streams/stats, semantically structured filters declared only as strings, and inline schemas that may drift from Go implementation structs.

Streaming and hijacked endpoints are hard for generic OpenAPI clients. Attach/logs/exec start require raw socket handling, optional `101` upgrades, TTY-dependent framing, and big-endian frame-size parsing. Clients generated from this spec may need hand-written transport overrides for these operations.

The API intentionally uses an open schema model. Clients must ignore unknown response fields and servers ignore unknown input fields. Strict decoders, generated clients that reject additional properties, or tests that assert exact JSON can break against newer daemons.

State-mutating prune/delete operations have broad blast radius. Container/image/volume/network prune accept label/until/dangling filters encoded as JSON strings; incorrect filter encoding can remove more objects than intended. Forced container, image, volume, node, plugin, and network operations can disrupt running workloads or dependent resources.

Swarm update semantics rely on object versions. Missing or stale `version` values should be tested because stale writes must fail rather than silently overwrite newer state. Swarm init/join address fields also affect both manager control traffic and VXLAN data traffic, so incorrect defaults can produce partially functional clusters.

Some fields are platform-specific or driver-specific. Linux-only pause behavior uses the cgroups freezer; container top is unsupported on Windows; Windows credential specs, isolation, and CPU controls have mutual-exclusion rules; volume usage data is unavailable for some drivers; plugin privilege and network operations vary by plugin/driver scope.

## Test Signals

Validation should include OpenAPI parsing of lines 1-7610 in the context of the full YAML, ensuring all `$ref` targets in this chunk resolve and generated types still compile. Because this chunk ends mid-operation, chunk-level textual review should not expect standalone YAML validity from lines 1-7610 alone.

Contract tests should cover representative JSON success and error bodies for major resource groups, especially required fields marked with `x-nullable: false`, enums such as restart policies, mount types, task states, endpoint modes, node roles/availability, and platform isolation values.

Transport tests should exercise attach, logs-follow, exec start, stats, events, archive, export/load, build, pull/push, and plugin pull/upgrade using real HTTP clients that can handle raw streams, tar bodies, binary formats, and connection upgrades.

Compatibility tests should verify clients tolerate extra response fields and ignored unknown input fields, encode filter query parameters as JSON map-of-list strings, and handle documented status codes such as `304`, `409`, and swarm `503`.

Stateful integration tests should cover create/start/wait/logs/remove container flows, image build/tag/push/delete/prune flows, volume/network lifecycle and pruning, plugin privilege/enable/disable behavior, node update with stale and current versions, and swarm init/inspect/join error cases.
