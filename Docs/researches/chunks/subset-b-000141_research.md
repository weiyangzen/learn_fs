# sources/cloud-native/moby/api/docs/v1.46.yaml lines 1-7698

## Scope

This chunk covers the beginning of the Docker Engine API v1.46 Swagger 2.0 contract. It includes the top-level API metadata, tag layout, all reusable `definitions` from `ImageHistoryResponseItem` through `Topology`, and the start of the `paths` section through the beginning of `GET /containers/{id}/stats`.

The source is an API specification rather than executable daemon code. Its main code-facing role is to generate API documentation and client/server types, and to define compatibility contracts for Engine API v1.46 clients.

## Purpose

The file describes the HTTP API served by Docker Engine at base path `/v1.46`. It establishes the default content types, versioning rules, registry-auth header format, ReDoc tag organization, reusable schema objects, and operation contracts for the first container endpoints.

Within this chunk, the schema layer is the dominant content. It defines the data model used by containers, images, volumes, networks, plugins, swarm nodes/services/tasks/secrets/configs, system information, registry distribution metadata, events, and CSI-backed cluster volumes. The path layer starts the container API group with list, create, inspect, top, logs, filesystem changes, export, and the initial part of stats.

## Important APIs And Types

- Top-level Swagger metadata declares `swagger: "2.0"`, `basePath: "/v1.46"`, HTTP/HTTPS schemes, JSON/text consumes/produces defaults, title `Docker Engine API`, and version `1.46`.
- API versioning notes state that unversioned calls use the current API version but are deprecated, that unsupported explicit versions return HTTP `400`, and that clients must ignore unknown response properties because the schema is open for forward compatibility.
- Registry authentication is documented as an `X-Registry-Auth` header containing base64url-encoded JSON credentials or an identity token from `/auth`.
- Tags group the API as `Container`, `Image`, `Network`, `Volume`, `Exec`, swarm resources (`Swarm`, `Node`, `Service`, `Task`, `Secret`, `Config`), plus `Plugin` and `System`.
- Container and host runtime schemas include `ContainerConfig`, `HostConfig`, `Resources`, `RestartPolicy`, `HealthConfig`, `Health`, `HealthcheckResult`, `ContainerState`, `ContainerSummary`, and `ContainerCreateResponse`.
- Storage and mount schemas include `MountType`, `MountPoint`, `Mount`, `DeviceMapping`, `DeviceRequest`, `ThrottleDevice`, `Volume`, `VolumeCreateOptions`, `VolumeListResponse`, `ClusterVolume`, `ClusterVolumeSpec`, and `Topology`.
- Image schemas include `ImageConfig`, `ImageInspect`, `ImageSummary`, `ImageHistoryResponseItem`, `ImageDeleteResponseItem`, build/push/create progress objects, `GraphDriverData`, `OCIDescriptor`, `OCIPlatform`, and `DistributionInspect`.
- Network schemas include `NetworkingConfig`, `NetworkSettings`, `PortMap`, `PortBinding`, `EndpointSettings`, `EndpointIPAMConfig`, `Network`, `IPAM`, `IPAMConfig`, `NetworkContainer`, `NetworkAttachmentConfig`, and peer/config-only references.
- Swarm schemas include optimistic-concurrency `ObjectVersion`, `NodeSpec`, `Node`, `SwarmSpec`, `ClusterInfo`, `Swarm`, `TaskSpec`, `Task`, `ServiceSpec`, `Service`, `EndpointSpec`, `EndpointPortConfig`, `SecretSpec`, `Secret`, `ConfigSpec`, and `Config`.
- System schemas include `SystemVersion`, `SystemInfo`, `ContainerdInfo`, `PluginsInfo`, `RegistryServiceConfig`, `IndexInfo`, `Runtime`, `Commit`, `SwarmInfo`, `LocalNodeState`, `PeerNode`, `EventActor`, and `EventMessage`.
- Shared response/error schemas include `ErrorResponse`, `ErrorDetail`, `ProgressDetail`, `IdResponse`, `ContainerWaitResponse`, and `ContainerWaitExitError`.
- Container path operations covered in this chunk are `ContainerList`, `ContainerCreate`, `ContainerInspect`, `ContainerTop`, `ContainerLogs`, `ContainerChanges`, `ContainerExport`, and the start of `ContainerStats`.

