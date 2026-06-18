# sources/cloud-native/containerd/plugins/nri/plugin.go

## Purpose
Registers the Node Resource Interface API plugin.

## Important APIs, Types, And Functions
`init` registers `plugins.NRIApiPlugin` with ID `nri`, default NRI config, and `initFunc`. `initFunc` calls `nri.New`.

## Control Flow
Startup requires the internal plugin type, casts config to `*nri.Config`, constructs the NRI listener/service, and returns it.

## State And Persistence
No direct persistence in this wrapper. Runtime state is managed by the internal NRI package.

## Dependencies And Integration Points
Integrates with `internal/nri` and plugin registry. Other CRI/runtime paths can use the NRI API plugin.

## Risks
All validation and side effects are delegated to `nri.New`; this wrapper has little defensive logic beyond dependency registration.

## Test Signals
No direct tests in this subset.
