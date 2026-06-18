# sources/cloud-native/moby/api/docs/v1.37.yaml lines 1-7561

## Scope And Purpose

This chunk is the first oversized-file segment of the Docker Engine API v1.37 Swagger 2.0 contract. It covers the document header, versioned API metadata, ReDoc tag ordering, every shared `definitions` entry, and path operations from container listing through the beginning of `GET /exec/{id}/json`. The source is not daemon runtime code; it is the declarative API contract used for generated API documentation and generated client/server types, as stated in the opening comments.

The file describes HTTP behavior under `basePath: "/v1.37"` for Docker Engine. Its introduction defines the public error body shape, API version-prefix behavior, open-schema compatibility rule, and registry authentication conventions. The path surface in this chunk spans containers, images, registry auth, system information, events, disk usage, image save/load, and exec instance creation/start/resize/inspection. Later paths for volumes, networks, plugins, nodes, swarm, services, tasks, secrets, configs, distribution, and sessions start after this chunk.

## Document Structure And Metadata

The document declares Swagger 2.0, `http` and `https` schemes, JSON and plain-text defaults for `produces` and `consumes`, and the v1.37 base path. The `info.description` is a client-facing compatibility contract: callers can pin a version by prefixing the URL, unversioned calls currently resolve to v1.37 but are deprecated, newer daemons should continue supporting this API version, clients must ignore unknown response properties, and servers ignore unknown input properties.

Tags are ordered for ReDoc navigation and also group generated operations. Primary object tags in this chunk are `Container`, `Image`, `Network`, `Volume`, and `Exec`; swarm tags include `Swarm`, `Node`, `Service`, `Task`, `Secret`, and `Config`; system-level tags include `Plugin` and `System`. Operation IDs follow the local singular-noun-plus-verb convention, for example `ContainerList`, `ImageBuild`, `SystemEvents`, and `ExecStart`.

Registry credentials are modeled as caller-supplied data rather than daemon sessions. Registry-touching endpoints use `X-Registry-Auth` or `X-Registry-Config` headers containing Base64-encoded JSON auth structures, while `/auth` can return an identity token that clients pass in place of a username/password payload.

## Shared Definitions And Type Model

The `definitions` block is the main generated-type input for this chunk. It uses Swagger `$ref`, `allOf`, maps through `additionalProperties`, arrays, enums, numeric formats, `x-go-name`, and `x-nullable` extensions. These extensions are important because generated Go-facing types need to preserve API naming, nullability, and composed structs that are not expressible in plain JSON Schema alone.

Container and host configuration definitions include `ContainerConfig`, `HostConfig`, `Resources`, `HealthConfig`, `RestartPolicy`, `Mount`, `MountPoint`, `MountType`, `DeviceMapping`, `ThrottleDevice`, `PortMap`, `PortBinding`, `NetworkSettings`, `EndpointSettings`, and `EndpointIPAMConfig`. `HostConfig` composes `Resources` with host-specific runtime settings: bind and named-volume mounts, log config, network mode, port bindings, restart behavior, auto-remove, namespace/security options, cgroup controls, tmpfs/sysctls, runtime choice, Windows console/isolation fields, and Unix-only capability, PID, IPC, UTS, userns, and SELinux/AppArmor-related options. `ContainerConfig` holds image/container portable settings such as command, entrypoint, environment, labels, exposed ports, healthcheck, stop signal, stop timeout, working directory, shell, and stdin/TTY attachment flags.

Image and registry definitions include `Image`, `ImageSummary`, `ImageHistoryResponseItem`, `GraphDriverData`, `BuildInfo`, `CreateImageInfo`, `PushImageInfo`, `ImageID`, `AuthConfig`, `ErrorDetail`, `ProgressDetail`, `ErrorResponse`, `IdResponse`, `RegistryServiceConfig`, `IndexInfo`, `Runtime`, and `Commit`. `Image` and `ImageSummary` distinguish full inspect records from list summaries. Registry definitions expose mirrors, insecure CIDRs, per-index secure/official status, and deprecated nondistributable-artifact allow lists.

Storage, network, and plugin definitions include `Volume`, `Network`, `IPAM`, `NetworkContainer`, `Plugin`, `PluginMount`, `PluginDevice`, `PluginEnv`, and `PluginInterfaceType`. Although most corresponding paths are outside this chunk, the schemas are present here for references from `/system/df`, container inspect/list data, and later chunks. Plugin schema is security-sensitive because it describes mount/device/env privileges, rootfs layers, Linux capabilities, host PID/IPC flags, plugin network mode, propagated mounts, and settable runtime settings.

