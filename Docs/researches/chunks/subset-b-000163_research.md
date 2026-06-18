# sources/cloud-native/moby/api/swagger.yaml lines 7938-13998

## Scope And Purpose

This chunk is the tail of the Docker Engine API Swagger 2.0 definition's `definitions` section followed by the main `paths` section for core daemon APIs. It starts inside the `ClusterVolume` schema's CSI plugin status fields, defines cluster-volume specs, topology, image attestation statements, and image manifest summaries, then enumerates HTTP operations for containers, images/builds, system metadata, exec sessions, volumes, networks, plugins, Swarm, nodes, services, tasks, secrets, configs, registry distribution inspection, and the deprecated interactive session endpoint.

The file is an API contract and documentation source, not executable daemon code. Its purpose is to lock down the externally visible Docker Engine HTTP surface: paths, methods, operation IDs, request parameters, body schemas, response schemas, response codes, media types, examples, enum values, and compatibility notes used by generated clients, server routing validation, and rendered API documentation.

## Important APIs, Types, And Operation Groups

The visible schema definitions extend Docker's cluster-storage and image metadata models. The partial `ClusterVolume` tail records CSI plugin output such as `VolumeContext`, plugin `VolumeID`, accessible topology, and per-node publish status. `ClusterVolumeSpec` describes Swarm CSI cluster-volume intent: volume grouping for scheduler interchangeability, access scope and sharing modes, mount or block volume options, CSI secrets, topology requirements, capacity limits, and `Availability` values of `active`, `pause`, or `drain`. `Topology` is a map of topology segments. `AttestationStatement` represents an in-toto statement attached to an image, optionally including the verbatim statement body. `ImageManifestSummary` summarizes an image or attestation manifest with an OCI descriptor, local availability, content/total size accounting, kind-specific image data, platform identity, container consumers, unpacked size, and attestation target digest.

Container APIs include listing and creation, inspect/top/logs/changes/export/stats/resize, lifecycle operations start/stop/restart/kill/update/rename/pause/unpause, attach via hijacked HTTP or websocket, wait, delete, archive metadata/download/upload, and stopped-container prune. These operations expose container identifiers as names or IDs, JSON filter maps, runtime sizing and resource update inputs, raw or multiplexed log/attach streams, tar archive bodies, and delete/prune force or volume cleanup controls.

Image and build APIs include `ImageList`, `ImageBuild`, `BuildPrune`, `ImageCreate`, `ImageInspect`, `ImageAttestations`, `ImageHistory`, `ImagePush`, `ImageTag`, `ImageDelete`, `ImageSearch`, `ImagePrune`, `ImageCommit`, `ImageGet`, `ImageGetAll`, and `ImageLoad`. The build endpoint accepts compressed tar contexts or remote contexts, Dockerfile selection, multiple tags, cache inputs, build args, resource limits, labels, network mode, registry config headers, platform, target, BuildKit output configuration, and builder backend selector `1` or `2`. Image inspect/list support manifest and identity metadata. Image attestations read in-toto statements for a platform and can filter by predicate type or include statement JSON only when requested.

System APIs include registry auth validation, daemon info and version, `GET`/`HEAD` ping with daemon capability headers, real-time event streaming, and disk usage accounting. Exec APIs create, start, resize, and inspect an exec instance, using attach flags, TTY and console size settings, detach keys, env, command, user, working directory, stream transport, and process state fields such as `Running`, `ExitCode`, open streams, container ID, and host PID.

Volume APIs list, create, inspect, update, delete, and prune volumes. `VolumeUpdate` is explicitly valid only for Swarm cluster volumes; it wraps `ClusterVolumeSpec` in a body object, currently allows only `Availability` changes, and requires the current volume version from the `ClusterVolume` field. Network APIs list, inspect, delete, create, connect, disconnect, and prune networks with driver, scope, internal/attachable/ingress, config-only/config-from, IPAM, IPv4/IPv6, options, labels, and swarm-scoped operation restrictions.

Plugin APIs cover listing, privilege inspection, pull/install, inspect, delete, enable, disable, upgrade, local tar creation, push, and set/configure. Pull and upgrade use registry auth and accepted privilege arrays. Enable/disable/delete include timeout or force behavior. Local plugin creation consumes an `application/x-tar` plugin rootfs/manifest bundle.

Swarm, node, service, task, secret, and config APIs expose cluster control-plane state. Node operations list, inspect, delete, and update nodes. Swarm operations inspect, init, join, leave, update, get unlock key, and unlock a locked manager. Service operations list, create, inspect, delete, update, and stream logs. Task operations list, inspect, and stream logs. Secret and config operations list, create, inspect, delete, and update versioned Swarm objects, with update prose limiting mutable fields to labels.

The final operations are `DistributionInspect`, which contacts a registry for image descriptor and platform metadata, and `Session`, a deprecated h2c connection-hijack endpoint that lets the daemon call back to client-exposed gRPC services.

## Control Flow

