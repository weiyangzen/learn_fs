# sources/control-plane/rook/pkg/daemon/ceph/osd/nsenter.go

## Purpose
`nsenter.go` provides a small helper for checking or invoking host binaries from inside the Rook container by entering the host mount namespace. It is used by OSD preparation code to ensure host-level tooling such as LVM exists where needed.

## Important APIs, Types, and Functions
`NSEnter` stores a daemon context, target binary name, and binary arguments. `NewNsenter()` constructs it. `buildNsEnterCLI()` produces arguments for `nsenter --mount=/rootfs/proc/1/ns/mnt -- <binary-path> ...`. `callNsEnter()` executes `nsenter` via the configured executor. `checkIfBinaryExistsOnHost()` iterates known host binary directories and succeeds if either executing through `nsenter` works or the binary can be found under `/rootfs`.

## Control Flow
For each candidate directory in `binPathsToCheck`, `checkIfBinaryExistsOnHost()` joins the path with the requested binary and tries to run it in the host mount namespace. If execution fails, it falls back to `os.Stat("/rootfs/<candidate>")` without executing the host binary, avoiding library mismatch problems between container and host. The first successful execution or stat returns nil; exhausting all paths returns an error.

## State and Persistence
The helper has no persistent state. It reads `/rootfs` and invokes the `nsenter` binary. Success depends on container privileges, host mount namespace visibility, and bind-mounted host root.

## Dependencies and Integration Points
It depends on Rook's executor abstraction and is called by `lvmPreReq()` in `volume.go` before LVM mode initialization. It integrates with host paths common to Linux distributions, including NixOS-style `/run/current-system/sw` paths.

## Risks
The fallback `os.Stat()` only proves the binary path exists, not that it can execute successfully in the host namespace. The list of binary directories is hard-coded and may miss unusual distributions. `callNsEnter()` wraps combined output on error, but the outer checker logs failures only at debug level until all candidates fail.

## Test Signals
`nsenter_test.go` verifies CLI construction and a mocked successful lookup for `/usr/sbin/lvm` or `/sbin/lvm`. It does not cover the `/rootfs` stat fallback, all-paths-fail errors, or non-LVM binaries.
