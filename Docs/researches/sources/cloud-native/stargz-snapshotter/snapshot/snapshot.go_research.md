<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/snapshot/snapshot.go -->
# sources/cloud-native/stargz-snapshotter/snapshot/snapshot.go

## Purpose
Implements a containerd snapshotter that behaves like overlayfs for normal snapshots and can internally commit remotely mounted lazy layers as snapshots.

## Important APIs, Types, And Functions
- `FileSystem` abstracts remote `Mount`, `Check`, and `Unmount` operations.
- Options: `AsynchronousRemove`, `NoRestore`, and `AllowInvalidMountsOnRestart`.
- `NewSnapshotter` initializes root, d_type support, metadata store, snapshot directory, userxattr detection, and remote restore.
- Snapshotter methods implement `Stat`, `Update`, `Usage`, `Prepare`, `View`, `Mounts`, `Commit`, `Remove`, `Walk`, `Cleanup`, and `Close`.
- Helpers include `createSnapshot`, `mounts`, `prepareRemoteSnapshot`, `checkAvailability`, and `restoreRemoteSnapshot`.

## Control Flow
`Prepare` first creates an active snapshot. If labels include `containerd.io/snapshot.ref`, it asks the remote filesystem to mount into the snapshot `fs` directory, labels it remote, commits it to the target name, logs preparation status, and returns `AlreadyExists` to containerd. Non-remote flows return bind or overlay mounts. `Mounts` and new child snapshots verify remote parent availability through `FileSystem.Check`.

## State And Persistence
Metadata lives in `metadata.db`; snapshot directories live under `root/snapshots/<id>/{fs,work}`. Remote snapshots are marked with labels and remounted on startup unless disabled. Cleanup unmounts through `FileSystem.Unmount` before removing directories.

## Dependencies And Integration Points
Built on containerd snapshot storage, overlay mount conventions, continuity disk usage, mountinfo, overlayutils, errdefs, and the stargz filesystem implementation. Log keys are consumed by scripts/tests.

## Risks And Edge Cases
Remote prepare failures fall back to local only before the remote filesystem has done work; commit failures after mount are returned without reusing the key. Startup force-unmounts mounts under the root before restoration. `AllowInvalidMountsOnRestart` can leave metadata for unusable layers. Parent availability checks run concurrently and any remote check failure makes the layer unavailable.

## Test Signals
Tests validate remote prepare/commit labels, overlay mounts over remote parents, failure detection through `Check`, overlayfs compatibility via containerd testsuite, bind/overlay mount options, view behavior, and root-required bind mount scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/snapshot/snapshot.go -->
