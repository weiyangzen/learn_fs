# sources/cloud-native/moby/daemon/cluster/controllers/plugin/controller.go

## Purpose
Implements a swarmkit task controller for Docker plugins, treating a plugin as a singleton with desired enabled/disabled state instead of a container-like process lifecycle.

## Important APIs, Types, And Functions
Defines `Controller`, `Backend`, `NewController`, `readSpec`, lifecycle methods `Update`, `Prepare`, `Start`, `Wait`, `Shutdown`, `Terminate`, `Remove`, `Close`, helper `isNotFound`, and `convertPrivileges`.

## Control Flow
`Prepare` parses the remote reference, defaults name, checks existing plugin ownership by swarm service ID, disables before upgrade when needed, pulls new plugins with service/env options, stores `pluginID`, and acquires a plugin ref on success. `Start` reconciles enabled state. `Wait` subscribes to enable/disable/remove events and returns errors when actual state diverges or plugin is removed. `Remove` releases the ref and removes only when refcount reaches zero.

## State And Persistence
Controller state holds desired spec, service ID, plugin ID, and logger. Persistent plugin state is managed by the plugin backend; refcounting protects singleton removal across multiple tasks.

## Dependencies And Integration Points
Connects swarmkit generic runtime plugin specs, daemon plugin manager backend, registry references, plugin events, and Docker plugin API privilege structures.

## Risks And Test Signals
Registry auth is intentionally unsupported. Existing plugin name conflicts across services fail prepare. Event races are mitigated in tests with `signalWaitReady`. Tests cover prepare pull/upgrade/conflict, start state, wait cancellation/state drift/removal, and refcounted remove.
