# sources/cloud-native/moby/api/docs/v1.28.yaml lines 1-7787

## Scope And Purpose

This chunk is the first oversized-file research slice for Docker Engine API `v1.28`. It covers the Swagger 2.0 document header, API version metadata, documentation tags, all schema definitions, and the path table from container operations through the beginning of `GET /services/{id}/logs`. The source file is consumed by the Moby API documentation and type-generation pipeline, so its contracts are not just prose: operation IDs, schema names, `x-go-name`, `x-nullable`, response shapes, parameter locations, and media types feed generated client/server types and rendered ReDoc documentation.

The document declares `basePath: "/v1.28"` for Docker Engine 17.04-era API compatibility. Its top-level description defines the versioned URL contract, the open-schema compatibility model, standard error response body, and registry authentication convention using `X-Registry-Auth` as base64-encoded JSON. The tag list groups endpoints into the public API menu and code-generation domains: `Container`, `Image`, `Network`, `Volume`, `Exec`, `Swarm`, `Node`, `Service`, `Task`, `Secret`, `Plugin`, and `System`.

This chunk ends at line 7787 in the middle of the `ServiceLogs` path parameters. The rest of `ServiceLogs`, all task and secret paths, and any trailing global sections are in the next chunk and must be reconciled there before a whole-file report is synthesized.

## Important Schemas

The `definitions` block provides the shared data model for container lifecycle, images, volumes, networks, plugins, swarm objects, services, tasks, and secrets.

Container-facing schemas split portable container config from host-dependent runtime config. `Config` covers image, command, entrypoint, environment, labels, healthcheck, stop behavior, shell, exposed ports, stdin/stdout/stderr attachment, TTY, working directory, user, and image build/runtime metadata. `HostConfig` composes `Resources` and adds host mounts, port bindings, networking mode, restart policy, auto-removal, log driver, capabilities, DNS, extra hosts, IPC/PID/UTS/user namespace settings, read-only rootfs, privileged mode, sysctls, runtime, storage options, tmpfs, Windows console and isolation fields. `Mount`, `MountPoint`, `MountType`, `DeviceMapping`, `ThrottleDevice`, `RestartPolicy`, and `HealthConfig` describe lower-level host filesystem, device, cgroup, and health behavior used both by containers and swarm service tasks.

Resource schemas are broad and platform-sensitive. `Resources` includes Unix cgroup controls such as CPU shares/quota/period/realtime, cpuset, memory and swap limits, swappiness, OOM behavior, pids limit, block IO weights/rates, device rules, ulimits, disk quota, and cgroup parent, plus Windows-only CPU and IO controls. This makes API compatibility fragile because some fields are legal only on selected platforms or daemon configurations, while the schema exposes them in a single object.

Image schemas include `ImageHistoryResponseItem`, `Image`, `ImageSummary`, `GraphDriverData`, `ImageDeleteResponseItem`, and streaming progress models `BuildInfo`, `CreateImageInfo`, `PushImageInfo`, `ErrorDetail`, and `ProgressDetail`. `Image` is the full inspect form with rootfs layers, graph driver data, repo tags/digests, container config, architecture, OS, size, and virtual size. `ImageSummary` is the smaller list form with required non-null fields for IDs, tags, digests, sizes, labels, and container counts.

Volume and networking schemas include `Volume`, `Network`, `IPAM`, `NetworkContainer`, and `EndpointSettings`. Volumes expose driver, mountpoint, labels, scope, options, status, and optional local-driver usage data. Networks expose scope, driver, IPv6, internal/attachable flags, IPAM, containers, options, and labels; endpoints carry IPAM overrides, aliases, links, network/endpoint IDs, gateways, IP prefixes, IPv6 data, and MAC address.

Plugin schemas include `Plugin`, `PluginMount`, `PluginDevice`, `PluginEnv`, and `PluginInterfaceType`. They model both installed plugin state and plugin config: enabled state, mutable settings, registry reference, interface socket/types, entrypoint, workdir, user, network mode, Linux capabilities/devices, propagated mount, rootfs diff IDs, arguments, environment, mounts, and devices. Several plugin subtypes use `required` and `x-nullable: false`, which affects generated Go pointer/non-pointer decisions.