Swarm orchestration definitions include `ObjectVersion`, `NodeSpec`, `Node`, `NodeDescription`, `Platform`, `EngineDescription`, `TLSInfo`, `NodeStatus`, `NodeState`, `ManagerStatus`, `Reachability`, `SwarmSpec`, `ClusterInfo`, `JoinTokens`, `Swarm`, `TaskSpec`, `TaskState`, `Task`, `ServiceSpec`, `EndpointPortConfig`, `EndpointSpec`, `Service`, `ServiceUpdateResponse`, `SecretSpec`, `Secret`, `ConfigSpec`, `Config`, `SystemInfo`, `PluginsInfo`, `SwarmInfo`, `LocalNodeState`, and `PeerNode`. `ObjectVersion` is a key concurrency primitive: update callers must send the current object version so conflicting writes can be rejected instead of silently overwriting each other.

`TaskSpec` and `ServiceSpec` model swarm scheduling in detail: plugin or container task payloads, command/env/user/group settings, Windows credential specs, SELinux context, mounts, secrets, configs, DNS configuration, isolation, resource limits/reservations including generic resources, restart policy, placement constraints/preferences/platforms, force-update counter, runtime, service networks, log driver, replicated/global mode, update strategy, rollback strategy, and endpoint publishing. `SwarmSpec` exposes Raft timing/snapshot settings, dispatcher heartbeat, CA and external CA configuration, encryption-at-rest manager autolock, and task default logging.

## Container Operations

The container path block defines list, create, inspect, process listing, logs, filesystem change reporting, export, stats, TTY resize, lifecycle mutation, attach, wait, delete, archive transfer, and pruning.

`GET /containers/json` (`ContainerList`) returns `ContainerSummary` arrays and accepts `all`, `limit`, `size`, and JSON-encoded filter maps for status, ancestor, label, health, network, volume, published/exposed ports, isolation, swarm task membership, and relative container selectors. The response intentionally uses a smaller representation than inspect.

`POST /containers/create` (`ContainerCreate`) accepts a body composed from `ContainerConfig` plus `HostConfig` and `NetworkingConfig.EndpointsConfig`. This is the primary bridge from portable image settings to host-specific resources, mounts, security, logging, namespace, and network endpoint configuration. It returns a created container ID plus warnings and documents distinct failures for bad input, missing image, name/config conflicts, and daemon errors.

`GET /containers/{id}/json` (`ContainerInspect`) returns low-level container state, paths under the daemon data root, log path, restart count, driver, labels, `HostConfig`, graph-driver data, optional size fields, mounts, original config, and network settings. The state object calls out an important semantic edge case: a paused Linux container can have both `Running` and `Paused` set, so clients should prefer the `Status` enum over boolean inference.

Runtime and lifecycle endpoints mutate daemon state: `ContainerStart`, `ContainerStop`, `ContainerRestart`, `ContainerKill`, `ContainerUpdate`, `ContainerRename`, `ContainerPause`, and `ContainerUnpause`. They mostly return `204` for successful mutation, `304` for already-started/stopped idempotence cases, `404` for missing containers, `409` for conflicts such as killing a non-running container or renaming to an existing name, and `500` for daemon failures. `ContainerUpdate` accepts a `Resources` body plus restart policy and can change cgroup/resource behavior without recreating the container.

Stream and filesystem operations require special clients. `ContainerLogs` can return either a string body or a `101` upgraded raw stream and only works for `json-file` or `journald` logging drivers. `ContainerStats` returns live JSON resource usage, with compatibility guidance for `online_cpus` fallback. `ContainerAttach` hijacks the HTTP connection for bidirectional raw I/O and documents Docker's eight-byte multiplexing frame format when TTY is disabled; `ContainerAttachWebsocket` exposes a websocket variant. Archive endpoints on `/containers/{id}/archive` use `HEAD` for Base64 JSON path metadata in `X-Docker-Container-Path-Stat`, `GET` for tar export, and `PUT` for tar extraction with read-only and directory/non-directory protections.

`POST /containers/prune` (`ContainerPrune`) deletes stopped containers and returns deleted IDs plus reclaimed bytes. Its filters include `until` and label include/exclude forms, which makes daemon-time parsing and destructive filter correctness important.

## Image, Build, Auth, And System Operations

Image operations in this chunk cover listing, building, builder-cache pruning, pulling/importing, inspect, history, push, tag, delete, search, image prune, commit, export, multi-export, and load.

