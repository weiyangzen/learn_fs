# sources/cloud-native/moby/daemon/pkg/oci/defaults.go

## Purpose
This file defines Docker's default OCI specs and default PATH environment values for Linux and Windows containers.

## Important APIs, Types, And Functions
`DefaultPathEnv`, `DefaultSpec`, `DefaultWindowsSpec`, and `DefaultLinuxSpec` are the public constructors. `iPtr` creates int64 pointers for device cgroup entries. `defaultLinuxMaskedPaths` computes and caches default masked paths.

## Control Flow
`DefaultSpec` dispatches by `runtime.GOOS`. Windows specs contain version, Windows, process, and root structs. Linux specs include default process capabilities, root, standard mounts (`/proc`, `/dev`, `/dev/pts`, `/sys`, cgroup, mqueue, `/dev/shm`), Linux namespaces, masked/readonly paths, empty device list, and default device cgroup allow/deny rules. `defaultLinuxMaskedPaths` starts with sensitive proc/sys paths and appends CPU thermal throttle paths that exist on the host.

## State, Persistence, And Dependencies
The only cached state is `defaultLinuxMaskedPaths` via `sync.OnceValue`. The function reads host CPU topology and filesystem path existence. Dependencies include runtime-spec types, default capability set, internal platform CPU helpers, standard `os/runtime/sync/fmt`.

## Integration Points
Linux and Windows daemon `createSpec` functions start from this default before applying container-specific mutations. Default masked paths include security-advisory-driven protections.

## Risks And Edge Cases
Default Linux mount and device cgroup rules are security-sensitive. Cached masked paths do not change until daemon restart. Windows returns an empty default PATH because Docker cannot infer it outside the image/container context.

## Test Signals
No direct tests in this subset. OCI Linux tests inspect downstream effects of these defaults, especially mounts and resources.