Swarm schemas include `ObjectVersion`, `NodeSpec`, `Node`, `SwarmSpec`, `ClusterInfo`, `TaskSpec`, `TaskState`, `Task`, `ServiceSpec`, `EndpointPortConfig`, `EndpointSpec`, `Service`, `ServiceUpdateResponse`, `SecretSpec`, and `Secret`. `ObjectVersion.Index` is the central optimistic concurrency token for updates. `SwarmSpec` carries raft, dispatcher, CA, encryption, orchestration, and task default settings. `TaskSpec` embeds container specs, resources, restart policy, placement, networks, log driver, force-update counter, DNS, hosts, and secret references. `ServiceSpec` adds replicated/global mode, update and rollback policies, service networks, and endpoint ports. `Service` adds update status and runtime endpoint state.

One schema risk is visible in this chunk: `Secret.Spec` references `#/definitions/ServiceSpec` rather than `SecretSpec`. Given the adjacent `SecretSpec` definition and the secret endpoint family in the next chunk, this looks inconsistent and can mislead generated clients or documentation unless downstream tooling patches it or a later version corrects it.

## Covered API Operations

The covered path operations are:

- Container: `ContainerList`, `ContainerCreate`, `ContainerInspect`, `ContainerTop`, `ContainerLogs`, `ContainerChanges`, `ContainerExport`, `ContainerStats`, `ContainerResize`, `ContainerStart`, `ContainerStop`, `ContainerRestart`, `ContainerKill`, `ContainerUpdate`, `ContainerRename`, `ContainerPause`, `ContainerUnpause`, `ContainerAttach`, `ContainerAttachWebsocket`, `ContainerWait`, `ContainerDelete`, `ContainerArchiveInfo`, `ContainerArchive`, `PutContainerArchive`, and `ContainerPrune`.
- Image: `ImageList`, `ImageBuild`, `ImageCreate`, `ImageInspect`, `ImageHistory`, `ImagePush`, `ImageTag`, `ImageDelete`, `ImageSearch`, `ImagePrune`, `ImageCommit`, `ImageGet`, `ImageGetAll`, and `ImageLoad`.
- System: `SystemAuth`, `SystemInfo`, `SystemVersion`, `SystemPing`, `SystemEvents`, and `SystemDataUsage`.
- Exec: `ContainerExec`, `ExecStart`, `ExecResize`, and `ExecInspect`.
- Volume: `VolumeList`, `VolumeCreate`, `VolumeInspect`, `VolumeDelete`, and `VolumePrune`.
- Network: `NetworkList`, `NetworkInspect`, `NetworkDelete`, `NetworkCreate`, `NetworkConnect`, `NetworkDisconnect`, and `NetworkPrune`.
- Plugin: `PluginList`, `GetPluginPrivileges`, `PluginPull`, `PluginInspect`, `PluginDelete`, `PluginEnable`, `PluginDisable`, `PluginUpgrade`, `PluginCreate`, `PluginPush`, and `PluginSet`.
- Swarm and node: `NodeList`, `NodeInspect`, `NodeDelete`, `NodeUpdate`, `SwarmInspect`, `SwarmInit`, `SwarmJoin`, `SwarmLeave`, `SwarmUpdate`, `SwarmUnlockkey`, and `SwarmUnlock`.
- Service: `ServiceList`, `ServiceCreate`, `ServiceInspect`, `ServiceDelete`, `ServiceUpdate`, and the start of `ServiceLogs`.

Common patterns are consistent across the API. Object identifiers are usually path parameters named `id` or `name` and accept either IDs or human-readable names where the daemon supports both. Filters are passed as JSON-encoded `map[string][]string` query strings. Mutating operations generally consume JSON request bodies and return `200`, `201`, or `204`, while missing resources return `404`, conflicts return `409`, swarm-unavailable endpoints return `503`, and server failures return the shared `ErrorResponse`.

## Container Control Flow

Container creation is a multi-stage contract. `POST /containers/create` accepts a body that composes `Config`, `HostConfig`, and `NetworkingConfig`, plus an optional `name` query parameter. The response returns a new `Id` and non-null `Warnings`. Starting is a separate `POST /containers/{id}/start`; stop, restart, kill, pause, unpause, rename, update, wait, delete, archive, export, logs, stats, attach, and exec operations all target an existing container.

