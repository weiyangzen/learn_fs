# sources/cloud-native/moby/daemon/server/router/plugin/plugin.go

## Purpose
`plugin.go` defines the plugin router and registers plugin HTTP API endpoints.

## Important APIs, Types, And Functions
`pluginRouter` stores a backend and route list. `NewRouter`, `Routes`, and `initRoutes` implement route setup.

## Control Flow
Routes include list, inspect, privileges, remove, enable, disable, pull, push, upgrade, set, and create. Upgrade is gated at API 1.26.

## State And Persistence
The router has no persistent state; plugin state changes occur in backend calls.

## Dependencies And Integration Points
Uses the shared router package and route constructors.

## Risks
The wildcard `{name:.*}` route patterns are necessary for plugin names containing slashes/tags but can overlap if new routes are added carelessly.

## Test Signals
Plugin API integration tests validate route behavior.