## Control Flow

The spec-level flow starts with global metadata and reusable definitions, then references those definitions from path operations. Generated clients and documentation depend on `$ref` links such as `HostConfig` extending `Resources`, container create bodies composing `ContainerConfig` with `HostConfig` and `NetworkingConfig`, and inspect/list endpoints returning different container shapes.

Container listing (`GET /containers/json`) accepts optional query controls for scope and shape: `all`, `limit`, `size`, and JSON-encoded `filters`. The response is an array of `ContainerSummary`, intentionally smaller than inspect output. Filters cover image ancestry, ID/name boundaries, exposed/published ports, labels, health, task status, network, volume, exit code, isolation, and container lifecycle state.

Container creation (`POST /containers/create`) accepts an optional `name`, optional `platform`, and a required JSON body. The daemon resolves the requested image/platform before container creation; a missing matching local image returns `404`, while an available but platform-mismatched image may still create the container with a warning when no platform was explicitly requested. The body combines portable container config, host-specific runtime config, and network endpoint config.

Container inspection (`GET /containers/{id}/json`) resolves an ID or name and returns low-level state: command path/args, persisted creation data, state, image ID, generated host files, log path, driver, platform, security labels, active exec IDs, host config, graph-driver metadata, optional size fields, mounts, original config, and network settings.

The remaining covered container flows are read-only or streaming. `ContainerTop` shells out to a Unix `ps` command and is unsupported on Windows. `ContainerLogs` streams stdout/stderr logs for compatible logging drivers, with follow, time-range, timestamp, and tail query options. `ContainerChanges` compares the container writable layer and returns `FilesystemChange` entries. `ContainerExport` emits a tarball of the container filesystem. `ContainerStats` starts a live resource-usage stream whose documentation includes CPU and memory calculation guidance and cgroup v1/v2 differences; this chunk ends before the full stats operation is complete.

## State And Persistence Behavior

The YAML does not persist state itself, but it documents Docker Engine state contracts. `DockerRootDir` in `SystemInfo` identifies the daemon's persistent state root, defaulting to `/var/lib/docker` on Linux and `C:\ProgramData\docker` on Windows. Container inspect examples expose persistent/generated paths for hostname, hosts, resolv.conf, and logs under the daemon data directory.

Container creation persists a container object with ID, name, image reference, config, host config, network attachments, mounts, labels, restart policy, and warnings. Container state tracks live/runtime flags (`Running`, `Paused`, `Restarting`, `OOMKilled`, `Dead`), process ID, exit code, errors, start/finish times, and health status. The spec explicitly warns that paused containers can have both `Running` and `Paused` true, so `Status` is the reliable lifecycle discriminator.

Volume and mount schemas distinguish host bind mounts, named volumes, tmpfs mounts, npipe mounts, and Swarm cluster volumes. Named volumes are not removed with their containers. Volume usage data is only available in `/system/df`-style contexts and can be `-1` when unavailable. Cluster volumes are Swarm objects with IDs, versions, publish state, CSI plugin volume IDs, topology, capacity, access mode, and availability state.

Image state is content-addressed through image IDs, layer/rootfs metadata, repo tags, repo digests, storage-driver data, and local cache metadata such as `LastTagTime`. The spec distinguishes local image configuration from OCI/image-spec fields and marks several image config fields deprecated for removal in API v1.50.

Swarm objects use `ObjectVersion.Index` for safe concurrent updates. The description states that write requests using stale base versions must not unintentionally overwrite newer object state. Swarm CA, raft, dispatcher, encryption-at-rest, task defaults, join tokens, nodes, services, tasks, secrets, configs, and cluster volumes are represented as manager-backed state even though the corresponding path operations mostly appear later in the file.

