# sources/cloud-native/moby/api/docs/v1.49.yaml lines 7768-13600

## Scope And Purpose

This chunk covers the transition from the final shared image-manifest schema into the main `paths` section of the Docker Engine API v1.49 Swagger/OpenAPI 2.0 document. It is API contract source rather than executable runtime code. The range starts inside `ImageManifestSummary`, then defines container, image/build, auth/system, exec, volume, network, plugin, swarm, service, task, secret, config, distribution, and session operations through `POST /session`.

The chunk is the public HTTP surface for most Docker daemon workflows: container lifecycle and I/O, image build/pull/push/save/load, daemon status and events, exec sessions, volume and network management, plugin installation/configuration, swarm cluster control, swarm resource CRUD, registry metadata lookup, and BuildKit-style session upgrade. It depends on definitions declared earlier in the YAML, including `ContainerConfig`, `HostConfig`, `Resources`, `ImageSummary`, `ImageInspect`, `SystemInfo`, `Volume`, `Network`, `Plugin`, `Node`, `Swarm`, `Service`, `Task`, `Secret`, `Config`, `ErrorResponse`, and common ID/update response envelopes.

## Important APIs And Types

`ImageManifestSummary` records a content-addressable manifest ID, an OCI descriptor, local availability, size accounting, kind (`image`, `attestation`, or `unknown`), optional `ImageData`, and optional `AttestationData`. `ImageData` ties a manifest to an OCI platform, container IDs using it, and unpacked image size. `AttestationData` points back to the image manifest digest it attests.

Container APIs run from `GET /containers/json` through `POST /containers/prune`. They include list, create, inspect, top, logs, filesystem changes, export, stats, TTY resize, start, stop, restart, kill, update, rename, pause/unpause, attach over hijacked HTTP or websocket, wait, delete, archive info/download/upload, and prune. Inputs combine query flags, JSON bodies, tar bodies, and binary streams. Outputs range from JSON summaries and inspect responses to raw streams and tar archives.

Image and build APIs include `ImageList`, `ImageBuild`, `BuildPrune`, `ImageCreate`, `ImageInspect`, `ImageHistory`, `ImagePush`, `ImageTag`, `ImageDelete`, `ImageSearch`, `ImagePrune`, `ImageCommit`, `ImageGet`, `ImageGetAll`, and `ImageLoad`. They use image summary/inspect/history/delete/build-cache response types, registry auth headers, platform selectors, build context tar streams, BuildKit output configuration, and image tarball formats compatible with OCI image layout plus Docker save metadata.

System APIs include `SystemAuth`, `SystemInfo`, `SystemVersion`, `SystemPing`, `SystemPingHead`, `SystemEvents`, and `SystemDataUsage`. These expose registry credential validation, daemon capability/version information, ping headers such as API version and builder version, a streaming event feed, and disk usage across images, containers, volumes, and build cache.

Exec APIs include `ContainerExec`, `ExecStart`, `ExecResize`, and `ExecInspect`. `ExecConfig` covers attached streams, TTY, console size, detach keys, environment, command, privilege, user, and working directory. `ExecStartConfig` controls detached versus interactive start, TTY, and console size. Inspect returns removable/running state, stream-open booleans, exit code, process config, container ID, and host PID.

Volume APIs include list, create, inspect, update, delete, and prune. `VolumeUpdate` is specific to swarm cluster volumes, wraps `ClusterVolumeSpec` under `Spec`, requires a `version` query parameter for optimistic concurrency, and documents that currently only availability may change.

Network APIs include list, inspect, delete, create, connect, disconnect, and prune. Network creation accepts driver, scope, internal/attachable/ingress flags, config-only/config-from fields, IPAM, IPv4/IPv6 enablement, options, and labels. Connect/disconnect operate on a container identifier and optional endpoint settings such as IPAM address, MAC address, and priority.

Plugin APIs cover list, privilege discovery, pull, inspect, delete, enable, disable, upgrade, create from tar, push, and set configuration. Pull and upgrade accept `PluginPrivilege` arrays and optional `X-Registry-Auth`. Local create consumes `application/x-tar`; set accepts an array of strings such as environment-style settings.

Swarm-mode APIs include node list/inspect/delete/update, swarm inspect/init/join/leave/update/unlock-key/unlock, service list/create/inspect/delete/update/logs, task list/inspect/logs, secret list/create/inspect/delete/update, and config list/create/inspect/delete/update. They reference swarmkit-style object specs and require object `version` values for mutable cluster objects.

