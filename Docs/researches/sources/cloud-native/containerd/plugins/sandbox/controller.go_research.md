# sources/cloud-native/containerd/plugins/sandbox/controller.go

## Purpose
Registers the shim-backed sandbox controller plugin that creates, starts, stops, waits, queries, and shuts down runtime v2 sandbox shims.

## Important APIs, Types, And Functions
`controllerLocal` implements `sandbox.Controller`. Key methods are `Create`, `Start`, `Platform`, `Stop`, `Shutdown`, `Wait`, `Status`, `Metrics`, `Update`, and `getSandbox`. `cleanupShim` handles failed creation/start cleanup.

## Control Flow
Startup loads shim manager and event exchange, creates/chmods root and state directories, loads existing shims, and returns a controller. Create ensures no existing shim, creates a bundle, starts a shim, builds a sandbox TTRPC client, and calls `CreateSandbox`. Start calls `StartSandbox` and returns instance metadata. Stop/Shutdown/Wait/Status/Metrics forward to shim sandbox services with error translation and cleanup behavior.

## State And Persistence
Bundles, shim state, and root/state directories are persisted under plugin paths. Active shim processes and TTRPC endpoints represent runtime state. Existing shims are loaded on daemon startup.

## Dependencies And Integration Points
Requires shim and event exchange plugins. Integrates with runtime v2 shim manager, sandbox API, mount proto conversion, typeurl options, errgrpc translation, and containerd sandbox core interfaces.

## Risks
Cleanup paths must shut down shim services and delete shim state to avoid leaks. Status returns an exited status when the shim is not found. `Update` is currently a no-op. Directory permission changes matter for upgrades and security.

## Test Signals
No direct tests in this subset; runtime sandbox service integration tests are needed.
