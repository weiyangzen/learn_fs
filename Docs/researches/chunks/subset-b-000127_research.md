# sources/cloud-native/moby/api/docs/v1.39.yaml lines 1-7774

## Scope And Purpose

This chunk is the first 7,774 lines of the Docker Engine API v1.39 Swagger/OpenAPI 2.0 specification. It is not executable daemon code, but it is an authoritative API contract used for generated Engine API documentation and client/server API types. The chunk declares global protocol metadata for `/v1.39`, documentation tags, schema definitions for major Docker resources, and the beginning of the `paths` table.

The in-scope path surface starts at `GET /containers/json` and continues through `POST /build/prune`. It covers container lifecycle, filesystem, stream, and prune endpoints, plus image listing, image build, and build-cache pruning. Later image, system, exec, volume, network, plugin, and swarm endpoints begin after line 7774 and are intentionally not summarized as in-scope operations here, although many of their shared schemas are already defined in this chunk.

## API Contract Structure

The document declares Swagger 2.0, `http` and `https` schemes, global JSON and text content types, and `basePath: "/v1.39"`. The `info` block identifies the Engine API as the HTTP API used by the Docker CLI, documents standard JSON error responses with a `message` field, and explains versioned URL prefixes. Clients are expected to call `/v1.39/...` to lock this API version, tolerate extra response properties, and understand that servers ignore unknown query and request-body fields.

The top-level tags define ReDoc grouping and operation ownership: primary objects (`Container`, `Image`, `Network`, `Volume`, `Exec`), swarm objects (`Swarm`, `Node`, `Service`, `Task`, `Secret`, `Config`), and system objects (`Plugin`, `System`). This chunk defines schemas for all of these groups, but only container and early image/build paths are within lines 1-7774.

Vendor extensions are part of the contract. `x-go-name` influences generated Go type names, and `x-nullable` controls nullability/pointer behavior in generated models. Edits to this file can therefore affect documentation, generated client shapes, and server-side type bindings even though the file itself is YAML.

## Important Schemas And Types

Container creation and inspection are split across portable container config, host-dependent runtime config, runtime state, and networking. `ContainerConfig` contains image/runtime fields such as hostname, user, attach flags, environment, command, healthcheck, image reference, volumes, working directory, entrypoint, labels, stop signal/timeout, and shell. `HostConfig` composes `Resources` with bind mounts, logging, network mode, port bindings, restart policy, volume inheritance, named `Mounts`, Linux namespace/security settings, runtime selection, masked/read-only paths, and Windows console/isolation options. `ContainerState` records lifecycle status, booleans such as running/paused/restarting/dead, PID, exit code, timestamps, OOM status, and optional health data.

Resource and storage schemas include `Resources`, `RestartPolicy`, `MountType`, `MountPoint`, `Mount`, `DeviceMapping`, `ThrottleDevice`, `PortMap`, `PortBinding`, and `GraphDriverData`. `Resources` centralizes cgroup and platform controls such as CPU shares/quota/period/realtime, cpusets, memory/swap/swappiness/OOM/PIDs, block IO throttles, devices, ulimits, and Windows CPU/IO limits. `Mount` is the create-time mount declaration for bind, npipe, tmpfs, and named volume mounts, while `MountPoint` is the inspect/list reporting shape for mounts already attached to a container.

Image schemas include `ImageInspect`, `ImageConfig`, `ImageSummary`, `ImageHistoryResponseItem`, `ImageDeleteResponseItem`, `BuildInfo`, `BuildCache`, `CreateImageInfo`, `PushImageInfo`, `ImageID`, `ErrorDetail`, and `ProgressDetail`. v1.39 uses an `ImageInspect` definition for the full local image cache record, including repo tags/digests, parent/comment/created metadata, architecture/OS/variant, size/virtual size, rootfs layers, graph-driver data, and local-only metadata such as `LastTagTime`. `ImageSummary` is the smaller image-list representation, with required ID, tags/digests, size fields, labels, and container reference count. `BuildCache` models BuildKit/classic builder cache records with ID, parent, type, description, in-use/shared flags, size, timestamps, and usage count.

