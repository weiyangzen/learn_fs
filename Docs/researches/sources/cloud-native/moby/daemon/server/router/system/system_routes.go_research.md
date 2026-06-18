# sources/cloud-native/moby/daemon/server/router/system/system_routes.go

## Purpose
`system_routes.go` implements daemon system endpoints for ping, info, version, disk usage, events, and registry authentication.

## Important APIs, Types, And Functions
Handlers include `optionsHandler`, `pingHandler`, `getInfo`, `getVersion`, `getDiskUsage`, `getEvents`, and `postAuth`. Helpers include `swarmStatus`, `nonNilSlice`, `invalidRequestError`, `jsonTypes`, and `backFillLegacy`.

## Control Flow
Ping writes cache-control, builder version, swarm status, and OK/HEAD response. Info uses singleflight, merges cluster swarm info/warnings, and strips/injects fields by API version. Disk usage parses object types, runs daemon and build-cache usage in an errgroup, emits legacy and/or new shapes, and injects image `VirtualSize` for older APIs. Events parse `since/until/filters`, choose content type from API version and Accept header, flush headers, emit buffered then live events, optionally backfilling legacy fields. Auth decodes credentials and delegates to the backend.

## State And Persistence
System routes mostly read daemon state. Event subscriptions allocate a backend channel until deferred unsubscribe. Auth may update registry auth state depending on backend implementation.

## Dependencies And Integration Points
Depends on API system/events/registry/swarm types, filters, timestamp parsing, content negotiation, build router builder-version helper, errgroup, stream encoders, and compatibility wrappers.

## Risks
Streaming events cannot return normal errors after headers flush. `/info` response shape is highly version-sensitive. Disk usage concurrently writes shared variables after errgroup tasks, so each variable has a single writer. API 1.52 dual legacy/current disk-usage behavior is temporary and fragile.

## Test Signals
Local disk-usage tests cover `VirtualSize`. Integration tests should cover ping headers, info fields by version, event streaming content types, and auth.
