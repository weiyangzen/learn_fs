# sources/cloud-native/moby/daemon/volume/drivers/adapter.go

## Purpose
Adapts legacy/HTTP volume plugin RPC clients to the daemon's `volume.Driver` and `volume.Volume` interfaces.

## Important APIs, Types, And Functions
`volumeDriverAdapter` implements driver operations by delegating to a generated `volumeDriver` proxy. `volumeAdapter` implements `volume.Volume` for plugin-returned volumes. `proxyVolume` mirrors plugin JSON fields. `getCapabilities` caches and normalizes driver capability scope.

## Control Flow
`Create` calls plugin `Create` and returns a `volumeAdapter`. `List` wraps each plugin `proxyVolume` and scopes mountpoints through plugin `ScopedPath`. `Get` handles the plugin edge case of nil volume plus nil error as `errNoSuchVolume`. `Path` lazily calls the plugin and caches an ephemeral mount path; `Mount` refreshes the cache, and successful `Unmount` clears it. Capability lookup defaults to local scope on endpoint error, lowercases scope, and falls back to local for invalid values.

## State And Persistence
State is in-memory only: cached capabilities, cached mount path, created time, and plugin status map. Persistent volume data belongs to the plugin.

## Dependencies And Integration Points
Integrates generated proxy RPC calls, plugin scoped paths, containerd logging, and the daemon volume interfaces consumed by `VolumeStore` and API service conversion.

## Risks
Path cache staleness is possible if plugin state changes out of band. Ignoring errors in `Path` can hide plugin failures. Capability fallback to local is conservative but can change cluster scheduling semantics for broken plugins. Status defensively copies maps; callers should preserve that protection.

## Test Signals
Proxy tests validate plugin error strings; store tests exercise adapter creation indirectly through fake plugin references and create-error dereferencing.
