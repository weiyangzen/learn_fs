# sources/cloud-native/containerd/internal/cri/opts/container.go

## Purpose

This file defines containerd `NewContainerOpts` used by CRI container creation for robust snapshot preparation and image-defined volume initialization.

## Important APIs, Types, and Functions

`WithNewSnapshot` wraps `containerd.WithNewSnapshot`; if snapshot creation fails with not-found, it unpacks the image for the snapshotter and retries. `unpackImage` creates a lease, builds an unpacker for the default platform/snapshotter, optionally appends snapshot labels, dispatches image content, and waits for unpack completion. `WithVolumes` mounts the container rootfs snapshot read-only and copies image volume contents to host volume directories. `copyExistingContents` requires the destination volume directory to be empty and copies source contents excluding SELinux xattrs.

## Control Flow

During container creation, snapshotter is configured first, then `WithNewSnapshot` prepares the rootfs. On missing unpacked content, the wrapper performs an unpack under a lease and retries snapshot creation. `WithVolumes` retrieves snapshot mounts, removes volatile/idmap options, optionally activates mount manager transforms, mounts into a temporary directory, copies each volume source from rootfs into the matching empty host path, and unmounts/deactivates on return.

## State and Persistence Behavior

It creates snapshots in the configured snapshotter, may unpack image content into snapshotter state, creates temporary mount directories, and copies files into CRI-managed host volume directories. Leases protect content during unpack. Temporary mount directories are removed with `os.Remove`.

## Dependencies and Integration Points

It depends on containerd client, images/unpack/snapshots/mount APIs, continuity filesystem copy, snapshotter label helpers, errdefs, platform matching, and semaphores. `server/container_create.go` uses these opts during `client.NewContainer`.

## Risks and Edge Cases

The retry only handles not-found errors. `WithVolumes` refuses non-empty destinations, which prevents overwriting but can fail restore/create if cleanup is incomplete. Windows only copies volumes under C:. Mount/unmount or mount-manager deactivation failures are propagated carefully. Removing only the temp root directory avoids accidentally removing snapshot contents.

## Test Signals

Tests should cover not-found unpack retry, non-not-found propagation, snapshot label behavior, volume copy from rootfs, non-empty destination errors, Windows drive filtering, and cleanup on mount/deactivation failures.