Control flow is encoded by REST method, path shape, operation ID, status code, and transport semantics. `GET` operations read or stream daemon state, registry metadata, logs, events, tar exports, and object inspections. `POST` operations create resources, mutate lifecycle state, run prune jobs, validate credentials, perform Swarm membership/control changes, start exec sessions, and establish interactive sessions. `PUT` is used for container archive extraction and cluster-volume update. `DELETE` removes resources. `HEAD` on container archive metadata and ping returns headers without a JSON body.

Several operations require multi-step client workflows. Container create precedes start, attach, logs, wait, exec, archive, update, and delete. Attach requires at least `logs` or `stream`, then the client must handle either a `200` hijacked connection or a `101` upgraded connection. Non-TTY attach streams use Docker's 8-byte multiplex header to separate stdout and stderr; TTY attach streams are raw PTY bytes.

Exec follows create/start/resize/inspect sequencing. `ContainerExec` records the command setup against a running container. `ExecStart` either detaches immediately or attaches to raw/multiplexed output. `ExecResize` only makes sense for a TTY exec session, and `ExecInspect` reports final process state and exit code.

Image build, pull/import, push, save/load, and attestation flows cross local and remote storage boundaries. Builds stream progress and are canceled when the client connection drops. Pull/import semantics depend on `fromImage`, `fromSrc`, tag, digest, repository, changes, platform, and registry auth headers. Attestation lookup first selects an image platform, locates attestation manifests that refer to the selected image manifest, and reads statement layers only when the `statement` query opts in.

Versioned Swarm updates use optimistic concurrency. Node, swarm, service, secret, config, and cluster-volume updates all require a `version` query parameter taken from a prior inspect/list result. Service update additionally supports registry auth selection through `registryAuthFrom` and server-side rollback via `rollback=previous`, in which case the supplied spec is ignored.

Prune operations consistently turn JSON-encoded filter maps into destructive cleanup jobs and return deleted object identifiers and reclaimed space where applicable. Filters such as `until`, labels, dangling state, build cache state, and `all` materially control the deletion scope.

## State And Persistence Behavior

The YAML itself persists no runtime state, but it specifies persistent and transient daemon state transitions. Container operations affect process state, cgroup freezer state, restart/stop/kill behavior, resource limits, container names, root filesystems, attached streams, anonymous volumes, logs, and archive extraction. Container archive upload can mutate the container filesystem and must honor read-only rootfs and volume permissions.

Image and build operations mutate local image content, tags, manifests, BuildKit/classic builder cache, import/export tar streams, and registry references. `ImageCommit` snapshots a container into a new image and can pause the container during capture. `ImageDelete`, `ImagePrune`, and `BuildPrune` reclaim storage and alter reference graphs. Manifest summaries and attestations introduce state that depends on OCI indexes, content-store availability, unpacked snapshots, and backend support.

Volumes and networks are driver-managed persistent resources. Cluster volumes are Swarm objects with versions, CSI plugin context, external plugin volume IDs, topology, publish states, and scheduler availability. Network operations mutate IPAM state, endpoint attachments, overlay/local driver state, and container membership. Some network operations are forbidden for builtin or swarm-scoped resources.

Plugins persist installed plugin content, accepted privileges, enabled/disabled state, configuration strings, and registry-pulled versions. Force removal or force disable can disrupt containers or networks that depend on the plugin.

Swarm resources are Raft-backed cluster state. Init, join, leave, unlock, token rotation, node update/delete, service create/update/delete, task scheduling, secrets, and configs all affect manager/worker membership or desired cluster state. Services persist desired state, while tasks expose scheduler and runtime observations. Secrets and configs carry sensitive or configuration data at creation time, but this contract restricts later updates to labels.

System info, ping, version, events, disk usage, distribution inspection, logs, and sessions mostly read live state or establish transports. They still expose sensitive operational details, can hold long-lived connections, and may cross daemon boundaries to registries or callback services.

## Dependencies And Integration Points

This chunk depends on shared definitions declared elsewhere in `sources/cloud-native/moby/api/swagger.yaml`, including `ErrorResponse`, `ContainerConfig`, `HostConfig`, `NetworkingConfig`, `ContainerSummary`, `ContainerInspectResponse`, `ContainerStatsResponse`, `FilesystemChange`, `ImageSummary`, `ImageInspect`, `ImageHistoryResponseItem`, `ImageDeleteResponseItem`, `AuthConfig`, `AuthResponse`, `SystemInfo`, `SystemVersion`, `EventMessage`, disk usage types, `IDResponse`, `Volume`, `VolumeCreateRequest`, `VolumeListResponse`, `NetworkSummary`, `Network`, `NetworkCreateResponse`, `NetworkConnectRequest`, `NetworkDisconnectRequest`, `Plugin`, `PluginPrivilege`, `Node`, `NodeSpec`, `Swarm`, `SwarmSpec`, `Service`, `ServiceSpec`, `ServiceCreateResponse`, `ServiceUpdateResponse`, `Task`, `Secret`, `SecretSpec`, `Config`, `ConfigSpec`, `DistributionInspect`, `OCIDescriptor`, `OCIPlatform`, `Identity`, and `ObjectVersion`.