System and runtime state includes daemon feature support, cgroup driver/version, registry config, configured runtimes, containerd namespace/socket details, security options, default address pools, CDI directories, proxy settings, and plugin inventories. Many of these fields are informational snapshots and may be omitted or unstable depending on platform, daemon mode, and debug settings.

## Dependencies

The file depends structurally on Swagger 2.0/OpenAPI tooling, ReDoc rendering, `$ref` resolution, vendor extensions such as `x-go-name` and `x-nullable`, and code generators that derive Go/client/server types from the YAML.

At runtime, the documented API depends on Docker Engine subsystems:

- container lifecycle, storage drivers, OCI runtimes, containerd, cgroups, namespaces, SELinux/AppArmor/seccomp, logging drivers, and healthcheck execution;
- image storage, build cache, registry auth/push/pull/search/distribution metadata, and content-addressable digests;
- libnetwork/network drivers, IPAM, port binding, endpoint settings, DNS aliases, and swarm overlay/ingress networks;
- volume drivers and CSI-capable swarm cluster volume plugins;
- swarmkit managers, raft state, certificates, join tokens, nodes, services, tasks, secrets, configs, and optimistic object versioning;
- host OS capabilities, kernel features, Windows-specific isolation/credential spec behavior, and platform-specific fields.

The container endpoints in this chunk depend on shared definitions earlier in the file: `ContainerSummary`, `ContainerConfig`, `HostConfig`, `NetworkingConfig`, `ContainerCreateResponse`, `ContainerState`, `GraphDriverData`, `MountPoint`, `NetworkSettings`, `FilesystemChange`, and `ErrorResponse`.

## Integration Points

Operation IDs are stable hooks for generated clients and documentation anchors. In this range, the path operations map to Docker CLI-style workflows: `docker ps` maps to `ContainerList`, `docker create` to `ContainerCreate`, `docker inspect` to `ContainerInspect`, `docker top` to `ContainerTop`, `docker logs` to `ContainerLogs`, `docker diff`-style filesystem change inspection to `ContainerChanges`, `docker export` to `ContainerExport`, and `docker stats` to `ContainerStats`.

The spec integrates strongly with Docker CLI compatibility expectations. The top-level description notes that most client commands map directly to endpoints, but running containers involves multiple API calls. This chunk therefore defines create/inspect/list primitives but does not yet include start/stop/attach/wait lifecycle operations beyond the line boundary.

Generated client integration must handle multiple media types. Most endpoints produce JSON, but logs produce Docker raw/multiplexed stream media, export produces `application/octet-stream`, and create consumes both JSON and `application/octet-stream`. Filter query parameters are JSON-encoded `map[string][]string`, not repeated query keys.

The registry auth header contract integrates with image push/pull/create endpoints later in the file, while the `AuthConfig` definition and `/auth` reference establish the shared credential shape. System info and version schemas integrate with feature detection: clients can check API version, min API version, cgroup version, security options, runtimes, swarm state, and daemon warnings before choosing request fields.

Vendor extensions integrate with Go generation. `x-go-name` renames generated types or fields, `x-nullable` distinguishes nullable/omitempty behavior, and comments such as FIXME/TODO note areas where schema generation is compensating for current Go type behavior or pending removal of deprecated fields.

## Risks And Edge Cases

