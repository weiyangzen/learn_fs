# sources/distributed-fs/ipfs-kubo/core/commands/mount_unix.go

## Purpose

`mount_unix.go` implements the real FUSE-backed `ipfs mount` command for Linux, Darwin, and FreeBSD builds without the `nofuse` tag. It mounts read-only `/ipfs`, `/ipns`, and `/mfs` views into the host filesystem.

## Important APIs, Types, and Functions

The file defines mount path option constants and `MountCmd`. It reads `config.Mounts`, retrieves the live `IpfsNode`, and delegates actual FUSE setup to `fuse/node.Mount`. The output type is `config.Mounts`, with a text encoder printing mounted paths.

## Control Flow

The command loads config from the old command context, obtains the node, rejects offline nodes with `ErrNotOnline`, resolves each mount point from explicit options or config defaults, and calls `nodeMount.Mount(nd, fsdir, nsdir, mfsdir)`. On success it emits the effective mount paths. The text encoder formats IPFS/IPNS/MFS lines and escapes non-printable path content.

## State and Persistence Behavior

The command does not persist config changes; option overrides affect only the invocation. It creates OS-level FUSE mounts that live outside the repo and must be unmounted by platform tooling or process lifecycle. It requires an online node because mounted paths resolve through the active node.

## Dependencies and Integration Points

Dependencies include `go-ipfs-cmds`, legacy command context config loading, `cmdenv.GetNode`, Kubo config types, and `github.com/ipfs/kubo/fuse/node`. Compile-time integration is governed by `(linux || darwin || freebsd) && !nofuse`.

## Risks and Test Signals

Risks include platform permissions, stale mount points, offline node rejection, missing config defaults, and FUSE implementation failures bubbling up. Tests should cover option fallback/override, offline error, encoder escaping, build-tag selection, and integration tests that validate mount readability for known IPFS/IPNS/MFS paths on supported platforms.