Container inspection returns a broad low-level object including process state, paths for resolv.conf/hostname/hosts/logs, restart count, driver, labels, apparmor profile, exec IDs, host config, graph driver, sizes, mounts, portable config, and network settings. List responses use the smaller `ContainerSummary` array with optional filesystem size fields activated by the `size` query flag.

Streaming and hijacked-connection endpoints are a major control-flow special case. `ContainerAttach` can return either `101` upgrade or `200` without upgrade and then uses a raw bidirectional stream. If TTY is disabled, stdout/stderr are multiplexed with an eight-byte frame header; if TTY is enabled, the stream is raw PTY data. `ContainerLogs` also supports `101` streaming when `follow=true` and uses the attach stream format. `ContainerAttachWebsocket` exposes a websocket variant. `ContainerStats` streams repeated JSON objects unless `stream=false`.

Filesystem transfer has three related endpoints under `/containers/{id}/archive`. `HEAD` returns file metadata in the `X-Docker-Container-Path-Stat` header as base64-encoded JSON. `GET` returns an `application/x-tar` archive for a path. `PUT` extracts a tar stream into a container path and can reject directory/non-directory overwrites via `noOverwriteDirNonDir`; it can also return `403` for read-only rootfs or volume targets.

Container deletion and pruning mutate persisted daemon state. `DELETE /containers/{id}` can remove anonymous volumes with `v=true`, forcibly kill a running container with `force=true`, or remove a legacy link. `POST /containers/prune` deletes stopped containers filtered by `until` and returns deleted IDs plus reclaimed bytes.

## Image, Build, Registry, And Tar Control Flow

Image operations cover local image store, registry IO, build, import/export, tagging, deletion, and prune. `GET /images/json` lists `ImageSummary` entries with optional digest information and filters for reference, label, dangling, before, and since. `GET /images/{name}/json` returns full `Image` inspect data, while `GET /images/{name}/history` returns image layer history.

`POST /build` builds an image from a tar archive or remote context. It exposes Dockerfile path, tags, extra hosts, remote URI, quiet/no-cache/cache-from, pull, intermediate-container cleanup, resource limits, build args, shm size, experimental squash, labels, network mode, and registry auth header. The build stream is documented as JSON progress and is cancelled when the client connection drops. A schema issue is visible here: `buildargs` is described as a JSON map of string pairs but typed as `integer`, which is likely a documentation or generator bug.

`POST /images/create` pulls or imports images based on query parameters such as `fromImage`, `fromSrc`, `repo`, and `tag`, with optional body image data and `X-Registry-Auth`. `POST /images/{name}/push` pushes tags or all tags for a local image and requires registry auth. `POST /images/{name}/tag` creates or overwrites a repository/tag reference. `DELETE /images/{name}` removes tags and image layers when not blocked by descendants, running containers, or builds, returning `ImageDeleteResponseItem` entries. `POST /images/prune` removes unused images and returns deleted entries plus reclaimed bytes.

Image archive endpoints use Docker's legacy image tarball format. `GET /images/{name}/get` exports one image/repository as `application/x-tar`; `GET /images/get` exports multiple names; `POST /images/load` imports a tar archive and can suppress progress. The documentation explicitly describes layer directories, `VERSION`, `json`, `layer.tar`, whiteout files, and repository metadata.

`POST /commit` creates a new image from a container, optionally pausing the container first and applying Dockerfile-style changes. This bridges mutable container filesystem state back into immutable image state.

## System, Exec, Volume, Network, Plugin, And Swarm Flow

System endpoints expose daemon-level capability and event streams. `POST /auth` validates registry credentials and may return an identity token. `GET /info` returns operational state such as counts, architecture, root dir, storage driver/status, plugin lists, proxy settings, daemon ID, registry config, kernel/OS data, resource capability booleans, event listener counts, server version, system time, and security options in examples. `GET /version` returns version/build metadata and API version bounds. `GET /_ping` returns `OK` and headers for max API version and experimental mode. `GET /events` streams daemon events with filters over object type, action, labels, names, IDs, and time bounds. `GET /system/df` returns layer size, images, containers, and volumes for data usage.

Exec is a two-step flow. `POST /containers/{id}/exec` creates an exec instance against a running container and accepts attach flags, detach keys, TTY, environment, command, privileged flag, and user. `POST /exec/{id}/start` starts it, either detached or attached through a raw stream. `POST /exec/{id}/resize` resizes only TTY exec sessions. `GET /exec/{id}/json` reports running state, exit code, process config, stdio flags, container ID, and host PID.