Networking schemas are present even before most network endpoints. `NetworkingConfig`, `NetworkSettings`, `Network`, `IPAM`, `NetworkContainer`, `EndpointSettings`, `EndpointIPAMConfig`, `Address`, and `NetworkAttachmentConfig` describe per-container endpoint settings, static IPAM overrides, deprecated default bridge fields, connected network maps, driver/IPAM metadata, and service-level network attachments. These schemas are used directly by container create and inspect in this chunk.

Plugin schemas include `Plugin`, `PluginMount`, `PluginDevice`, `PluginEnv`, and `PluginInterfaceType`. They model installed plugin identity, enabled state, mutable settings, declared mounts/devices/env, interface socket/types, rootfs layers, entrypoint/workdir/user, network mode, Linux capabilities/devices, propagated mount, and host namespace requirements. Plugin paths are outside this chunk, but the definitions are available for later operations.

Swarm schemas are extensively defined before their path operations. `ObjectVersion` provides optimistic concurrency through an `Index`. `NodeSpec`, `Node`, `NodeDescription`, `NodeStatus`, `ManagerStatus`, `SwarmSpec`, `ClusterInfo`, `JoinTokens`, `Swarm`, `TaskSpec`, `TaskState`, `Task`, `ServiceSpec`, `EndpointSpec`, `EndpointPortConfig`, `Service`, `SecretSpec`, `Secret`, `ConfigSpec`, and `Config` model swarm cluster state, node status, task placement, service updates/rollbacks, secrets/configs, and endpoint publication. In this chunk they mostly serve as shared definitions for later path sections.

System schemas include `SystemVersion`, `SystemInfo`, `PluginsInfo`, `RegistryServiceConfig`, `IndexInfo`, `Runtime`, `Commit`, `SwarmInfo`, `LocalNodeState`, and `PeerNode`. These expose daemon version metadata, persistent Docker root location, host capabilities, configured runtimes, registry/insecure-registry settings, plugin inventory, proxy settings, live-restore state, security options, and swarm manager/node information.

Common responses include `ErrorResponse`, `IdResponse`, `ContainerWaitResponse`, and `ContainerWaitExitError`. `ErrorResponse` is the repeated 4xx/5xx shape; `ContainerWaitResponse` is the blocking wait result with an exit status and optional wait error.

## In-Scope Path Surface

Container list and create operations are `ContainerList` and `ContainerCreate`. Listing supports `all`, `limit`, `size`, and JSON-encoded `filters` over status, ancestor, labels, network, volume, ports, health, and related fields. Creation accepts a body combining `ContainerConfig`, `HostConfig`, and `NetworkingConfig`, plus an optional query `name`, and returns a created container ID with warnings. Creation failure modes include bad parameters, missing image, conflicts, and server errors.

Container inspection and observation operations include `ContainerInspect`, `ContainerTop`, `ContainerLogs`, `ContainerChanges`, `ContainerExport`, and `ContainerStats`. Inspect returns detailed state, config, host config, graph-driver data, mounts, and network settings. Top delegates to a Unix `ps`-style process listing and is documented as unsupported on Windows. Logs can return a body or a hijacked stream, depending on `follow`, and are limited to supported log drivers. Changes report filesystem diff kinds for modified, added, and deleted paths. Export returns an octet-stream tarball of the container filesystem. Stats streams or returns one JSON object with CPU, memory, network, pids, and block IO data plus documented CLI percentage formulas.

Container lifecycle operations include `ContainerResize`, `ContainerStart`, `ContainerStop`, `ContainerRestart`, `ContainerKill`, `ContainerUpdate`, `ContainerRename`, `ContainerPause`, and `ContainerUnpause`. They expose TTY resizing, start/stop/restart timing, signal delivery, live resource/restart-policy updates, renaming, and cgroup-freezer pause semantics. Status codes distinguish idempotent or invalid state: start and stop can return `304`, kill can return `409` if the container is not running, rename can conflict on name reuse, and missing containers consistently return `404`.

