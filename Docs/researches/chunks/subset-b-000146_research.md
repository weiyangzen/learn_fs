# sources/cloud-native/moby/api/docs/v1.48.yaml lines 7759-13579

## Scope And Purpose

This chunk is the central path table of the Docker Engine API v1.48 Swagger/OpenAPI 2.0 specification. It begins at the tail of the image manifest summary schema, then defines `paths:` from `GET /containers/json` through `POST /session`. The file is not executable runtime code; it is a public API contract used by generated documentation, client bindings, and server contract tests.

The chunk covers most top-level Docker Engine workflows: container creation and lifecycle, image build/pull/push/save/load, daemon system information, event streaming, exec sessions, volumes, networks, plugins, swarm nodes and cluster management, services, tasks, secrets, configs, registry distribution inspect, and the BuildKit session callback transport.

## Important APIs And Types

The opening schema fragment describes an image manifest entry with required `ID`, `Descriptor`, `Available`, `Size`, and `Kind`. `Descriptor` references `OCIDescriptor`; `Size` separates `Content` bytes in the content store from `Total` bytes including kind-specific local data. `Kind` is `image`, `attestation`, or `unknown`. `ImageData` is present only for runnable image manifests and carries `OCIPlatform`, container users, and unpacked size. `AttestationData` links an attestation manifest to the image manifest digest it describes.

Container APIs include `ContainerList`, `ContainerCreate`, `ContainerInspect`, `ContainerTop`, `ContainerLogs`, `ContainerChanges`, `ContainerExport`, `ContainerStats`, TTY resize, start/stop/restart/kill/update/rename/pause/unpause, attach over raw HTTP or websocket, wait, delete, archive head/get/put, and prune. These operations bind to shared definitions such as `ContainerSummary`, `ContainerConfig`, `HostConfig`, `NetworkingConfig`, `ContainerInspectResponse`, `FilesystemChange`, `ContainerWaitResponse`, `Resources`, `RestartPolicy`, and `ErrorResponse`.

Image APIs include `ImageList`, `ImageBuild`, `BuildPrune`, `ImageCreate`, `ImageInspect`, `ImageHistory`, `ImagePush`, `ImageTag`, `ImageDelete`, `ImageSearch`, `ImagePrune`, `ImageCommit`, `ImageGet`, `ImageGetAll`, and `ImageLoad`. Important referenced schemas include `ImageSummary`, `ImageInspect`, `ImageHistoryResponseItem`, `ImageDeleteResponseItem`, `BuildCache`, `ContainerConfig`, `IDResponse`, `AuthConfig`, and OCI platform/manifest structures. Build and registry operations use base64 or base64url authentication headers such as `X-Registry-Config`, `X-Registry-Auth`, and platform selectors encoded as strings or JSON.

System APIs are `SystemAuth`, `SystemInfo`, `SystemVersion`, `SystemPing`, `SystemPingHead`, `SystemEvents`, and `SystemDataUsage`. They expose registry credential validation, daemon and host capability inventory, API version headers, builder recommendation headers, swarm status headers, live event streams, and disk usage grouped by containers, images, volumes, and build cache.

Exec APIs include `ContainerExec`, `ExecStart`, `ExecResize`, and `ExecInspect`. Inline request/response schemas define `ExecConfig`, `ExecStartConfig`, and `ExecInspectResponse`. These include attach flags, `ConsoleSize` arrays, detach-key overrides, TTY mode, environment, command, privileged/user/working directory settings, process state, exit code, PID, and links back to `ProcessConfig`.

Volume APIs are `VolumeList`, `VolumeCreate`, `VolumeInspect`, `VolumeUpdate`, `VolumeDelete`, and `VolumePrune`, using `VolumeListResponse`, `VolumeCreateOptions`, `Volume`, and cluster-volume specs. `VolumeUpdate` is restricted to swarm cluster volumes and currently allows only availability changes through a wrapped `ClusterVolumeSpec`, guarded by a required `version` query parameter.

Network APIs are `NetworkList`, `NetworkInspect`, `NetworkDelete`, `NetworkCreate`, `NetworkConnect`, `NetworkDisconnect`, and `NetworkPrune`. They use `Network`, `NetworkCreateResponse`, `ConfigReference`, `IPAM`, and `EndpointSettings`. The create body requires `Name` and can set driver, scope, internal/attachable/ingress/config-only flags, `ConfigFrom`, IPAM, IPv4/IPv6 enablement, driver options, and labels.

Plugin APIs are `PluginList`, `GetPluginPrivileges`, `PluginPull`, `PluginInspect`, `PluginDelete`, `PluginEnable`, `PluginDisable`, `PluginUpgrade`, `PluginCreate`, `PluginPush`, and `PluginSet`. They use `Plugin` and `PluginPrivilege`, with plugin names accepting an optional `:latest` tag. Pull and upgrade take privilege grants in the body and registry auth headers; create consumes a plugin rootfs/manifest tar.