- This chunk ends inside the `ContainerStats` operation example. Research or generated summaries for this chunk should not treat stats as fully covered until later chunks are merged.
- The API uses an open schema model. Strict JSON decoders that reject unknown fields can break when talking to newer daemons.
- Versionless API calls currently resolve to v1.46 but are deprecated. Clients should send an explicit `/v1.46` prefix when they need this contract.
- Many schemas include deprecated fields that are still present for compatibility, especially `ImageConfig` fields planned for API v1.50 removal and default-bridge fields in `NetworkSettings`. Generated clients need deprecation handling without dropping fields prematurely.
- `ContainerState.Running` and `ContainerState.Paused` are not mutually exclusive. State machines based only on booleans can misclassify paused containers.
- Resource controls are platform and cgroup-version sensitive. Windows CPU controls have precedence rules; cgroup v2 omits or changes stats fields; kernel memory TCP limits are no longer supported by the default runc runtime.
- Mount behavior has subtle safety implications: bind sources usually must already exist unless `CreateMountpoint` is set, tmpfs cannot specify `Source`, `ReadOnlyNonRecursive` has version-dependent defaults before v1.44, and recursive read-only enforcement can fail.
- `DeviceRequests`, CDI directories, privileged mode, capabilities, seccomp, AppArmor, SELinux, sysctls, and user namespaces expose host/runtime security boundaries. Incorrect client defaults can widen access unexpectedly.
- `HostConfig.AutoRemove` has no effect with restart policies. Tests should cover the conflict rather than assuming both settings compose.
- The container create `platform` behavior can return warnings rather than errors when no platform was specified and a mismatched local image exists. Clients that require exact platform matching should pass the platform explicitly.
- Log streaming only works for `json-file` and `journald` logging drivers in this endpoint. Other logging drivers may not support API log reads.
- `ContainerTop` depends on Unix `ps` and is not supported on Windows. Cross-platform client tests must avoid assuming this operation is universally available.
- Several informational fields explicitly say their format or existence is not stable, including storage driver status, OS version, runtime status, daemon ID format, and component details. These should not be parsed as stable contracts unless separately tested against daemon behavior.
- Insecure registry configuration is represented in `RegistryServiceConfig`/`IndexInfo`; the spec warns it should be testing-only because it permits unencrypted or untrusted HTTPS registry communication.
- Swarm specs contain mutually exclusive substructures (`ContainerSpec`, `PluginSpec`, `NetworkAttachmentSpec`; credential spec file/registry/config; config file/runtime; cluster volume mount/block modes). Schema validation alone may not enforce all daemon-side exclusivity rules.
- Object versions are required for safe swarm updates. Clients that cache stale `Version.Index` values risk update conflicts.

## Test Signals

Useful validation signals for this chunk include:

- Swagger validation should parse the file as Swagger 2.0, resolve all `$ref` links in lines 1-7698, and preserve vendor extensions used for Go generation.
- Generated type tests should assert important nullability and required-field behavior for `ErrorResponse`, `ContainerCreateResponse`, `ImageSummary`, `Volume`, `GraphDriverData`, `ObjectVersion`, and `ClusterVolume`.
- API compatibility tests should verify that clients ignore unknown response properties and tolerate omitted nullable or platform-specific fields.
- Container list tests should cover default running-only behavior, `all`, `limit`, `size`, and JSON-encoded filters for state, label, network, volume, health, ancestor, exposed/published port, and exit code.
- Container create tests should cover name validation, platform matching and mismatch warnings, required body handling, missing-image `404`, duplicate-name/conflict `409`, host config/resource fields, networking config, mounts, device requests, healthchecks, restart policy, and warning propagation.
- Container inspect tests should cover ID and name lookup, optional size fields, state booleans versus `Status`, health log decoding, mount/network/graph-driver structures, active `ExecIDs`, generated host paths, and missing container `404`.
- Container top tests should cover custom `ps_args`, Unix-only behavior, and unsupported Windows behavior.
- Container logs tests should cover stdout/stderr selection, `follow`, `since`, `until`, `timestamps`, `tail`, raw/multiplexed stream decoding, empty selector behavior, and unsupported logging-driver responses.
- Container changes tests should verify `Kind` enum values `0`, `1`, and `2` map to modified/added/deleted paths.
- Container export tests should verify binary tar streaming and error handling for missing containers.
- Stats tests, once later chunks are merged, should cover live versus one-shot stream behavior, cgroup v1/v2 field differences, CPU percentage formula inputs, memory cache/inactive-file calculations, and absent/empty blkio or per-CPU fields.
- System/schema regression tests should compare real daemon `/info` and `/version` responses against `SystemInfo` and `SystemVersion`, while allowing documented unstable informational fields to vary.
