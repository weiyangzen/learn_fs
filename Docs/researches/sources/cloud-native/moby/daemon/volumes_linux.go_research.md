# sources/cloud-native/moby/daemon/volumes_linux.go

## Purpose
Linux implementation of daemon-root bind validation used while registering bind mounts.

## Important APIs and Types
Defines `(*Daemon).validateBindDaemonRoot(mount.Mount) (bool, error)`.

## Control Flow, State, and Persistence
Non-bind mounts are ignored. For bind mounts, the function checks whether the mount source is inside the daemon root or the daemon root is inside the source. If unrelated, no special handling is required. If related and no propagation is specified, it returns `needsProp=true`, allowing callers to force `rslave`. Explicit `rslave` and `rshared` are accepted; private, shared, slave, and recursive-private modes are rejected as invalid parameters.

## Dependencies, Integration Points, Risks, and Test Signals
Used by `registerMountPoints` for both legacy binds and structured mounts. It depends on string prefix checks, `api/types/mount`, and `errdefs.InvalidParameter`. The risk is filesystem-prefix ambiguity if paths are not normalized upstream, because this file uses raw prefixes. `volumes_linux_test.go` exercises root, parent, child, and `/` sources with valid and invalid propagation modes.