Swarm APIs include node list/inspect/delete/update, swarm inspect/init/join/leave/update/unlockkey/unlock, service list/create/inspect/delete/update/logs, task list/inspect/logs, secret list/create/inspect/delete/update, and config list/create/inspect/delete/update. Key schemas are `Node`, `NodeSpec`, `Swarm`, `SwarmSpec`, `Service`, `ServiceSpec`, `ServiceCreateResponse`, `ServiceUpdateResponse`, `Task`, `Secret`, `SecretSpec`, `Config`, and `ConfigSpec`. Updates to swarm-managed objects require current object versions to avoid conflicting writes.

The final endpoints are `DistributionInspect`, which contacts registries to return descriptor and platform information through `DistributionInspect`, and `Session`, which hijacks an HTTP connection to h2c so the daemon can call client-provided gRPC services.

## Control Flow And Protocol Behavior

The container workflow is expressed as separate HTTP state transitions: list or create a container, inspect it, start it, stream logs or attach, collect stats, update resources, pause/unpause, stop/restart/kill, wait for a condition, copy archive data in or out, and delete or prune. Status codes encode state: start and stop use `204` for a transition and `304` for already-started/already-stopped; kill uses `409` if the container is not running; delete uses `409` when a running container is removed without force.

Container archive APIs use three different methods on `/containers/{id}/archive`. `HEAD` returns a base64-encoded JSON path-stat object in `X-Docker-Container-Path-Stat`, `GET` returns an `application/x-tar` archive, and `PUT` extracts a tar stream with `noOverwriteDirNonDir` and `copyUIDGID` query controls. These are binary stream APIs even though most of the surrounding surface is JSON.

Several APIs are long-running or streaming. Container logs, service logs, task logs, exec start, attach, events, image build, pull/import, push, save/load, and plugin operations can keep the connection open or return stream-style progress data. Attach and session are the most protocol-sensitive: attach can hijack HTTP and return raw or multiplexed Docker streams, websocket attach wraps similar container streams in websocket transport, and `/session` upgrades to h2c for BuildKit-style callbacks.

Image build control flow accepts either a build-context tar body or remote contexts. It validates the Dockerfile before running instructions, cancels when the client connection drops, and chooses builder backend with `version=1` for classic builder or `version=2` for BuildKit. Query parameters carry build args, cache sources, target stage, labels, network mode, resource limits, platform, and BuildKit output configuration.

Swarm control flow is optimistic and versioned. Node, swarm, service, volume, secret, and config updates require the current object `version`. Service update can source registry auth from `spec` or `previous-spec`, and `rollback=previous` triggers a server-side rollback where the supplied spec is ignored. Swarm update can rotate worker tokens, manager tokens, and manager unlock key. Swarm init/join/leave mutate node cluster membership and return `503` for wrong membership state.

List and prune endpoints repeatedly use JSON-in-query strings for `filters`, commonly documented as `map[string][]string` even when Swagger can only model them as a `string`. `SystemDataUsage.type` is one of the clearer array query parameters and uses `collectionFormat: multi` with allowed values `container`, `image`, `volume`, and `build-cache`.

## State And Persistence Behavior

Container create persists container configuration, host configuration, network endpoint configuration, labels, mount declarations, restart policy, and image/platform selection. Runtime endpoints mutate live state without replacing the object: start/stop/restart/kill, pause/unpause, rename, resize, resource update, attach, and wait all operate on an existing container ID or name. Logs are available only when the container uses supported log drivers, and stats are live observations rather than persistent configuration.

Filesystem state appears through changes, export, and archive endpoints. `ContainerChanges` reports modified, added, and deleted paths in the writable layer. `ContainerExport` exports a full filesystem tar stream. Archive put can mutate container filesystems and may fail with `403` when a volume or rootfs is read-only.

Image operations mutate the daemon image store, content store, manifest metadata, build cache, and registry references. Pull/import creates images; build creates layers/cache and may leave or prune intermediate state depending on `rm` and `forcerm`; tag adds or overwrites references; delete can remove tags and untagged parents; prune reclaims unused storage. Platform query parameters are central for multi-platform stores and can select a single variant for history, push, save, or load.

Volumes and networks are daemon-managed persisted resources. Volume update is limited to swarm cluster volumes and guarded by object version. Volume removal can conflict when in use unless forced where supported. Network create persists driver/IPAM/options/labels, connect/disconnect changes endpoint attachments, and swarm-scoped or predefined networks reject unsupported operations.

Swarm objects persist in raft-backed cluster state. Node specs, swarm specs, service specs, tasks, secrets, and configs all have object versions and `CreatedAt`/`UpdatedAt` fields in examples. Secrets and configs can be created, listed, inspected, deleted, and label-updated, but their update docs say all fields except labels must remain unchanged. Service and task logs depend on service log drivers (`local`, `json-file`, or `journald`).

Plugins are installed daemon extensions with lifecycle state. Pull/create installs plugin content, privileges describe required host capabilities, enable/disable changes activation state, set mutates plugin settings, upgrade replaces the remote implementation while accepting privileges, and delete may disable first if forced.