`GET /images/json` (`ImageList`) returns `ImageSummary` entries with optional digest display and JSON filters for dangling, label, reference, before, and since. `POST /build` (`ImageBuild`) consumes a tar build context and exposes a large query/header surface: Dockerfile path, tags, remote contexts, quiet/no-cache/cache-from behavior, pull, intermediate container cleanup, memory and CPU limits, build args, shm size, squash, labels, network mode, content type, `X-Registry-Config`, platform, and target stage. Build output is JSON progress, and the build is cancelled if the client disconnects.

`POST /build/prune` (`BuildPrune`) deletes builder cache and reports reclaimed space. `POST /images/create` (`ImageCreate`) either pulls from a registry or imports from a source URL/request body, supports auth through `X-Registry-Auth`, and supports a target platform. `GET /images/{name}/json`, `GET /images/{name}/history`, `POST /images/{name}/push`, `POST /images/{name}/tag`, and `DELETE /images/{name}` implement inspect, layer history, registry push, tag creation/overwrite, and image deletion. Delete returns per-layer/tag `Untagged` and `Deleted` records and guards conflicts for descendants, running-container usage, and builds.

`GET /images/search` targets Docker Hub and returns description, official/automated flags, name, and star count with filters for automation, official status, and minimum stars. `POST /images/prune` deletes unused images using dangling, until, and label filters. `POST /commit` snapshots a container into a new image, optionally pausing it first and applying Dockerfile-style changes.

Image archive operations use tar streams rather than JSON-only bodies. `GET /images/{name}/get` exports one image/repository and documents legacy image tarball contents (`VERSION`, `json`, `layer.tar`, and optional `repositories`). `GET /images/get` exports multiple names through a query array. `POST /images/load` consumes an image tarball and can suppress progress details.

System endpoints expose auth, daemon info, version info, ping, event streaming, and data usage. `POST /auth` validates `AuthConfig` and may return `IdentityToken`; `/info` returns the large `SystemInfo` schema with host resource capabilities, daemon root, plugins, cgroup/logging drivers, registry config, runtimes, swarm info, proxy settings, live-restore, default isolation, init binary, component commits, and security options. `/version` returns platform, component versions, API/min API version, Git commit, Go version, OS/arch, kernel, experimental flag, and build time. `/_ping` returns text plus `Api-Version` and `Docker-Experimental` headers. `/events` streams event objects for container, image, volume, network, daemon, plugin, node, service, secret, and config activity with JSON filters. `/system/df` reports layer size, images, containers, and volumes with usage data.

## Exec Operations

Exec is modeled as a two-step control flow. `POST /containers/{id}/exec` (`ContainerExec`) creates an exec instance in a running container and returns an ID. The body controls stdin/stdout/stderr attachment, detach keys, TTY allocation, environment, command, privilege elevation, user/group, and working directory. It can fail when the container is missing, paused, or the daemon errors.

`POST /exec/{id}/start` (`ExecStart`) starts a previously created exec instance. If detached, it returns after starting; otherwise it establishes an interactive raw stream using `application/vnd.docker.raw-stream`. `POST /exec/{id}/resize` changes TTY dimensions and only applies to exec sessions created and started with TTY enabled. `GET /exec/{id}/json` (`ExecInspect`) begins in this chunk and defines the successful response properties visible through line 7561: removability, detach keys, exec ID, running flag, exit code, `ProcessConfig`, open stream booleans, container ID, and process PID. Error responses for this endpoint continue in the next chunk.

## Control Flow And State Behavior

The file itself has no runtime state, but it defines state transitions for Docker Engine. Container creation combines image config, host config, and endpoint networking into persistent daemon container metadata. Lifecycle endpoints move containers among created, running, paused, restarting, removing, exited, and dead states. Archive, export, changes, logs, stats, attach, and wait are read or stream views over container state and filesystem content, while update and rename mutate stored metadata or cgroup/resource settings.

Image and build operations mutate the image graph, tags, layer store, build cache, and registry state. Pull, push, create, build, commit, load, save, delete, and prune are all persistent or external side-effecting operations. Build cancellation is tied to client connection lifetime, and push/create operations explicitly cancel when the HTTP connection closes.

Swarm-related definitions in this chunk describe Raft-backed and versioned cluster state even though most swarm paths are later. Nodes, services, tasks, secrets, configs, join tokens, CA material, manager autolock, root rotation, scheduler placement, update/rollback state, and generic resources are represented as typed API objects. Optimistic concurrency is expressed through `ObjectVersion`.

