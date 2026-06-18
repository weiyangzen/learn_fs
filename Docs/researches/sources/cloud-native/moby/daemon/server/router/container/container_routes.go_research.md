# sources/cloud-native/moby/daemon/server/router/container/container_routes.go

## Purpose
Implements the Docker container HTTP API handler layer. It parses and validates requests, applies API-version compatibility behavior, negotiates stream formats, handles hijacked/websocket streams, and delegates actual container work to the container backend interface.

## Important APIs, Types, And Functions
Major handlers include `postCommit`, `getContainersJSON`, `getContainersStats`, `getContainersLogs`, `postContainersStart`, `postContainersStop`, `postContainersKill`, `postContainersRestart`, `postContainersPause`, `postContainersUnpause`, `postContainersWait`, `getContainersChanges`, `getContainersTop`, `postContainerRename`, `postContainerUpdate`, `postContainersCreate`, `deleteContainers`, `postContainersResize`, `postContainersAttach`, `wsContainersAttach`, `postContainersPrune`, exec handlers, and archive handlers. Compatibility helpers include `decodeCommitRequest`, `handleVolumeDriverBC`, `rejectLegacyCapabilities`, `handleMACAddressBC`, `handleSysctlBC`, `handlePortBindingsBC`, and `epConfigForNetMode`.

## Control Flow
Handlers generally call `httputils.ParseForm` and/or `ReadJSON`, convert query/body data to backend option structs, check `httputils.VersionFromContext`, and call backend methods. Create is the most complex path: it decodes the create request while teeing the body for removed legacy fields, normalizes default network mode, applies many API-version shims for mounts, IPC, cgroup namespace, console size, annotations, healthcheck start interval, multiple networks, image mounts, gateway priority, MAC address, sysctls, port bindings, and pids limits, then calls `ContainerCreate` and appends warnings. Logs validate stdout/stderr before streaming, parse since/until, optionally select experimental JSON streaming by query or strict Accept header, and otherwise choose raw versus multiplexed stream content type. Attach hijacks HTTP or uses websockets, prepares streams, and writes in-band error responses when hijack-time attach fails. Wait handles legacy pre-1.30 and pre-1.34 response timing/removal behavior.

## State And Persistence
The router itself persists no daemon state, but backend calls mutate containers, execs, archives, logs, images, and prune state. Handlers mutate decoded request structs for backward compatibility before passing them down. Streaming handlers commit headers early; after that, errors are written in-band or logged.

## Dependencies And Integration Points
This file is the main integration point between HTTP routes and daemon backends. It depends on Docker API media types, container/mount/network types, daemon filters, runconfig decoding, timestamp parsing, API version helpers, netlabel endpoint sysctls, backend option structs, HTTP status mapping, content negotiation, log stream writers, errdefs, OpenTelemetry, and websockets.

## Risks And Edge Cases
API compatibility logic is dense and version-sensitive. Create request body teeing is required because removed fields would otherwise disappear during JSON decoding. Hijack attach paths manually write HTTP status lines and ignore some write errors. Once logs/stats/wait streams write headers, status-code error reporting is no longer possible. MAC/sysctl migration must avoid ambiguous networks. The commented-out future port-binding behavior shows pending compatibility debt.

## Test Signals
The listed files do not include route-specific tests, but this handler should be covered by API integration tests for create compatibility, logs media types, attach streams, wait behavior, resize parsing, archive operations, exec lifecycle, prune, commit, update, and route error mapping.
