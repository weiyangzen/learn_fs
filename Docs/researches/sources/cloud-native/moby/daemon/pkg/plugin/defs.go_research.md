<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/defs.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/defs.go

## Purpose
Defines shared plugin store state and option hooks used by the plugin manager and daemon subsystems.

## Important APIs, Types, And Functions
`Store` holds plugins, runtime spec modifiers, and legacy handlers under an RW mutex. `NewStore` initializes maps. `SpecOpt`, `CreateOpt`, `WithSwarmService`, `WithEnv`, and `WithSpecMounts` provide extension points.

## Control Flow
`WithEnv` builds effective environment values from configured defaults and user-provided `key=value` entries, then stores de-duplicated settings. `WithSpecMounts` appends mounts to an OCI spec when invoked.

## State, Dependencies, And Integration Points
Store is the in-memory plugin inventory; plugin config persists elsewhere through manager save. Hooks integrate managed plugins with swarm, env overrides, runtime spec customization, and legacy plugin handlers.

## Risks And Test Signals
`WithEnv` uses map iteration, so environment order is unstable. Invalid env lines are ignored. Store concurrency relies on callers using the provided locks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/defs.go -->
