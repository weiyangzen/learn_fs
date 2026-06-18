<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/snapshots/snapshots.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/snapshots/snapshots.go

## Purpose
Implements `ctr snapshots` lifecycle, inspection, diffing, mount command generation, tree display, labels, and unpacking.

## Important APIs, Types, And Functions
Exports `Command`; defines list/diff/usage/delete/prepare/view/mounts/commit/tree/info/label/unpack commands, `withMounts`, snapshot tree helpers, and `printMounts`.

## Control Flow
Commands open a client and selected snapshotter, then call snapshot service methods. Diff creates a lease, compares mounted snapshots or rootfs diff, optionally roots content with labels, and streams layer bytes. Prepare/view/commit create snapshot records with optional GC root labels. Mounts prints mount commands, optionally via mount manager activation. Unpack locates an image by digest and applies layers.

## State And Persistence
Mutates snapshot metadata, content store uploads, leases, labels, mounts, and unpacked rootfs state; prints JSON/table/mount shell lines to stdout.

## Dependencies And Integration Points
Containerd snapshot/content/diff/rootfs APIs, leases, mount manager, progress formatting, digest parsing, OCI descriptors, tabwriter.

## Risks And Test Signals
`printMounts` is Unix-specific despite command availability; temporary view keys are best-effort removed; diff with `--keep` roots content with GC labels. No direct tests here; behavior is integration-sensitive. Source size reviewed: 680 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/snapshots/snapshots.go -->
