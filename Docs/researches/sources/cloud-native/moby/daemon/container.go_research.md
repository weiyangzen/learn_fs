<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container.go -->
# sources/cloud-native/moby/daemon/container.go

## Purpose
Implements daemon-level container lookup, loading, registration, creation, dependency discovery, and common container/host-config validation.

## Important APIs, Types, And Functions
`GetContainer`, `load`, `register`, `newContainer`, `getEntrypointAndArgs`, `GetByName`, `GetDependentContainers`, `setSecurityOptions`, `verifyContainerSettings`, `validateContainerConfig`, `validateHostConfig`, `validateCapabilities`, `validateHealthCheck`, `validatePortBindings`, `translateWorkingDir`.

## Control Flow
Lookup tries exact ID, exact name, then unique prefix through the replica view. Registration initializes stdin pipes, locks the container, adds it to the live store, and checkpoints to the replica/disk. Creation generates ID/name, sets hostname, entrypoint args, image/platform fields, and base metadata. Validation checks working dir, stop signal, env, healthcheck timing, mounts, extra hosts, ports, restart policy, capabilities, isolation, annotations, then platform validation.

## State And Persistence Behavior
`load` reads from disk; `register` writes checkpoint data and updates in-memory stores. `newContainer` constructs unsaved state.

## Dependencies And Integration Points
Integrates container store/view DB, image service, network settings, link index, mount parser, capabilities normalization, errdefs, and daemon platform validation.

## Risks And Test Signals
Risks include non-atomic register add/checkpoint, `getEntrypointAndArgs` assuming non-empty cmd when entrypoint absent, replica/live store skew, and validation gaps on nil configs. Container creation/start tests are downstream signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container.go -->