Volume endpoints manage named persistent storage. Listing supports filters for dangling/in-use status, driver, label, and name. Creation accepts name, driver, driver options, and labels, returning a `Volume`. Inspect and delete operate by volume name or ID, with delete optionally forced and able to return conflict when in use. Prune deletes unused volumes and reports names plus reclaimed bytes.

Network endpoints manage local and custom networks. Listing and inspect return the `Network` schema; creation accepts name, duplicate-check hint, driver, internal and attachable flags, IPAM, IPv6, options, and labels. The schema notes `CheckDuplicate` is best-effort because networks are keyed by ID, not name. Connect and disconnect attach containers to networks with optional endpoint settings or force disconnect. Network prune deletes unused networks filtered by creation time.

Plugin endpoints manage the plugin lifecycle: list, privileges preview, pull/install with accepted privileges and registry auth, inspect, delete, enable with timeout, disable with force, upgrade with new remote and accepted privileges, create from tar, push, and set mutable config. Plugins integrate with registry auth, tar rootfs/manifest upload, and privileged host resources such as network, mounts, and devices.

Node and swarm endpoints are stateful and versioned. Node list/inspect/delete/update require swarm mode and return `503` if the node is not in a swarm. Updates require `version` query parameters to prevent conflicting writes. Swarm inspect exposes cluster info plus join tokens. Swarm init, join, leave, update, unlock key retrieval, and unlock handle cluster membership, raft/CA/config state, token rotation, auto-lock, and manager unlock state.

Service endpoints create and manage swarm services. List supports id, label, and name filters. Create accepts `ServiceSpec` and optional `X-Registry-Auth`, returning a service ID and optional image-pinning warning. Inspect/delete target service ID or name. Update requires a `version` query parameter and supports registry auth source selection plus rollback to previous spec. This chunk reaches the start of service log streaming, which mirrors container logs with raw stream and JSON media types but is incomplete here.

## State And Persistence Behavior

This Swagger file itself is declarative, but it encodes daemon state transitions that clients and generated handlers rely on.

Containers have lifecycle states controlled by create, start, stop, restart, kill, pause, unpause, wait, update, rename, delete, archive transfer, logs, stats, attach, exec, and prune. Container state persists in the daemon's container store and in filesystem layers, writable diffs, logs, attached volumes, network endpoints, exec instances, and events. Some operations are idempotent or state-sensitive: start can return `304` if already started; stop can return `304` if already stopped; delete can conflict if running unless forced; exec creation conflicts if the container is paused.

Images persist as tags, digests, layers, rootfs metadata, graph-driver data, and history. Pull, import, build, commit, tag, push, delete, prune, save, and load endpoints mutate or export that state. Deletion has dependency rules for descendants, containers, tags, and builds. Build state is affected by cache-from, no-cache, resource constraints, context source, registry credentials, and cancellation by client disconnect.

Volumes persist independently of containers unless anonymous volumes are removed during container deletion or pruning. Volume usage data tracks size and reference count where supported. Networks persist independently and own endpoint attachments, IPAM settings, and driver options; connect/disconnect mutates endpoint state.

Swarm state is distributed and versioned. Nodes, swarm spec, services, tasks, secrets, CA settings, raft settings, join tokens, unlock keys, service update status, and task history are cluster objects. Updates require `ObjectVersion.Index` values through query parameters so stale clients cannot overwrite newer object state. Several endpoints return `503` when swarm mode is unavailable, which clients need to treat differently from object-not-found errors.

Streams are persistent connections rather than simple request/response state: attach, logs, stats, build, image create/push/load progress, events, exec start, and service logs can keep sockets open and may stop server work when the client disconnects.

## Dependencies And Integration Points

The file depends on Swagger 2.0 semantics and Moby's OpenAPI generation conventions. `$ref` ties path schemas to shared definitions, `allOf` composes request bodies, `x-go-name` and `x-nullable` influence generated Go identifiers and pointer/nullability behavior, examples support generated docs, and `operationId` values map to client/server method names.