Container streaming and blocking operations include `ContainerAttach`, `ContainerAttachWebsocket`, and `ContainerWait`. Attach uses raw hijacked HTTP or optional upgrade responses for bidirectional stdin/stdout/stderr. When TTY is disabled, the stream is multiplexed with 8-byte headers containing stream type and big-endian frame size; when TTY is enabled, the stream is raw PTY data. Websocket attach exposes similar stream/log controls. Wait blocks until a condition is met: `not-running`, `next-exit`, or `removed`, and returns the container exit status.

Container deletion and archive operations include `ContainerDelete`, `ContainerArchiveInfo`, `ContainerArchive`, `PutContainerArchive`, and `ContainerPrune`. Delete supports removing anonymous volumes, force-killing running containers, and removing links. Archive `HEAD` returns a base64-encoded `X-Docker-Container-Path-Stat` JSON header, `GET` returns an `application/x-tar` archive, and `PUT` extracts a tar stream into a container directory with overwrite and UID/GID mapping controls. Prune deletes stopped containers and accepts JSON-encoded label and `until` filters, returning deleted IDs and reclaimed bytes.

The image/build operations in scope are `ImageList`, `ImageBuild`, and `BuildPrune`. Image list returns `ImageSummary` records and supports `all`, `digests`, and JSON-encoded filters for dangling, label, reference, before, and since. Image build accepts a compressed tar context or remote context, Dockerfile path, tags, build cache hints, resource limits, build args, labels, network mode, platform, target, registry auth config, and a builder backend version where `1` is classic and `2` is BuildKit. Build prune deletes build cache, supports `keep-storage`, `all`, and JSON-encoded filters over age, id, parent, type, description, in-use/shared/private, and returns deleted cache IDs plus reclaimed space.

## Control Flow And Protocol Behavior

The contract models Docker CLI workflows as multiple HTTP calls rather than single high-level transactions. A typical container run flow creates a container, may attach streams or inspect configuration, starts it, optionally resizes TTY or streams stats/logs, waits for exit, then archives/export/removes/prunes it. The create/start/wait/delete sequence is therefore the core state-machine path exposed by this chunk.

Streaming and binary transport are first-class concerns. Attach and log-follow require connection hijacking or upgrade-aware clients; archive/export/build exchange tar or octet-stream bodies; stats may be an unbounded stream; build responses are progress-oriented rather than a single stable JSON object. Generic OpenAPI clients generally need custom transport code for these operations.

Filters are repeatedly represented as query strings whose semantic content is JSON `map[string][]string`. This appears on container list/prune, image list, and build prune within this chunk. The OpenAPI type is only `string`, so clients must URI-encode structured JSON and tests must validate both encoding and daemon interpretation.

The spec relies on HTTP status codes to expose state transitions and conflicts. `201` indicates successful creation, `204` successful no-body state changes, `200` successful data returns or archive extraction, `304` already-started/already-stopped, `400` invalid parameters, `403` read-only extraction denial, `404` missing resources, `409` conflicts, and `500` daemon errors.

## State And Persistence Behavior

Containers persist config, host config, restart policy, runtime state, names, logs, writable filesystem changes, graph-driver metadata, network attachments, mounts, healthcheck state, and restart counts until removed. Archive and changes endpoints expose the mutable container filesystem; export serializes container contents; update mutates resource and restart settings without recreating the container.

Images persist content-addressed configuration and rootfs layers, tags, digests, size metadata, graph-driver data, local metadata, and image config defaults used by future containers. Image list is a summary view over this local image store. Build mutates the image store and may also create or reuse build cache records; build prune mutates the cache store and can reclaim disk space.

Build cache state is explicitly represented in v1.39 through `BuildCache` and `BuildPrune`. Cache entries can have parent relationships, type categories, in-use/shared/private state, timestamps, sizes, and usage counts. Pruning cache records is stateful and potentially destructive, especially when `all` is set or filters are too broad.

Volumes and networks are represented in definitions because container create/inspect can bind mounts and endpoints even though the standalone volume/network paths are later. Mount documentation emphasizes named volumes outlive container removal unless separately removed. Network settings persist endpoint and address data that links container state to network driver/IPAM state.

