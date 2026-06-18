# sources/cloud-native/moby/daemon/volume/volume.go

## Purpose
Defines daemon volume interfaces and shared constants for driver/volume implementations.

## Important APIs, Types, And Functions
`DefaultDriverName` is `local`. Scopes are `LocalScope` and `GlobalScope`. Interfaces are `Driver`, `Volume`, optional `LiveRestorer`, and `DetailedVolume`. `Capability` carries driver scope.

## Control Flow
No runtime logic; this is an interface contract file.

## State And Persistence
No state. Implementations such as local driver and plugin adapters provide persistence and runtime behavior.

## Dependencies And Integration Points
Implemented by local volumes, plugin adapters, wrappers, and test fakes. Consumed by driver store, volume store/service, mount setup, and API conversion.

## Risks
Interface changes have a wide blast radius across daemon drivers, plugins, tests, and persisted mountpoint behavior. Scope values influence swarm/cluster handling and plugin validation.

## Test Signals
Compilation plus broad service/store/local/driver tests validate that implementations satisfy the contracts. `volumeWrapper` and `localVolume` explicitly assert optional live restore support.
