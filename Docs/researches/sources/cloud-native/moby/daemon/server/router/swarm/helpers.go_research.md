# sources/cloud-native/moby/daemon/server/router/swarm/helpers.go

## Purpose
`helpers.go` contains shared swarm route helpers for log streaming and API-version normalization of service specs.

## Important APIs, Types, And Functions
`swarmLogs` validates log flags, builds `backend.ContainerLogsOptions`, detects TTY from selected services/tasks, calls `ServiceLogs`, sets raw or multiplexed stream media type, and streams via `logstream.Write`. `adjustForAPIVersion` strips unsupported service-spec fields for older API versions.

## Control Flow
Log handling validates `stdout`/`stderr` before starting the stream, parses `since`, computes `Follow`, `Tail`, `Details`, and TTY mode, then writes logs. Version adjustment removes swap/memory swappiness before 1.52, tmpfs options before 1.46, sysctls/credential config/config runtime/max replicas before 1.40, capabilities/ulimits/pids/jobs before 1.41, security options and health start interval before 1.44, maps legacy `Networks` into `TaskTemplate.Networks` before 1.44, and strips `OomScoreAdj` before 1.46.

## State And Persistence
No persistent state is written directly. `adjustForAPIVersion` mutates the in-memory request spec before backend persistence.

## Dependencies And Integration Points
Integrates timestamp parsing, version helpers, backend log APIs, logstream writer, and API swarm/container/mount types.

## Risks
Errors must be returned before log streaming begins. TTY detection requires backend reads for every selector. Version stripping must remain synchronized with API evolution to avoid unsupported fields reaching swarmkit.

## Test Signals
`helpers_test.go` exercises key stripping boundaries for resources, tmpfs options, sysctls, credential specs, runtime config refs, max replicas, ulimits, and pids.