HTTP integration points include JSON request/response bodies, plain text responses, binary tar and octet-stream bodies, websocket attach, HTTP connection hijacking, upgrade responses, custom headers such as `X-Registry-Auth`, `X-Registry-Config`, `Content-type`, response headers such as `Api-Version`, `Docker-Experimental`, and `X-Docker-Container-Path-Stat`, plus query strings that often contain JSON-encoded filters.

Runtime integrations are broad: registry authentication and token flow, Docker Hub search, image pull/push, Dockerfile builds, storage drivers, graph drivers, Linux cgroups, Windows resource controls, log drivers, network drivers and IPAM, volume drivers, plugin registries and rootfs tar uploads, swarmkit raft/dispatcher/CA/task orchestration, event broadcasting, and daemon data-usage accounting.

The API also exposes compatibility boundaries. The top-level description says clients should ignore unknown response fields and servers ignore unknown query/body fields. That open-schema rule is central for clients talking to newer daemons while pinned to `/v1.28`.

## Risks And Edge Cases

Schema and documentation drift is the main risk. This chunk contains fields whose examples and schemas do not fully align, such as `Secret.Spec` pointing at `ServiceSpec`, `buildargs` typed as `integer` despite being a JSON map, and several broad object responses with weakly typed or placeholder `TODO` descriptions. Generated clients may either overconstrain valid daemon behavior or expose incorrect types if these details are consumed literally.

Streaming/hijack endpoints are easy to implement incorrectly. Attach, logs, exec start, service logs, build, events, stats, pull, push, and load do not behave like ordinary finite JSON responses. Clients must handle `101` and `200` stream variants, raw multiplexed frames, raw TTY mode, websocket transport, cancellation on connection close, and long-lived JSON event streams.

State-dependent status codes matter. `304` for already-started/stopped containers, `403` for read-only archive writes or ineligible service networks, `409` for container/image/volume/name conflicts, and `503` for missing swarm mode all encode actionable distinctions. Flattening all non-2xx responses into a generic error would lose behavior expected by Docker CLI compatibility.

Platform-specific fields are exposed in common schemas. Unix and Windows resource/isolation controls, Linux mount propagation, cgroup behavior, freezer pause semantics, log driver limitations, and swarm scoped network restrictions need platform-aware validation outside the schema.

Security-sensitive data passes through headers and specs. Registry credentials and identity tokens use base64 JSON rather than encryption. Swarm join tokens and unlock keys are returned or accepted by API calls. Plugins may request host network, mounts, and devices. Build args are explicitly not meant for secrets, but the API cannot prevent misuse. Clients and logs need to avoid accidentally persisting these values.

The covered `ServiceLogs` operation is incomplete in this chunk. The merge lane must combine this report with chunk 2 before treating service log parameters and the remaining task/secret APIs as fully researched.

## Test Signals

Strong validation signals for this file are generated documentation and generated Go/client types. A successful ReDoc render should group endpoints by the listed tags, resolve every `$ref`, display examples, and preserve the versioned `/v1.28` base path. Code generation should produce stable operation names from `operationId`, honor `x-go-name` and `x-nullable`, and fail fast on invalid schema references or incompatible type definitions.

Contract tests should exercise representative endpoint classes rather than only parsing the YAML. Container tests should cover create/start/inspect/logs/attach/stats/archive/delete/prune, including raw stream framing and TTY versus non-TTY behavior. Image tests should cover build progress, registry auth headers, pull/import/push, tag/delete/prune, save/load tar media types, and build cancellation on client disconnect. System tests should assert `/version`, `/_ping` headers, `/info`, `/events` streaming filters, and `/system/df`.

Swarm tests should check `503` when not in swarm mode, optimistic concurrency failures with stale `version` values, token rotation, init/join/leave, service create/update/delete, and registry auth handling for services. Volume and network tests should cover filter JSON parsing, in-use conflicts, prune output, connect/disconnect, duplicate-name best-effort behavior, and driver/plugin errors. Plugin tests should cover privilege discovery, pull/create/enable/disable/upgrade/set/push/delete, including registry auth and accepted privilege bodies.

Static validation should specifically flag unresolved references, duplicate operation IDs, schema/request example mismatches, non-JSON media types, binary body schemas, and partial-chunk continuity at `ServiceLogs`. The next chunk must complete `ServiceLogs` and add task/secret endpoint coverage before a final source-tree-aligned per-file research document is generated.