`DistributionInspect` contacts a registry for descriptor and platform information about an image name. `Session` upgrades an HTTP request to an h2c raw stream so the daemon and client can run advanced callback services over the upgraded connection.

## Control Flow And Protocol Behavior

The container surface models the Docker CLI workflow as discrete HTTP calls: list or create a container, inspect it, start it, attach/log/exec/stats/resize while it runs, update resources, pause or unpause, stop/restart/kill, wait for termination, copy archives in or out, delete the object, and prune stopped containers in bulk. State transitions are encoded with status codes: start/stop use `204` for success and `304` for already-started or already-stopped states; kill returns `409` when a target is not running; delete returns `409` for conflicts such as removing a running container without force.

Streaming and upgraded transports are central. Container logs and stats can hold long-lived responses. Attach can hijack the HTTP connection with `200` or use `101 UPGRADED` when upgrade headers are supplied. Non-TTY attach streams are multiplexed with an 8-byte header containing stream type and payload size; TTY streams are raw PTY data. Exec start reuses the same raw or multiplexed stream media types. Service and task logs also produce raw/multiplexed stream bodies. `Session` upgrades to h2c rather than ordinary JSON request/response.

Image build/create/push/load operations are cancellation-sensitive: the build and push descriptions state the operation is cancelled when the client connection closes. Build accepts a tar archive or remote context, validates Dockerfile syntax before executing instructions, supports classic builder versus BuildKit selection by `version`, and can pass registry credentials in a base64-encoded `X-Registry-Config` header. Image save/load endpoints use tar streams and platform selectors for multi-platform images.

Swarm control flow is optimistic and cluster-state dependent. Init creates a swarm; join requires manager addresses and a token; leave can be forced; update requires a current swarm version and can rotate worker, manager, or unlock credentials. Node, service, secret, config, and cluster-volume updates all require a version number to avoid conflicting writes. Service update has a special `rollback=previous` branch where the submitted spec is ignored.

List and prune endpoints repeatedly encode structured filters as JSON inside a string query parameter. This pattern appears on containers, images, build cache, events, volumes, networks, plugins, nodes, services, tasks, secrets, and configs. Generated clients need custom handling because the OpenAPI type is usually just `string` even though the semantic contract is `map[string][]string`.

## State And Persistence Behavior

Container state is persisted by the daemon and exposed through list, inspect, logs, filesystem-diff, archive, wait, and lifecycle endpoints. Create-time `ContainerConfig`, `HostConfig`, and `NetworkingConfig` become durable container configuration; runtime fields such as PID, health, mounts, network attachments, restart count, log path, and active exec IDs appear through inspect. Archive PUT mutates a container filesystem, while export/archive GET expose filesystem snapshots as tar streams.

Images and build cache are content-addressed persistent daemon resources. Image list/inspect/history/delete/search/prune operate on local metadata and registry references. Build creates image content and cache records; build prune deletes cache according to space targets and filters. Image save/load preserve image metadata in tar archives; platform query parameters select one variant or all variants for multi-platform image stores.

Volumes persist independently of containers and are mediated by volume drivers. Volume delete can fail if a volume is still in use; prune deletes unused volumes and reports reclaimed space. Cluster volume update is swarm-scoped and versioned, with the spec requiring most fields to remain unchanged.

Networks persist driver, IPAM, labels, options, scope, config-only/config-from relationships, and endpoint attachments. Built-in networks have protected behavior; swarm-scoped networks require attachability for direct container connects. Network list intentionally returns a smaller representation than inspect.

Plugins persist installed rootfs/manifest content, enabled state, accepted privileges, mutable settings, and registry references. Force disable/delete can change active daemon extension points that may be used by other resources. Pull and upgrade persist registry-sourced plugin artifacts but do not by themselves imply all runtime configuration is safe or active.

Swarm objects are replicated cluster state. Nodes, swarm spec, services, tasks, secrets, and configs are available only when the daemon is part of a swarm, otherwise many operations return `503`. Services store desired state and produce tasks as scheduler output. Secrets and configs use create/inspect/delete/update lifecycles, but updates document label-only mutation while payload/spec fields must remain unchanged from inspect responses.

Events and stats are observational streams rather than durable objects, but they expose transitions from persisted daemon resources. System data usage aggregates persisted image, container, volume, and build cache state.

## Dependencies And Integration Points

This chunk depends on OpenAPI 2.0 tooling, Docker's API documentation/generation pipeline, and vendor extensions from the surrounding file such as `x-nullable`, `x-omitempty`, and `x-go-name`. Operation IDs are stable integration names for generated SDK methods and documentation anchors.

