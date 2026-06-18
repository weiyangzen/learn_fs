# sources/cloud-native/moby/daemon/server/router/system/system.go

## Purpose
`system.go` defines the system router, including routes for ping, events, info, version, disk usage, auth, and OPTIONS.

## Important APIs, Types, And Functions
`systemRouter` stores backend, cluster, builder, features callback, route list, and a `singleflight.Group` for `/info` responses keyed by API version. `NewRouter` registers all system routes.

## Control Flow
Construction stores backends and route metadata. `/info` later uses the singleflight group to collapse concurrent collection for the same API version.

## State And Persistence
The router stores in-memory backend references and singleflight state. It does not persist data.

## Dependencies And Integration Points
Integrates `compat`, shared router constructors, and `resenje.org/singleflight`.

## Risks
The singleflight key is API version because response shape differs by version; using a broader key would leak wrong compatibility fields.

## Test Signals
System API tests validate route behavior; no direct tests for router construction here.
