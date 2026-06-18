# sources/cloud-native/moby/daemon/cluster/convert/pluginadapter.go

## Purpose
Adapts Docker's plugin getter interfaces to swarmkit's plugin getter/plugin interfaces while preserving optional address support.

## Important APIs, Types, And Functions
Exports `SwarmPluginGetter`. Defines `pluginGetter`, `swarmPlugin`, `addrPlugin`, `adaptPluginForSwarm`, and methods `Get` and `GetAllManagedPluginsByCap`.

## Control Flow
`Get` calls the daemon plugin getter with lookup mode and wraps the returned compatible plugin. `GetAllManagedPluginsByCap` wraps every managed plugin. `adaptPluginForSwarm` chooses `addrPlugin` if the plugin also exposes `PluginAddr`; otherwise it uses `swarmPlugin`.

## State And Persistence
No state beyond holding the delegated plugin getter.

## Dependencies And Integration Points
Used when constructing swarmkit components that need plugin access. Bridges `pkg/plugingetter` and `swarmkit/node/plugin`.

## Risks And Test Signals
Compile-time interface assertions verify adapter shape. No direct tests; integration failures would appear in swarm networking/volume plugin discovery.