Runtime integrations implied by the contract include Docker daemon HTTP routing, request validation, container runtime and cgroups, PTY handling, stream multiplexing, websocket upgrades, logging drivers, filesystem tar/archive handling, local image/content stores, registry resolvers, BuildKit and classic builder backends, build cache accounting, volume drivers and CSI plugins, network drivers and IPAM, plugin management, swarmkit managers/agents, Raft persistence, scheduler/orchestrator state, secret/config storage, event broadcasting, and h2c/gRPC session transport.

Client integrations are broad. The Docker CLI and generated SDKs must handle JSON bodies, repeated query parameters, JSON-encoded filter maps, names or IDs in path parameters, base64/base64url auth headers, binary tar request and response bodies, raw-stream and multiplexed-stream media types, HTTP connection hijacking, websocket attach, long-lived event/log/build streams, optimistic update versions, and open-ended driver option/label maps.

## Risks And Edge Cases

Public API compatibility is the dominant risk. Changing operation IDs, route names, method choices, required flags, enum values, parameter names, query collection formats, response status codes, media types, referenced schemas, or examples can break generated clients, Docker CLI expectations, and third-party integrations.

The source slice exposes several high-risk transports. Attach, websocket attach, exec start, container logs, service logs, task logs, events, image build, push/pull progress, tar export/import, container archive transfer, and session h2c upgrades do not behave like ordinary short JSON requests. Proxies, clients, and generated SDKs must preserve connection lifetime, binary framing, content type, upgrade behavior, cancellation, and TTY versus non-TTY stream differences.

Destructive APIs need strict validation. Container/image/build/volume/network prune can remove broad resource sets when filters are missing or parsed incorrectly. Image delete and tag mutation can alter shared references. Volume/network/plugin force operations can break active consumers. Archive extraction can overwrite paths or cross read-only boundaries if flags such as `noOverwriteDirNonDir` and `copyUIDGID` are mishandled.

Concurrency-sensitive Swarm updates can lose writes if version checks are skipped or stale versions are accepted. Secret/config and cluster-volume updates are especially easy to implement incorrectly because their schemas accept rich specs while prose currently permits only labels or volume availability to change.

Security-sensitive paths include registry auth headers, build registry config headers, secret/config creation bodies, plugin privilege approval, plugin rootfs tar upload, swarm join tokens, manager unlock keys, session callback transport, and distribution inspection. Implementations and tests should ensure credentials and secret data are not logged, echoed, cached, or exposed through examples or errors.

Compatibility edges include name-or-ID ambiguity, platform selection for multi-platform images, attestation support returning `501` on legacy graphdriver stores, cgroup v1/v2 stats differences, logging-driver limitations for log endpoints, Windows unsupported behavior for container top, Swarm `503` behavior when not in a cluster, and registry `401` versus missing-image errors.

## Test Signals

Static tests should parse the Swagger YAML, resolve every `$ref`, validate Swagger 2.0 shape, ensure operation IDs are unique, verify all path parameters are declared and required, check enum/default compatibility, and regenerate docs/clients without schema or rendering failures.

API conformance tests should cover success and documented error status codes: `200`, `201`, `204`, and `101` success paths; `400` bad parameters; `401` registry authentication or missing registry image; `403` forbidden network/archive cases; `404` missing objects; `409` conflicts such as running containers, paused containers, or name collisions; `500` daemon failures; `501` unsupported attestation backend; and `503` Swarm state mismatches.

Stateful integration tests should exercise representative flows for each operation family: container create/start/logs/stats/attach/wait/archive/update/delete/prune; image build/create/inspect/attestations/history/push/tag/delete/search/prune/commit/export/load; build cache prune; exec create/start/resize/inspect; volume create/cluster-update/delete/prune; network create/connect/disconnect/delete/prune; plugin pull/create/privileges/enable/disable/set/upgrade/push/delete; swarm init/join/leave/update/unlock; node update/delete; service create/update/rollback/logs/delete; task list/inspect/logs; and secret/config create/update/delete.

Transport tests should verify raw and multiplexed stream framing, TTY and non-TTY attach behavior, websocket attach, service/task/container log filters, event stream `since`/`until` handling, build cancellation on client disconnect, binary tar import/export, base64 `X-Docker-Container-Path-Stat` archive headers, archive extraction flags, image attestation filtering and statement opt-in, and deprecated `/session` h2c hijacking.

Compatibility tests should verify JSON filter encoding as `map[string][]string`, repeated array query encoding for platform/type and disk-usage selectors, preservation of `X-Registry-Auth` and `X-Registry-Config` headers, correct optimistic concurrency failures for stale versions, label-only mutation restrictions for secrets/configs, availability-only mutation for cluster volumes, and stable behavior when object identifiers can be names, IDs, or partial IDs.