Swarm schemas define persisted cluster state with versioned writes, join tokens, CA material, Raft settings, task history, services, tasks, secrets, configs, and node metadata. Those state domains are not modified by in-scope paths, but the definitions show the broader persistence model this file serves.

## Dependencies And Integration Points

This file depends on Swagger/OpenAPI 2.0 tooling, ReDoc rendering conventions, and Docker's API generation pipeline. Markdown in descriptions, examples, `$ref` structure, `x-go-name`, and `x-nullable` all affect generated documentation and types.

Docker Engine subsystems represented by this chunk include container runtime execution, cgroups and resource controls, filesystem/archive handling, graph/storage drivers, logging drivers, healthchecks, networking/IPAM, image storage, registry authentication configuration for builds, and classic/BuildKit builder backends. Platform-specific contracts cover Linux cgroups, capabilities, namespaces, SELinux/AppArmor, mount propagation, and Windows isolation, credential specs, console size, and CPU/IO controls.

External integration points include clients and proxies that must support HTTP hijacking/upgrades, Docker registries through the `X-Registry-Config` header during builds, remote Git/HTTP build contexts, OCI runtimes through daemon configuration, logging drivers, volume drivers, network drivers, and insecure/mirrored registry settings surfaced in system definitions.

## Risks And Edge Cases

Because this OpenAPI document feeds generated clients and documentation, schema drift can cause broad compatibility defects. Risks include inline response schemas drifting from Go implementation structs, loose `type: "object"` schemas for stats/build streams, and semantically structured query filters represented only as strings.

Streaming endpoints are hard for generic generated clients. Attach/log-follow need raw socket handling, optional `101` upgrades, TTY-dependent framing, and big-endian frame-size parsing. Build and stats can be long-running streams, and build cancellation is tied to the client connection being dropped.

Prune and delete operations have high blast radius. Container prune and build prune accept JSON string filters; incorrect filter encoding or missing labels can remove more state than intended. `ContainerDelete` with `force` can kill running workloads, and archive `PUT` can mutate container filesystems, fail on read-only volumes/rootfs, or hit directory/non-directory replacement rules.

Platform and driver variation is substantial. `ContainerTop` is unsupported on Windows, pause relies on Linux freezer cgroups, several resource controls are Linux-only or Windows-only, volume/network/logging behavior depends on configured drivers, and system definitions include fields documented as deprecated, unstable, omitted when empty, or informational only.

The API's open schema model means strict clients are fragile. Clients must ignore extra response fields and should not depend on exact object shapes for driver-specific maps, system status tuples, graph-driver metadata, registry config, or future daemon-added properties.

## Test Signals

Validation should parse the full YAML with OpenAPI 2.0 tooling and ensure all `$ref` targets used in lines 1-7774 resolve. Because this is a chunk of a larger file and ends just before the next path, standalone parsing of only the extracted lines is not the right test signal.

Generated-code tests should verify Go/client model changes around `x-go-name`, `x-nullable`, required fields, enums, `allOf` composition, and inline schemas for container create, inspect, wait, update, prune, image list, build, and build prune.

Protocol tests should exercise container create/inspect/start/stop/restart/kill/update/rename/pause/unpause/wait/delete, plus logs-follow, attach, websocket attach, stats stream and one-shot mode, archive `HEAD`/`GET`/`PUT`, export, image list filters, image build inputs, and build-cache pruning.

Compatibility tests should assert JSON filter query encoding as `map[string][]string`, status-code handling for `304`, `403`, `404`, and `409`, tolerance of unknown response fields, and correct interpretation of documented container states, wait conditions, mount types, restart policies, task states, endpoint modes, and platform isolation values.

Stateful tests should cover destructive boundaries: deleting a running container with and without `force`, pruning containers with `until` and label filters, archive upload into read-only and non-directory targets, build cancellation on client disconnect, BuildKit versus classic builder selection, and build prune behavior with `keep-storage`, `all`, and in-use/shared/private filters.