Streaming control flow is a recurring integration constraint: logs, attach, stats, events, build, image create/push/load, image save, and exec start can return long-lived streams, raw binary/tar data, or upgraded/hijacked connections. Generated clients must support these transports separately from ordinary JSON request/response handling.

## Dependencies And Integration Points

This YAML depends on Swagger/OpenAPI 2.0 tooling, ReDoc rendering conventions, and Docker-specific schema extensions such as `x-go-name` and `x-nullable`. It integrates with Docker's API documentation pipeline and with client/server type generation mentioned in the file header.

Runtime integration points implied by the contract include Docker Engine HTTP routing, daemon object stores, containerd/runc and OCI runtime configuration, cgroups, namespaces, SELinux/AppArmor/seccomp/userns security settings, storage and graph drivers, logging drivers, volume drivers, network/IPAM drivers, registry clients, build context processing, Docker Hub search, swarmkit/Raft state, certificate authorities, and plugin interfaces.

The path contracts also integrate with Docker CLI and SDK behavior. Several descriptions explicitly map CLI behavior to multiple API calls: running containers requires more than one endpoint, `docker exec` wraps exec create/start, attach/log streams use Docker's raw-stream protocol, and image save/load tarball formats must remain compatible with CLI import/export.

## Risks And Edge Cases

The open-schema rule is both a compatibility feature and a client-generation risk. Strict clients that reject unknown response fields will break against newer daemons, while servers may silently ignore unknown request properties or query parameters. Generators need to preserve this tolerance.

Several schemas mix Linux-only, Windows-only, deprecated, experimental, and daemon-version-sensitive fields. Examples include Windows isolation/credential spec/CPU controls, Unix cgroup and namespace options, deprecated default bridge network fields in `NetworkSettings`, standalone Swarm `SystemStatus`, experimental plugin tasks and squash builds, and runtime/security options whose availability depends on the host daemon.

Streaming and hijacked connections are easy to mishandle in generic OpenAPI clients. `101` upgrade responses, raw bidirectional attach/exec streams, multiplexed stdout/stderr frames, unframed TTY streams, tar bodies, build/pull/push progress, stats/event streams, and log driver limitations all need explicit tests outside ordinary JSON client generation.

Auth and secret-bearing fields are sensitive. Registry headers encode credentials or identity tokens; `SystemInfo` may expose proxy URLs that include credentials; build args are documented as inappropriate for secrets but cannot be schema-enforced; `SecretSpec.Data` is base64-encoded and only used at create time; CA signing keys and certificates appear in swarm config schemas. Logging and tracing around generated clients must avoid leaking these values.

Destructive endpoints have broad effects. Container, image, and build prune/delete operations depend on filters, daemon time parsing, in-use conflict detection, and reclaimed-space accounting. Image delete/tag/push semantics also need careful handling around tags versus digests, descendants, running containers, and concurrent builds.

The YAML contains known ambiguity signals: TODO descriptions for some fields, examples with legacy or extra properties not always declared in the adjacent schema, nullable map/list fields, schema composition through `allOf`, and path/query parameter names that are not always idiomatic. These are risks for generated models, validators, and conformance tests.

## Test Signals

Useful validation for this chunk includes Swagger/OpenAPI linting for syntax, `$ref` resolution, operation ID uniqueness, valid required lists, enum consistency, response schema shape, and compatibility of `x-go-name`/`x-nullable` extensions with the generator.

Generated Docker API clients and server stubs should compile from this document and preserve composed definitions, maps, nullable fields, string-or-array command examples, binary body formats, header parameters, array query parameters, and raw-stream/tar endpoints.

API conformance tests should cover documented status codes and error bodies for each operation ID in this chunk, especially lifecycle idempotence (`304`), missing-object `404`, conflict `409`, read-only archive extraction `403`, bad filter/body `400`, and normal mutation status codes (`201`, `204`, `200`).

Transport tests are required for attach, logs, stats, events, build, image create/push/save/load, and exec start. They should verify connection upgrade/hijack behavior, multiplexed frame parsing, TTY non-multiplexed mode, cancellation on disconnect, streaming JSON progress, tar content types, and logging-driver limitations.

Persistence and destructive-operation tests should exercise create/start/stop/update/rename/pause/wait/delete container flows, archive round trips, image build/import/pull/tag/push/delete/prune/load/save/commit flows, builder-cache pruning, `/system/df` accounting, event emission/filtering, and registry auth/header handling. Platform-aware tests should cover Linux and Windows field differences where supported.