## Dependencies And Integration Points

This chunk depends on OpenAPI 2.0 semantics plus Docker-specific vendor extensions and shared `definitions` declared earlier in the file. `$ref` targets such as `ContainerConfig`, `HostConfig`, `Network`, `ServiceSpec`, and `ErrorResponse` must remain stable because generated clients and documentation rely on them.

The API integrates with Docker daemon subsystems: container runtime and cgroups, graph/content/image stores, BuildKit and classic builder backends, registry authentication and distribution, volume drivers, network drivers and IPAM, plugin runtime, swarmkit raft/orchestration, logging drivers, event bus, and system information collectors.

External protocol dependencies are significant. Clients need normal JSON request/response handling, JSON serialized into query parameters, multipart-like repeated query parameters, binary tar bodies, raw HTTP hijacking, websocket support, h2c upgrade support, long-lived streaming responses, and Docker stream demultiplexing. Registry auth headers and build registry config use encoded JSON blobs that generic OpenAPI tooling will not understand semantically.

Platform integration appears throughout. The daemon may choose host platform by default, warn about mismatches, or error when a requested OCI platform variant is unavailable. Windows and Linux builder/runtime behavior diverges through builder recommendations, platform-specific image selection, network support, and cgroup/runtime details inherited from the referenced definitions.

## Risks And Edge Cases

The biggest risk is contract drift. This YAML is a public source of truth, so incorrect status codes, required flags, enum values, nullability, header names, or `$ref` targets can break generated clients or mislead users. Inline schemas such as `ExecConfig`, `NetworkCreateRequest`, `SystemDataUsageResponse`, and prune response bodies are easy to miss because they are not top-level definitions.

Generic OpenAPI clients are likely to mishandle non-JSON transports. Attach, websocket attach, exec start, logs, events, stats, build, push/pull, archive, image save/load, plugin create, and session all need special stream or binary handling. In particular, successful attach may be `101` or `200`, and `/session` success is only `101`.

JSON-in-query fields are under-specified by the Swagger type system. Filters, build args, labels, BuildKit outputs, cache sources, OCI platform selectors, and registry config/auth headers need URI encoding and stable map/list serialization. Tests should not treat the YAML `type: string` as meaning arbitrary plain text.

State-changing endpoints have conflict and membership hazards. Container delete conflicts with running containers, image delete conflicts with descendants/running use/build use, volume delete conflicts when in use, service create conflicts on names, secret/config create conflicts on names, and swarm endpoints commonly return `503` when the node is not in the required swarm state. Forced removal/leave/disable options can disrupt running workloads or cluster availability.

Security-sensitive data flows through this chunk. Registry credentials are supplied in request bodies or encoded headers. Secret and config data are base64 examples in the API surface. Build args explicitly should not be used for secret values, but clients can still send them. Plugin privileges grant host capabilities and must be reviewed before pull or upgrade.

Compatibility risks include deprecated or evolving fields. Build prune keeps `keep-storage` only for backward compatibility and documents removal in API v1.52. `ImageSearch.is_automated` is deprecated and always false. Builder default recommendations vary by OS and daemon config. Multi-platform image behavior adds new manifest fields and platform query parameters that older clients may ignore.

## Test Signals

Parse the full `sources/cloud-native/moby/api/docs/v1.48.yaml` as OpenAPI 2.0 and verify that all `$ref` targets used in lines 7759-13579 resolve. The chunk itself starts inside a schema and is not intended to parse independently.

Contract tests should verify the operation IDs, path methods, expected status codes, content types, and required parameters for every endpoint in this chunk. Pay special attention to inline schemas, required body parameters, required `version` query parameters for optimistic updates, required path IDs/names, and headers such as `X-Registry-Auth`, `X-Registry-Config`, and `X-Docker-Container-Path-Stat`.

Container integration tests should exercise create, inspect, lifecycle transitions, logs, stats, attach/websocket attach, wait conditions (`not-running`, `next-exit`, `removed`), archive head/get/put, delete with and without force/volumes, and prune filters. Assertions should include documented `204`, `304`, `400`, `403`, `404`, `409`, and `500` cases.

Image and build tests should cover build-context tar uploads, remote build contexts, BuildKit versus classic builder selection, encoded build args/labels/outputs, build cancellation on dropped connections, pull/import/tag/delete/search/prune, multi-platform history/push/save/load selection, registry auth headers, and tarball save/load format expectations.

Swarm tests should cover node update version checks, swarm init/join/leave/update token rotation, service create/update/delete/logs including rollback and registry auth source, task list/inspect/logs, and secret/config create/update/delete with label-only update constraints. Negative tests should assert `503` when swarm endpoints are used on a non-swarm node.

Transport tests should use clients capable of binary and upgraded connections. They should validate raw stream and multiplexed stream media types, websocket streams, h2c session upgrade, event streaming with `since`/`until`, tar archive upload/download, image save/load tar streams, and behavior when the client closes long-running build or push connections.