Daemon subsystem dependencies include the container runtime, cgroups, storage graph drivers, log drivers, tar archive handling, image content store, BuildKit/classic builder, registry client, auth configuration, libnetwork/IPAM, volume drivers, plugin manager, swarmkit, secrets/config stores, event bus, and system inventory collectors.

External integrations include image and plugin registries using base64 or base64url registry auth headers, remote Git/HTTP build contexts, OCI image layout consumers, HTTP clients and proxies capable of raw hijack/websocket/h2c upgrade, volume/network/logging/auth plugins, swarm managers reachable by remote addresses, and logging backends supported by service/task/container log endpoints.

Platform integration points are explicit. `ContainerTop` is Unix-only; stats differ across cgroup v1 and cgroup v2; create and image APIs use `os[/arch[/variant]]` or JSON-encoded OCI platform selectors; Windows-specific isolation and host controls are carried by shared schemas referenced in this path section.

## Risks And Edge Cases

The biggest contract risk is mismatch between the OpenAPI shape and the real protocol. Binary streams, tar bodies, raw hijacked connections, websocket attach, h2c session upgrades, and JSON-in-query filters are poorly represented by simple generated clients. Tests should exercise these with real HTTP transports.

Destructive operations have broad side effects. Container, image, build-cache, volume, and network prune endpoints can delete many resources depending on filters. Force flags on container delete, volume delete, plugin delete/disable, node delete, and swarm leave can disrupt running workloads or cluster health. Incorrect filter encoding can make destructive calls broader than intended.

Versioned swarm writes are vulnerable to stale-client behavior. Node, swarm, service, secret, config, and cluster-volume updates must reject or otherwise handle stale `version` values. Service rollback is another edge case because the server ignores the submitted spec when `rollback=previous`.

Platform and daemon capability differences affect compatibility. cgroup v2 omits or changes stats fields; `one-shot` stats must be paired with `stream=false`; container logs work only for documented logging drivers; service/task logs require `local`, `json-file`, or `journald`; swarm endpoints use `503` when not in the right swarm state; overlay/network operations may be forbidden outside swarm.

Registry and auth responses can be ambiguous. Distribution inspect uses `401` for both authentication failure and no image found. Image pull/create platform selection can warn or pull different variants depending on local cache state. Push without an explicit platform may try all available variants.

Mutable archive and exec endpoints need careful authorization and path handling. `PutContainerArchive` can replace filesystem content, has read-only rootfs/volume `403` behavior, and has flags controlling directory/non-directory overwrite and UID/GID mapping. Exec creation can request privileged execution inside a running container and fails on paused containers.

## Test Signals

Validation should parse the full `sources/cloud-native/moby/api/docs/v1.49.yaml` as OpenAPI 2.0 and verify all `$ref` targets used in lines 7768-13600 resolve. This chunk is not standalone YAML because it begins inside a definition and relies on earlier shared schemas.

Container integration tests should cover list filters, create with `HostConfig` and `NetworkingConfig`, platform mismatch warnings, inspect with and without `size`, start/stop `204` versus `304`, kill `409`, pause/unpause, wait conditions, update warnings, archive HEAD/GET/PUT, delete conflicts, and prune filter behavior.

Transport tests should cover attach with and without upgrade headers, websocket attach, TTY raw stream versus non-TTY multiplex framing, logs with `follow`, stats streaming and `stream=false&one-shot=true`, exec start interactive streams, service/task logs, image tar export/load, plugin tar create, and h2c session upgrade.

Image/build tests should cover build context tar input, remote context, Dockerfile path, BuildKit output JSON, builder version selection, registry config header decoding, image pull/import branches, push auth, platform-specific inspect/history/save/load/push, image delete force/noprune, build/image prune filters, and OCI/Docker save tarball contents.

Swarm tests should distinguish `404` missing-object responses from `503` not-in-swarm responses. They should exercise swarm init/join/update/leave/unlock, node update with stale/current versions, service create/update/delete/logs including `registryAuthFrom` and rollback, task list/inspect/logs, secret/config create/inspect/delete/update with label-only update enforcement, and cluster-volume update version checks.

System and plugin tests should verify auth success/identity-token and failure cases, ping headers for API/builder/experimental/swarm/cache-control, event stream filters, system data usage type filtering, plugin privilege discovery, pull/enable/disable/set/upgrade/push/delete flows, registry auth for plugin operations, and force behavior when plugins are in use.
