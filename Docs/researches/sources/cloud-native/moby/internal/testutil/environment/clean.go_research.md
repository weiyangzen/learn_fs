# sources/cloud-native/moby/internal/testutil/environment/clean.go

## Purpose
Implements environment cleanup for integration tests by removing all unprotected daemon resources after each test while preserving baseline protected objects.

## Important APIs, Types, And Functions
- `(*Execution).Clean` coordinates cleanup for containers, images, volumes, networks, Linux plugins, and default bridge restoration.
- `unpauseAllContainers` and `getPausedContainers` ensure paused containers can be removed.
- `deleteAllContainers`, `deleteAllImages`, `removeImage`, `deleteAllVolumes`, `deleteAllNetworks`, and `deleteAllPlugins` perform resource-specific cleanup.

## Control Flow
`Clean` starts an OpenTelemetry span, obtains the environment API client, unpauses containers when supported, removes unprotected containers/images/volumes/networks, then on Linux removes unprotected plugins and restores default bridge state. Resource deletion helpers list current objects, skip protected IDs/names and default networks, and force removal where appropriate.

## State And Persistence
Mutates the shared test daemon by deleting resources created during tests. Protected maps in `Execution` decide what persists. Linux cleanup also restores default bridge settings.

## Dependencies And Integration Points
Uses Moby client interfaces for container/image/volume/network/plugin APIs, containerd errdefs, OpenTelemetry, and environment protection state. Called by package `setupTest` cleanup functions across integration packages.

## Risks And Edge Cases
Broad cleanup can hide resource leaks but is required for isolation. It ignores not-found images and container removal already in progress. Windows preserves predefined NAT network and skips plugin/default-bridge cleanup. Docker EE may return not-implemented for cluster-wide plugin management, which is ignored.

## Test Signals
Expected signals are no unprotected containers/images/volumes/networks/plugins remaining after cleanup, paused containers unpaused before removal, protected resources preserved, and bridge state restored on Linux.
